"""
Main file: contains standard processing functions
"""
import random
import timeit
from typing import Union, Tuple

import numpy as np

from aufgabe1_common import *

@randomized
def process_standard(tInput: TaskInput, onChange: Callable[[ProposedChange], None] = None) -> TaskOutput:
    """
    Processes input with heuristic method, dynamic structures and optional randomization
    """
    def yesorno(yesProb: float):
        return rnd.random() < yesProb

    def findInSet(nPlaced: PlacedRequest) -> Tuple[List[PlacedRequest], int]: #O(len(placedRequests))
        """Finds collision by iterating through set"""
        tArea = 0
        colliders = []
        for pReq in placedRequests: 
            if doCollide(pReq, nPlaced):
                tArea += pReq.area
                colliders.append(pReq)
        return colliders, tArea

    def findInArray(nPlaced: PlacedRequest) -> Tuple[List[PlacedRequest], int]: #O(tLen*zLen)
        """
        Finds collisions by iterating through array
        """
        tArea = 0
        colliders = set()
        for col in range(nPlaced.tStart-LOWER, nPlaced.tEnd-LOWER):
            for row in range(nPlaced.zStart, nPlaced.zEnd):
                pReq = zArray[col, row]
                if pReq is not None and not pReq in colliders:
                    colliders.add(pReq)
                    tArea += pReq.area
        return list(colliders), tArea


    def findColliders(nPlaced: PlacedRequest) -> Tuple[List[PlacedRequest], int]: #O(min(len(placedRequests), tLen*zLen))
        if tInput.forceSet:
            return findInSet(nPlaced)
        elif tInput.forceArray:
            return findInArray(nPlaced)
        elif len(placedRequests)  < nPlaced.area:
            return findInSet(nPlaced)
        else:
            return findInArray(nPlaced)
    
    def applyChange(change: ProposedChange): #O(len(colliders)*col.tLen*col.zLen)
        nonlocal didChange
        if onChange is not None: #Call hook
            onChange(change)
        #Remove colliding placements
        for collider in change.colliders: 
            if not tInput.forceSet:
                zArray[collider.tStart-LOWER:collider.tEnd-LOWER, collider.zStart:collider.zEnd] = None
            placedRequests.remove(collider)
            isPlaced[collider.localID] = False
        #Add new placement
        nPlaced = change.nPlaced
        if not tInput.forceSet: 
            zArray[nPlaced.tStart-LOWER:nPlaced.tEnd-LOWER, nPlaced.zStart:nPlaced.zEnd] = nPlaced

        placedRequests.add(nPlaced)
        isPlaced[nPlaced.localID] = True
        didChange = True

    sTime = timeit.default_timer()
    if tInput.useRandomization:
        rnd = random.Random()
        if tInput.seed == -1:
            rnd.seed()
        else:
            rnd.seed(tInput.seed)
    
    requests = tInput.requests.copy()
    requests.sort(key=areaSort, reverse=tInput.reverseRequests)  

    placedRequests: Set[PlacedRequest] = set()

    if tInput.forceArray or not tInput.forceSet:
        zArray = np.full(shape=(UPPER-LOWER, TLEN), dtype=PlacedRequest, fill_value=None)
    
    isPlaced: List[bool] = [False for _ in requests]

    for i in range(len(requests)):
        requests[i].localID = i
    
    didChange = True
    finalRound = False
    cycleCount = 0
    while (didChange or finalRound) and (tInput.maxCycles == -1 or cycleCount < tInput.maxCycles):
        cycleCount += 1
        didChange = False

        for req in requests:  
            if isPlaced[req.localID]:
                continue
            if tInput.useRandomization:
                if not finalRound and not yesorno(tInput.considerElementProb):
                    continue
            
            bChange: Union[ProposedChange, None] = None

            for zStart in range(TLEN-req.zLen):
                nPlaced = PlacedRequest(req, zStart)
                colliders, tArea = findColliders(nPlaced)
                if tArea < req.area and (bChange is None or bChange.addedArea < nPlaced.area-tArea):
                    bChange = ProposedChange(colliders, nPlaced, tArea)
            
            if bChange is not None:
                applyChange(bChange)

        if tInput.useRandomization:
            if not didChange and not finalRound:
                finalRound = True
            else:
                finalRound = False

    assert checkNoCollisions(placedRequests)
    tOutput = TaskOutput(placedRequests)
    tOutput.runtime = timeit.default_timer()-sTime
    return tOutput

def main():
    for t in range(1, 8):
        fName = f"flohmarkt{t}.txt"
        tInput = readInput(fName)
        print(f"Processing: {fName}")
        tOutput = process_standard(tInput)
        writeOutput(f"ausgabe{t}.txt", tOutput, verbose=False)
        print(f"Area: {tOutput.tArea}")
        print(f"Done: {tOutput.runtime}")
    pass

if __name__ == "__main__":
    main()
