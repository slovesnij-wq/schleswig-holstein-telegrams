CC ?= cc
CFLAGS ?= -O3

all: search known_solve

search: search.c
	$(CC) $(CFLAGS) -o $@ $<

known_solve: known_solve.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f search known_solve

.PHONY: all clean
