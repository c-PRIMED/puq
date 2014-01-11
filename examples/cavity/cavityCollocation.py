#!/usr/bin/env python

import optparse
import fvm
import fvm.fvmbaseExt
from mpi4py  import MPI
fvm.set_atype('double')

from FluentCase import FluentCase

## this is our random  parameter
usage = "usage: %prog --v viscosity"
parser = optparse.OptionParser(usage)
parser.add_option("--v", type=float)
(options, args) = parser.parse_args()
viscosity = options.v
print "viscosity =",viscosity

numIterations = 300
fileBase = "cav20"

reader = FluentCase(fileBase+".cas")

reader.read();

meshes = reader.getMeshList()

geomFields =  fvm.models.GeomFields('geom')
metricsCalculator = fvm.models.MeshMetricsCalculatorA(geomFields,meshes)

metricsCalculator.init()

flowFields =  fvm.models.FlowFields('flow')

fmodel = fvm.models.FlowModelA(geomFields,flowFields,meshes)

reader.importFlowBCs(fmodel)

foptions = fmodel.getOptions()


foptions.momentumTolerance=1e-5
foptions.continuityTolerance=1e-5
foptions.setVar("momentumURF",0.7)
foptions.setVar("pressureURF",0.3)

vcMap = fmodel.getVCMap()
for i,vc in vcMap.iteritems():
    vc.setVar('viscosity',viscosity)

fmodel.init()


fmodel.advance(numIterations)

## the indices of cells at x=0.5 and y=0.5 line on a RCM ordered 40x40 mesh
x_eq_0_5_line_cells = [  65,  76,  88,  101,  115,  130,  146,  163,  181,
                         200,  219,  237,  254,  270,  285,  299,  312,
                         324,  335,  345]

y_eq_0_5_line_cells = [  45 ,56 ,68 ,81 ,95 ,110,126,143,161,180,200,
                         220,239,257,274,290,305,319,332,344]

mesh0 = meshes[0]
vCells = flowFields.velocity[mesh0.getCells()].asNumPyArray()

## these are the four arrays with u and v velocity data that we want
## to post process to produce the mean and variances of

u_x_eq_0_5 = vCells[x_eq_0_5_line_cells,0]
v_x_eq_0_5 = vCells[x_eq_0_5_line_cells,1]

u_y_eq_0_5 = vCells[y_eq_0_5_line_cells,0]
v_y_eq_0_5 = vCells[y_eq_0_5_line_cells,1]


### the following code writes the above data in format suitable for
### plotting in Fluent. Replace this as needed to do our post processing

from puqutil import dump_hdf5
#dump_hdf5('Viscosity', viscosity)
dump_hdf5('u_x_eq_0_5', u_x_eq_0_5 , 'u velocity where x = 0.5')
dump_hdf5('v_x_eq_0_5', v_x_eq_0_5)
dump_hdf5('u_y_eq_0_5', u_y_eq_0_5)
dump_hdf5('v_y_eq_0_5', v_y_eq_0_5)

