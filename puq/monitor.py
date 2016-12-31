from .util import vprint
from logging import info, debug, exception, warning, critical


class Monitor(object):
    pass


class QtMonitor(Monitor):
    def __init__(self, host):
        raise Exception('PyQt not installed')


class TextMonitor(Monitor):
    def start_job(self, cmd, id):
        vprint(2, "Executing '%s' as job %s" % (cmd, id))
