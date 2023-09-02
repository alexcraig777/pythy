#include <arpa/inet.h>
#include <dlfcn.h>
#include <endian.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "dispatcher.h"
#include "socklib.h"


#define RTN_VOID 0
#define RTN_INT  1
#define RTN_STR  2


// Private function declarations.
static int handle_call(int sockfd, void* lib);


int main(int argc, char** argv) {
    void* lib = NULL;
    int sockfd = -1;
    int rtn = 0;
    char directive[4];

    if (argc < 3) {
        printf("Usage: %s <library> <bind ip> <bind port>\n", argv[0]);
        rtn = -1;
    } else {
        lib = dlopen(argv[1], RTLD_LAZY);
        if (lib == NULL) {
            printf("Couldn't load library %s\n", argv[1]);
            rtn = -1;
        }
    }

    if (rtn == 0) {
        sockfd = make_connection(argv[2], argv[3]);

        if (sockfd == -1) {
            printf("Failed to make the connection :(\n");
            rtn = -1;
        }
    }

    // TODO: Clarify when to break.
    while (rtn == 0) {
        recv_n(sockfd, directive, sizeof(directive));
        if (strncmp(directive, "call", 4) == 0) {
            rtn = handle_call(sockfd, lib);
        } else if (strncmp(directive, "exit", 4) == 0) {
            //printf("Received request to exit\n");
            break;
        } else {
            //printf("Received unknown directive `%4s`\n",
            //       directive);
            break;
        }
    }

    if (lib != NULL) {
        dlclose(lib);
    }

    if (sockfd != -1) {
        close(sockfd);
    }

    return rtn;
}


// Private functions.
static int handle_call(int sockfd, void* lib) {
    char* func_name;
    uint32_t num_args;
    uint32_t* arg_types;
    uint32_t rtn_type;

    void** args;

    void* func_addr;
    void* func_rtn = (void*) -1;

    int rtn = 0;

    // Receive the length-prefixed function name.
    func_name = recv_msg(sockfd);

    // Receive the 4-byte number of args.
    recv_n(sockfd, &num_args, sizeof(num_args));
    num_args = ntohl(num_args);

    // Allocate space for the arguments.
    args = calloc(num_args < 6 ? 6: num_args, sizeof(*args));
    arg_types = calloc(num_args, sizeof(*arg_types));

    uint32_t i;
    for (i = 0; i < num_args; i++) {
        // Receive the 4-byte argument type.
        // This is (uint32_t) (-1) for int, and the length for strings.
        recv_n(sockfd, arg_types + i, sizeof(*arg_types));
        arg_types[i] = ntohl(arg_types[i]);

        // If the arg type is -1, the argument itself is an 8-byte
        // integer; otherwise the argument type represents the length
        // of the following string.
        if (arg_types[i] == (uint32_t) -1) {
            recv_n(sockfd, args + i, sizeof(args[i]));
            args[i] = (void*) be64toh((uint64_t) args[i]);

            //printf("Received integer argument #%d: %ld (0x%lx)\n", i,
            //       (uint64_t) args[i], (uint64_t) args[i]);
        } else {
            args[i] = calloc(arg_types[i] + 1, 1);
            recv_n(sockfd, args[i], arg_types[i]);
            //printf("Received string argument #%d: %s\n",
            //       i, (char*) args[i]);
        }
    }

    // Finally, receive the return type.
    recv_n(sockfd, &rtn_type, sizeof(rtn_type));
    rtn_type = ntohl(rtn_type);

    func_addr = dlsym(lib, func_name);

    if (func_addr == NULL) {
        //printf("Unknown function: %s\n", func_name);
        rtn = -1;
    } else {
        func_rtn = call_func(func_addr, num_args, args);

        if (rtn_type == RTN_STR) {
            // The return value is a string, so we need to send back
            // a message.
            send_msg(sockfd, func_rtn);
        } else if (rtn_type == RTN_INT) {
            // The return value is an integer.
            func_rtn = (void*) be64toh((uint64_t) func_rtn);
            send_n(sockfd, &func_rtn, sizeof(func_rtn));
        }
    }

    // Free the function name.
    free(func_name);

    // Free all the received arguments.
    for (i = 0; i < num_args; i++) {
        if (arg_types[i] != (uint32_t) -1) {
            free(args[i]);
        }
    }

    free(args);
    free(arg_types);

    return rtn;
}
