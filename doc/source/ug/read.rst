Using PUQ Read
==============

Use **puq read** to read parameters, PDFs, and response surfaces from json files or
python control scripts.  ::

	~/puq/examples/basic> puq read -h
	Usage: puq read [options] [object] ...
	    where 'object' is a URI, python file, or JSON file

	Options:
	  -h, --help  show this help message and exit
	  -c          Compare plots.

	~/puq/examples/basic> puq read basic.py

	List PDFs you want displayed, separated by commas.

	Found the following PDFs:
	0: x
	1: y
	Which one(s) to display? (* for all) *

You can use *puq analyze* to save PDFs to json files, then *puq read* to compare them.
Or you can compare input parameters from a control file. ::

	~/puq/examples/basic> puq read -c f.json g.json

.. figure:: images/compare.png
   :align: left
