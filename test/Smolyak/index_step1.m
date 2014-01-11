function p1 = index_step1( p )
% 
% This routine takes a matrix p and generates matrix p1 whose entries
% are all the combination of those of rows of p plus one.
%
[row, col]=size(p);
%p1 = zeros(row*col,col);

p1 = index_p1(p(1,:),1);
for i=2:row
  dp = index_p1(p(i,:),1);
  
  [rr,cc] = size(dp);
  [r0,c0] = size(p1);
  for k=1:rr
    noadd = 0;
    for m = 1:r0
      if isequal( dp(k,:), p1(m,:) ) == 1
        noadd = 1;
        break;
      end
    end
    if noadd == 0;
      p1 = cat(1, p1, dp(k,:));
    end
  end
  
end
