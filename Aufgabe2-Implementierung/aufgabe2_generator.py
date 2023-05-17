import random
from aufgabe2_common import *
from bisect import bisect_left

def generateCase(F: int, N: int, mA: int, wA: int, seed: int = -1) -> TaskInput:
    """
    Generates random input\n
    F: Amount of fruit types
    N: Amount of observations
    mA: Maxmimum amount of bowls in observation
    wA: Amount of desired fruit types
    """
    if seed < 0:
        seed = random.randrange(1_000_000)
    rnd = random.Random(seed)

    tInput = TaskInput()
    tInput.F = F
    tInput.N = N
    for fruit in aFruits(F):
        tInput.fStrings.append(f"fruit{fruit}")
        tInput.fObjects[f"fruit{fruit}"] = Fruit(fruit)
    
    assigned: Dict[Bowl, Fruit] = {}
    rFruits = list(aFruits(F))
    for bowl in aBowls(F):
        fruit = rnd.choice(rFruits)
        del rFruits[bisect_left(rFruits, fruit)]
        assigned[bowl] = fruit

    for _ in range(N):
        nObservation = Observation()
        nObservation.bowls = set(rnd.sample(set(aBowls(F)), k=rnd.randint(1, mA)))
        nObservation.fruits = set()
        for bowl in nObservation.bowls:
            nObservation.fruits.add(assigned[bowl])
        
        tInput.observations.append(nObservation)
    tInput.fruitWanted = set(rnd.sample(set(aFruits(F)), wA))
    return tInput
