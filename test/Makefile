CC = gcc
CFLAGS = -g -Wall -Wextra

# These are the library names that are required for testing.
libs = funcs classes

libs_so = $(foreach lib, $(libs), $(lib).so)
libs_o  = $(foreach lib, $(libs), $(lib).o)

test: all
	pytest

all: $(libs_so)

$(libs_o): %.o: %.c
	$(CC) $(CFLAGS) -fPIC $^ -c -o $@

$(libs_so): %.so: %.o
	$(CC) $< -shared -o $@

clean:
	rm -rf __pycache__ .pytest_cache
	rm -f *.o *.so

.PHONY: test all clean
