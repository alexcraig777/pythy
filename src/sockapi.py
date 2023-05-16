import multiprocessing
import os
import socket
import struct
import time

class Socket:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.recv_buf = b""

    def close(self):
        self.sock.close()

    def send_all(self, buffer):
        """ Send all the bytes in `buffer` """
        while buffer:
            bytes_sent = self.sock.send(buffer)
            buffer = buffer[bytes_sent:]

    def send_msg(self, msg):
        """ Send `msg` preceeded by its length """
        self.send_all(struct.pack("!I", len(msg)))
        self.send_all(msg)

    def recv_all(self, length):
        """ Receive `length` bytes """
        while len(self.recv_buf) < length:
            self.recv_buf += self.sock.recv(length - len(self.recv_buf))
        rtn = self.recv_buf[:length]
        self.recv_buf = self.recv_buf[length:]
        return rtn

    def recv_msg(self):
        """ Receive a message, preceeded by its length """
        len_bytes = self.recv_all(4)
        length = struct.unpack("!I", len_bytes)[0]
        msg = self.recv_all(length)
        return msg


class Session:
    def __init__(self, lib, host = "localhost", port = 55555,
                 debug = True):
        self.lib = lib
        self.host = host
        self.port = port
        self.debug = debug
        self.start_server()

    def start_server(self):
        """ Actually kick off the C-side of the API in a new process """
        # Detect if either `./sockapi` or `self.lib` don't exist.
        with open("sockapi/sockapi") as f:
            pass
        with open(self.lib) as f:
            pass

        cmd = f"sockapi/sockapi {self.lib} {self.host} {self.port}"

        if self.debug:
            vg = "valgrind --leak-check=full"
            vg += " --track-origins=yes --show-leak-kinds=all "
            cmd = vg + cmd

        args = cmd.split()
        args.insert(0, args[0])
        self.server_process = multiprocessing.Process(target = os.execlp,
                                                      args = args)
        self.server_process.start()

        # TODO: We somehow need to give the server enough time to start
        # up before trying to connect to it. We could make it a client
        # rather than a server, but we'd still need to know how long to
        # wait before timing out.
        time.sleep(2)

        # TODO: Why does this sometimes fail to connect?
        self.sock = Socket(self.host, self.port)


    def stop_server(self):
        """ Send the exit command to the server process and join with it """
        self.sock.send_all(b"exit")
        self.server_process.join()
        self.sock.close()

    def call(self, func_name, rtn_type, *args):
        """ Call `func_name` over the socket

        `rtn_type` can be `int` or `str` """
        # First, send the "call" directive.
        self.sock.send_all(b"call")
        # Next, send the name, preceeded by its length.
        self.sock.send_msg(func_name.encode())

        # Next, send the number of arguments as a 4-byte int.
        self.sock.send_all(struct.pack("!I", len(args)))

        # Next, send each argument, preceeded by a type flag.
        for arg in args:
            # We don't accept strings: only bytes!
            if not isinstance(arg, bytes) and not isinstance(arg, int):
                print(f"Argument '{arg}' has incorrect type!")
                raise TypeError("Arguments must be ints or bytes!")
            if isinstance(arg, bytes):
                self.sock.send_msg(arg)
            else:
                if arg < 0:
                    arg += 1 << 64
                self.sock.send_all(struct.pack("!iQ", -1, arg))

        # Next, send `0` for a string return or `1` for an int return.
        if rtn_type == str:
            rtn_flag = 0
        else:
            rtn_flag = 1
        self.sock.send_all(struct.pack("!I", rtn_flag))

        # And now we can receive the return value.
        if rtn_type == str:
            rtn = self.sock.recv_msg()
        else:
            rtn = struct.unpack("!Q", self.sock.recv_all(8))[0]

        return rtn


if __name__ == "__main__":
    s = Session("../test/funcs.so", "localhost", debug=True)

    x = s.call("interface_add", int, 4, 5)
    print("Received x =", x)

    y = s.call("interface_add", int, 9, -16)
    print("Received y =", y)

    a = s.call("interface_concatenate", str,
               b"madison ", b"craig!")
    print("Received a =", a)

    s.stop_server()
