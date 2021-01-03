# Import required modules
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from random import random, randint
from collections import Counter, namedtuple, deque
from math import hypot
from abc import ABC, abstractmethod
from vector import Vector
       
Entities = namedtuple("Entities", ["population", "food"])

def trial(chance):
    """ Returns the boolean outcome of a trial given it's chance of success."""
    return random() <= chance

def distance(source, target):
    """ Returns the distance between two Entity objects."""
    dx = source.x - target.x
    dy = source.y - target.y
    return hypot(dx, dy)

def collision(source, target):
    """ Detect whether two round objects are touching."""
    if distance(source, target) <= source.radius + target.radius:
        return True
    return False

def resolve_organism_collision(source, target):
    """ Simple collision resolution wherein source and target entities
        trade vector.
    """
    source.motion, target.motion = target.motion, source.motion

def resolve_border_collision(source, extent):
    """ ."""
    if (source.x >= (extent.width - source.radius) or 
        source.x <= (0 + source.radius)
        ):
        source.motion.vx = -source.motion.vx
    if (source.y >= (extent.height - source.radius) or 
        source.y <= (0 + source.radius)
        ):
        source.motion.vy = -source.motion.vy

def resolve_overlap(source, target):
    """ Resolve the overlap between two entities such that the target entity
        and the source entity positions are adjusted to the position along
        their respective vectors at which the entities make first contact.
    """
    v_st = Vector(source.x - target.x, source.y - target.y)
    touch_distance = source.radius + target.radius
    overlap_distance = touch_distance - v_st.mag

    source += v_st.unit * round((source.radius / touch_distance) * overlap_distance, 5)
    target += -v_st.unit * round((target.radius / touch_distance) * overlap_distance, 5)


class Extent():
    """ The rectangular extent of a habitat"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def contains(self, entity):
        """ Check whether entity is contained completely within bounds of extent"""
        return (entity.x <= (self.width - entity.radius) and
                entity.x >= (0 + entity.radius) and
                entity.y <= (self.height - entity.radius) and
                entity.y >= (0 + entity.radius))

class Point():
    """ ."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iadd__(self, vector):
        """  Update the location of self by Vector."""
        self.x = self.x + vector.vx
        self.y = self.y + vector.vy
        return self

class Entity(ABC, Point):
    """ Abstract base class for entities. An entity is any interactable object in 
        the Environment that has location (x, y) and radius.

        Parameters:
            x (int or float):                   x location of Entity.
            y (int or float):                   y location of Entity.
            radius (float):                     the radius of the Entity.
            energy (float):                     the amount of energy stored by Entity.
        Attributes:
            patch (matplotlib.patches.Circle):  patch for visualization on plot.
            alive (bool):                       alive if True, dead if False.
    """

    def __init__(self, x, y, radius, energy=1):
        super().__init__(x, y)
        self.radius = radius
        self.energy = energy
        self.patch = plt.Circle((x, y), radius) # matplotlib patch
        self.alive = True
   
    @staticmethod
    @abstractmethod
    def spawn(environment):
        """ Every child of Entity must have a static spawn method
            that accepts a required extent parameter."""
        pass


class Organism(Entity):
    """ The Organism object represents a live entity.

        Parameters:
            x (int or float):                   x location of Organism.
            y (int or float):                   y location of Organism.
            radius (float):                     the radius of the Organism.
            energy (float):                     the amount of energy stored by Organism.
            motion (Vector):                    the speed and direction of Organism.
        Attributes:
            patch (matplotlib.patches.Circle):  patch for visualization on plot.
            alive (bool):                       alive if True, dead if False.
            period (int):                       the current age of Organism.
            reproduce_thresh (float):           can reproduce if energy greater.
            reproduce_chance (float):           chance of reproduction.
            reproduce (bool):                   duplicate if True else don't.
            consumption (float):                energy consumed per period.

    """
    
    def __init__(self, x, y, radius =0.25, motion=Vector(0, 0)):
        super().__init__(x, y, radius)
        self.motion = motion
        self.period = 0
        self.reproduce_thresh = 2
        self.reproduce_chance = 0.25
        self.reproduce = False
        self.consumption = 0.05


    def __str__(self):
        return f"Organism <age: {self.period!r}, location({self.x!r}, {self.y!r})>"
    
    def __repr__(self):
        return f"{self.period!r}"
    
    def __call__(self):
        """ advance the entity by one period."""
        self.period += 1
        self += self.motion
        self.energy -= self.consumption
        if self.energy <= 0:
            self.alive = False
        elif self.energy > self.reproduce_thresh:
            if trial(self.reproduce_chance):
                self.reproduce = True
        self.patch.center = (self.x, self.y)
        return self

    def eat(self, food):
        food.alive = False
        self.energy += food.energy

    def duplicate(self, environment):
        while True:  # Try creating child, repeat if collision with other
            # Create a child organism adjacent to the parent organism
            loc = Point(self.x, self.y)
            touch_distance = self.radius * 2
            vector = Vector.generate(1).unit * round(touch_distance, 5)
            loc += vector
            child =  Organism(
                x=loc.x,
                y=loc.y,
                motion=Vector.generate(0.15))
            # Must spawn inside of habitat and must not overlap with organisms
            if environment.extent.contains(child):
                if not any(collision(child, target) for group in environment.ents for target in group):
                    environment.ents.population.append(child)
                    environment._ax.add_patch(child.patch)
                    break
        self.reproduce = False
        self.energy -= 1
        return child

    @staticmethod
    def spawn(environment):
        while True:  # Try creating child, repeat if collision with other
            organism = Organism(
                x=random() * environment.extent.width,
                y=random() * environment.extent.height,
                motion=Vector.generate(0.15)
            )
            # Must spawn inside of habitat and must not overlap with organisms
            if environment.extent.contains(organism):
                if not any(collision(organism, target) for group in environment.ents for target in group):
                    return organism


