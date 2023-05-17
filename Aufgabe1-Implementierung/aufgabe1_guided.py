
import random
import json
import os.path as path
from typing import Union, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

from aufgabe1_common import *
from aufgabe1_generator import *

MAX_N = 750   #Nums used are 32 bit

def yesorno(yesProb: float):
    return random.random() < yesProb

#region Container Definitions
class Episode:
    dataIn: tf.Tensor
    expected: tf.Tensor
    value: int
    def __init__(self, dataIn: np.ndarray, expected: np.ndarray) -> None:
        self.dataIn = tf.convert_to_tensor(dataIn, dtype=tf.float32)
        self.expected = tf.convert_to_tensor(expected, dtype=tf.float32)

class EpisodeMemory:
    """
    Serialization not implemented!!
    """
    maxEpisodes: int
    _episodes: List[Episode]
    def __init__(self, maxEpisodes: int) -> None:
        self.maxEpisodes = maxEpisodes
        self._episodes = []
    def push(self, episodes: List[Episode]):
        self._episodes.extend(episodes)
        if len(self._episodes) > self.maxEpisodes:
            del self._episodes[:len(self._episodes)-self.maxEpisodes]
    def draw(self, n, overflow = True):
        """Draws random sample of size n"""
        if n > len(self._episodes):
            return self._episodes + (random.choices(self._episodes, k=n-len(self._episodes)) if overflow else [])
        else:
            return random.sample(self._episodes, n)

class TaskOutputGuided(TaskOutput):
    """
    Adds episode list
    """
    orderingEp: Episode
    placementEps: List[Episode]
    def __init__(self, placedRequests: Set[PlacedRequest], orderingEp: Episode, placementEps: List[Episode]) -> None:
        super().__init__(placedRequests)
        self.orderingEp = orderingEp
        self.placementEps = placementEps

#region Net definitions
def getOrderingNet():
    """
    Model takes processing state and returns value for each request (larger value is placed first / ordering of requests)
    """
    model = keras.Sequential()
    model.add(keras.Input(shape=(MAX_N, 6), dtype=tf.int32))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(MAX_N*4, activation="relu"))
    model.add(keras.layers.Dense(MAX_N*4, activation="relu"))
    model.add(keras.layers.Dense(MAX_N, activation="sigmoid"))
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.01),
              loss=keras.losses.MeanSquaredError())
    return model

def getPlacementNet():
    """
    Model takes processing state and returns value for each placement position to TLEN (where to try and place first)
    """
    model = keras.Sequential()
    model.add(keras.Input(shape=(MAX_N+1, 6), dtype=tf.int32)) #Add current req at end
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(MAX_N*2, activation="relu"))
    model.add(keras.layers.Dense(TLEN*2, activation="relu"))
    model.add(keras.layers.Dense(TLEN+1, activation="sigmoid"))
    model.compile(optimizer=keras.optimizers.Adam(),
              loss=keras.losses.MeanSquaredError())
    return model
#endregion

def orderingSelector(model: keras.Model, rProb: float):
    def wrapper(reqArray: np.ndarray) -> tf.Tensor:
        assert reqArray.shape == (MAX_N, 6)
        if yesorno(rProb):
            return tf.convert_to_tensor(np.random.dirichlet(np.ones(MAX_N),size=1), dtype=tf.float32)
        else:
            return model(tf.convert_to_tensor(np.expand_dims(reqArray, 0), dtype=tf.int32)) #type: ignore
    return wrapper

def placementSelector(model: keras.Model, rProb: float):
    def wrapper(reqArray: np.ndarray) -> tf.Tensor:
        assert reqArray.shape == (MAX_N+1, 6)
        if yesorno(rProb):
            return tf.convert_to_tensor(np.random.dirichlet(np.ones(TLEN+1),size=1), dtype=tf.float32)
        else:
            return model(tf.convert_to_tensor(np.expand_dims(reqArray, 0), dtype=tf.int32)) #type: ignore
    return wrapper

def getTrainingData(memory: EpisodeMemory, sampleSize: int, overflow = True):
    eps = memory.draw(sampleSize, overflow)
    xT = tf.stack(list(map(lambda x: x.dataIn, eps)))
    yT = tf.stack(list(map(lambda x: x.expected, eps)))
    return xT, yT

