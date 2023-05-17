"""
Common containers and functions
"""

import timeit
from typing import Callable, Iterable, List, Set

import numpy as np

#Constants
LOWER = 8
UPPER = 18
TLEN = 1000

class ZoneRequest:
    """Container for one request / "Voranmeldung"""
    tStart: int
    tEnd: int
    zLen: int
    area: int
    localID: int #Used to identify request internaly

    def __init__(self, tStart: int, tEnd: int, zLen: int, localID: int = -1) -> None:
        assert LOWER <= tStart < tEnd <= UPPER and zLen <= TLEN
        self.tStart = tStart
        self.tEnd = tEnd
        self.zLen = zLen
        self.area = (tEnd-tStart)*zLen
        self.localID = localID

class PlacedRequest(ZoneRequest):
    """Container for one placed request"""
    zStart: int
    zEnd: int

    def __init__(self, zRequest: ZoneRequest, zStart: int) -> None:
        assert 0 <= zStart < zStart+zRequest.zLen <= TLEN
        super().__init__(zRequest.tStart, zRequest.tEnd, zRequest.zLen, localID=zRequest.localID)
        self.zStart = zStart
        self.zEnd = zStart + self.zLen

class ProposedChange:
    """Container for possible change: \n
    Includes colliding placements and new placement"""
    colliders: List[PlacedRequest] #Placed requests that need to be removed
    nPlaced: PlacedRequest
    addedArea: int
    def __init__(self, colliders: List[PlacedRequest], nPlaced: PlacedRequest, colliderArea: int) -> None:
        self.colliders = colliders
        self.nPlaced = nPlaced
        self.addedArea = nPlaced.area - colliderArea

class TaskInput:
    N: int
    requests: List[ZoneRequest]
    #region Optional Params
    #Structure params
    forceSet: bool = False #Force set structure
    forceArray: bool = False #Force array structure
    maxCycles: int = -1
    reverseRequests: bool = False
    #Randomization params
    useRandomization: bool = False
    maxRepetitions: int = -1 #Default to unlimited
    maxRuntime: float = 0 #Defaults to one repetition
    seed: int = -1 #Defaults to random
    considerElementProb: float = 0.5 #Probability that element is considered during cycle
    #endregion
    def __init__(self) -> None:
        self.requests = []

class TaskOutput:
    placedRequests: Set[PlacedRequest]
    tArea: int
    runtime: float = -1
    def __init__(self, placedRequests: Set[PlacedRequest]) -> None:
        self.placedRequests = placedRequests
        self.tArea = sum([pReq.area for pReq in placedRequests])

def readInput(fileName: str) -> TaskInput:
    """Reads file in specified format"""
    tInput = TaskInput()
    with open(fileName, "r") as fIn:
        N = int(fIn.readline())
        tInput.N = N
        for _ in range(N):
            tStart, tEnd, zLen = [int(i) for i in fIn.readline().strip().split(" ")]
            tInput.requests.append(ZoneRequest(tStart, tEnd, zLen))
    return tInput

def getSamples():
    """Generator on all provided samples 1-8"""
    for t in range(1, 8):
        fName = f"flohmarkt{t}.txt"
        yield readInput(fName)

def writeOutput(fileName: str, tOutput: TaskOutput, verbose = False):
    """Writes output in plaintext"""
    def vOnly(string: str) -> str:
        return string if verbose else ''
    with open(fileName, "w", encoding="utf-8") as fOut:
        fOut.write(f"{vOnly('Laufzeit: ')}{tOutput.runtime}{vOnly('s')}\n")
        fOut.write(f"{vOnly('Einnahmen: ')}{tOutput.tArea}{vOnly('€')}\n")
        fOut.write(f"{vOnly('Standplätze: ')}{len(tOutput.placedRequests)}\n")
        for pReq in tOutput.placedRequests:
            fOut.write(f"{pReq.tStart} {pReq.tEnd} {pReq.zStart} {pReq.zEnd}\n")

def doCollide(a: PlacedRequest, b: PlacedRequest): 
    if b.zStart <= a.zStart < b.zEnd or b.zEnd >= a.zEnd > b.zStart or a.zStart <= b.zStart < a.zEnd or a.zEnd >= b.zEnd > a.zStart:
        if b.tStart <= a.tStart < b.tEnd or b.tEnd >= a.tEnd > b.tStart or a.tStart <= b.tStart < a.tEnd or a.tEnd >= b.tEnd > a.tStart:
            return True
    return False

def checkNoCollisions(placedRequests: Iterable[PlacedRequest]):
    """Checks whether placements are valid"""
    arr: np.ndarray = np.zeros(shape=(UPPER-LOWER, TLEN))
    for pReq in placedRequests:
        arr[pReq.tStart-LOWER:pReq.tEnd-LOWER, pReq.zStart:pReq.zEnd] += 1
    arr = arr.reshape((UPPER-LOWER)*TLEN)
    if len(np.where(arr > 1)[0]) != 0: #type: ignore
        return False
    return True

def areaSort(a: ZoneRequest):
    return a.area

def randomized(func: Callable[[TaskInput], TaskOutput]):
    """Enables repeated execution for randomized functions"""
    def wrapper(tInput: TaskInput, *args, **kwargs) -> TaskOutput:
        if not tInput.useRandomization or tInput.seed != -1: #No randomization or constant seed
            return func(tInput, *args, **kwargs)
        sTime = timeit.default_timer()
        bRes = TaskOutput(set()) #Best result
        lRTime = 0 #last runtime
        k = 0 #Repetition count
        while (k < tInput.maxRepetitions or tInput.maxRepetitions == -1) and (timeit.default_timer()+(lRTime/2)-sTime <= tInput.maxRuntime):
            nRes = func(tInput, *args, **kwargs)
            if nRes.tArea > bRes.tArea:
                bRes = nRes
            lRTime = nRes.runtime
            k += 1
        bRes.runtime = timeit.default_timer()-sTime
        return bRes
    return wrapper
