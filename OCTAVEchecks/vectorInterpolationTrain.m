function [model, errors] = vectorInterpolationTrain(pcaVectors_VxN,truth_1xN,updates,model)
  if nargin ==0
    close all
    dummyData2
    return;
  end
  if nargin<4
    model.N=size(pcaVectors_VxN,2);    
    model.V=size(pcaVectors_VxN,1);
    model.v=1;
    model.M=0;
    model.degree=1;%degree of polynomial for interpolation
    model.independent=1;%skip cross terms
    model.neighborhoodScale=8;
    model.supportVectors_VxM=[];%centers like?is SVM
    model.supportModels_Mxv=[];%centers like?is SVM
    model.run=@vectorInterpolation;
  end
  N=model.N;
  V=model.V;
  v=model.v;
  M=model.M;
  estimate = model.run(pcaVectors_VxN,model);
  errors=zeros(updates,1);
  selected=[];
  for step=1:updates
    e=(estimate-truth_1xN).^2;
    rmse=mean(e(:)).^0.5;
    errors(step)=rmse;
    disp(['rmse =' num2str(rmse) ' on step ' num2str(step)]);
    e(selected)=0;
    [val,ind]=max(e(:));
    selected=[selected ind];
    model.supportVectors_VxM=[model.supportVectors_VxM pcaVectors_VxN(:,ind)];
    model.M=model.M+1;
    w=getWeights(pcaVectors_VxN,model);
    X0=[ones(1,N);pcaVectors_VxN(1:v,:)];
    vp1=(1+v);
    X=zeros(model.M*vp1,N);
    for m=1:model.M
      X((m-1)*vp1+(1:vp1),:)=bsxfun(@times,w(m,:),X0);
    end
    poly=(X*X.')^-1*X*truth_1xN.';%poly for error; update likely needs work
    model.supportModels_Mxv=reshape(poly,vp1,[]).';
    estimate = model.run(pcaVectors_VxN,model);
  end  
  if 1
    w=getWeights(pcaVectors_VxN,model);
    figure(3)
    subplot(2,2,1)    
    imagesc(w);
    subplot(2,2,2)    
    [s, order]=sort(selected,'ascend');
    imagesc(w(order,:));
    subplot(2,2,3)
    plot(sum(w,1))
    subplot(2,2,4)
    plot(sum(w,2))
  end
end

function w=getWeights(pcaVectors_VxN,model)
  r2=model.neighborhoodScale*model.neighborhoodScale;
  dists=zeros(model.M,model.N);
  for m=1:model.M
    delta=bsxfun(@minus,model.supportVectors_VxM(:,m),pcaVectors_VxN);
    dists(m,:)=1./(sum(delta.^2,1)+r2);
  end
  if model.M==0
    w=[];
  else
    w=bsxfun(@rdivide,dists,sum(dists,1));
  end
##  if 1
##    figure(4)
##    plot(sum(w,1))
##    pause(0.1)
##  end
end

function  estimate = vectorInterpolation(pcaVectors_VxN,model)
  %e=sum(w_m(pcaVectors(1:v,:),model.supportVectors_MxV)*polyModel_m*pcaVectors(1:v,:)))
  V=size(pcaVectors_VxN,1);
  N=size(pcaVectors_VxN,2);
  M=size(model.supportVectors_VxM,2);
  v=size(model.supportModels_Mxv,2)-1;
  w=getWeights(pcaVectors_VxN,model);
  estimate=zeros(1,N);
  for m=1:M
    estimate=estimate+w(m,:).*(model.supportModels_Mxv(m,:)*[ones(1,N);pcaVectors_VxN(1:v,:)]);
  end
end


