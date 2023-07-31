import numpy as np
import tensorflow as tf
from synergyAnalyzer import plot
import matplotlib.pyplot as plt
from os.path import exists
import dill
from time import *
import gc

print("TensorFlow version:", tf.__version__)


class LearnedSynergy:
    def __init__(self, modelSaveLoc, userSaveLoc):
        self.model=[]
        self.modelSaveLoc=modelSaveLoc
        self.userSaveLoc=userSaveLoc
        self.scaleValue=1.0
    
    def trainModel2(self, vector, chaff, decks, combos, reps, reset, relevancePower, showPlots=False):
        
        cardlist=chaff.copy()
        for deck in decks:
            for card in deck:
                if(card in chaff):
                    print("deck card in chaff")
                if not card in cardlist:
                    cardlist.append(card);
        for combo in combos:
            for card in combo:
                if(card in chaff):
                    print("combo card in chaff")
                if not card in cardlist:
                    cardlist.append(card);
        cardlist.sort()#this should reasonably randomize good and bad
        #cardlistNoChaff=list(set(cardlist).difference(set(chaff)))
        #cardlistNoChaff.sort()
        
        chaffValue=0
        baselineValue=self.scaleValue/4
        deckValue=self.scaleValue/2
        comboValue=self.scaleValue
        Ntrain=len(cardlist)
        match=np.ones((Ntrain,Ntrain))*baselineValue
        for card in chaff:
            c=cardlist.index(card)
            match[c,:]=chaffValue
            match[:,c]=chaffValue
        for deck in decks:
            for card1 in deck:
                c1=cardlist.index(card1)
                for card2 in deck:
                    c2=cardlist.index(card2)
                    match[c1,c2]=max(match[c1,c2],deckValue)
        for combo in combos:
            for card1 in combo:
                c1=cardlist.index(card1)
                for card2 in combo:
                    c2=cardlist.index(card2)
                    match[c1,c2]=max(match[c1,c2],comboValue)
        #match=match/comboValue# cant tell if there are internal constants that benefit from a non-0-1 scaling

        # c000=np.sum(match==0)
        # c025=np.sum(match==0.25)
        # c050=np.sum(match==0.5)
        # c100=np.sum(match==1.0)
        # #training is failing; maybe I need to weight it better
        # #E(match)=c000*0+c025*0.25+c050*0.5+c100*1.0
        # #E=c000*V0+c025*V1+c050*V2+c100*V3
        # #using an SSE cost function so balance about the mean:
        # #Weasy*c000*(V0-E)^2=Whard*c100*(V3-E)^2
        # #let Weasy=1
        # Whard=0.05;# so V3-E is about (c000/(Whard*c100))^0.5 smaller than V0-E
        # #warning, at some point Whard will push V1<V0=0
        # #(c000/(Whard*c100))^.5*(E-V0)=(V3-E)
        # #let V0=0
        # #(1+(c000/(Whard*c100))^.5)*E=V3
        # # want an easy scaling let V3 = 1.0
        # #E=1/(1+(c000/(Whard*c100))^.5)
        # E=1/(1+np.sqrt(c000/(Whard*c100)))
        # #let V3-E have a similar weight at V2-E 
        # #Whard*c050*(V2-E)^2=Whard*c100*(1-E)^2
        # #(V2-E)^2=(c100/c050)*(1-E)^2
        # #V2^2-2*V2*E+E^2=(c100/c050)*(1-2*E+E^2)
        # #V2^2-2*V2*E+E^2-(c100/c050)*(1-2*E+E^2)
        # A=1
        # B=-2*E
        # C=E**2-(c100/c050)*(1-2*E+E**2)
        # D=B**2-4*A*C
        # V2=(-B+np.sqrt(D))/(2*A)#positive side is the only one hat could be positive
        # #E=(c025*V1+c050*V2+c100)/(c000+c025+c050+c100)
        # #c025*V1=E*(c000+c025+c050+c100)-(c050*V2+c100)
        # V1=(E*(c000+c025+c050+c100)-(c050*V2+c100))/c025
        # match[match==0.25]=V1;
        # match[match==0.5]=V2;

        if showPlots:
            fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=showPlots)
            h = ax.imshow(match, vmin=0,
                vmax=np.max(match), aspect='auto')
            plt.show(block=False)

        #about 700 basis cards, sizein~2*(700*3)=4200 for card pairs of basis vectors of size 3
        #expect ~1000 cards from a pool of ~10000 about 10% of the combos are relevent
        #maybe as many as 700*700*0.1~=50000 relevent good groups
        #the pair input structure implies a symetric training scheme on the input layer would be best; 
        # trust that the basis made that layer
        #4200 values for defining which basis each card belongs to 
        #50000/4200~need about 12 nodes after input to mix enough; maybe want ~4x few to control granualrity of underlying distribution
    
        
        #about 1500 cards of interest; maybe close to 150-300 for types
        # need about 2x to to bound the sides with simple sigmoinds (1d aprox)
        # need about three classes; chaff, decks, combo

        V=vector.shape[0]
        width=np.ceil(32)#32 close to 4*50000/(V*2);~128 combo parts but many overlap; 
        width2=3**2#combinations of subgroups
        #width=np.ceil(4*50000/(V*2))
        #width=4#np.ceil(5000/(V*2))
        sizeIn=V*2 
        self.RESET()
        if not reset and exists(self.modelSaveLoc):
            self.model=tf.keras.models.load_model(self.modelSaveLoc)
        else:
            self.model = tf.keras.models.Sequential([
                tf.keras.layers.Flatten(input_shape=(sizeIn,1)),
                #tf.keras.layers.Dense(width,  activation='softmax'),
                #tf.keras.layers.Dense(width2,  activation='softmax'),
                #tf.keras.layers.Dense(width,  activation='tanh'),
                tf.keras.layers.Dense(width,  activation='sigmoid'),
                tf.keras.layers.Dense(width2,  activation='sigmoid'),
                tf.keras.layers.Dense(1, activation='linear')
            ])                   
            self.model.compile(optimizer='RMSprop',#'FTRL',#'adadelta',#
                loss='mean_squared_error',  # self.error,#
                #loss='mean_squared_logarithmic_error',  # self.error,#
                #loss='log_cosh',  # self.error,#
                metrics=['mean_absolute_error']
                )
        dataBytes=(2*V*8)*Ntrain*Ntrain #(vector to train, 8bytes/double)*rows*cols
        dataBytesTarget=6e9#memory spikes killing python terminal#8e9
        blocks=int(np.ceil(dataBytes/dataBytesTarget))
        trainStep=int(np.ceil(Ntrain/blocks))
        #consider iterations of training on the outside
        #reps=8
        trainVecsT=vector[:,cardlist].transpose()

        fullErr=0
        lastErr=np.nan
        trainVec=np.zeros((trainStep*Ntrain,2*V))
        weights=np.zeros((trainStep*Ntrain,1))
        relevance=np.ones((trainStep*Ntrain,1))
        fullRelevance=0*match;
        nCombo=np.sum(match==comboValue)
        fullRelevance[match==chaffValue]=(nCombo/np.sum(match==chaffValue))**relevancePower
        fullRelevance[match==baselineValue]=(nCombo/np.sum(match==baselineValue))**relevancePower
        fullRelevance[match==deckValue]=(nCombo/np.sum(match==deckValue))**relevancePower
        fullRelevance[match==comboValue]=1
        epochs=1;
        if reps>16:
            epochs=int(reps/16);
            reps=16

        for rep in range(reps):
            t0=time()
            for C in range(blocks):
                CBlock=[c for c in range(C*trainStep,min((C+1)*trainStep,Ntrain))]
                Nblock=len(CBlock)
                #TV=trainVecsT[CBlock,:]
                for r in range(Ntrain):
                    region=[r*Nblock+c for c in range(Nblock)]#let the prior samples get reused
                    #top=np.repeat(trainVecsT[r,:].reshape((1,V)),Nblock,axis=0)+TV
                    #top=trainVecsT[r,:]+TV
                    #bot=trainVecsT[r,:]-TV
                    #trainVec[region,0:V]=top
                    #trainVec[region,V:(2*V)]=bot
                    #del top
                    #del bot
                    #gc.collect()
                    weights[region,0]=match[CBlock,r]
                    relevance[region,0]=fullRelevance[CBlock,r]
                    trainVec[region,0:V]=trainVecsT[r,:]+trainVecsT[CBlock,:]
                    trainVec[region,V:(2*V)]=trainVecsT[r,:]-trainVecsT[CBlock,:]
                    trainVec[region,V:(2*V)]=np.abs(trainVec[region,V:(2*V)])
                    #del trainVecC #can probably eliminate this variable
                #del TV
                print("starting rep "+ str(rep)+" of "+str(reps)+" colBlock " +str(C) +" of "+ str(blocks))
                #self.model.fit(trainVec, weights, epochs=32,shuffle=True, batch_size=128, verbose=1)
                BS=2048;
                hist=self.model.fit(trainVec, weights,sample_weight=relevance, epochs=epochs,shuffle=True, batch_size=BS, verbose=0)
                gc.collect()
                meanTime=(time()-t0)/(C+1)/60
                lastErr=hist.history['mean_absolute_error'][-1]
                fullErr=fullErr+lastErr*Nblock
                print("Err around " + str(hist.history['mean_absolute_error'][epochs-1]) + ", about "+str(meanTime*((blocks-C-1)+blocks*(reps-rep-1)))+" minutes left")
                del hist
                tf.keras.backend.clear_session()
                gc.collect()

        self.model.save(self.modelSaveLoc,overwrite=True)
        
        if showPlots:
            self.useModel2(vector[:,cardlist], False, showPlots)
            plt.show(block=False)
        
        return fullErr/self.scaleValue/Ntrain/reps

    
    def useModel2(self, vector, reset, showPlots=0):
        if exists(self.modelSaveLoc):
            self.model=tf.keras.models.load_model(self.modelSaveLoc)
        else:
            print('missing '+ self.modelSaveLoc)
            return None
        print("begin use")
        if not showPlots and exists(self.userSaveLoc) and not reset:
            with open(self.userSaveLoc, 'rb') as file:
                trainedCardMatch = dill.load(file)
                file.close()
        else:
            N=vector.shape[1]
            V=vector.shape[0]
            trainedCardMatch=np.zeros((N,N))
            dataBytes=(2*V*8)*N*N #(vector to train, 8bytes/double)*rows*cols
            dataBytesTarget=4e9#serious overhead issues#8e9
            blocks=dataBytes/dataBytesTarget#aproximation from memory
            trainStep=int(np.maximum(1,np.floor(N/blocks)))
            blocks=int(np.ceil(N/trainStep))
            #consider iterations of training on the outside
            #reps=8
            trainVecsT=vector.transpose()

            trainVec=np.zeros((trainStep*N,2*V))
            
            t0=time()
            for C in range(blocks):
                CBlock=[c for c in range(C*trainStep,min((C+1)*trainStep,N))]
                Nblock=len(CBlock)
                TV=trainVecsT[CBlock,:]
                if(not Nblock == trainStep):
                    del trainVec
                    gc.collect()
                    trainVec=np.zeros((Nblock*N,2*V))
                for r in range(N):
                    region=[r*Nblock+c for c in range(Nblock)]#let the prior samples get reused
                    trainVec[region,0:V]=trainVecsT[r,:]+TV
                    trainVec[region,V:(2*V)]=trainVecsT[r,:]-TV
                    trainVec[region,V:(2*V)]=np.abs(trainVec[region,V:(2*V)])

                print("colBlock " +str(C) +" of "+ str(blocks))                
                temp= self.model.predict(trainVec,verbose=0)[:, 0]
                trainedCardMatch[:,CBlock] =temp.reshape((N,Nblock))
                del temp                
                gc.collect()
                meanTime=(time()-t0)/(C+1)/60
                print("about "+str(meanTime*((blocks-C-1)))+" minutes left")
            
            del trainVec
            del trainVecsT
            gc.collect()
            with open(self.userSaveLoc, "wb") as f:
                dill.dump(trainedCardMatch, f)
                f.close()
        
        if showPlots:
            fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=showPlots+1)
            h = ax.imshow(trainedCardMatch, vmin=0,
                vmax=self.scaleValue, aspect='auto')
            plt.show(block=False)

        return trainedCardMatch;

    def trainModel(self, sampleIn, sampleOut, seed=0):
        sizeIn=[1,1]
        if not self.model:
            self.model = tf.keras.models.Sequential([
                    tf.keras.layers.Flatten(input_shape=sizeIn),
                    tf.keras.layers.Dense(128, activation='sigmoid'),
                    tf.keras.layers.Dense(1, activation='linear')
                ])
        tf.random.set_seed(seed)
        self.model.compile(optimizer='adam',
                           loss='mean_squared_error',  # self.error,#
                           metrics=['mean_absolute_error']
                           )
        # tf.config.run_functions_eagerly(True)
        # self.model.run_eagerly = True
        self.model.fit(sampleIn, sampleOut, epochs=100, batch_size=10, verbose=0)
        # todo:xval and likely self.model.evaluate(x_test, y_test, verbose=0)

    def useModel(self, dataIn):
        return self.model.predict(dataIn,verbose=0)

    @classmethod
    def selfTest(cls):
        test = LearnedSynergy("","")
        x = np.arange(-100, 100) / 12
        y = (x ** 2 + 2 * x + 1)/120
        test.trainModel(x, y)
        yEst = test.useModel(x)
        plot(x.reshape(x.size,1), y.reshape(x.size,1), 'Expected', 1)
        plot(x.reshape(x.size,1), yEst.reshape(x.size,1), 'Estimated', 2)
        # self.model = tf.keras.models.Sequential([
        #     tf.keras.layers.Flatten(input_shape=sizeIn),
        #     tf.keras.layers.Dense(256, activation='sigmoid'),
        #     tf.keras.layers.Dense(1, activation='linear')
        # ])
        # self.model.fit(sampleIn, sampleOut, epochs=20, batch_size=1)
        # about 0.06 mean_absolute_error
        plt.show()

    def RESET(self, seed_value= 0):
        #https://stackoverflow.com/questions/54432394/keras-getting-different-results-with-set-seed
        # Seed value (can actually be different for each attribution step)
        #seed_value= 0

        # 1. Set `PYTHONHASHSEED` environment variable at a fixed value
        import os
        os.environ['PYTHONHASHSEED']=str(seed_value)

        # 2. Set `python` built-in pseudo-random generator at a fixed value
        import random
        random.seed(seed_value)

        # 3. Set `numpy` pseudo-random generator at a fixed value
        import numpy as np
        np.random.seed(seed_value)

        # 4. Set `tensorflow` pseudo-random generator at a fixed value
        import tensorflow as tf
        #tf.set_random_seed(seed_value)
        tf.random.set_seed(seed_value)

        ## 5. Configure a new global `tensorflow` session
        #from keras import backend as K
        #session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
        #sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
        #K.set_session(sess)

if __name__ == '__main__':

    LearnedSynergy.selfTest()