CC = gcc
CFLAGS = -g -Wall -Wextra

libs = stuff

$(libs).o: %.o: %.c
	$(CC) $(CFLAGS) -fPIC $^ -c -o $@

$(libs).so: %.so: %.o
	$(CC) $< -shared -o $@

clean:
	rm -rf __pycache__ .pytest_cache
	rm -f *.o *.so
