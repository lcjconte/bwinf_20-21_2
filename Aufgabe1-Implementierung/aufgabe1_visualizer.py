from aufgabe1_common import PlacedRequest
try:
    import matplotlib.pyplot #Checks if matplotlib is available
except:
    import aufgabe1_visualizer_t as visu_t
    mode = "turtle"
else:
    import aufgabe1_visualizer_m as visu_m
    mode = "plt"

class Visualizer:
    def __init__(self, tStart: int = 8, tEnd: int = 18, zLen: int = 1000, interact: bool = False):
        """Initializes window"""
        if mode == "turtle":
            self.visu = visu_t.Visualizer(tStart, tEnd, zLen)
        else:
            self.visu = visu_m.Visualizer(tStart, tEnd, zLen, interact)

    def block(self):
        """Block execution until window is closed"""
        return self.visu.block()

    def drawRect(self, x: int, y: int, lx: int, ly: int):
        """Draws rectangle with lower left corner at x y"""
        return self.visu.drawRect(x, y, lx, ly)

    def drawPlaced(self, pReq: PlacedRequest):
        """Draws placed registration"""
        return self.visu.drawPlaced(pReq.tStart, pReq.tEnd, pReq.zStart, pReq.zEnd)
    
    def removeElement(self, uuid: int):
        if mode=="turtle":
            raise Exception("removeElement requires matplotlib")
        else:
            return self.visu.removeElement(uuid) #type: ignore



