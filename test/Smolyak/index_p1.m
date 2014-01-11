function p1 = index_p1( p, k )
% 
% This routine takes a row vector p and generates p1 whose entries
% are all the combination of those entries starting from k of p plus one.
%

d=length(p);
row=d-k+1;
p1 = zeros(row,d);

for i=k:d
  row = i-k+1;
  p1(row,:) = p;
  p1(row,i) = p(i) + 1;
end
%p1 = sortrows(p1);