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
    
    def trainModel2(self, vector, chaff, decks, combos):
        
        if exists(self.modelSaveLoc):
            self.model=tf.keras.models.load_model(self.modelSaveLoc)
        else:
            #about 700 basis cards, sizein~2*(700*3)=4200 for card pairs of basis vectors of size 3
            #expect ~1000 cards from a pool of ~10000 about 10% of the combos are relevent
            #maybe as many as 700*700*0.1~=50000 relevent good groups
            #the pair input structure implies a symetric training scheme on the input layer would be best; 
            # trust that the basis made that layer
            #4200 values for defining which basis each card belongs to 
            #50000/4200~need about 12 nodes after input to mix enough; maybe want ~4x few to control granualrity of underlying distribution
        
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
            deckValue=0.5
            comboValue=1.0
            Ntrain=len(cardlist)
            match=np.ones((Ntrain,Ntrain))*0.25
            trainVecs=vector[:,cardlist]
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
                

            if False:
                fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=0)
                h = ax.imshow(match, vmin=0,
                    vmax=1, aspect='auto')
                plt.show(block=False)
            
        
            V=vector.shape[0]
            width=np.ceil(4*50000/(V*2))
            #width=4#np.ceil(5000/(V*2))
            sizeIn=V*2
            self.model = tf.keras.models.Sequential([
                tf.keras.layers.Flatten(input_shape=(sizeIn,1)),
                tf.keras.layers.Dense(width,  activation='sigmoid'),
                tf.keras.layers.Dense(1, activation='linear')
            ])                    
            tf.random.set_seed(0)
            self.model.compile(optimizer='RMSprop',
                loss='mean_squared_error',  # self.error,#
                metrics=['mean_absolute_error']
                )

            dataBytes=(2*V*8)*Ntrain*Ntrain #(vector to train, 8bytes/double)*rows*cols
            dataBytesTarget=8000000000
            blocks=int(np.ceil(dataBytes/dataBytesTarget))
            trainStep=int(np.ceil(Ntrain/blocks))
            #consider iterations of training on the outside
            reps=2
            for rep in range(reps):
                t0=time()
                for C in range(blocks):
                    CBlock=[c for c in range(C*trainStep,min((C+1)*trainStep,Ntrain))]
                    Ccards=[cardlist[c] for c in CBlock]
                    Nblock=len(CBlock)

                    trainVec=np.zeros((Nblock*Ntrain,2*V))
                    weights=np.zeros((Nblock*Ntrain,1))
                    for r in range(Ntrain):
                        region=[r*Nblock+c for c in range(Nblock)]
                        top=np.repeat(trainVecs[:,r].reshape((V,1)),Nblock,axis=1)+vector[:,Ccards]#
                        bot=np.absolute(top-2*vector[:,Ccards])#vector[:,Ccards]#
                        trainVecC=np.concatenate((top,bot),axis=0).transpose()
                        weights[region,0]=match[r,CBlock].transpose()
                        trainVec[region,:]=trainVecC

                    print("starting colBlock " +str(C) +" of "+ str(blocks))
                    self.model.fit(trainVec, weights, epochs=32,shuffle=True, batch_size=128, verbose=0)
                    del trainVec
                    del weights
                    gc.collect()
                    meanTime=(time()-t0)/(C+1)/60
                    print("about "+str(meanTime*((blocks-C-1)+blocks*(reps-rep-1)))+" minutes left")
            self.model.save(self.modelSaveLoc)
        
        if False:
            N=vector.shape[1]
            V=vector.shape[0]
            V2=V*2;
            trainedCardMatchSUB = np.zeros([Ntrain, Ntrain])
            X2 = np.zeros([Ntrain, 2*V])
            t0=time()
            for r in range(Ntrain):
                rI=cardlist[r]
                if r % round(Ntrain / 10) == 0:
                    print('using model loop ' + str(r) + ' of ' + str(Ntrain))
                for c in range(Ntrain):
                    cI=cardlist[c]
                    X2[c, 0:V] = vector[:, rI]+vector[:, cI]#
                    X2[c, V:V2] = np.absolute(vector[:, rI]-vector[:, cI])#vector[:, cI]#
                trainedCardMatchSUB[r, :] = self.model.predict(X2,verbose=0)[:, 0]
                if r % round(Ntrain / 10) == 0:
                    meanTime=(time()-t0)/(r+1)/60
                    print("about "+str(meanTime*(Ntrain-r-1))+" minutes left")
                gc.collect()
            fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=1)
            h = ax.imshow(trainedCardMatchSUB, vmin=0,
                vmax=1, aspect='auto')
            plt.show(block=True)

        print("begin use")
        if exists(self.userSaveLoc):
            with open(self.userSaveLoc, 'rb') as file:
                trainedCardMatch = dill.load(file)
                file.close()
        else:
            N=vector.shape[1]
            V=vector.shape[0]
            V2=V*2;
            trainedCardMatch = np.zeros([N, N])
            X2 = np.zeros([N, 2*V])
            t0=time()
            for r in range(N):
                if r % round(N / 100) == 0:
                    print('using model loop ' + str(r) + ' of ' + str(N))
                for c in range(N):
                    X2[c, 0:V] = vector[:, r]
                    X2[c, V:V2] = vector[:, c]
                trainedCardMatch[r, :] = self.model.predict(X2,verbose=0)[:, 0]
                if r % round(N / 100) == 0:
                    meanTime=(time()-t0)/(r+1)/60
                    print("about "+str(meanTime*(N-r-1))+" minutes left")
                gc.collect()
            with open(self.userSaveLoc, "wb") as f:
                dill.dump(trainedCardMatch, f)
                f.close()
        return trainedCardMatch;

    def trainModel(self, sampleIn, sampleOut, seed=0):
        sizeIn=sampleIn.shape[0]
        if not self.model:
            self.model = tf.keras.models.Sequential([
                    tf.keras.layers.Flatten(input_shape=sizeIn),
                    tf.keras.layers.Dense(256, activation='sigmoid'),
                    tf.keras.layers.Dense(1, activation='linear')
                ])
        tf.random.set_seed(seed)
        self.model.compile(optimizer='adam',
                           loss='mean_squared_error',  # self.error,#
                           metrics=['mean_absolute_error']
                           )
        # tf.config.run_functions_eagerly(True)
        # self.model.run_eagerly = True
        self.model.fit(sampleIn, sampleOut, epochs=1, batch_size=1, verbose=0)
        # todo:xval and likely self.model.evaluate(x_test, y_test, verbose=0)

    def useModel(self, dataIn):
        return self.model.predict(dataIn,verbose=0)

    @classmethod
    def selfTest(cls):
        test = LearnedSynergy([1])
        x = np.arange(-100, 100) / 12
        y = (x ** 2 + 2 * x + 1)/120
        test.trainModel(x, y)
        x2 = np.arange(-100, 100) / 10 + 0.005
        y2 = (x2 ** 2 + 2 * x2 + 1)/120
        y2Est = test.useModel(x2)
        plot(x2.reshape(x2.size,1), y2.reshape(x2.size,1), 'Expected', 1)
        plot(x2.reshape(x2.size,1), y2Est.reshape(x2.size,1), 'Estimated', 2)
        # self.model = tf.keras.models.Sequential([
        #     tf.keras.layers.Flatten(input_shape=sizeIn),
        #     tf.keras.layers.Dense(256, activation='sigmoid'),
        #     tf.keras.layers.Dense(1, activation='linear')
        # ])
        # self.model.fit(sampleIn, sampleOut, epochs=20, batch_size=1)
        # about 0.06 mean_absolute_error
        plt.show()
