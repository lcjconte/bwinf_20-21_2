"""
Common functions and containers
"""
from typing import List, Dict, NewType, Set, Union

Bowl = NewType("Bowl", int) #Bowl type for better readability
Fruit = NewType("Fruit", int) # Fruit type for better readability

def aBowls(F: int):
    """Returns all bowls in range F"""
    for b in range(F):
        yield Bowl(b)

def aFruits(F: int):
    """Returns all fruits in range F"""
    for f in range(F):
        yield Fruit(f)

class Observation:
    bowls: Set[Bowl]
    fruits: Set[Fruit]
    def __init__(self, bowls: Set[Bowl] = set(), fruits: Set[Fruit] = set()) -> None:
        self.bowls = bowls
        self.fruits = fruits
    

class TaskInput:
    F: int #F: int #Amount of fruit types
    N: int #N: int #Amount of observations
    fruitWanted: Set[Fruit] #
    observations: List[Observation]
    fStrings: List[str] 
    fObjects: Dict[str, Fruit]
    inputFile: str #Name of input file (optional)
    def __init__(self) -> None:
        self.inputFile = ""
        self.fruitWanted = set()
        self.observations = []
        self.fStrings = []
        self.fObjects = {}
    def readFruit(self, s: str) -> Fruit:
        """Fruit string to fruit object"""
        if not s in self.fObjects.keys():
            self.fObjects[s] = Fruit(len(self.fStrings))
            self.fStrings.append(s)
        return self.fObjects[s]
    
    def readBowl(self, s: str) -> Bowl:
        """Bowl string to bowl object"""
        return Bowl(int(s)-1)

class TaskOutput:
    tInput: TaskInput #Reference to input
    pBowls: List[Set[Bowl]] #Possible containing bowls foreach fruit
    pFruits: List[Set[Fruit]] #Possible contained fruits foreach bowl
    possibleBowls: Dict[str, Set[Bowl]] #Same as pBowls with fruit strings instead of indices
    possibleFruits: Dict[Bowl, Set[str]] #Same as pFruits with fruit strings instead of indices
    containsWanted: List[Union[int, float]] #Probability that a bowl contains a wanted fruit    
    runtime: float #Run duration
    def __init__(self, tInput: TaskInput) -> None:
        self.tInput = tInput
        self.pBowls = []
        self.pFruits = []
    
    def addpBowls(self, pBowls: List[Set[Bowl]]):
        """Adds pBowls to output"""
        self.pBowls = pBowls
        self.possibleBowls = {}
        for fruit in aFruits(self.tInput.F):
            self.possibleBowls[self.tInput.fStrings[fruit]] = pBowls[fruit]

    def addpFruits(self, pFruits: List[Set[Fruit]]):
        """Adds pFruits to output"""
        self.pFruits = pFruits
        self.possibleFruits = {}
        for bowl in aBowls(self.tInput.F):
            self.possibleFruits[bowl] = set([self.tInput.fStrings[fruit] for fruit in pFruits[bowl]])

def readInput(fileName: str) -> TaskInput:
    """
    Reads file\n
    Returns task input
    """
    tInput = TaskInput()
    tInput.inputFile = fileName
    
    with open(fileName, "r") as fIn:
        tInput.F = int(fIn.readline())
        tInput.fruitWanted = set([tInput.readFruit(s) for s in fIn.readline().strip().split(" ")])
        tInput.N = int(fIn.readline())
        tInput.observations = []
        for _ in range(tInput.N):
            nObservation = Observation()
            nObservation.bowls = set([tInput.readBowl(s) for s in fIn.readline().strip().split(" ")])
            nObservation.fruits = set([tInput.readFruit(s) for s in fIn.readline().strip().split(" ")])
            tInput.observations.append(nObservation)
    
    for i in range(tInput.F-len(tInput.fStrings)):
        tInput.fStrings.append(f"Unknown{i}")
        tInput.fObjects[f"Unknown{i}"] = Fruit(len(tInput.fStrings)-1)
    
    return tInput

def writeOutput(fileName: str, tOutput: TaskOutput, verbose: bool=True, detailed: bool = False):
    def vOnly(string: str) -> str:
        return string if verbose else ''
    with open(fileName, "w", encoding="utf-8") as fOut:
        if detailed:
            fOut.write(f"{vOnly('Ergebnisse für ')}{tOutput.tInput.inputFile if tOutput.tInput.inputFile != '' else 'Unknown'}\n")
            fOut.write(f"{vOnly('Laufzeit: ')}{tOutput.runtime}\n")
        fOut.write(f"{vOnly('Wahrscheinlichkeit, dass Schüssel i gesuchte Frucht enthält: ')}{' '.join([str(i) for i in tOutput.containsWanted])}\n")
        mContain = ' '.join([str(bowl+1) for bowl in aBowls(tOutput.tInput.F) if tOutput.containsWanted[bowl] == 1])
        fOut.write(f"{vOnly('Schüsseln, die gesuchte Früchte enthalten: ')}{mContain}\n")
        cContain = ' '.join([str(bowl+1) for bowl in sorted(aBowls(tOutput.tInput.F), key=tOutput.containsWanted.__getitem__, reverse=True) if not tOutput.containsWanted[bowl] in [0, 1]])
        fOut.write(f"{vOnly('Schüsseln, die gesuchte Früchte enthalten könnten: ')}{cContain}\n")
        if detailed:
            fOut.write(vOnly('Mögliche Schüsseln für jede Frucht:\n'))
            for fruit in aFruits(tOutput.tInput.F):
                fOut.write(f"{tOutput.tInput.fStrings[fruit]} {' '.join([str(bowl+1) for bowl in tOutput.pBowls[fruit]])}\n")

