function [z,w] = ClenshawZW( n )
%
% To generate 1D, n-level Clenshaw-Curtis quadrature rule in [-1,1]
% Number of points are 2^(n-1)+1, n>=1.
%
% Syntax: [z,w] = ClenshawZW( n ), n is the level of approximation.
%
% Created by Dongbin Xiu, 12/19/2003.
%
if n <= 0
  fprintf('Quad_Clenshaw: Invalid level !\n');
  return;
elseif n == 1
  m = 1;
  z = 0;  w=2;
else
  m = 2^(n-1) + 1;
  z = zeros(m,1);  w=z;
  for j = 1:m
    z(j) = -cos(pi*(j-1)/(m-1));
  end
  for j = 2:(m-1)
    w(j) =  1 - cos(pi*(j-1))/(m*(m-2));
    for k = 1:(m-3)/2
      w(j) = w(j) - 2 * cos(2*pi*k*(j-1)/(m-1))/(4*k^2-1);
    end
    w(j) = 2*w(j) /(m-1);
  end
  w(1) = 1/(m*(m-2));  w(m) = w(1);
end

% map to [0,1]
%z=(z+1)/2;  w = w/2;
