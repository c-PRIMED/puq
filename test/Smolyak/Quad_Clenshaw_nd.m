function Q=Quad_Clenshaw_nd( index )

d = length(index);
Q = TensorProd(Quad_Clenshaw(index(2)), Quad_Clenshaw(index(1)));
for n=3:d
  Q=TensorProd(Quad_Clenshaw(index(n)), Q);
end
