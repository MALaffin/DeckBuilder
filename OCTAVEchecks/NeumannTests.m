K=5;
N=100;


rand("seed",12345);
A=rand(K)/(2*K);
Ai=zeros(K);
Ap=eye(K)
for n=1:N
  Ap=Ap*(eye(K)-A);
  Ai=Ai+Ap
end
Ai*A