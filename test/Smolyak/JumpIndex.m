function pz = JumpIndex( num, s )

if s <= 0
  pz = 0;  
else
  m= 2^(s-1)+1;  
  if s > 1
    mid=2^(s-2)+1;
  else
    mid = m;
  end

  ss=2^(s-num);

  if num == 1
    pz = mid;
  else
    pz = (1:ss:m)';
  end

  pz=pz-mid;
end
