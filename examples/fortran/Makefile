FC = gfortran

.SUFFIXES: .f90
.f90.o: ;
	$(FC) -c $*.f90

objs = ../../puqutil/dump_hdf5.f90 fortran_test.f90 

all: fortran_test

fortran_test : $(objs)
	$(FC) -o $@ $^

.PHONY : clean
clean :
	$(RM) fortran_test $(objs)
