
M=[4 -1 6;2 1 6;2 -1 8];
N=size(M,1);
[X E]=eig(M);
e=1;
Mme=M-eye(N)*E(e,e);
Mme=diag([-1/5 1 1])*(Mme);
Mme(2,:)=Mme(2,:)-2*Mme(1,:);
Mme(3,:)=Mme(3,:)-2*Mme(1,:);
Mme=diag([1 -1/8.4 1])*(Mme);
Mme(1,:)=Mme(1,:)-.2*Mme(2,:);
Mme(3,:)=Mme(3,:)+1.4*Mme(2,:);
Mme=-Mme
s=eye(N)+Mme;
(M-eye(N)*E(e,e))*s

e=2;
Mme=M-eye(N)*E(e,e);
Mme=0.5*(Mme);
Mme(2,:)=Mme(2,:)-Mme(1,:);
Mme(3,:)=Mme(3,:)-Mme(1,:);
Mme=-Mme;
s=eye(N)+Mme;
(M-eye(N)*E(e,e))*s

##
##M=[1 6;5 2];
##N=size(M,1);
##[X E]=eig(M);
##e=1;
##Mme=M-eye(N)*E(e,e);
##Mme=diag([1/5 1/5])*(Mme);
##Mme(2,:)=Mme(2,:)-Mme(1,:)
##e=2;
##Mme=M-eye(N)*E(e,e);
##Mme=diag([1/6 1/5])*(Mme);
##Mme(2,:)=Mme(2,:)+Mme(1,:)
##Mme=diag([1 -1/8.4])*(Mme);
##Mme(1,:)=Mme(1,:)-.2*Mme(2,:);