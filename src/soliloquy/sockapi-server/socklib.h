#ifndef SOCKLIB_H
#define SOCKLIB_H

#include <stdint.h>


// Receive exactly `n` bytes from `sockfd` into `buf`.
int recv_n(int sockfd, void* buf, uint32_t n);

// Receive a message prefixed with its length.
//
// The returned buffer must be freed by the callee.
// The buffer contains the data sent over the socket followed by a
// null byte.
void* recv_msg(int sockfd);

// Send exactly `n` bytes from `buf` over `sockfd`.
int send_n(int sockfd, void* buf, uint32_t n);

// Send a message prefixed with its length.
int send_msg(int sockfd, char* msg);


// Make the connection to the Python side.
//
// Returns the socket file descriptor for the connection.
int make_connection(char* host, char* port);

#endif
