"""
Interactive processing methods
"""
from aufgabe2_common import *
from aufgabe2 import applyObservation, getProbabilities, process_static

class ProcessDynamic:
    pFruits: List[Set[Fruit]]
    containsWanted: List[Union[int,float]]
    unusedBowls: Set[Bowl]
    foundFruits: Set[Fruit]
    tInput: TaskInput
    def __init__(self, tInput: TaskInput) -> None:
        self.tInput = tInput
        tOutput = process_static(tInput)
        self.pFruits = tOutput.pFruits
        self.containsWanted = tOutput.containsWanted
        self.unusedBowls = set(aBowls(tInput.F))
        self.foundFruits = set()
    def askNext(self):
        return max(self.unusedBowls, key=self.containsWanted.__getitem__)+1
    def useBowl(self, bowl: Bowl, fruitFound: Fruit):
        self.unusedBowls.discard(bowl)
        self.foundFruits.add(fruitFound)
        applyObservation(Observation({bowl}, {fruitFound}), self.pFruits)
        self.containsWanted = getProbabilities(self.tInput.fruitWanted, self.pFruits)

class Context:
    tInput: Union[TaskInput, None] = None
    processDynamic: ProcessDynamic
    active: bool = True
    usedBowls: Set[Bowl]
    obtainedFruits: Set[Fruit]

def onReadFile(context: Context):
    print("Please enter filename:")
    fName = input()
    try:
        context.tInput = readInput(fName)
    except Exception as e:
        print(f"An error has occured: {e}") 

def suggestBowls(context: Context):
    assert context.tInput is not None
    context.processDynamic = ProcessDynamic(context.tInput)
    while True:
        print("Options: (g)et bowl suggestion (u)se bowl (e)xit")
        res = input()
        if res == "g":
            nBowl = context.processDynamic.askNext()
            print(f"Try bowl number {nBowl} (Probability: {context.processDynamic.containsWanted[nBowl-1]})")
        elif res == "u":
            print("Which bowl did you use")
            res = input()
            if (int(res)-1 < 0 or int(res)-1 >= context.tInput.F):
                print("Bowl invalid")
                continue
            print("Which fruit did you find?")
            res2 = input()
            if not res2 in context.tInput.fStrings:
                if len(res2) < 1:
                    continue
                for s in context.tInput.fStrings:
                    if s[0] == res2[0]:
                        print(f"Did you mean {s}?")
                        break
                continue
            context.processDynamic.useBowl(Bowl(int(res)-1), context.tInput.fObjects[res2])
            if context.processDynamic.foundFruits.issuperset(context.tInput.fruitWanted):
                print("All desired fruit types where found")
                break
        elif res == "e":
            return
        else:
            print("Please enter a valid selection")
            continue

def onStart(context: Context):
    print("Options: (r)ead file (q)uit")
    res = input()
    if not res in ["r", "q"]:
        print("Please supply a valid selection")
        return
    if res == "r":
        onReadFile(context)
    elif res == "q":
        context.active = False
        return

def main():
    context = Context()
    while context.active:
        onStart(context)
        if context.tInput == None or not context.active:
            continue
        suggestBowls(context)

if __name__ == "__main__":
    main()