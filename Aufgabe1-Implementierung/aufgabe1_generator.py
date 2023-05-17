from aufgabe1_common import *
import random as rnd
import math

def generateCase(N: int, tInput: TaskInput = None, seed: int = -1, dense=False) -> TaskInput:
    """
    Generates random input\n
    If dense is True the sizes will be on the gamma distribution with shape = 3 (seed will not be used)
    """
    if tInput is None:
        tInput = TaskInput()
    tInput.N = N
    tInput.requests = []
    rnd.seed(seed if seed != -1 else None)
    if not dense:
        for _ in range(N):
            tStart = rnd.randint(LOWER, UPPER-1)
            tInput.requests.append(ZoneRequest(tStart, rnd.randint(tStart+1, UPPER), rnd.randint(1, TLEN)))
    else:
        sizes = np.random.gamma(3, scale=40, size=N) 
        for i in range(N):
            s = round(sizes[i])
            timeLen = rnd.randint(1, min(10, s))
            tStart = rnd.randint(LOWER, UPPER-timeLen)
            tInput.requests.append(ZoneRequest(tStart, tStart+timeLen, int(s/timeLen)))
    return tInput

def inputToFile(tInput: TaskInput, fileName: str):
    with open(fileName, "w") as fOut:
        fOut.write(f"{tInput.N}\n")
        for req in tInput.requests:
            fOut.write(f"{req.tStart} {req.tEnd} {req.zLen}\n")
    