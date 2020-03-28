"""Source:     https://github.com/csamuelsm/covid19-simulations/blob/master/corona.pde   """


import random
from math import sqrt, cos, sin, log10, atan2, degrees, radians
import turtle as t
import pandas as pd
import matplotlib.pyplot as plt


POPULATION = 100
PARTICLE_RADIUS = 20
HEIGTH = 400
WIDTH = 900
TRANSMISSION_PROBABILITY = 0.4
HOSPITAL_CAPACITY = POPULATION*0.2
INCUBATION_PERIOD = 500
PROTECTION = 2  # 0: nobody, 1: doctors, 2: doctors and patients, 3: doctors and infected, 4: everybody
PROTECTION_EFFICIENCY = 0.7


def dist(x1, y1, x2=0, y2=0):
    return sqrt((x1-x2) ** 2 + (y1-y2) ** 2)


class ParticleSystem(object):
    def __init__(self, pop_size):
        self.lst_particles = [Particle(0, 20)]
        for i in range(1, pop_size):
            if i >= pop_size - HOSPITAL_CAPACITY*2:
                self.lst_particles.append(Particle(job="doc"))
            else:
                self.lst_particles.append(Particle())

        self.hospital = Hospital(capacity=HOSPITAL_CAPACITY, radius=200)

        self.stats = {"healthy": [], "infected": [], "cured": [], "dead": []}
        t.tracer(0, 0)
        t.ht()
        self.run()
        t.done()

    def run(self):
        while sum([part.is_contagious() for part in self.lst_particles]) > 0:
            healthy, infected, cured, dead = 0, 0, 0, 0
            self.hospital.patients = sum([part.hospital for part in self.lst_particles])

            for i in range(len(self.lst_particles)):
                part1 = self.lst_particles[i]
                if part1.alive:
                    part1.update()
                for j in range(i+1, len(self.lst_particles)):
                    part2 = self.lst_particles[j]
                    if part1.alive and part2. alive and part1.check_collisions(part2):
                        ParticleSystem.collision(part1, part2)
                        if (part1.is_contagious() or part2.is_contagious()) \
                                and random.random() <= TRANSMISSION_PROBABILITY \
                                * (1-PROTECTION_EFFICIENCY*max(part1.protection, part2.protection)):
                            part1.time_since_infected = max(0, part1.time_since_infected)
                            part2.time_since_infected = max(0, part2.time_since_infected)

                # Hospital and stuff
                if part1.is_sick():
                    if dist(*part1.pos) > self.hospital.radius:
                        if part1.hospital or self.hospital.capacity > self.hospital.patients:
                            part1.dir = (degrees(atan2(part1.pos[1], part1.pos[0]))+180) % 360
                            self.hospital.patients += 1
                    elif not part1.hospital and self.hospital.capacity > self.hospital.patients:
                        part1.hospital = True
                if not part1.is_sick() and part1.job != "doc" and dist(*part1.pos) < self.hospital.radius:
                    part1.dir = degrees(atan2(part1.pos[1], part1.pos[0])) % 360

                # protection setup
                part1.set_protection()

                if part1.cured:
                    cured += 1
                elif not part1.alive:
                    dead += 1
                elif part1.time_since_infected >= 0:
                    infected += 1
                healthy = len(self.lst_particles) - (infected+cured+dead)

                self.stats["healthy"].append(healthy)
                self.stats["infected"].append(infected)
                self.stats["cured"].append(cured)
                self.stats["dead"].append(dead)

            self.draw()

        self.stats = pd.DataFrame(self.stats)
        print(self.stats)
        self.stats.plot.area(stacked=False)
        plt.show()

    def draw(self):
        t.clear()

        w, h = WIDTH+PARTICLE_RADIUS, HEIGTH+PARTICLE_RADIUS
        t.up()
        t.goto(w, h)
        t.down()
        t.color("black", "white")
        t.begin_fill()
        for x, y in ((-1, 1), (-1, -1), (1, -1), (1, 1)):
            t.goto(x*w, y*h)
        t.end_fill()

        self.hospital.draw()

        for part in self.lst_particles:
            t.up()
            t.goto(part.pos)
            t.down()
            if part.hospital:
                t.color("dark orange")
                t.dot(PARTICLE_RADIUS+7)
            if part.protection == 1:
                t.color("green")
                t.dot(PARTICLE_RADIUS+4)
            t.color(part.color)
            t.dot(PARTICLE_RADIUS)
        t.update()

    @staticmethod
    def collision(part1, part2):
        x1, y1 = part1.pos
        x2, y2 = part2.pos
        part1.dir = degrees(atan2(y1 - y2, x1 - x2)) % 360
        part2.dir = (part1.dir + 180) % 360


