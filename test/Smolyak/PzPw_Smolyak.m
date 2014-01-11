function [Z,W] = PzPw_Smolyak( d, q )

s=q-d+1; 
[PZ,Z,W] = PzPw_Sparse(d,q, s);

if s>=1
  for m=(q-1):-1:s
    if m >= d
      [pz,zz,ww] = PzPw_Sparse(d,m, s);
      ww = (-1)^(q-m)*nchoosek(d-1,q-m)*ww;
      [pp,ip,iz] = intersect(pz, PZ, 'rows');
      for i=1:length(iz)
        W(iz(i)) = W(iz(i)) + ww(ip(i));
      end
      %attach the newly added points and their uniform weights 
      %dZ = setdiff(pz,PZ,'rows');
      %PZ = [PZ; dZ];
      %[row, col] = size(dZ);
      %PW = [PW; ones(row,1)];
    end
  end
end

