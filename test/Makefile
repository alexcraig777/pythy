# This Makefile has 3 main rules:
#  1. libs (default): Build the shared objects needed by the tests.
#  2. test: Run the pytests
#  3. clean: Clean the directory.
#
# To run `test`, we must be in a Python environment where the
# package is already installed.

CC = gcc
CFLAGS = -g -Wall -Wextra

# These are the library names that are required for testing.
libs = funcs classes

libs_so = $(foreach lib, $(libs), $(lib).so)
libs_o  = $(foreach lib, $(libs), $(lib).o)

libs: $(libs_so)

test: libs
	pytest

$(libs_o): %.o: %.c
	$(CC) $(CFLAGS) -fPIC $^ -c -o $@

$(libs_so): %.so: %.o
	$(CC) $< -shared -o $@

clean:
	rm -rf __pycache__ .pytest_cache
	rm -f *.o *.so

.PHONY: libs test clean
