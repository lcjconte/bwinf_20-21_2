"""
Performance testing and other functions
"""
from random import randint

import matplotlib.pyplot as plt
import numpy as np

from aufgabe2 import *
from aufgabe2_common import *
from aufgabe2_generator import generateCase

def testSamples():
    rTime = np.zeros((8,))
    for i in range(8):
        tInput = readInput(f"spiesse{i}.txt")
        print(f"Processing spiesse{i}.txt")
        tOutput = process_static(tInput)
        rTime[i] = tOutput.runtime
        print(f"Took {tOutput.runtime}")
    plt.xlabel("Beispiel")
    plt.ylabel("Laufzeit")
    plt.plot(rTime)
    plt.show()
#testSamples()

def testRandom(t: float):
    """
    Runs for approx. t seconds with random input
    """
    sTime = timeit.default_timer()
    tRuns = 0
    fList = []
    nList = []
    maxN = 200
    rTimes = []
    while (timeit.default_timer()-sTime < t):
        f = randint(2, 400)
        n = randint(2, 200)
        m = randint(1, f//2)
        tInput = generateCase(f, n, m, f)
        tOutput = process_static(tInput)
        tRuns += 1
        rTimes.append(tOutput.runtime)
        fList.append(f)
        nList.append((n/maxN, n/maxN, n/maxN))
        print(f"Remaining: {round(t-timeit.default_timer()+sTime)} Done: {tRuns}", end="\r")
    print(f"Done {tRuns}")
    plt.xlabel("F")
    plt.ylabel("Laufzeit")
    plt.scatter(fList, rTimes, s=2, c=nList)
    plt.show()

#testRandoms(40)
