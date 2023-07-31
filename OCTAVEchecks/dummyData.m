close all

classes=4;
hidden=320;
dimentions=16;%8;
samples=100;
rand("seed",1234);
weights=rand(classes,1);
weights=weights./sum(weights);
means=rand(hidden,classes);
covariances=rand(dimentions,hidden,classes);

for tt=1:2
  truth=zeros(1,samples);
  vectors=zeros(dimentions,samples);
  N0=0;
  for c=1:classes
    N=ceil(weights(c)*samples);
    N=min(samples-N0,N);#close enough...
    truth(1,(1:N)+N0)=c;
    vectors(:,(1:N)+N0)=covariances(:,:,c)*(means(:,c)*ones(1,N)+rand(hidden,N));
    N0=N0+N;
  end
  if(tt==1)
    train_truth=truth;
    train_vectors=vectors;
  end
end 
 
#quadratic with cross terms
 train_terms=[ones(1,samples);train_vectors];
 terms=[ones(1,samples);vectors];
 for r=1:dimentions
   for c=r+1:dimentions
     terms=[terms; vectors(r,:) .* vectors(c,:)];
     train_terms=[train_terms; train_vectors(r,:) .* train_vectors(c,:)];
   endfor
 endfor
 
 model=train_truth*train_terms.'*(train_terms*train_terms.')^-1;
 
 test=model*terms;
 
 figure;
 plot(truth,test,'rx')
