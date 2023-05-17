"""
Main file: Contains processing functions
"""
import timeit
from aufgabe2_common import *

def applyObservation(obs: Observation, pFruits: List[Set[Fruit]]):
    for bowl in aBowls(len(pFruits)):
        if bowl in obs.bowls:
            pFruits[bowl].intersection_update(obs.fruits)  
        else:
            pFruits[bowl].difference_update(obs.fruits)

def getProbabilities(fruitWanted: Set[Fruit], pFruits: List[Set[Fruit]]) -> List[Union[int, float]]:
    containsWanted: List[Union[int, float]] = [-1 for _ in range(len(pFruits))]
    for bowl in aBowls(len(pFruits)):
        prob = len(pFruits[bowl].intersection(fruitWanted))/len(pFruits[bowl])
        prob = round(prob) if round(prob) == prob else prob
        containsWanted[bowl] = prob
    return containsWanted

def process_static(tInput: TaskInput) -> TaskOutput:
    sTime = timeit.default_timer()

    pFruits: List[Set[Fruit]] = [set(aFruits(tInput.F)) for _ in aBowls(tInput.F)] #Time: O(F^2) Space: O(F^2)

    for obs in tInput.observations: #Time: O(N*F*avg(len(obs.fruits)))
        applyObservation(obs, pFruits)

    pBowls: List[Set[Bowl]] = [set() for _ in aFruits(tInput.F)]
    for bowl in aBowls(tInput.F):  #Max Time: O(F^2) Max Space: O(F^2)
        for fruit in pFruits[bowl]:
            pBowls[fruit].add(bowl)

    containsWanted = getProbabilities(tInput.fruitWanted, pFruits) #Avg Time: O(F) Max Time: O(F^2)
    
    tOutput = TaskOutput(tInput)
    tOutput.containsWanted = containsWanted
    tOutput.addpBowls(pBowls)
    tOutput.addpFruits(pFruits)
    tOutput.runtime = timeit.default_timer()-sTime
    return tOutput


def main():
    for i in range(8):
        tInput = readInput(f"spiesse{i}.txt")
        print(f"Processing spiesse{i}.txt")
        tOutput = process_static(tInput)
        print(f"Took {tOutput.runtime}")
        writeOutput(f"ausgabe{i}.txt", tOutput, verbose=True, detailed=True)

if __name__ == "__main__":
    main()
