.PHONY : all clean
all: rosen_cprog

rosen_cprog:	rosen_cprog.o
	$(CXX) -O3 -o $@ $^

clean:
	$(RM) *.o *~ rosen_cprog

