%want aproximations of growth that acount for 
%inflation, without needing to adjust initial 
% values for everything that grows with inflation
years=50;
seed=100;
growth=.069;%
growthStd=0.65*growth;
loss=0.024;
lossStd=0.012;
trials=10000;

rand("seed",1234);
randG=randn(years,trials);
randL=randn(years,trials);
values=[seed*ones(1,trials); zeros(years-1,trials)];
model1=.95*seed*(1+growth*.9).^(0:years-1);
for year=2:years
  values(year,:)=values(year-1,:)...
          .*((1+growth)+growthStd*randG(year,:))...
          ./((1+loss)+lossStd*randL(year,:))...today dolars value with noise
          .*(1+loss);%absolute budget dolars without noise
end
modelMean=mean(values,2);
sortedV=sort(values,2);
P=.15;
modelPhigh=sortedV(:,max(1,floor(trials-P*trials)));
modelPlow=sortedV(:,max(1,floor(P*trials)));

growths=exp(log(values(end,:)/seed)/(years-1))-1;
mean(growths)
anualizedGrowths=mean(diff(values,1)./values(1:end-1,:));
mean(anualizedGrowths)

%seed*(1+growth2).^(1:years)=v
%log(vyears/v1)=log(seed*(1+growth2).^(years)/seed*(1+growth2).^(1))
%log(vyears/v1)=log((1+growth2).^(years)/(1+growth2).^(1))
%log(vyears/v1)=log((1+growth2).^(years-1))
%log(vyears/v1)=(years-1)log((1+growth2))
%log(vyears/v1)/(years-1)=log((1+growth2))
%exp(log(vyears/v1)/(years-1))=(1+growth2)
%exp(log(vyears/v1)/(years-1))-1=growth2
growth2=exp(log(modelMean(end)/seed)/(years-1))-1;
model2=seed*(1+growth2).^(0:years-1);

figure(1)
plot(1:years,values(:,4),'-c', 'linewidth',0.5)
hold on
plot(1:years,model1,'-r', 'linewidth',2)
plot(1:years,model2,'-m', 'linewidth',2)
plot(1:years,modelMean,'-b', 'linewidth',3)
plot(1:years,modelPhigh,':b', 'linewidth',3)
plot(1:years,modelPlow,':b', 'linewidth',3)
hold off
