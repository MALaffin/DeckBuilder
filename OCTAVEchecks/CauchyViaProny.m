function [medians, aads, weights]=CauchyViaProny(data)
  %sum of cauchy distributions as a way to find a basis for the data
  %the cauchy is a lorenzian that has a nice form on one side
  
  if nargin==0
    CauchyViaPronyTest();
    medians=[];
    aads=[];
    weights=[];
    return;
  endif
  
  k=1;
  err=inf;
  N=numel(data);
  w=(0:N-1)*2*pi/N;
  for k=1:floor(numel(data)*.45)
    disp(err)
    [C_hats, B_hats, A_hats]=CauchyViaPronyWithModelSize(k,data);
    [c_hats, order]=sort(C_hats,'ascend');
    b_hats=-B_hats(order);
    a_hats=A_hats(order);
    data2=sum((2*(a_hats.*b_hats)*ones(1,N))./((b_hats.^2)*ones(1,N)+((ones(k,1)*w-c_hats*ones(1,N)).^2)),1);
    errK=sum((data2(:)-data(:)).^2); 
    if errK<err
      err=errK;
      medians=c_hats;
      aads=b_hats;
      weights=a_hats;
    endif
  endfor

  
endfunction

function [medians, aads, weights]=CauchyViaPronyWithModelSize(numModels,data)  
  %data = sum(a_b*2b_n/(b_n^2+(w-c_n)^2),n,1,numModels)
  dw=1/numel(data);
  sd=sum(data);
  N=floor(numel(data)/2);
  DATA=fft(data(:))*dw/sd;%numeric integral with dw
  %consider filtering for non-?compact? data
  %DATA = sum(a_b*exp(-b_n*|x|)*exp(i*c_n*x),n,1,numModels)
  pad=0;%floor(N*0.05);
  N=numel(data);%2*numModels;%N-2*pad;
  F=DATA(1:N);%  F=DATA(pad+(1:N));
  Y=F((numModels+1):end);
  X=zeros(N-numModels,numModels);
  for offset=0:numModels-1
    X(offset+1,:)=F((numModels:-1:1)+offset);
  endfor
  %not sure if psedo inverse needs conjugation
  P=[1;-(X'*X)^-1*X'*Y];
  r=roots(P).';
  M=numModels;%N;%
  pad2=0;%numModels-1;
  Z=zeros(M,numModels);
  for k=0:M-1
    Z(k+1,:)=r.^(k+pad+pad2);
  endfor
  F2=F(pad2+(1:M));
  weights= real((Z'*Z)^-1*Z'*F2)*sd;
  %how-to: https://en.wikipedia.org/wiki/Prony's_method
  R=log(r');
  aads=real(R);
  medians=imag(R);
  medians(medians<0)=2*pi+medians(medians<0);
endfunction


function CauchyViaPronyTest()
%https://en.wikipedia.org/wiki/Fourier_transform
rand('seed',44);
k=20;
%this could be very noisy in fft step... bound bs&cs for testing
cs=sort((rand(k,1)/2+.25)*2*pi,'ascend');
minB=.05;
maxB=.5;
bs=minB+rand(k,1)*(maxB-minB);
minA=.05;
as=minA+rand(k,1)*(1-minA);
N=128;
w=(0:N-1)*2*pi/N;
data=sum((2*(as.*bs)*ones(1,N))./((bs.^2)*ones(1,N)+((ones(k,1)*w-cs*ones(1,N)).^2)),1);


[C_hats, B_hats, A_hats]=CauchyViaProny(data);
[c_hats, order]=sort(C_hats,'ascend');
b_hats=B_hats(order);
a_hats=A_hats(order);

k=numel(a_hats);
data2=sum((2*(a_hats.*b_hats)*ones(1,N))./((b_hats.^2)*ones(1,N)+((ones(k,1)*w-c_hats*ones(1,N)).^2)),1);

clc
close all
##disp([as a_hats])
##disp([bs b_hats])
##disp([cs c_hats])
figure(1)
plot(w,data,'-k','linewidth',2)
hold on
plot(w,data2,'-r','linewidth',1)
hold off
title(sqrt(mean((data-data2).^2))/mean(data),'FontSize',30)

endfunction
