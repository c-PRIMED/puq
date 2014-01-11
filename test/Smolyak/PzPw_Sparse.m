function [PZ, Z, W] = PzPw_Sparse(d, q, ss)

step=q-d;  
if step < 0
  fprintf('Invalida input (q<d). Quit.\n');
elseif d == 1
  [PZ, Z, W] = PzPw_nd(q, ss);
else
  index=ones(1,d);
  for m=1:step
    index = index_step1(index);
  end

  [row, col]=size(index);

  [PZ, Z, W] = PzPw_nd(index(1,:), ss);
  for m=2:row
    [pz,zz, ww] = PzPw_nd(index(m,:), ss);
    [pp,ip,IZ] = intersect(pz, PZ, 'rows');
    [dZ, iw] = setdiff(pz,PZ,'rows');
    PZ = [PZ; dZ];
    for i=1:length(IZ)
      W(IZ(i)) = W(IZ(i)) + ww(ip(i));
    end
    % attach the newly added uniform weights
    for i=1:length(iw)
      Z = [Z; zz(iw(i),:)];    W = [W; ww(iw(i))];
    end
  end

end
