CC = gcc
CFLAGS = -g -Wall -Wextra

sockapi: sockapi.c socklib.c dispatcher.s
	$(CC) $(CFLAGS) $^ -o $@

clean:
	rm -rf sockapi
