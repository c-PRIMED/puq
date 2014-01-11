.PHONY : all clean
all: zeta

zeta:	zeta.c
	mpicc -O3 -o $@ $^ -lm

clean:
	$(RM) *.o *~ zeta

