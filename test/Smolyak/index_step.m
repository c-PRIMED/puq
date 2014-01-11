function pn = index_step( p, n )
% 
% This routine takes a matrix p and generates matrix p1 whose entries
% are all the combination of those of rows of p plus 1 to n.
%

p1 = index_step1(p);
pn = cat(1, p, p1);
for i=2:n
  ptmp = p1;
  p1 = index_step1(ptmp);
  pn = cat(1, pn, p1);
end
