import turtle as trt 
import random as rnd
from typing import Tuple

padding = (0.075, 0.075)

class Visualizer:
    def __init__(self, tStart: int=8, tEnd: int=18, zLen: int=1000) -> None:

        screen = trt.Screen()
        width, height = zLen, tEnd-tStart
        screen.setworldcoordinates(0-width*padding[0], tStart-height*padding[1], width+width*padding[0], tEnd+height*padding[1])

        self.m_turtle = trt.Turtle(visible=False)
        trt.colormode(255)
        self.m_turtle.speed(0)
        self.m_turtle.up()
        init_done = True

        self.drawRect(0, tStart, zLen, tEnd-tStart, fill=(255, 255, 255))

    def drawRect(self, x: int, y: int, lx: int, ly: int, fill: Tuple[int, int, int]=(-1, -1, -1)):
        if (fill == (-1, -1, -1)):
            fill = (rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255))
        self.m_turtle.setpos(x, y)
        self.m_turtle.setheading(0)
        self.m_turtle.color((0, 0, 0), fill)
        self.m_turtle.begin_fill()
        self.m_turtle.down()
        
        self.m_turtle.goto(x+lx, y)
        self.m_turtle.goto(x+lx, y+ly)
        self.m_turtle.goto(x, y+ly)
        self.m_turtle.goto(x, y)

        self.m_turtle.up()
        self.m_turtle.end_fill()

    def drawPlaced(self, tStart: int, tEnd: int, zStart: int, zEnd: int):
        self.drawRect(zStart, tStart, zEnd-zStart, tEnd-tStart)
        return 0
    
    def block(self):
        trt.mainloop()



#region Module tests
testActive = False
if testActive:
    visu = Visualizer()
    visu.drawPlaced(8, 9, 100, 600)

    visu.block()
#endregion