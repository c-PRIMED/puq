#include <stdio.h>
#include <math.h>
#include <sys/time.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <mpi.h>

#include "dump_hdf5.h"

void usage(char *name)
{
  fprintf(stderr, "Usage: %s -n n\n", name);
  fprintf(stderr, "Calculates zeta(n)\n");
  exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
  double sum, p_sum, pi, pi_exact;
  int opt, n=2;
  int tid, nthreads;
  char cpu_name[80];
  long i, loop_max, loop_min, iterations = 0;

  sum = 0.0;
  p_sum	= 0.0;
  pi_exact = 4.0*atan(1.0);
  iterations = 1e9;

  while ((opt = getopt(argc, argv, "n:")) != -1) {
    switch (opt) {
    case 'n':
      n = atoi(optarg);
      break;
    default:
      usage(argv[0]);
    }
  }

  if (n < 0)
    usage(argv[0]);

  MPI_Init(&argc,&argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &tid);
  MPI_Comm_size(MPI_COMM_WORLD, &nthreads);

  gethostname(cpu_name, sizeof(cpu_name));
  printf("tid=%d of %d: running on machine = %s\n",tid, nthreads, cpu_name);


  loop_min 	= 1 +  (long)((tid + 0)  *  (iterations-1)/nthreads);
  loop_max	=      (long)((tid + 1)  *  (iterations-1)/nthreads);

  for(i=loop_max-1; i>=loop_min; i--)
    p_sum += 1.0/pow(i,(double)n);

  MPI_Reduce(&p_sum,&sum,1,MPI_DOUBLE,MPI_SUM,0,MPI_COMM_WORLD);
  MPI_Finalize();

  if (tid == 0) {
    printf("zeta(%d)  = %-.15f \n",n,sum);
    dump_hdf5_d("z", sum, "zeta");
  }

  return 0;
}
