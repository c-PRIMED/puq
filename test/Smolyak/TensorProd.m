function C = TensorProd(a, B)
%
% This routine creates C = a \otimes B, where \otimes is the tensor
% product. a  is a vector and B can be a matrix.
% The entries of a are attached at the end of B.
%
% Written by Dongbin Xiu, 12/18/2003.
%

na=length(a);
[rr,cc] = size(B);
ai = a(1)*ones(rr,1);
C = cat(2, B, ai);
for i=2:na
  ai = a(i)*ones(rr,1);
  C = cat(1, C, cat(2,B,ai)); 
end
