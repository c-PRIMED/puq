function[]=rosen(x,y)

z = 100*(y-x^2)^2 + (1-x)^2;

fprintf('HDF5:{"name": "z", "value": %.16g, "desc": ""}:5FDH\n', z);



