Using The PBS Scheduler
=======================

.. currentmodule:: puq

There are two different ways to run PUQ on compute clusters.

Batch Scripts
-------------
The first method uses a batch script to run PUQ.  The PUQ control script uses :class:`InteractiveHost`
like normal.  A typical PBS script would look like this::

	#!/bin/bash -l
	#PBS -q standby
	#PBS -l nodes=1:ppn=48
	#PBS -l walltime=0:02:00
	#PBS -o run_pbs.pbsout
	#PBS -e run_pbs.pbserr
	cd  $PBS_O_WORKDIR
	source /scratch/prism/memosa/env-hansen.sh
	puq start my_control_script

Of course you need to set the walltime, nodes and ppn for your run.

Using PBSHost
-------------

Another way to use PUQ with clusters is by using :class:`PBSHost`.
This method runs a PUQ monitor process on the frontend which submits PBS or Moab jobs
as needed. This allows you to monitor the progress of PUQ.  The disadvantage of this
approach is that submission of new batch jobs stops if the PUQ monitor is killed.

To use PBSHost, in any script where you see::

	host = InteractiveHost()

simply replace **InteractiveHost** with **PBSHost**.  You will need to give
PBSHost a few additional arguments.

- **env** : Bash environment script (.sh) to be sourced.
	The is a sh or bash script that normally loads modules and sets paths.
- **cpus** : Number of cpus each process uses.
- **cpus_per_node** : How many cpus to use on each node. PUQ has no
	way to determine the number of cpus per node, so there is no default.
	You must supply this. It does not have to be the actual number of CPUs
	in the clusters' nodes, but it should not be more.
- **qname** : The name of the queue to use. 'standby' is the default
- **walltime** : How much time to allow for the process to complete. Format
	is HH:MM:SS.  Default is 1 hour.
- **modules** : List of additional required modules. Default is none.
	Used when the testprogram requires modules to be loaded to run.  For
	example, to run a matlab script you will need to set this to ['matlab']
- **pack** : Number of sequential jobs to run in each PBS script. Default is 1.
	This is used to pack many small jobs into one PBS script.

Examples
--------

1. You want to run Monte Carlo with 10000 jobs, each just a few seconds:
	- cpus=1
 	- cpus_per_node=8
 	- pack=1000
 	- walltime='00:10:00'

	PBSHost will create 10 PBS scripts, each with 1000 jobs, running 8 at a time
	(because each takes only 1 CPU and nodes have 8).  Walltime is 1000 * 3 / 8 seconds
	which is a bit over 6 minutes. I rounded up to 10.

2. Like the previous, except each job uses lots of memory, so you can have only two running in a node at a time.
 	- cpus=1
 	- cpus_per_node=2
 	- pack=1000
 	- walltime='00:25:00'

	PBSHost will create 10 PBS scripts, each with 1000 jobs, running 2 at a time
	(because each takes only 1 CPU and nodes have 2).  Walltime is 1000 * 3 / 2 seconds
	which is 25 minutes.

3. You want to run Monte Carlo with 10000 jobs, each just a few seconds:
	- cpus=1
	- cpus_per_node=8
	- walltime='00:00:01'

	PBSHost will create 1250 PBS scripts, each with 8 jobs, running 8 at a time
	(because each takes only 1 CPU and nodes have 8).

.. note::  There is currently a hardcoded limit of 200 PBS jobs queued at once.
	PUQ will monitor PBS jobs, and as they complete, will submit more until all
	1250 have completed.

4. You have 128 mpi jobs that run on 48 CPUs.
	- cpus=48
	- cpus_per_node=8
	- pack=2

	PBSHost will allocate 6 nodes for each job. 64 PBS jobs will be submitted.
	Each PBS job will run two mpi jobs sequentially. walltime should be set to
	twice what each job takes to run.

