function [z,w] = ZWtest(d,q)

[z,w] = ClenshawZW_Sparse(d,q);

s=q-d+1; 
if s>=1
for m=(q-1):-1:s
  if m>= d
    [zz,ww] = ClenshawZW_Sparse(d,m);
    ww = (-1)^(q-m)*nchoosek(d-1,q-m)*ww;
    z = [z; zz];
    w = [w; ww];
  end
end
end