class TrainingState:
    """
    Contains one generation of models and methods to step forward
    """
    generation: int = 0
    repetitions: int = 10 #Repetitions per generation
    updateRepetition: int = 3 #Update target nets every x repetitions
    rememberedOrderings: int = 100
    sampledOrderings: int = 5 #Exactly |repetitions| unique episodes available 
    rememberedPlacements: int = 1000
    sampledPlacements: int = 200
    rProb: float = 0.2

    modelCount: int = 2 #Models of each type per generation
    promoteModels: int = 1 #How many models of each type are passed to next generation (Should be less than modelCount)

    orderingEpochs: int = 10
    placementEpochs: int = 5
    
    orderingModels: List[keras.Model] 
    placementModels: List[keras.Model]

    def __init__(self, modelCount: int = 2, saveName: str = None, saveLocation: str = None) -> None:
        self.modelCount = modelCount
        self.orderingModels = []
        self.placementModels = []
        if saveName is None or saveLocation is None:
            for _ in range(self.modelCount):
                self.orderingModels.append(getOrderingNet())
                self.placementModels.append(getPlacementNet())
        else:
            self.load(saveName, saveLocation)

    def load(self, saveName: str, saveLocation: str):
        """Save location is not checked!!!"""
        savePath = path.join(saveLocation, saveName)
        print(f"Loading: {savePath}")
        with open(path.join(savePath, "params.json"), "r") as fIn:
            fDict = json.load(fIn)
            for field in fDict.keys():
                self.__dict__[field] = fDict[field]
        for i in range(self.modelCount):
            self.orderingModels.append(keras.models.load_model(path.join(savePath, f"o{i}.h5"))) #type: ignore
            self.placementModels.append(keras.models.load_model(path.join(savePath, f"p{i}.h5"))) #type: ignore

    def save(self, saveName: str, saveLocation: str):
        """Save location is not checked!!!"""
        savePath = path.join(saveLocation, saveName)
        print(f"Saving to: {savePath}")
        for (i, model) in enumerate(self.orderingModels):
            model.save(path.join(savePath, f"o{i}.h5"))
        for (i, model) in enumerate(self.placementModels):
            model.save(path.join(savePath, f"p{i}.h5"))
        with open(path.join(savePath, "params.json"), "w") as fOut:
            fDict = {}
            for field in self.__dict__:
                if type(self.__dict__[field]) in [str, int, float, bool]:
                    fDict[field] = self.__dict__[field]
            json.dump(fDict, fOut)

    def step(self, dense=False):
        """
        Steps to next generation \n
        dense will be passed to generateCase
        """
        orderingModels_f: List[keras.Model] = [keras.models.clone_model(model) for model in self.orderingModels]
        for model in orderingModels_f:
            model.compile(keras.optimizers.Adam(learning_rate=0.01), keras.losses.MeanSquaredError())
        placementModels_f: List[keras.Model] = [keras.models.clone_model(model) for model in self.placementModels]
        for model in placementModels_f:
            model.compile(keras.optimizers.Adam(), keras.losses.MeanSquaredError())

        orderingMemory = EpisodeMemory(self.rememberedOrderings)
        placementMemory = EpisodeMemory(self.rememberedPlacements)

        orderingScore = np.zeros((self.modelCount,))
        placementScore = np.zeros((self.modelCount,))

        for r in range(self.repetitions):
            print(f"Starting repetition: {r+1}")
            oOrder: List[int] = list(range(self.modelCount)) 
            random.shuffle(oOrder) 
            plOrder: List[int] = list(range(self.modelCount))
            random.shuffle(plOrder)
            oResults: List[TaskOutputGuided] = [None for _ in range(self.modelCount)] #type: ignore
            pResults: List[TaskOutputGuided] = [None for _ in range(self.modelCount)] #type: ignore
            tInput = generateCase(random.randint(1, MAX_N), dense=dense)
            print("Processing ...")
            for (oIdx, pIdx) in zip(oOrder, plOrder):
                oModel = self.orderingModels[oIdx]
                pModel = self.placementModels[pIdx]
                tOutput = process_guided(tInput, orderingSelector(oModel, self.rProb), placementSelector(pModel, self.rProb))
                oResults[oIdx] = tOutput
                pResults[pIdx] = tOutput
            print("Done")
            oScores = sorted(range(self.modelCount), key=lambda x: oResults[x].tArea) #Smallest to largest
            pScores = sorted(range(self.modelCount), key=lambda x: pResults[x].tArea)
            for i, j in enumerate(oScores): #Best element has largest index gets largest score
                orderingScore[j] += i
            for i, j in enumerate(pScores):
                placementScore[j] += i
            bestRes = max(oResults, key=lambda x: x.tArea)
            orderingMemory.push([bestRes.orderingEp]) #Only decisions leading to best result are remembered
            placementMemory.push(bestRes.placementEps)
            #Train frequent nets
            print("Training ordering models:")
            for model in orderingModels_f:
                xT, yT = getTrainingData(orderingMemory, self.sampledOrderings)
                assert xT.shape == (self.sampledOrderings, MAX_N, 6) and yT.shape == (self.sampledOrderings, MAX_N)
                model.fit(xT, yT, batch_size=16, epochs=self.orderingEpochs, verbose=0)
            print("Training placement models: ")
            for model in placementModels_f:
                xT, yT = getTrainingData(placementMemory, self.sampledPlacements)
                assert xT.shape == (self.sampledPlacements, MAX_N+1, 6) and yT.shape == (self.sampledPlacements, TLEN+1)
                model.fit(xT, yT, batch_size=16, epochs=self.placementEpochs, verbose=0)
            
            if (r+1) % self.updateRepetition == 0 or r == self.repetitions-1:
                print("Updating target")
                for (i, model) in enumerate(orderingModels_f):
                    self.orderingModels[i] = keras.models.clone_model(model)
                for (i, model) in enumerate(placementModels_f):
                    self.placementModels[i] = keras.models.clone_model(model)
                    
            print("Done with repetition")
        print("Promoting models ...")
        for i in range(self.modelCount): #Tag index
            self.orderingModels[i].position_tag = i
            self.placementModels[i].position_tag = i
        self.orderingModels.sort(key=lambda x: orderingScore[x.position_tag]) #type: ignore
        self.placementModels.sort(key=lambda x: placementScore[x.position_tag]) #type: ignore
        del self.orderingModels[self.promoteModels: self.modelCount]
        del self.placementModels[self.promoteModels: self.modelCount]
        idx = 0
        while (len(self.orderingModels) != self.modelCount):
            self.orderingModels.append(keras.models.clone_model(self.orderingModels[idx]))
            self.placementModels.append(keras.models.clone_model(self.placementModels[idx]))
            idx += 1
            idx = (idx if idx != self.promoteModels else 0) #Return to start
        for i in range(self.modelCount):
            self.orderingModels[i].compile(keras.optimizers.Adam(learning_rate=0.01), keras.losses.MeanSquaredError())
            self.placementModels[i].compile(keras.optimizers.Adam(), keras.losses.MeanSquaredError())
        print("Creating variation ...")
        for model in self.orderingModels:
            xT, yT = getTrainingData(orderingMemory, round(self.sampledOrderings/2)+1, overflow=False) # Less samples more epochs for more bias
            model.fit(xT, yT, batch_size=16, epochs=self.orderingEpochs*2, verbose=0)
        for model in self.placementModels:
            xT, yT = getTrainingData(placementMemory, round(self.sampledPlacements/2)+1, overflow=False)
            model.fit(xT, yT, batch_size=16, epochs=self.placementEpochs*2, verbose=0)
        self.generation += 1
        print("Step done!")

