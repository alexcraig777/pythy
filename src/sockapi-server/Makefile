CC = gcc
CFLAGS = -g -Wall -Wextra

sockapi: sockapi.c socklib.c dispatcher.o
	$(CC) $(CFLAGS) $^ -o $@

dispatcher.o: dispatcher.asm
	nasm -f elf64 -g -F dwarf $^ -o $@

clean:
	rm -rf *.o sockapi
