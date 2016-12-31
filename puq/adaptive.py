"""
h-Adaptive Stochastic Collocation
"""
from __future__ import absolute_import, division, print_function

import numpy as np
from puq.hdf import get_result, get_params, get_param_names
from puq.options import options
from puq.psweep import APSweep
from adap import uqsolver
from logging import info, debug, exception, warning, critical
import h5py, sys
from puq.util import process_data
from puq.pdf import PDF
import matplotlib
from puq.meshgridn import meshgridn
from puq.response import SampledFunc

class AdapStocColl(APSweep):
    """
    Class implementing h-Adaptive Stochastic Collocation.

    - **params** : Input list of :class:`Parameter`\s
    - **tol** : Tolerance.  Try 0.1 first, then decrease if further\
    accuracy is needed.
    - **max_iterations** : Maximum number of iterations to perform.\
    The method will loop, performaning additional calculations and\
    refining its results until either the specified tolerance is met,\
    or the number of iterations is *max_iterations*. Default\
    is None.
    - **level** : Interpolation level.  Default is 2
    - **sel** : Dimensional Selectivity. Default is 0.5.
    - **callback** : Optional function that is called every iteration.
    """

    def __init__(self, params, tol, max_iterations=None, level=2, sel=0.5, callback=None):
        APSweep.__init__(self)
        self.params = params
        self.level = level
        self.tol = tol
        self.sel = sel
        self.max_iter = max_iterations
        self._callback = callback
        self._uqsolver = uqsolver(params, level, tol, sel)


    def reinit(self):
        print("REINIT %s %s %s %s" % (self.params, self.level, self.tol, self.sel))
        APSweep.reinit(self)
        self._callback = None # FIXME
        self._uqsolver = uqsolver(self.params, self.level, self.tol, self.sel)
        for p in self.params:
            del p.values
        return True

    def extend(self, h5, args):
        from optparse import OptionParser
        debug(args)
        usage = "Usage: sweep extend [keyword args] hdf5_filename.\n"
        parser = OptionParser(usage)
        parser.add_option("--tol", type='float', default = self.tol)
        parser.add_option("--max_iter", type='int', default = self.max_iter)
        (opt, ar) = parser.parse_args(args=list(args))
        if opt.tol > self.tol:
            print("Error: Previous tolerance was %s. You cannot" % self.tol)
            print("increase the tolerance.")
            sys.exit(1)
        if opt.max_iter == self.max_iter and opt.tol == self.tol:
            print("Error: Tolerance and Iterations are unchanged.")
            print("Nothing to do here.")
            sys.exit(0)
        if opt.max_iter and self.max_iter and opt.max_iter < self.max_iter \
                and opt.tol == self.tol:
            print("Error: Previous iterations was %s. You cannot" % self.iter_max)
            print("decrease the iterations.")
            sys.exit(1)
        if opt.tol != self.tol:
            print("Changing tol from %s to %s" % (self.tol, opt.tol))
        if opt.max_iter != self.max_iter:
            print("Changing max_iter from  %s to %s" % (self.max_iter, opt.max_iter))
        self.tol = opt.tol
        self.max_iter = opt.max_iter
        self._sweep._reinit = True
        self.reinit()
        # Remove old results
        try:
            del h5['output/data']
        except:
            pass

        self._sweep.host.reinit()

    # Returns a list of name,value tuples
    # For example, [('t', 1.0), ('freq', 133862.0)]
    def get_args(self):
        par = self._uqsolver.iadaptiveparams()
        plist = par.tolist()
        if plist == []:
            return
        for i, p in enumerate(self.params):
            pcol = par[:, i]
            try:
                p.values.append(pcol)
            except AttributeError:
                p.values = [pcol]
        for row in plist:
            yield zip([p.name for p in self.params], row)

    def analyze(self, hf):
        process_data(hf, 'AdapStocColl', self._do_pdf)

    def iteration_cb(self, sw, iter):
        """
        Callback for each iteration.  The sweep method calls this for
        every iteration.  This method then calls its registered callback.
        """

        z = sw.get_result(iteration=iter)

        # fixme: z must be floats
        m, v, e = self._uqsolver.doiadaptive(z)

        """
        put mean, var, std, err, pdf in /AdapStocColl
        These will be indexed for each iteration, so
        /AdapStocColl/mean/1 will be the mean after iteration 1.
        """
        hf = h5py.File(sw._fname)
        try:
            hf['/AdapStocColl/mean/%d' % iter] = m
            hf['/AdapStocColl/variance/%d' % iter] = v
            hf['/AdapStocColl/std/%d' % iter] = np.sqrt(v)
            hf['/AdapStocColl/error/%d' % iter] = e
        except:
            pass
        # Call the callback, if defined
        if self._callback:
            finished = self._callback(iter, hf, z, m, v, e)
        else:
            finished = False
            if iter == 0:
                print("Iter        mean           var           dev        errind   points   cached")
            print("%d:    %.4e    %.4e    %.4e    %.4e    %5d    %5d"
                  % (iter, m, v, np.sqrt(v), e, self._num_jobs, self._num_jobs_cached))
        hf.close()
        if self.max_iter and iter >= self.max_iter:
            finished = True
        return finished

    # plot types:
    # surface - resampled using interpolate()
    # scatter - all points
    # scatter - for each iteration

    def plot_response(self, h5, ivars=''):
        fmt = options['plot']['format']
        if fmt == 'png' or fmt == 'i':
            load = options['plot']['iformat']
        else:
            load = fmt
        matplotlib.use(load, warn=False)
        import matplotlib.pyplot as plt

        if ivars:
            num_params = len(ivars)
        else:
            ivars = get_param_names(h5)
            num_params = len(ivars)

        if num_params > 2:
            print("Error: Cannot plot in more than three dimensions.")
            print("Use '-v' to select a subset of input parameters.")
            raise ValueError()

        if num_params > 1:
            self.scatter3(h5, ivars)
            self.scatter3(h5, ivars, iteration='sum')
        else:
            self.scatter2(h5, ivars[0])
            self.scatter2(h5, ivars[0], iteration='sum')

        if fmt == 'i':
            try:
                plt.show()
            except KeyboardInterrupt :
                pass

    def _do_pdf(self, hf, data):
        num = 10000
        params = get_params(hf['/'])
        ndims = len(params)
        pts = np.empty((num, ndims + 1))
        for i, p in enumerate(params):
            pts[:, i] = p.pdf.ds(num)
        self._uqsolver.interpolate(pts)

        rs = self.response_func()

        last_iter = self.iteration_num-1
        mean = hf['/AdapStocColl/mean/%d' % last_iter].value
        var = hf['/AdapStocColl/variance/%d' % last_iter].value
        std = hf['/AdapStocColl/std/%d' % last_iter].value
        error = hf['/AdapStocColl/error/%d' % last_iter].value

        return [('sampled_pdf', pts[:, -1]),
                ('mean', mean),
                ('dev', std),
                ('var', var),
                ('error', error),
                ('response_func', rs)]

    def response_func(self):
        iters = self.iteration_num
        ndims = len(self.params)

        # calculate the optimal flat grid based on the hierarchal grid
        vecs = []
        for p in self.params:
            x = []
            for iteration in range(0, iters):
                x = np.concatenate((x, p.values[iteration]))
            last = None
            mindist = 1e309
            for v in sorted(x):
                if v != last:
                    if last is not None:
                        mindist = min(mindist, v-last)
                    last = v
            debug("%s: %s %s grids" % (p.name, mindist,
                              (p.pdf.range[1] - p.pdf.range[0])/mindist))
            vecs.append(np.arange(p.pdf.range[0], p.pdf.range[1] + mindist, mindist))

        xx = meshgridn(*vecs)
        pts = np.vstack(map(np.ndarray.flatten, xx)).T

        # add column for results
        pts = np.append(pts, np.zeros((len(pts), 1)), axis=1)

        # interpolate function requires array in contiguous memory
        if pts.flags['C_CONTIGUOUS'] is False:
            pts = np.ascontiguousarray(pts)

        self._uqsolver.interpolate(pts)
        return SampledFunc(pts, params=self.params)

        """
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm
        import matplotlib.pyplot as plt
        fig = plot_figure()
        ax = Axes3D(fig, azim = 30, elev = 30)
        X = pts[:,0].reshape(xx[0].shape)
        Y = pts[:,1].reshape(xx[0].shape)
        try:
            Z = pts[:,2].reshape(xx[0].shape)
            ax.plot_surface(X,Y,Z, rstride = 1, cstride = 1, cmap=cm.jet, alpha = 0.5)
        except:
            plt.plot(X, Y, color='green')
        plt.show()
        """