def samplePerformance(oModel: keras.Model, pModel: keras.Model):
    """Tests performance on examples"""
    for (i, tInput) in enumerate(getSamples()):
        print(f"Processing: {i+1}")
        tOutput = process_guided(tInput, orderingSelector(oModel, 0), placementSelector(pModel, 0))
        print(f"Area: {tOutput.tArea}")
        print(f"Took: {tOutput.runtime}")

def process_guided(tInput: TaskInput, reqOrder: Callable[[np.ndarray], tf.Tensor], placeOrder : Callable[[np.ndarray], tf.Tensor]) -> TaskOutputGuided:
    """
    Processes input with guide
    """
    #Utility
    def findInSet(nPlaced: PlacedRequest) -> bool: #O(len(placedRequests))
        """True if conflict exists"""
        for pReq in placedRequests:
            if doCollide(pReq, nPlaced):
                return True
        return False

    def findInArray(nPlaced: PlacedRequest) -> bool: #O(tLen*zLen)
        """
        True if conflict exists
        """
        return not (zArray[nPlaced.tStart-LOWER:nPlaced.tEnd-LOWER, nPlaced.zStart:nPlaced.zEnd] == None).all()

    def findColliders(nPlaced: PlacedRequest) -> bool: #
        if tInput.forceSet:
            return findInSet(nPlaced)
        elif tInput.forceArray:
            return findInArray(nPlaced)
        elif len(placedRequests) < nPlaced.area:
            return findInSet(nPlaced)
        else:
            return findInArray(nPlaced)
    
    def applyChange(change: ProposedChange): #O(len(colliders)*col.tLen*col.zLen)
        """
        Applies change
        """
        assert reqArray[change.nPlaced.localID][4] == -1
        assert len(change.colliders) == 0
        #Add new placement
        nPlaced = change.nPlaced
        if not tInput.forceSet: #O(tLen*zLen)
            for col in range(nPlaced.tStart-LOWER, nPlaced.tEnd-LOWER):
                for row in range(nPlaced.zStart, nPlaced.zEnd):
                    zArray[col, row] = nPlaced
        placedRequests.add(nPlaced)
        isPlaced[nPlaced.localID] = True

        reqArray[nPlaced.localID][4] = nPlaced.zStart
        reqArray[nPlaced.localID][5] = nPlaced.zEnd

    def reqOrdered(reqArray) -> Tuple[List[ZoneRequest], np.ndarray]:
        """Returns ordering for requests"""
        def sortByRating(a: ZoneRequest):
            return rating[a.localID]
        rating = reqOrder(reqArray)[0].numpy() #type: ignore
        assert rating.shape == (MAX_N,)
        rating[tInput.N:MAX_N] = 0 #Zeroing of out of bounds
        reqs = sorted(requests, key=sortByRating, reverse=True) #1->0
        return (reqs, rating) #Returns rating for comparison
    
    def placeOrdered(reqArray, req: ZoneRequest) -> Tuple[List[int], np.ndarray]:
        """Returns ordering for placements"""
        def sortByRating(a: int):
            return rating[a]
        rating = placeOrder(reqArray)[0].numpy() #type: ignore
        assert rating.shape == (TLEN+1,)
        rating[TLEN-req.zLen:TLEN] = 0
        return (sorted(range(TLEN+1), key=sortByRating), rating)

    def reqsAsArray(requests: List[ZoneRequest]) -> np.ndarray:
        """Returns requests as net input array"""
        reqArray: np.ndarray = np.array([[req.localID, req.tStart, req.tEnd, req.zLen, -1, -1] for req in requests], dtype=np.int)
        if tInput.N != MAX_N:
            reqArray: np.ndarray = np.concatenate((reqArray, np.array([[-1, -1, -1, -1, -1, -1] for _ in range(MAX_N-tInput.N)], dtype=np.int))) #type: ignore
        assert reqArray.shape == (MAX_N, 6)
        return reqArray
    
    def concCurrent(reqArray: np.ndarray, req: ZoneRequest):
        """Concats current req to end"""
        out: np.ndarray = np.concatenate([reqArray, [[req.localID, req.tStart, req.tEnd, req.zLen, -1, -1]]]) #type: ignore
        assert out.shape == (MAX_N+1, 6)
        return out

    sTime = timeit.default_timer()
    
    requests = tInput.requests.copy()
    isPlaced: List[bool] = [False for _ in requests]

    for i in range(len(requests)):
        requests[i].localID = i

    placedRequests: Set[PlacedRequest] = set()

    if tInput.forceArray or not tInput.forceSet:
        zArray = np.full(shape=(UPPER-LOWER, TLEN), dtype=PlacedRequest, fill_value=None)

    reqArray = reqsAsArray(requests)
    requests, res1 = reqOrdered(reqArray)
    orderingEpisode = Episode(reqArray, res1)

    for i in range(len(requests)): #Reassign local ids
        requests[i].localID = i
    reqArray = reqsAsArray(requests) #Update local ids and ordering

    placementEpisodes: List[Episode] = []
    for req in requests:
        zStarts, res2 = placeOrdered(concCurrent(reqArray, req), req)
        bChange: Union[ProposedChange, None] = None
        for zStart in zStarts:
            if zStart+req.zLen > TLEN: #Reached end
                break
            nPlaced = PlacedRequest(req, zStart)
            doesCollide = findColliders(nPlaced)
            if doesCollide:
                continue
            if bChange is None:
                bChange = ProposedChange([], nPlaced, 0)
                break

        placementEpisodes.append(Episode(concCurrent(reqArray, req), res2))
        if bChange is not None:
            applyChange(bChange)
    assert checkNoCollisions(placedRequests)
    tOutput = TaskOutputGuided(placedRequests, orderingEpisode, placementEpisodes)
    tOutput.runtime = timeit.default_timer()-sTime
    return tOutput

def doTraining(state: TrainingState, generations: int, decay: float):
    for s in range(generations):
        print(f"Generation: {state.generation}")
        state.step((s%2 == 1))
        state.rProb *= decay

def main():
    state = TrainingState()
    print("Training ...")
    doTraining(state, 20, 0.95)
    print("Performance after 20 generations:")
    samplePerformance(state.orderingModels[0], state.placementModels[0])

if __name__ == "__main__":
    main()

