module dump_hdf5
contains

! dump double presision number
subroutine  dump_hdf5_d(name, val, desc)
	implicit none
	integer, parameter :: dp = kind(1.0d0)
	character(len=*), parameter :: fmt = "(3A, E20.7E2, 3A)"
	real(dp), intent(in) :: val
	character(len=*) :: name, desc

	write(*,fmt) "HDF5:{'name':'", name, "','value':", val, ",'desc':'", desc, "'}:5FDH"
end subroutine  dump_hdf5_d

end module dump_hdf5