class Food(Entity):
    """ The Food object provides energy for a live
        entity. This food object is stationary.

        Parameters:
            x (int or float):                   x location of Food.
            y (int or float):                   y location of Food.
            energy (float):                     The energy value of Food.
        Attributes:
            patch (matplotlib.patches.Circle):  patch for visualization on plot.
            alive (bool):                       alive if True, dead if False.
    """

    def __init__(self, x, y, radius=0.1):
        super().__init__(x, y, radius)
        self.patch.set_color("green")
    
    def __repr__(self):
        return f"Food <energy: {self.energy!r}, location({self.x!r}, {self.y!r})>"

    @staticmethod
    def spawn(environment):
        while True:  # Try creating child, repeat if collision with other
            food = Food(
                x=random() * environment.extent.width,
                y=random() * environment.extent.height
            )
            # Must spawn inside of habitat and must not overlap with organisms
            if environment.extent.contains(food):
                if not any(collision(food, target) for group in environment.ents for target in group):
                    return food


class Environment():
    """ The environment tracks the population and parameters of the simulation.

        Parameters:
            starting_pop (int):                 Starting population
            extent (iterable [width, height]):  Extent of habitat
        
        TODO: Explain remaining attributes once fully established.
    """

    def __init__(self, starting_pop, starting_food, food_rate, extent):
        # Simulation arguments
        self.starting_pop = starting_pop
        self.starting_food = starting_food
        self.food_rate = food_rate
        self.extent = Extent(*extent)
        self.period = 0
        # Simulation data
        self.ents = Entities(population=[], food=[]) # entities existing at start of simulation 
        for _ in range(0, self.starting_pop):
            self.ents.population.append(Organism.spawn(self))
        for _ in range(0, self.starting_food):
            self.ents.food.append(Food.spawn(self))
        self.history = [starting_pop]
        self.mortuary = Counter()
        # Plot attributes
        self._fig, self._ax = plt.subplots(1, 1)
        self._ax.set_xlim(0, self.extent.width)     #Set habitat plane x size
        self._ax.set_ylim(0, self.extent.height)    #Set habitat plane y size
        self._ax.set_aspect('equal')                #Make sure x and y scales equal

    def __repr__(self):
        return f"Environment <population: {self.ents.population!r}, extent: {self.extent!r}>"

    def __call__(self):
        """ Advance the simulation by one frame."""
        # Simulate period
        
        self.period += 1
        
        # Update organism motion
        collision_queue = deque(self.ents.population)
        for organism in self.ents.population:
            collision_queue.remove(organism)
            # Organism collides with extent boundary
            resolve_border_collision(organism, self.extent)
            # organism collides with other organsim
            for target in collision_queue:
                if collision(organism, target):
                    resolve_organism_collision(organism, target)
                    resolve_overlap(organism, target)
            # organism collides with food
            for target in self.ents.food:
                if collision(organism, target):
                    organism.eat(target)
            # Update organism
            organism()
        
        # Update deaths and births
        mortuary, offspring = [], []
        for organism in self.ents.population:
            if not organism.alive:
                mortuary.append(organism.period)
                self._ax.patches.remove(organism.patch)
                self.ents.population.remove(organism)
        for organism in self.ents.population:
            if organism.reproduce:
                child = organism.duplicate(self)
                offspring.append(child)
                

        # Update food eaten
        eaten = [food for food in self.ents.food if not food.alive]
        for food in eaten:
            self._ax.patches.remove(food.patch)
            self.ents.food.remove(food)

        # update data
        self.mortuary.update(mortuary)
        self.ents.population + offspring

    def run(self, n_period):
        ''' Run the simulation for n periods.'''
        return animation.FuncAnimation(self._fig,
                                       self._fig_animate,
                                       init_func=self._fig_init,
                                       frames=n_period)

    def _fig_init(self):
        for group in self.ents:
            for ent in group:
                self._ax.add_patch(ent.patch)
        
    def _fig_animate(self, frame):
        self() #Advance simulation by one frame
