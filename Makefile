
all:	srcs 

srcs:	force
	$(MAKE) -C src all

#adap:	force
#	$(MAKE) -C adap/src all

clean:	force
	$(MAKE) -C src clean
#	$(MAKE) -C adap/src clean

force	:
	true
	