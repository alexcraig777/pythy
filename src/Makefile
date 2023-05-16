CC = gcc
CFLAGS = -g -Wall -Wextra


sockapi/sockapi: sockapi/sockapi.c sockapi/socklib.c sockapi/dispatcher.o
	$(CC) $(CFLAGS) $^ -o $@

sockapi/dispatcher.o: sockapi/dispatcher.asm
	nasm -f elf64 -F dwarf -g $^ -o $@

clean:
	rm -rf __pycache__ sockapi/*.o sockapi/sockapi
