function PronyModel()
  dims=50;
  regions=50;
  rand('seed',55);
  trueth=rand(dims+1,regions);

  resolution=100;
  
  ModelResolution=10;
  model=zeros(dims+1,ModelResolution);
  for d=1:dims
    data=compressed(trueth,d,resolution);
    
    if d ==1
      figure(1)
      plot(data)
      waitfor(1);
      model(end,:)=data;
      model(dim,:)=(1:ModelResolution)/ModelResolution;
    else
      for a=[]
      end
    endif
    
    
  endfor
endfunction


function data=compressed(model,dim,resolution)
  locs=min(ceil(model(dim,:)*resolution),resolution);
  data=zeros(resolution,1);
  for loc=1:size(model,2)
    data(locs(loc))=data(locs(loc))+model(end,loc);
  endfor
endfunction

function model=updateModel(model0,dim,binnedData)
  significance=0.05;
  okay=0==1;
  while ~okay
    [means, stds]=Pronys(numModels);
    %could interplate to convert bins to function values
    okay = checkModel(means,stds,binnedData,significance);
  endwhile
endfunction



function okay = checkModel(medians,aads,binnedData,significance)
  %any reason not to consider the existance of function differently than the existance of data in a pdf?
  %seems like a solid methdology for model building
  bins=numel(binnedData);
  locs=(1:bins)/bins;
  binomial_p=0
  
endfunction

