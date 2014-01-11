# If you need to manipulate the data before it is processed, you need
# to create this datafilter function. You will get an open hdf5 file.
# You must add and/or remove data from the /output/data group. 

# This function can be placed in the control script or kept in 
# a separate file, like here.  

def datafilter(hf):
    print "NOW IN DATA FILTER 2"

    # read the old data for 'x'
    x = hf['output/data/x'].value

    # delete old data
    del hf['output/data/x']

    hf['output/data/x'] = 4 * x
    # Optionally, give it a description    
    hf['output/data/x'].attrs['description'] = 'x fixed'
