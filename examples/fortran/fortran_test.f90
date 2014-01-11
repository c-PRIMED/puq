program fortran_test
use dump_hdf5
implicit none

integer, parameter :: dp = kind(1.0d0)
real(dp) x, y, z
integer :: i, count
character(len=32) :: argbuf

count = command_argument_count()

!Reading the command line argument
do i = 1, count-1, 2

	call get_command_argument(i, argbuf)
	! print *, argbuf

	select case(argbuf)
		case('-x')
			call get_command_argument(i+1, argbuf)
			read(argbuf,'(F20.0)') x
			! write(*,*) 'x=',x

		case('-y')
			call get_command_argument(i+1, argbuf)
			read(argbuf,'(F20.0)') y
			! write(*,*) 'y=', y

	end select
end do

! Rosenbrock function
z = 100.0 * (y - x**2)**2 + (1.0 - x)**2

! dump variable. Description is optional.
call dump_hdf5_d("z", z, "The value of the Rosenbrock function")

end program fortran_test
