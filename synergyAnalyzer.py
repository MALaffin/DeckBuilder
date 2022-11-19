import gc

import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor
from time import *
import random


def findLoops(A0, iterations=16, plotType=0):
    N = A0.shape[1]
    K = np.zeros([N, 1])
    A1 = np.copy(A0)
    inf = float('inf')
    # for r in range(N):
    #     A1[r, A1[r, :] != max(A1[r, :])] = -inf
    for c in range(N):
        A1[A1[:, c] != max(A1[:, c]), c] = -inf
    C = K
    Cs = C
    states = np.resize(range(N), [N, 1])
    x = np.resize(0, [1, 1])
    tmp = ParIterations()
    for iteration in range(iterations):
        C, stateOrder = iterate(A1, C)
        # C, stateOrder = tmp.iterate2(A, C)
        A1 = A1[:, stateOrder[:, 0]]
        Cs = np.concatenate((Cs, C))
        states = np.concatenate((states, states[stateOrder, -1]))
        x = np.concatenate([x, np.resize(iteration, [1, 1])])
        print(iteration)
    if plotType >= 1:
        imagesc(A1, 'TBD', 2)
    keep = np.unique(np.argmax(A1, 1))
    if plotType >= 0:
        Cs = np.resize(Cs, [iterations + 1, N])
        # keep = np.unique(states[:, -1])
        plotInteresting = Cs[:, keep]
        plot(x, plotInteresting, iterations, 1)
    combos = []
    for check in keep:
        fill = True
        for combo in combos:
            if check in combo:
                fill = False
        if fill:
            combo = [check]
            nextCard = np.argmax(A0[:, check])
            coreCombo = True
            while nextCard != check:
                if nextCard in combo:
                    nextCard = check
                    coreCombo = False
                else:
                    combo = combo + [nextCard]
                    nextCard = np.argmax(A0[:, nextCard])
            if coreCombo:
                print(combo)
                combos = combos + [combo]
    return combos


def findLoops2(A0, iterations=16, plotType=0):
    N = A0.shape[1]
    cost = np.zeros([N, 1])
    A1 = np.copy(A0)
    inf = float('inf')
    Cs = cost.copy()
    for iteration in range(iterations):
        # A1=iterate(A1, A1)
        [cost, state] = iterate(A1, cost)
        Cs = np.concatenate([Cs, cost])
        print(iteration)
    x = np.resize(np.array(range(iterations + 1)), [iterations + 1, 1])
    # if plotType >= 1:
    #     imagesc(A1, 'TBD', 2)
    if plotType >= 0:
        Cs = np.resize(Cs, [iterations + 1, N])
        costOrder = cost.argsort(axis=0)
        keep = costOrder[1:20].flatten()
        plotInteresting = Cs[:, keep]
        plot(x, plotInteresting, iterations, 1)
    combos = []
    for check in keep:
        combo = [check]
        nextCard = np.argmax(A0[:, check])
        for iteration in range(iterations):
            while nextCard != check:
                if nextCard in combo:
                    nextCard = check
                else:
                    combo.append(nextCard)
                    nextCard = np.argmax(A0[:, nextCard])
        combos = combos + [combo]
    return combos


# def prod(A, B):
#     AB = zeros(size(A, 1), size(B, 2));
#     for c = 1:size(B, 2):
#         for r=1:size(A, 1):
#             AB(r, c) = max(A(r,:)+B(:, c)');

def iterate(A, B):
    R = A.shape[0]
    C = B.shape[1]
    AB = np.zeros([R, C])
    ABargs = AB.astype(int)
    for c in range(C):
        for r in range(R):
            t = A[r, :] + B[:, c]
            ABargs[r, c] = int(np.argmax(t))
            AB[r, c] = t[ABargs[r, c]]
    return [AB, ABargs]


class ParIterations:

    def __init__(self):
        self.sharedA = None
        self.sharedB = None
        self.R = None
        self.C = None

    def subIt(self, c):
        AB = np.zeros([self.R, 1])
        ABargs = AB.astype(int)
        for r in range(self.R):
            t = self.sharedA[r, :] + self.sharedB[:, c]
            ABargs[r, 0] = int(np.argmax(t))
            AB[r, 0] = t[ABargs[r, 0]]
        return [AB, ABargs, c]

    mxPrcs = 3

    def iterate(self, A, B):
        self.sharedA = A
        self.sharedB = B
        self.R = A.shape[0]
        self.C = B.shape[1]
        AB = np.zeros([self.R, self.C])
        ABargs = AB.astype(int)
        with ProcessPoolExecutor(max_workers=self.mxPrcs) as pool:
            for res in pool.map(self.subIt, range(self.C)):
                AB[:, res[2]] = res[0][:, 0]
                ABargs[:, res[2]] = res[1][:, 0]
        return [AB, ABargs]

    def subIt2(self, r):
        AB = np.zeros([self.R, 1])
        ABargs = AB.astype(int)
        for c in range(self.C):
            t = self.sharedA[r, :] + self.sharedB[:, c]
            ABargs[r, 0] = int(np.argmax(t))
            AB[r, 0] = t[ABargs[r, 0]]
        return [AB, ABargs, c]

    def iterate2(self, A, B):
        self.sharedA = A
        self.sharedB = B
        self.R = A.shape[0]
        self.C = B.shape[1]
        AB = np.zeros([self.R, self.C])
        ABargs = AB.astype(int)
        with ProcessPoolExecutor(max_workers=self.mxPrcs) as pool:
            for res in pool.map(self.subIt2, range(self.R)):
                AB[:, res[2]] = res[0][:, 0]
                ABargs[:, res[2]] = res[1][:, 0]
        return [AB, ABargs]


