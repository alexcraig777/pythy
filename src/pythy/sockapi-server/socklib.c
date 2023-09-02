#include "socklib.h"

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <dlfcn.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


// Receive exactly `n` bytesh from `sockfd` into `buf`.
int recv_n(int sockfd, void* buf, uint32_t n) {
    size_t received = 0;
    int recv_rtn;
    while (received < n) {
        recv_rtn = recv(sockfd, (char*) buf + received, n - received, 0);
        if (recv_rtn == -1) {
            printf("Error in recv!\n");
            received = -1;
            break;
        } else if (recv_rtn == 0) {
            printf("Socket closed!\n");
            break;
        }
        received += recv_rtn;
    }
    return received;
}

// Receive a message prefixed with its length.
//
// The returned buffer must be freed by the callee.
// The buffer contains the data sent over the socket followed by a
// null byte.
void* recv_msg(int sockfd) {
    uint32_t len;
    void* buf;

    recv_n(sockfd, &len, sizeof(len));
    len = ntohl(len);

    buf = malloc(len + 1);
    ((char*) buf)[len] = 0;
    recv_n(sockfd, buf, len);

    return buf;
}

// Send exactly `n` bytes from `buf` over `sockfd`.
int send_n(int sockfd, void* buf, uint32_t n) {
    uint32_t sent = 0;
    int send_rtn;
    while (sent < n) {
        send_rtn = send(sockfd, (char*) buf + sent, n - sent, 0);

        if (send_rtn == -1) {
            printf("Error in send!\n");
            sent = -1;
            break;
        } else if (send_rtn == 0) {
            printf("Socket closed!\n");
            break;
        }
        sent += send_rtn;
    }
    return sent;
}

// Send a message prefixed with its length.
int send_msg(int sockfd, char* msg) {
    uint32_t len = strlen(msg);
    uint32_t bytes_to_send = len;
    int rtn;

    len = htonl(len);
    send_n(sockfd, &len, sizeof(len));

    rtn = send_n(sockfd, msg, bytes_to_send);

    return rtn;
}


// Make the connection to the Python side.
//
// Returns the socket file descriptor for the connection.
int make_connection(char* host, char* port) {
    struct addrinfo hints;
    struct addrinfo* result;
    struct sockaddr client_addr;
    socklen_t client_addr_size = sizeof(client_addr);
    int sub_rtn;
    int yes = 1;
    int listen_sock;
    int rtn_sock;


    // Set up the hints for `getaddrinfo`.
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    hints.ai_protocol = 0;
    hints.ai_canonname = NULL;
    hints.ai_addr = NULL;
    hints.ai_next = NULL;

    //printf("Getting addrinfo for %s:%s\n", host, port);

    // Get the actual address we can bind to.
    sub_rtn = getaddrinfo(host, port, &hints, &result);
    if (sub_rtn != 0) {
        printf("Failed to get address :(\n");
        listen_sock = -1;
    } else {
        listen_sock = socket(AF_INET, SOCK_STREAM, 0);
    }

    // Bind to the address.
    if (listen_sock != -1) {
        setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes);
        sub_rtn = bind(listen_sock, result->ai_addr, result->ai_addrlen);

        if (sub_rtn != 0) {
            printf("Could not bind to %s:%s\n", host, port);
            close(listen_sock);
            listen_sock = -1;
        }
    }

    // Listen.
    if (listen_sock != -1) {
        sub_rtn = listen(listen_sock, 1);
        if (sub_rtn != 0) {
            printf("Could not listen :(\n");
            close(listen_sock);
            listen_sock = -1;
        }
    }

    //printf("About to accept!\n");

    // Accept.
    if (listen_sock != -1) {
        rtn_sock = accept(listen_sock, &client_addr,
                           &client_addr_size);
        //printf("Accepted %d\n", rtn_sock);
        close(listen_sock);
    } else {
        rtn_sock = -1;
    }

    if (rtn_sock == -1) {
        printf("Could not accept connection from client :(\n");
    }

    freeaddrinfo(result);

    return rtn_sock;
}
