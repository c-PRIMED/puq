#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

#include "dump_hdf5.h"

int main(int argc, char *argv[]) {
	int c;
	double x, y, z;
	while ((c = getopt(argc, argv, "x:y:")) != -1)
		switch (c) {
		case 'x':
			x = atof(optarg);
			break;
		case 'y':
			y = atof(optarg);
			break;
		default:
			printf("Usage: %s -x val -y val\n", argv[0]);
			return(1);
		}

	/* compute rosenbrock function */
	z = 100.0 * (y - x*x)*(y - x*x) + (1.0 - x)*(1.0 - x);

	dump_hdf5_d("z", z, "f(x,y)");

	/* important! return code of 0 indicates success */
	return 0;
}
