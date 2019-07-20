"""What have I got myself into..

Let's break down initially.

1. we want each particle to have a mass value + velocity vector

2. we want to calculate the particle positions between arbitrary time 
   intervals.

3. we want to cull particles that fly off the screen. (sorry in advance, speedy particles)

3.5 maybe later we will need to add a cutoff min velocity for "clumped" particles (for efficiency?)

4. lets give it a go

work log:
    HOUR 1: '_______'
    HOUR 3: -.-
"""
import logging
import numpy as np
import math

GRAVITY = .01
FORCES = []

def calculate_force(ax, ay, am, bx, by, bm):
    """Get xy components of force between masses.
    
    Args:
        ax (float): x pos of a
        ay (float): y pos of a
        am (float): mass of a
        bx (float): x pos of b
        by (float): y pos of b
        bm (float): mass of b
    
    Returns:
        tuple(float*2): (x component, y component)
    """
    dx = (bx - ax)
    dy = (by - ay)
    # Distance between masses
    d = math.sqrt(dx**2 + dy**2)

    # Catch collisions
    if abs(d < 0.001):
        print("COLLISION")
        from time import sleep
        sleep(1)
        return None

    # Force Magnitude
    f = GRAVITY * am * bm / (d**2)

    # X & Y components
    theta = math.atan2(dy, dx)
    fx = math.cos(theta) * f
    fy = math.sin(theta) * f
    #print(fx, fy)
    return fx, fy


def resultant_velocity(vx, vy, ax, ay, m, time):
    """Get resultant velocity, given current velocity + acceleration."""
    return (vx + ((ax / m) * time), vy + ((ay / m) * time))


class _SimulationInstance():
    def __init__(self, simulation, dt, max_frames=0, cull_outsiders=False):
        self.cull_outsiders = cull_outsiders
        self.particles = simulation.particles
        self._sim = simulation
        self.max_frames = max_frames
        self.dt = dt
    
    def __iter__(self):
        self.time = 0
        self.frame = 0
        return self

    def __next__(self):
        global FORCES
        if self.max_frames <= self.frame:
            print("FORCES:\n{}".format("\n".join(str(i) + " " + str(f) for i,f in enumerate(FORCES))))
            raise StopIteration("Exceeded frame max: {0}".format(
                    self.max_frames
            ))
        particles = self.particles
        new_particles = []

        FORCES += [[]]
        for i, particle in enumerate(particles):
            # import pdb; pdb.set_trace()
            x, y, vx, vy, m = particle
            # arr[...,1]
            if self.cull_outsiders and max(abs(x), abs(y)) > self._sim.cutoff_square:
                continue
            # new_particles.append((
            #     x + vx * self.dt,
            #     y + vy * self.dt,
            #     vx,
            #     vy,
            #     m
            # ))
            if self.frame==3:
                #import pdb; pdb.set_trace()
                pass
            fx, fy = 0, 0
            for j, pcl in enumerate(particles):
                if j == i:
                    continue
                if list(pcl) == list(particle):
                    import pdb; pdb.set_trace()
                pcl_f = calculate_force(x, y, m, pcl[0], pcl[1], pcl[4])
                if pcl_f:
                    fx += pcl_f[0]
                    fy += pcl_f[1]
            nvx, nvy = resultant_velocity(vx, vy, fx, fy, m, self.dt)
            FORCES[self.frame].append((nvx, nvy))
            new_particle = (
                x + nvx * self.dt,
                y + nvy * self.dt,
                vx,
                vy,
                m
            )
            #print(new_particle)
            new_particles.append(new_particle)
        from time import sleep
        sleep(.1)
        self.particles = np.asarray(new_particles, dtype="float32")
        self.frame += 1
        return self.particles


class ParticleSimulation2d():
    PTC_ATTRS = tuple("x y vx vy m".split())
    def __init__(self, time_interval=.1, cutoff_square=2):
        self.callbacks = []
        self.time_interval = time_interval
        self.cutoff_square = cutoff_square
        self.particles = np.zeros((0,5), dtype="float32")
        # Todo: could store immovables as int in future.
        self.immovables = []

    def add_particles(self, particles):
        """Add particles to Simulation.
        
        Args:
            particles (list[tuple OR np.array]): Particles in the format
                (X pos, Y pos, X velocity, Y velocity, Mass).
        """
        self.particles = np.append(self.particles, particles, 0)

    def start(self, max_frames=0):
        from copy import deepcopy
        cloned_self = deepcopy(self)
        instance = _SimulationInstance(
            self, dt=self.time_interval, max_frames=max_frames)
        return instance


# class ParticleSimulation3d(object):
#     def __init__(self, time_interval=.1), cutoff_size=(2,2,2):
#         pass

#     def start(self):
#         pass

#     def place_sun(self):
#         pass

def test():
    from random import random as r
    sim = ParticleSimulation2d()
    sim.add_particles(
        [
            (r(), r(), r()/10, r()/10, 1)
            for _ in range(10)
        ]
    )
    for i in sim.start(max_frames=5):
        print(i)





if __name__ == "__main__":
    test()