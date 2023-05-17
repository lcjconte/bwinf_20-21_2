import random as rnd
from typing import Dict, Tuple

import matplotlib.patches as patches
import matplotlib.pyplot as plt


class Visualizer:
    """Visualizer using matplotlib"""

    def __init__(self, tStart: int=8, tEnd: int=18, zLen: int=1000, interact: bool = False) -> None:
        self.interactive = interact
        if self.interactive:
            plt.ion()
        self.rects: Dict[int, patches.Patch] = {}

        self.fig, self.ax = plt.subplots()
        self.ax.plot()                  #type: ignore
        
        self.drawRect(0, tStart, zLen, tEnd-tStart, fill=(255, 255, 255)) #Draw boundary

        self.fig.show()

    def __del__(self):
        if self.interactive:
            plt.ioff()
        
    def block(self):
        plt.show(block=True)

    def drawRect(self, x: int, y: int, lx: int, ly: int, fill: Tuple[int, int, int]=(-1, -1, -1)) -> int:
        if (fill == (-1, -1, -1)):
            fill = (rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255))
        fill = tuple([i/255 for i in fill]) #Scale colour 
        nRect = patches.Rectangle((x, y), lx,ly,edgecolor = 'black',facecolor = fill,fill=True) #type: ignore
        uuid = rnd.getrandbits(32)
        self.rects[uuid] = nRect
        self.ax.add_patch(nRect) 
        if self.interactive:
            self.refresh()
        return uuid

    def drawPlaced(self, tStart: int, tEnd: int, zStart: int, zEnd: int):
        return self.drawRect(zStart, tStart, zEnd-zStart, tEnd-tStart)

    def removeElement(self, uuid: int):
        self.rects[uuid].remove()
        self.rects.pop(uuid)
        if self.interactive:
            self.refresh()

    def refresh(self):
        self.ax.relim() 
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

#region Module tests

testActive = False
if testActive:
    visu = Visualizer()
    uj = visu.drawPlaced(8, 9, 100, 600)
    
    import time
    time.sleep(2)
    visu.removeElement(uj)
    visu.block()
#endregion