class Hospital(object):
    def __init__(self, capacity, radius):
        self.capacity = capacity
        self.patients = 0
        self.radius = radius
        self.working_force = capacity*2
        self.pos = 0, 0

    def draw(self):
        t.up()
        t.goto(0, -self.radius)
        t.seth(0)
        t.color("red")
        t.down()
        t.circle(self.radius)


class Particle(object):
    def __init__(self, infected=-1, age=-1, job=""):
        # TODO some things are missing here
        self.age = age if age >= 0 else random.randint(0, 100)
        self.job = job
        self.alive = True
        self.hospital = False
        self.cured = False
        self.time_since_infected = infected
        self.pos = (random.randint(-WIDTH, WIDTH), random.randint(-HEIGTH, HEIGTH))
        self.dir = random.randint(0, 360)
        self.velocity = random.random()*3+2
        self.color = ""
        self.set_color()
        self.protection = 0
        self.set_protection()

    def set_protection(self):
        if PROTECTION == 4 \
                or (PROTECTION == 3 and (self.job == "doc" or self.is_sick())) \
                or (PROTECTION == 2 and (self.job == "doc" or self.hospital)) \
                or (PROTECTION == 1 and self.job == "doc"):
            self.protection = 1
        else:
            self.protection = 0

    def death(self):
        # Random probability, if under this probability, subject dies
        random_probability = random.random()*100
        # Compute the probabilities of death for each condition
        if 10 <= self.age <= 19:
            if random_probability <= 0.02*3:
                self.alive = False
        elif 20 <= self.age <= 29:
            if random_probability <= 0.09*3:
                self.alive = False
        elif 30 <= self.age <= 39:
            if random_probability <= 0.18*3:
                self.alive = False
        elif 40 <= self.age <= 49:
            if random_probability <= 0.4*3:
                self.alive = False
        elif 50 <= self.age <= 59:
            if random_probability <= 1.3*3:
                self.alive = False
        elif 60 <= self.age <= 69:
            if random_probability <= 4.6*3:
                self.alive = False
        elif 70 <= self.age <= 79:
            if random_probability <= 9.8*3:
                self.alive = False
        elif self.age >= 80:
            if random_probability <= 18*3:
                self.alive = False

        if not self.alive:
            self.velocity = 0

    def set_color(self):
        if not self.alive:
            self.color = "light gray"
        elif self.cured:
            self.color = "green"
        elif self.time_since_infected >= 0:
            self.color = "red"
        else:
            self.color = "black"

    def update(self):
        self.check_boundary_collision()
        x, y = self.pos
        x += cos(radians(self.dir))*self.velocity
        y += sin(radians(self.dir))*self.velocity
        self.pos = x, y
        if self.is_contagious():
            self.time_since_infected += 1

            lower_limit = 3
            upper_limit = 10
            if self.hospital and \
                    log10(self.time_since_infected) > lower_limit+random.random()*(upper_limit-lower_limit)-0.1:
                self.cured = True
                self.hospital = False
            if not self.cured and \
                    log10(self.time_since_infected) > lower_limit+random.random()*(upper_limit-lower_limit):
                self.death()
                if self.alive:
                    self.cured = True
                self.hospital = False

        self.set_color()

    def is_contagious(self):
        return self.alive and self.time_since_infected >= 0 and not self.cured

    def is_sick(self):
        return self.alive and self.time_since_infected >= INCUBATION_PERIOD and not self.cured

    def check_boundary_collision(self):
        x, y = self.pos
        if (x < -WIDTH and 90 < self.dir < 270) or (x > WIDTH and 90 < (180-self.dir) % 360 < 270):
            self.dir = (180-self.dir) % 360
        if (y < -HEIGTH and self.dir > 180) or (y > HEIGTH and self.dir < 180):
            self.dir = (-self.dir) % 360

    def check_collisions(self, other):
        return dist(*self.pos, *other.pos) < PARTICLE_RADIUS


if __name__ == "__main__":
    sys = ParticleSystem(POPULATION)