def imagesc(data, title, figId):
    fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=figId)
    h = ax.imshow(data, extent=[.5, len(data) + .5, .5, len(data[0]) + .5], vmin=-1,
                  vmax=0, aspect='auto')
    plt.colorbar(h)
    ax.set_title(title)
    plt.tight_layout()
    plt.show(block=False)


def plot(x, y, title, figId):
    plt.close(figId)
    fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=figId)
    for p in range(y.shape[1]):
        h = plt.plot(x[:, 0], y[:, p])
    ax.set_title(title)
    plt.tight_layout()
    # plt.show(block=False)
    plt.pause(0.5)


def findBasis(dist, basisSize, factor=.99):
    N = np.shape(dist)[0]
    candidates = np.flip(np.argsort(np.sum(dist, axis=0)))
    basis = []
    lastErr = float('inf')
    sizes = []
    errors = []
    t = time()
    test = -1
    altErr = np.ones([N, 1]) * float('inf')
    bestErr = np.ones([N, 1]) * float('inf')
    for candidate in candidates:
        test = test + 1
        basisTest = basis + [candidate]
        e = 0
        altErr = np.copy(bestErr)
        # for element in range(N):
        #     # errs = np.reshape(dist[:, element],[N, 1])-np.reshape(dist[:, candidate],[N, 1])
        #     errs = dist[:, element]-dist[:, candidate]
        #     er = np.sum(np.square(errs), axis=0)
        #     e=e+er
        #     if er<bestErr[element]:
        #         altErr[element]=er
        errs = dist - np.reshape(dist[:, candidate], [N, 1])
        er = np.sum(np.square(errs), axis=0)
        e = np.sum(er)
        altErr = np.minimum(altErr, bestErr)
        if lastErr * factor > e:
            elapsed1 = time() - t
            bestErr = np.copy(altErr)
            basis = basisTest
            lastErr = e
            print(f"cards checked: {test} basisSize: {len(basis)} error: {e} time: {elapsed1} basis: {basis}")
            if test % 50 == 0:
                sizes = sizes + [len(basis)]
                errors = errors + [e]
                plot(np.array(sizes).reshape([len(sizes), 1]), np.array(errors).reshape([len(sizes), 1]),
                     'basis size vs error', 'basis builder')
        if len(basis) == basisSize:
            return basis
    return basis


def findBasis2(dist, basisSize, factor=.99):
    N = np.shape(dist)[0]
    candidates = np.flip(np.argsort(np.sum(dist, axis=0)))
    basis = []
    bestErr = np.ones([N, 1]) * float('inf')
    sizes = []
    errors = []
    lastErr = float('inf')
    t = time()
    for test in range(N):
        if test == 0:
            candidate = candidates[0]
        else:
            repesentation = np.sum(np.square(dist[:, basis]), axis=1)
            repesentation[basis] = float('inf')
            candidate = np.argmin(repesentation)
        errs = dist - np.reshape(dist[:, candidate], [N, 1])
        er = np.sum(np.square(errs), axis=0)
        possibleErr = np.minimum(er, bestErr)
        e = np.sum(possibleErr)
        # if e<lastErr:
        #     basis = basis + [candidate]
        #     bestErr=possibleErr
        #     lastErr=e
        basis = basis + [candidate]
        bestErr = possibleErr
        elapsed1 = time() - t
        print(f"cards checked: {test} basisSize: {len(basis)} error: {e} time: {elapsed1} basis: {basis}")
        sizes = sizes + [len(basis)]
        errors = errors + [e]
        if test % 50 == 0:
            plot(np.array(sizes).reshape([len(sizes), 1]), np.log(np.array(errors).reshape([len(sizes), 1])),
                 'basis size vs error', 'basis builder')
        if len(basis) == basisSize:
            plt.show(block=True)
            return basis
    plt.show(block=False)
    return basis


