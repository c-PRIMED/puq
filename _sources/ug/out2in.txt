Using Output PDFs as Inputs
===========================

Often the output of one simulation needs to be used as an input parameter
in another simulation.  Currently the easiest way to do this is by
:doc:`analyze`.  You simply export the PDF as a json file, then in the next
simulation, import that json file as an input PDF.  This scenario is explained
in great detail in the next section, :doc:`correlated`.
