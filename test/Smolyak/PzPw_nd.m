function  [Pz, Z, W] = PzPw_nd( index, s )
% 
% Obtain the indices for zeros, s is the level of quadrature where
% m = 2^(s-1)+1 is the total number of grid points. 'index' is the
% input index vector.
%
% by Dongbin Xiu 3/9/04.
%
d = length(index);

Pz = JumpIndex(index(1),s);
[Z, PW] = ClenshawZW( index(1) );
for n=2:d
  pz = JumpIndex(index(n),s);
  [zz, ww] = ClenshawZW( index(n) );
  Pz = TensorProd(pz, Pz);
  Z = TensorProd(zz, Z);  PW = TensorProd(ww, PW);
end
W = prod(PW,2);