def findBasis3(dist, basisSize, factor=.99):
    N = np.shape(dist)[0]
    W = np.sqrt(np.mean(np.square(dist), axis=0))
    candidates = np.flip(np.argsort(W))
    basis = []
    bestErr = np.ones([N, 1]) * float('inf')
    sizes = []
    errors = []
    lastErr = float('inf')
    t = time()
    for test in range(N):
        if test == 0:
            basis = [candidates[0]]
            distEst = np.reshape(dist[:, basis], [N, 1])
        else:
            # repesentation = np.sum(np.square(dist[:, basis]), axis=1)
            # repesentation[basis]=float('inf')
            # candidate=np.argmin(repesentation)
            # basis = basis + [candidate]
            # basis = basis + [candidates[test]]
            repesentation = np.sum(np.square(dist[:, basis]), axis=1)
            repesentation[basis] = float('inf')
            weightedRepresentation = repesentation / W
            weightedRepresentation[W == 0] = float('inf')
            candidate = np.argmin(weightedRepresentation)
            basis = basis + [candidate]
            # linear model
            # dist~=B*model;B=dist[:, basis]
            # B*dist~=Bt*B*model
            # (Bt*B)^-1*B*dist~=model
            B = np.square(dist[:, basis])
            Bt = np.transpose(B)
            BtB = np.matmul(Bt, B)
            BtD = np.matmul(Bt, dist)
            del Bt
            try:
                model = np.matmul(np.linalg.inv(BtB), BtD)
            except:
                basis = basis[0:-1]
                plot(np.array(sizes).reshape([len(sizes), 1]), np.log(np.array(errors).reshape([len(sizes), 1])),
                     'basis size vs error', 'basis builder')
                # plt.show(block=True)
                return basis  # if there are lineaity issues, it is over
                del BtB
                del BtD
                del B
                W[candidate] = 0
                continue  # or just remove and try the next [relevent for simple word lists]
            del BtB
            del BtD
            distEst = np.matmul(B, model)
            del B
            gc.collect()
        errs = dist - distEst
        del distEst
        gc.collect()
        er = np.sum(np.square(errs), axis=0)
        del errs
        gc.collect()
        possibleErr = np.minimum(er, bestErr)
        e = np.sum(possibleErr)
        bestErr = possibleErr
        elapsed1 = time() - t
        print(f"cards checked: {test} basisSize: {len(basis)} error: {e} time: {elapsed1} basis: {basis}")
        sizes = sizes + [len(basis)]
        errors = errors + [e]
        if test % 50 == 0:
            plot(np.array(sizes).reshape([len(sizes), 1]), np.log(np.array(errors).reshape([len(sizes), 1])),
                 'basis size vs error', 'basis builder')
        if len(basis) == basisSize:
            plt.show(block=True)
            return basis
    plot(np.array(sizes).reshape([len(sizes), 1]), np.log(np.array(errors).reshape([len(sizes), 1])),
         'basis size vs error', 'basis builder')
    plt.show()#plt.show(block=True)
    return basis


def findNetworks(synergy, constraints, iterations=5, maxDeckPool=50):
    # networks will be deck seeds grown off of synergy
    # growth will be near exponential, so 5 iterations will likely fill up the decks
    # constraints will be size dim 1 of synergy
    # it will contain positive numbers for required deck and negative values for
    # those that must eventually be connected; if not connected after iteration need error
    connections = np.array(constraints).flatten()
    allowed = 0 * connections
    allowed[connections > 0] = -float('inf')
    growBy = 1
    for iteration in range(iterations):
        print('iteration ' + str(iteration))
        cmdrs = np.unique(np.array(constraints))
        deckCount = np.sum(cmdrs > 0)
        numStillRequired = np.sum(connections == -1) \
            + np.sum(connections == -2)# to be spread between decks
        collectionCount = np.sum(connections > 0)  # to be spread between decks
        allowed = 0 * connections
        if numStillRequired:  # sort required cards first
            allowed[connections >= 0] = -float('inf')
        else:
            allowed[connections > 0] = -float('inf')
        for c in range(1, deckCount + 1):
            temp = np.nonzero(connections == c)
            cards = temp[0]
            for card in cards:
                deckSize = np.sum(connections == c)
                quota = (numStillRequired / deckCount + collectionCount / deckCount - deckSize)
                if (numStillRequired > 0 and quota < 0) \
                        or deckSize > maxDeckPool \
                        or deckSize > 3 ** (iteration + 1):  # try to align deck size with 3^iteration
                    break
                connect = np.argmax(synergy[card, :] + allowed)
                connections[connect] = c
                allowed[connections > 0] = -float('inf')
                connect = np.argmax(synergy[:, card] + allowed)
                connections[connect] = c
                allowed[connections > 0] = -float('inf')
            print(str(c) + ' started with ' + str(deckSize) + ' and ended with ' + str(np.sum(connections == c)))
    cmdrs = np.unique(connections)
    deckpools = []
    for c in range(cmdrs.size):
        temp = np.nonzero(connections == cmdrs[c])
        cards = temp[0]
        if cmdrs[c] > 0:
            deckpools.append(cards)
        if cmdrs[c] == -1:
            notSet = len(cards)
            print(str(notSet) + ' not placed')
    return deckpools

