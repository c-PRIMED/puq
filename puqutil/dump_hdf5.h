/* dump double value */
void dump_hdf5_d(char *name, double val, char *desc)
{
	printf("HDF5:{'name':'%s','value':%.16e,'desc':'%s'}:5FDH\n", name, val, desc);
}

/* dump long integer value */
void dump_hdf5_l(char *name, long val, char *desc)
{
	printf("HDF5:{'name':'%s','value':%ld,'desc':'%s'}:5FDH\n", name, val, desc);
}

