
from typing import Dict

import matplotlib.pyplot as plt

from aufgabe1 import *
from aufgabe1_generator import *
from aufgabe1_visualizer import Visualizer

def testSort_samples():
    rTimes_01 = np.zeros((7,))
    rTimes_10 = np.zeros((7,))
    tArea_01 = np.zeros((7,))
    tArea_10 = np.zeros((7,))
    x = np.arange(1, 8)
    for t, tInput in enumerate(getSamples()):
        tInput.reverseRequests = False
        tOutput = process_standard(tInput)
        rTimes_01[t] = tOutput.runtime
        tArea_01[t] = tOutput.tArea

        tInput.reverseRequests = True
        tOutput = process_standard(tInput)
        rTimes_10[t] = tOutput.runtime
        tArea_10[t] = tOutput.tArea
    plt.xlabel("Beispiel")
    plt.ylabel("Einnahmen")
    plt.plot(x, tArea_01, label="0->1")
    plt.plot(x, tArea_10, label="1->0")
    plt.legend(loc='best')
    plt.show()

#testSort_samples()

def testSort_randoms(nMin: int = 1, nMax = 200, step = 10, repeat: int=1):
    x = np.arange(nMin, nMax+1, step)
    rTimes_01 = np.zeros((len(x),))
    rTimes_10 = np.zeros((len(x),))
    tArea_01 = np.zeros((len(x),))
    tArea_10 = np.zeros((len(x),))
    for t, n in enumerate(x):
        rTim_01 = []
        rTim_10 = []
        tA_01 = []
        tA_10 = []
        for _ in range(repeat):
            tInput = generateCase(n)
            tOutput = process_standard(tInput)
            rTim_01.append(tOutput.runtime) 
            tA_01.append(tOutput.tArea) 

            tInput.reverseRequests = True
            tOutput = process_standard(tInput)
            rTim_10.append(tOutput.runtime) 
            tA_10.append(tOutput.tArea) 
        rTimes_01[t] = sum(rTim_01)/len(rTim_01)
        rTimes_10[t] = sum(rTim_10)/len(rTim_10)
        tArea_01[t] = sum(tA_01)/len(tA_01)
        tArea_10[t] = sum(tA_10)/len(tA_10)
    plt.xlabel("N")
    plt.ylabel("Laufzeit")
    plt.plot(x, rTimes_01, label="0->1")
    plt.plot(x, rTimes_10, label="1->0")
    plt.legend(loc='best')
    plt.show()

#testSort_randoms(nMin = 100, nMax=200, step=5, repeat=5)

def showChanges(animateChange: bool = True, tInterval: float = 0):
    from time import sleep
    def onChange(change: ProposedChange):
        placedDict[change.nPlaced] = visu.drawPlaced(change.nPlaced)
        for pReq in change.colliders:
            print("rem")
            visu.removeElement(placedDict[pReq])
            placedDict.pop(pReq)
        sleep(tInterval)
    for (t, tInput) in enumerate(getSamples()):
        visu = Visualizer(interact=(True if animateChange else False))
        placedDict: Dict[PlacedRequest, int] = {}
        print(f"Processing: {t+1}")
        tOutput = process_standard(tInput, (onChange if animateChange else None))
        if not animateChange:
            for pReq in tOutput.placedRequests:
                visu.drawPlaced(pReq)
        print(tOutput.tArea)
        print(f"Done: {tOutput.runtime}")
        visu.block()
        
#showChanges(animateChange=False)

def standardVrandom(sRTime: float, cProb: float):
    """Compares normal vs randomized processing"""
    tArea_norm = np.zeros((7,))
    tArea_ran = np.zeros((7,))
    for (i, tInput) in enumerate(getSamples()):
        print(f"Processing: {i+1}")
        tOutput = process_standard(tInput)
        tArea_norm[i] = tOutput.tArea
        tInput.useRandomization = True
        tInput.considerElementProb = cProb
        tInput.maxRuntime = sRTime
        tInput.reverseRequests = True
        tOutput = process_standard(tInput)
        tArea_ran[i] = tOutput.tArea
    plt.xlabel("Beispiel")
    plt.ylabel("Einnahmen")
    plt.plot(np.arange(1, 8), tArea_norm, label="Normal")
    plt.plot(np.arange(1, 8), tArea_ran, label="Randomisiert")
    plt.legend(loc='best')
    plt.show()
    pass
#standardVrandom(60, 0.6)

def getResults_samples(sRTime: float, cProb: float):
    """Randomized results for samples"""
    for (i, tInput) in enumerate(getSamples()):
        tInput.useRandomization = True
        tInput.considerElementProb = cProb
        tInput.maxRuntime = sRTime
        tInput.reverseRequests = True
        print(f"Processing: {i+1}")
        tOutput = process_standard(tInput)
        writeOutput(f"ausgabe{i+1}.txt", tOutput, verbose=True)
        print(f"Done: {tOutput.tArea} | {tOutput.runtime}")

#getResults_samples(sRTime=60, cProb=0.6)

def getResults_randoms(sCount: int, rTime: float, reverse: bool = True, mN=200):
    """Randomied results for random input"""
    tArea = []
    eProb = []
    x = []
    for xV in np.random.random((sCount)):
        n = random.randint(1, mN)
        tInput = generateCase(n)
        tInput.useRandomization = True
        tInput.considerElementProb = xV
        tInput.reverseRequests = reverse
        tInput.maxRuntime = rTime
        x.append(n)
        eProb.append((xV, xV, xV))
        tOutput = process_standard(tInput)
        tArea.append(tOutput.tArea)
    plt.xlabel("N")
    plt.ylabel("Einnahmen")
    plt.scatter(x, tArea, c=eProb)
    plt.show()
    pass
#getResults_randoms(25, 60)

def pyVScpp():
    x = np.arange(1, 8)
    y1 = [3.6147339, 7.1946025, 7.550735999999999, 0.031351399999998364, 0.15099220000000102, 0.06969959999999986, 5.517988800000001]
    y2 = [2.32800007, 6.95200014, 7.27400017, 0.00400000019, 0.0340000018, 0.0130000003, 5.70800018]
    plt.xlabel("Beispiel")
    plt.ylabel("Laufzeit")
    plt.plot(x, y1, label="Python")
    plt.plot(x, y2, label="C++")
    plt.legend(loc='best')
    plt.show()
#pyVScpp()

def randVSNN():
    x = np.arange(1, 8)
    sTArea = np.array([8028, 9060, 8721, 7370, 8599, 7883, 9749])
    nnTAreab = np.array([6190, 6659, 6729, 4943, 6384, 4361, 7053])
    nnTArea50 = np.array([7414, 7700, 7701, 5929, 6854, 7381, 8158])
    plt.xlabel("Beispiel")
    plt.ylabel("Einnahmen")
    plt.bar(x, height=sTArea-4000, bottom=np.full((7,), 4000),label="Standard 60s")
    plt.bar(x, height=nnTArea50-4000, bottom=np.full((7,), 4000),label="5 Netzwerke Gen 50")
    plt.bar(x, height=nnTAreab-4000, bottom=np.full((7,), 4000),label="5 Netzwerke Gen 0")
    plt.legend(loc='best')
    plt.show()
#randVSNN()

def additionalExamples():
    tInput = readInput("beispiel8_ein.txt")
    writeOutput("beispiel8_aus.txt", process_standard(tInput))
    tInput = readInput("beispiel9_ein.txt")
    writeOutput("beispiel9_aus.txt", process_standard(tInput))

#additionalExamples()
