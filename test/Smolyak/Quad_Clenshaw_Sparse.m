function Q = Quad_Clenshaw_Sparse(d, q)

step=q-d;
index=ones(1,d);
for m=1:step
  index = index_step1(index);
end

[row, col]=size(index);

Q=Quad_Clenshaw_nd(index(1,:));
for m=2:row
  Q = [Q; Quad_Clenshaw_nd(index(m,:))];
end
