function [model, errors] = vectorInterpolationTrain(pcaVectors_VxN,truth_1xN,updates,model)
  if nargin ==0
    close all
    dummyData2
    model=[]
    errors=[]
    return;
  end
  if nargin<4
    model.N=size(pcaVectors_VxN,2);    
    model.V=size(pcaVectors_VxN,1);
    model.v=4;
    model.degree=1;%degree of polynomial for interpolation
    %model.independent=1;%skip cross terms; PCA (or SVD) first should practically limit the need for this
    model.neighborhoodTrainScale=.05;
    model.neighborhoodUseScale=model.neighborhoodTrainScale;
    model.trainSubs=1;
    model.decay=1;
    
    model.run=@vectorInterpolation;
    %intialized empty model
    model.M=0;
    model.supportVectors_VxM=[];%centers like?is SVM
    model.supportModels_Mxv=[];%centers like?is SVM
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
    w=getWeights(pcaVectors_VxN,model,1);
    switch model.degree
      case 1
        X0=[ones(1,N);pcaVectors_VxN(1:v,:)];
      otherwise
        X0=ones(1,N);
    end
    if(model.trainSubs)
      model.supportModels_Mxv=[];
      ests=[];
      for m=1:model.M
        X=bsxfun(@times,w(m,:),X0);
        poly=(X*X.')^-1*X*truth_1xN.';%poly for error; update likely needs work
        model.supportModels_Mxv=[model.supportModels_Mxv; poly.'];
        ests=[ests, poly.'*X0(:,selected(:,m))];
      end
      if 1
        figure(5)
        plot(truth_1xN(selected),ests,'rx')
      end
    else
      vp=size(X0,1);
      X=zeros(model.M*vp,N);
      for m=1:model.M
        X((m-1)*vp+(1:vp),:)=bsxfun(@times,w(m,:),X0);
      end
      poly=(X*X.')^-1*X*truth_1xN.';%poly for error; update likely needs work
      model.supportModels_Mxv=reshape(poly,vp,[]).';
    end
    estimate = model.run(pcaVectors_VxN,model);
  end  
  if 1
    w=getWeights(pcaVectors_VxN,model,1);
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

function w=getWeights(pcaVectors_VxN,model,train)
  if train
    r2=model.neighborhoodTrainScale^2;
  else
    r2=model.neighborhoodUseScale^2;
  end
  dists=zeros(model.M,model.N);
  for m=1:model.M
    delta=bsxfun(@minus,model.supportVectors_VxM(:,m),pcaVectors_VxN);
    dists(m,:)=1./(mean(delta.^2,1)+r2);
  end
  if model.M==0
    w=[];
  else
    if(model.decay==0)
      w=bsxfun(@rdivide,dists,sum(dists,1));
    else
      w=dists;
    end    
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
  M=model.M;
  v=model.v;
  w=getWeights(pcaVectors_VxN,model,0);
  estimate=zeros(1,N);
  for m=1:M
    switch model.degree
      case 1
        X0=[ones(1,N);pcaVectors_VxN(1:v,:)];
      otherwise
        X0=ones(1,N);
    end
    estimate=estimate+w(m,:).*(model.supportModels_Mxv(m,:)*X0);
  end
end


