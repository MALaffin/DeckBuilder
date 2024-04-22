K=5;
N=10;


rand("seed",12345);
A=rand(K);

dA=det(A);
Ap=cell(K,1);
trAp=zeros(K-1,1);
Ap{1}=eye(K);
for p=1:K-1
   Ap{p+1}=A*Ap{p};
   trAp(p)=trace(Ap{p+1});
end
Ai=0;
for n=0:N-1
  
  Ai=Ai=Ap{p+1}*
end
Ai=Ai/dA;
Ai*A