function q = Quad_Clenshaw( n )
%
% To generate 1D, n-level Cleashaw-Curtis quadrature point in [-1,1]
% Number of points are 2^(n-1)+1, n>=1.
%
% Created by Dongbin Xiu, 12/19/2003.
%
if n <= 0
  fprintf('Quad_Clenshaw: Invalid level !\n');
  return;
elseif n == 1
  m = 1;
  q = 0;
else
  m = 2^(n-1) + 1;
  q = zeros(m,1);
  for j = 1:m
    q(j) = -cos(pi*(j-1)/(m-1));
  end
end
