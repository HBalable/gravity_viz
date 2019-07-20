"""The fun, colourful bit :D

1. we want each particle to have a colour proportional a value it has

2. we want to calculate the particle positions between arbitrary time 
   intervals.

3. lets give it a go
"""
# standard
import sys
from collections import namedtuple, OrderedDict
from bisect import bisect_left
from operator import mul
from subprocess import call
# external
import numpy as np
# local
from colour_magic import rgb_hl
from gravity_sim import ParticleSimulation2d
from terminalsize import get_terminal_size

class DecayScreen():
    def __init__(self, screen_size, space="rgb"):
        self.screen_size = screen_size
        self.max_pixel = mul(*screen_size)
        self.pixels = []
        self.pixel_map = {}
        self.colours = []
        self.space = space

    def __setitem__(self, xy, vals):
        pixel = self.xy_to_ordinal(*xy)
        # if pixel in self.pixel_map:
        #     import pdb; pdb.set_trace()
        target_index = self.pixel_map.get(pixel)
        if target_index is not None:
            target_index = self.pixels.index(pixel)
            self.pixels[target_index] = pixel
            self.colours[target_index] = list(vals)
        else:
            target_index = bisect_left(self.pixels, pixel)
            self.pixel_map[pixel] = target_index
            self.pixels.insert(target_index, pixel)
            self.colours.insert(target_index, list(vals))

    def __getitem__(self, xy):
        pixel = self.xy_to_ordinal(*xy)
        self.colours[self.pixel_map(pixel)]

    def decay(self, channels, amount):
        for colour in self.colours:
            for channel in channels:
                channel_value = colour[channel] - amount
                colour[channel] = channel_value if channel_value >= 0 else 0

    def cleanup(self):
        to_discard = []
        for i, colour in enumerate(self.colours):
            if not sum(colour[:3]):
                to_discard.append(i)
        for index in reversed(to_discard):
            if len(self.pixels)-1 < index:
                import pdb; pdb.set_trace()
            pixel_val = self.pixels[index]
            del self.colours[index]
            del self.pixels[index]
            del self.pixel_map[pixel_val]        

    def draw(self):
        #call(["Clear-Host"])
        current_pixel = 0
        out_str = ""
        for i, pixel in enumerate(self.pixels): 
            out_str += (
                " " * (pixel - current_pixel) +
                (self.colours[i][3] if self.colours[i][0] == 255 else ".")
            )
            current_pixel = pixel + 1
        # import pdb; pdb.set_trace()
        out_str += " " * (self.max_pixel - current_pixel)
        sys.stdout.write(out_str)
        # print(self.pixels)
        # print(len(out_str))
        # print(list(zip(self.pixels, self.colours)))
        sys.stdout.write("\n_____________________\n")

    def xy_to_ordinal(self, x,y):
        # ordi = x + (y*self.screen_size[0])
        # print("[[{},{} to {}]]".format(x,y,ordi))
        return x + (y*self.screen_size[0])



class SimulationVisualiser():
    def __init__(
            self, simulation, screen_size=None, offset=(0,0),
            squeeze_factor=2.5, scale_factor=None, trails=3):
        if screen_size:
            self.screen_size = screen_size
        else:
            self.screen_size = list(get_terminal_size())
        

        # print(self.screen_size)
        # exit()
        self.offset = offset
        self.simulation = simulation
        self.squeeze_factor = squeeze_factor
        self.scale_factor = min(self.screen_size)
        self.screen = DecayScreen(self.screen_size)
    
    def start(self, frame_count):
        for frame, particles in enumerate(self.simulation.start(max_frames=frame_count)):
            global PIXELS
            PIXELS += [[]]
            visible_particles = 0
            for i, particle in enumerate(particles):
                x, y = particle[:2]
                
                # import pdb
                # pdb.set_trace()
                #print(x, y)
                screen_x = int(round((
                    (x + self.offset[0]) * self.scale_factor) * self.squeeze_factor
                ))
                screen_y = int(round((
                    (y + self.offset[1]) * self.scale_factor)
                ))
                if 0<=screen_x<self.screen_size[0] and 0<=screen_y<self.screen_size[1]:
                    PIXELS[frame].append((x,y, screen_x, screen_y))
                    visible_particles += 1
                    self.screen[screen_x, screen_y] = 255, 255, 255, str(i)
                else:
                    PIXELS[frame].append(("FAIL",x,y, screen_x, screen_y))
                self.screen[90,50] = 255, 255, 255, str(frame)
            
            if visible_particles:
                self.screen.draw()
            self.screen.decay((0,1,2),40)
            self.screen.cleanup()

global PIXELS
PIXELS = []

def test():
    from random import random as r
    sim = ParticleSimulation2d(time_interval=.04)
    sim.add_particles(
        [
            (.3,.3,0,.6,5),
            (.5,.5,0,0,50)
        ] 
        # +[
        #     (r(), r(), r()/3, r()/3, 1)
        #     for _ in range(3)
        # ]
    )
    viz = SimulationVisualiser(sim)
    viz.start(40)
    print("Visable Pixels:")
    for i, step in enumerate(PIXELS): print(i, step)

    # screen_size = list(get_terminal_size())
    # #screen_size[1] -= 40
    # print(screen_size)
    # screen = DecayScreen(screen_size)
    # r = [(0,0), (5,0),(162,50), (1,5)]
    # for i in r:
    #     screen[i] = 255, 255, 255, "O"
    # screen.draw()





if __name__ == "__main__":
    test()