"""
    def scatter2(self, hf, input_var='', output_var='', iteration='all'):
        import matplotlib.pyplot as plt
        from matplotlib import cm
        fmt = options['plot']['format']
        parameters =  hdf5_get_params(hf)
        parameter_names = [p.name for p in parameters]
        if input_var:
            ivar = [p for p in parameters if p.name == input_var][0]
        else:
            ivar = parameters[0]
        if not ivar:
            print "Error: Unrecognized input variable: %s" % input_var
            raise ValueError

        num_iterations = hdf5_get_iterations(hf)
        if iteration == 'all':
            for iteration in range(0, num_iterations):
                fig = plot_figure()
                plt.xlabel(ivar.description)
                data = hdf5_get_result(hf, var=output_var, iteration=iteration)
                plt.scatter(ivar.values[iteration], data)
                plt.suptitle("Iteration %s" % iteration)
                fig.canvas.manager.set_window_title("Iteration %s" % iteration)
        elif iteration == 'sum':
            fig = plot_figure()
            plt.xlabel(ivar.description)
            x = []
            y = []
            iters = []
            for iteration in range(0, num_iterations):
                x = np.concatenate((x, ivar.values[iteration]))
                tmp = np.empty((len(ivar.values[iteration])))
                tmp[:] = float(iteration)
                iters = np.concatenate((iters, tmp))
            data = hdf5_get_result(hf, var=output_var, iteration='sum')
            plt.scatter(x, data, c=iters, cmap=cm.jet)
            plt.suptitle("All %s Iterations" % num_iterations)
            fig.canvas.manager.set_window_title("All %s Iterations" % num_iterations)
        else:
            fig = plot_figure()
            plt.xlabel(ivar.description)
            plt.suptitle("Iteration %s" % iteration)
            fig.canvas.manager.set_window_title("Iteration %s" % iteration)
            data = hdf5_get_result(hf, var=output_var, iteration=iteration)
            plt.scatter(ivar.values[iteration], data, color='blue', alpha=.5)

        #plot_customize()
        if fmt != 'i':
            plt.savefig("%s-scatter[%s].%s" % (output_var, input_var, fmt))

    # 3D scatter plot
    # iteration='all', 'last', 'sum' or number
    def scatter3(self, hf, input_vars=[], output_var='', iteration='all'):
        print "scatter %s" % (input_vars)
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        from matplotlib import cm

        input_vars =  hdf5_get_params(hf, input_vars)
        outvars = hdf5_get_output_names(hf)
        outdesc = hdf5_prog_description(hf)
        if output_var and not output_var in outvars:
            print "Error: Unrecognized output variable: %s" % output_var
            return
        if not output_var:
            output_var = outvars[0]

        fmt = options['plot']['format']
        num_iterations = hdf5_get_iterations(hf)
        if iteration == 'all':
            for iteration in range(0, num_iterations):
                print "iteration: %s" % iteration
                fig = plot_figure()
                ax = Axes3D(fig, azim = 30, elev = 30)

                plt.xlabel(param_description(input_vars[0]))
                plt.ylabel(param_description(input_vars[1]))
                plt.suptitle("Iteration %s" % iteration)
                fig.canvas.manager.set_window_title("Iteration %s" % iteration)
                x = np.array(input_vars[0].values[iteration])
                y = np.array(input_vars[1].values[iteration])
                odata = hdf5_get_result(hf, var=output_var, iteration=iteration)
                ax.scatter(x, y, odata, linewidths=(2.,))
                ax.set_zlabel(hdf5_data_description(hf, output_var))
        elif iteration == 'sum':
            fig = plot_figure()
            ax = Axes3D(fig, azim = 30, elev = 30)
            ax.set_zlabel(hdf5_data_description(hf, output_var))
            x = []
            y = []
            iters = []
            for iteration in range(0, num_iterations):
                x = np.concatenate((x, input_vars[0].values[iteration]))
                y = np.concatenate((y, input_vars[1].values[iteration]))
                tmp = np.empty((len(input_vars[0].values[iteration])))
                tmp[:] = float(iteration)
                iters = np.concatenate((iters, tmp))
            odata = hdf5_get_result(hf, var=output_var, iteration='sum')
            ax.scatter(x, y, odata, c=iters, cmap=cm.jet)
            plt.xlabel(param_description(input_vars[0]))
            plt.ylabel(param_description(input_vars[1]))
            plt.suptitle("All %s Iterations" % num_iterations)
            fig.canvas.manager.set_window_title("All %s Iterations" % num_iterations)
        else:
            print "iteration: %s" % iteration
            fig = plot_figure()
            ax = Axes3D(fig, azim = 30, elev = 30)

            plt.xlabel(param_description(input_vars[0]))
            plt.ylabel(param_description(input_vars[1]))
            plt.suptitle("Iteration %s" % iteration)
            fig.canvas.manager.set_window_title("Iteration %s" % iteration)
            x = np.array(input_vars[0].values[iteration])
            y = np.array(input_vars[1].values[iteration])

            odata = hdf5_get_result(hf, var=output_var, iteration=iteration)
            ax.scatter(x, y, odata, linewidths=(2.,))
            ax.set_zlabel(hdf5_data_description(hf, output_var))

        #plot_customize()
        if fmt != 'i':
            plt.savefig("%s-scatter.%s" % ('test', fmt))


    def plot_pdfs(self, h5, kde, hist, vars):
        from plot import plot_pdf
        fmt = options['plot']['format']
        if fmt == 'png' or fmt == 'i':
            load = options['plot']['iformat']
        else:
            load = fmt
        matplotlib.use(load, warn=False)
        import matplotlib.pyplot as plt

        if vars:
            print "Plotting PDFs with a subset of variables"
            print "is not implemented yet."
            return

        title = hdf5_prog_description(h5)
        var = hdf5_get_output_names(h5)[0]
        xlabel = hdf5_data_description(h5, var)
        data = h5['AdapStocColl/%s/sampled_pdf' % var].value
        plot_pdf(data, kde, hist, title, xlabel, var)
        if fmt == 'i':
            try:
                plt.show()
            except KeyboardInterrupt :
                pass
"""
