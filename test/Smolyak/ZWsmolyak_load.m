function [z,w] = ZWsmolyak_load(dim, level)
%
% [z,w] = ZWsmolayk_load(dim, level) is the nodes for Smolyak sparse grid
% based on 1d Chebyshev extrema H(N+k,N);
% Interpolation A(N+k,N) on H(N+k,N) is extra for N-variate polynomials 
% of total degree up to k;
% 
%    dim = dimensionality N;
%    level = level of approximation k;
%
%    z = matrix M x N; N-variate coordinates of total of M points;
%    w = array  M x 1; weight for each of the M point. 
%   
% The function reads the quadrature rules [z,w] of Smolyak sparse grid.
% The dimension ranges from 1 to 100 and the order 1 to 8.
% For higher dimensions, the order is lower to keep the number of points
% reasonably low (less 10,000).
%
% No check of available dimensions and orders is done. Will be unable to
% open the files if the parameters are unavailable.
%
% by Dongbin Xiu, Mar 2004
%
q = dim+level;

fname = sprintf('CCsmolyak_d%ds%d.dat',dim,level);
fp = fopen(fname, 'r');
row = fscanf(fp, '%d',[1 1]);
zw = fscanf(fp, '%e', [dim+1 row]);

zw = zw';
z=zw(1:row, 1:dim);
w=zw(1:row, dim+1);

fclose(fp);
