K=5;
N=10;


rand("seed",12345);
A=rand(K);
Ai=eye(K);
for n=1:N
  Ai=2*Ai-Ai*A*Ai
end
Ai*A