CC=gcc
CFLAGS=-I. -W -Wall -Wextra -Wuninitialized -Wstrict-aliasing -march=native
LDLIBS=-lpthread -lnuma -lm

DEPS=utils.h
OBJ=utils.o main.o

.PHONY: all
all: bench

%.o: %.c $(DEPS)
	$(CC) $(INCLUDES) -c -o $@ $< $(CFLAGS)

bench: $(OBJ)
	$(CC) $(INCLUDES) -o $@ $^ $(CFLAGS) $(LDLIBS)

.PHONY: clean
clean:
	$(RM) *~ *.o bench
