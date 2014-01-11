#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
using namespace std;

#include "sparse_grid_cc.h"

using namespace webbur;

void usage(char *name)
{
  cerr << "Usage: " << name << " -d dims -l levels\n\n";
  cerr << "Prints sparse Clenshaw Curtis grid points and weights.\n";
  exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{
  int opt;
  int dim_num=0, level_max=0;
  double *grid_point;
  double *grid_weight;
  int point, dim;
  int point_num;

  while ((opt = getopt(argc, argv, "d:l:")) != -1) {
    switch (opt) {
    case 'd':
      dim_num = atoi(optarg);
      break;
    case 'l':
      level_max = atoi(optarg);
      break;
    default: 
      usage(argv[0]);
    }
  }

  if (dim_num == 0 || level_max == 0)
      usage(argv[0]);
    
  point_num = webbur::sparse_grid_cc_size ( dim_num, level_max );

  //
  //  Allocate space for the weights and points.
  //
  grid_weight = new double[point_num];
  grid_point = new double[dim_num*point_num];
  //
  //  Compute the weights and points.
  //
  webbur::sparse_grid_cc ( dim_num, level_max, point_num, grid_weight, grid_point );
  //
  //  Print them out.
  //
  cout.precision(16);
  for (point = 0; point < point_num; point++ ) {
    for ( dim = 0; dim < dim_num; dim++ ) {
      cout << setw(24) << grid_point[dim+point*dim_num];
    }
    cout << setw(24) << grid_weight[point] << endl;
  }

  delete [] grid_point;
  delete [] grid_weight;
  return 0;
}