def findNetworks2(classes,comanderClasses,commanderPoolsByIdentity, synergy, constraints, sourceInfo, mannaCurve, format=100):
    # networks will be deck seeds grown off of synergy
    # growth will be near exponential, so 5 iterations will likely fill up the decks
    # constraints will be size dim 1 of synergy
    # it will contain positive numbers for required deck and negative values for
    # those that must eventually be connected; if not connected after iteration need error
    connections = np.array(constraints).flatten()
    deckCount = len(comanderClasses)  
    deckpools = [[] for i in range(deckCount+1)]
    for c in range(1, deckCount + 1):
        temp = np.nonzero(connections == c)
        cards = temp[0]
        deckpools[c-1] = cards.tolist()
    for iteration in range(format):
        print('iteration ' + str(iteration))           
        for c in range(1, deckCount + 1):
            deckSize = np.sum(connections == c)
            #if deckSize>iteration:
            #    continue
            if deckSize>=format:
                if deckSize>format:
                    print("size error")
                continue
            #validate colors       
            allowed=0+commanderPoolsByIdentity[c-1,:]
            if(sum(allowed==0)==0):
                print("none allowed")
            #cant use a card twice
            allowed[connections > 0] = -float('inf')
            if(sum(allowed==0)==0):
                print("none allowed")
            if deckSize < mannaCurve[0]:#allow cards by mana curve next                
                # allow required cards first     
                numStillRequired = np.sum(np.logical_and(connections == 0, classes.astype(int)&comanderClasses[c-1].astype(int)))
                if numStillRequired>0:       
                    allowed[0==(classes.astype(int)&comanderClasses[c-1].astype(int))] = -float('inf')
                else:
                    allowed[sourceInfo[:,0]>0]=-float('inf')
                if(sum(allowed==0)==0):
                    print("none allowed")
            else:
                #must make manna
                allowed[sourceInfo[:,0]<1]=-float('inf')
                if(sum(allowed==0)==0):
                    print("none allowed")
                if deckSize < mannaCurve[1]:#sort by casting cost
                    allowed[sourceInfo[:,1]>0]=-float('inf')
                elif deckSize < mannaCurve[2]:
                    allowed[sourceInfo[:,1]>1]=-float('inf')
                elif deckSize < mannaCurve[3]:
                    allowed[sourceInfo[:,1]>2]=-float('inf')
                elif deckSize < mannaCurve[4]:
                    allowed[sourceInfo[:,1]>3]=-float('inf')
                elif deckSize < mannaCurve[5]:
                    allowed[sourceInfo[:,1]>4]=-float('inf')
            if(sum(allowed==0)==0):
                print("none allowed")
            temp = np.nonzero(connections == c)
            cards = temp[0]
            deckSynergy=np.mean(synergy[cards, :], axis=0)
            connect = np.argmax(deckSynergy + allowed)
            connections[connect] = c
            deckpools[c-1].append(connect)
            #print(str(c) + ' started with ' + str(deckSize) + ' and ended with ' + str(np.sum(connections == c)))
    
    temp = np.nonzero(connections < 0)
    cards = temp[0]
    deckpools[deckCount]=cards
    if len(cards)>0:
        notSet = len(cards)
        print(str(notSet) + ' not placed')
    return deckpools


def findDecksGA(synergy, constraints, iterations=5, maxDeckPool=50):
    seeds = findNetworks(synergy, constraints, iterations, maxDeckPool)
    N = np.shape(synergy)[0]
    random.seed(0)
    random.randint(0, N - 1)


def findLoops3(A0, maxiterations=16, numcombos=30):
    N = A0.shape[1]
    syn0 = np.zeros([N, 1])
    A1 = A0
    inf = -1*float('inf')
    Cs = syn0.copy()
    state0 = range(N)
    combos = []
    for combo in range(numcombos):
        syn = syn0
        states = []
        for iteration in range(maxiterations):
            # A1=iterate(A1, A1)
            [syn, state] = iterate(A1, syn)
            states.append(state)
        testLoc = np.argmax(syn)
        states = np.array(states)
        used = np.unique(states[:, testLoc])
        combos.append(used)
        A1[used, :] = inf
        A1[:, used] = inf
        syn[used] = inf

    return combos
