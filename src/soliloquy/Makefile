CC = gcc
CFLAGS = -g -Wall -Wextra


sockapi-server:
	$(MAKE) -C $@

clean:
	rm -rf __pycache__
	$(MAKE) -C sockapi-server $@

.PHONY: clean sockapi-server
