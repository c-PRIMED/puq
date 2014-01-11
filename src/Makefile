.PHONY : all clean
all: sparse_grid_cc

sparse_grid_cc:	sg_main.o sparse_grid_cc.o
	$(CXX) -O3 -o $@ $^

clean:
	$(RM) *.o *~ sparse_grid_cc

