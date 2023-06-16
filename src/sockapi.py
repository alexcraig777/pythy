""" Interface for calling functions in a shared object over a socket """


import ctypes
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
    fmt_map = {ctypes.c_char: "c",
        ctypes.c_short: "h",
        ctypes.c_int: "i",
        ctypes.c_long: "l",
        ctypes.c_size_t: "N",
        ctypes.c_void_p: "p"}

    def __init__(self, lib, host = "localhost", port = 55555,
                 debug = True):
        self.lib = lib
        self.host = host
        self.port = port
        self.debug = debug
        self.start_server()

    def start_server(self):
        """ Actually kick off the C-side of the API in a new process """
        # Detect if either `sockapi` or `self.lib` don't exist.
        with open("sockapi-server/sockapi") as f:
            pass
        with open(self.lib) as f:
            pass

        cmd = f"sockapi-server/sockapi {self.lib} {self.host} {self.port}"

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

    def call(self, func_name, rtn_type, args, arg_types):
        """ Call `func_name` over the socket

        All types should be ctypes types. The valid integer types are
        given in the class attribute `fmt_map`; all such arguments are
        passed as 8-byte, big-endian byte strings. The only other valid
        type is `ctypes.c_chap_p`; such arguments are passed as length-
        prefixed byte arrays. """

        # First, send the "call" directive.
        self.sock.send_all(b"call")
        # Next, send the name, preceeded by its length.
        self.sock.send_msg(func_name.encode())

        # Next, send the number of arguments as a 4-byte int.
        self.sock.send_all(struct.pack("!I", len(args)))

        # Next, send each argument, preceeded by a type flag.
        for arg, ctype in zip(args, arg_types):
            if ctype == ctypes.c_char_p:
                self.sock.send_msg(arg)
            else:
                self.sock.send_all(struct.pack("!i", -1))
                self.sock.send_all(self._encode_arg(arg, ctype))

        # Next, send `0` for a string return or `1` for an int return.
        if rtn_type == ctypes.c_char_p:
            rtn_flag = 0
        else:
            rtn_flag = 1
        self.sock.send_all(struct.pack("!I", rtn_flag))

        # And now we can receive the return value.
        if rtn_type == ctypes.c_char_p:
            rtn = self.sock.recv_msg()
        else:
            rtn = self.sock.recv_all(8)
            rtn = self._decode_rtn(rtn, rtn_type)

        return rtn

    def make_function(self, name, arg_types, rtn_type):
        """ Create and return a function that automatically converts
        its arguments, calls into the shared object, and converts the
        output """
        def func(*args):
            rtn = self.call(name, rtn_type, args, arg_types)
            return rtn
        return func

    @classmethod
    def _encode_arg(cls, arg, ctype):
        """ Encode `arg` as a `ctype` integer

        This verifies that `arg` fits in the byte-size indicated by `ctype`,
        but it then returns an 8-byte big-endian byte string that can be
        passed over a socket.
        This should only be used for integer types. """

        b = struct.pack("!" + cls.fmt_map[ctype], arg)
        b = b"\x00" * (8 - len(b)) + b
        return b

    @classmethod
    def _decode_rtn(cls, rtn, ctype):
        """ Decode `rtn` as a `ctype` integer

        `rtn` will always be an 8-byte, big-endian byte string.
        This verifies that the unused bytes of `rtn` are 0. """

        fmt = "!" + cls.fmt_map[ctype]

        n = struct.calcsize(fmt)
        z, b = rtn[:-n], rtn[-n:]
        if any(z):
            print(rtn)
            raise ValueError("`rtn` (see above) is not a valid", ctype)

        return struct.unpack(fmt, b)[0]


if __name__ == "__main__":
    s = Session("../test/funcs.so", "localhost", debug=True)

    add = s.make_function("interface_add",
                          [ctypes.c_int, ctypes.c_int],
                          ctypes.c_int)

    x = add(4, 5)
    print("Received 4 + 5 =", x)

    y = add(9, -16)
    print("Received 9 + -16 =", y)

    cat = s.make_function("interface_concatenate",
                          [ctypes.c_char_p, ctypes.c_char_p],
                          ctypes.c_char_p)

    mc = cat(b"madison", b" craig")
    print("Received b'madison' + b' craig' = ", mc.decode())

    s.stop_server()
