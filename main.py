"""Source:     https://github.com/csamuelsm/covid19-simulations/blob/master/corona.pde   """

# IMPORTS ----------------------------------
import random
from math import sqrt, cos, sin, atan2, degrees, radians
import turtle as t
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import font


d = dict(
        POPULATION = 100,
        PARTICLE_RADIUS = 12,
        HEIGHT = 400,
        WIDTH = 400,
        TRANSMISSION_PROBABILITY = 0.4,
        HOSPITAL_CAPACITY = 100*0.1,
        HOSPITAL_RADIUS = 100,
        INCUBATION_PERIOD = 200,
        PROTECTION = 3,  # 0: nobody, 1: doctors, 2: doctors and patients, 3: doctors and infected, 4: everybody
        PROTECTION_EFFICIENCY = 0.8,
        HOUSE_NUMBER = 25,
        HOUSE_RADIUS = 40,
        QUARANTINE = False,
        QUARANTINE_THRESHOLD = 1, # number of sick people required to start quarantine
        AGE_THRESHOLD_ELDER = 65, # Threshold to be considered as elder)  
)

d['HOSPITAL_CAPACITY'] = d['POPULATION']*0.1

# GLOBAL FUNCTIONS -------------------------
def dist(x1, y1, x2=0, y2=0):
    return sqrt((x1-x2) ** 2 + (y1-y2) ** 2)


# CLASSES ----------------------------------
class ParticleSystem(object):
    def __init__(self, pop_size, d):
        self.quarantine = d["QUARANTINE"]  # is quarantine set or not ?
        self.quarantine_start = 0  # to remember when the quarantine will (or not) start
        self.hospital = Hospital(capacity=d["HOSPITAL_CAPACITY"], radius=d["HOSPITAL_RADIUS"])
        self.days = 0
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        self.lst_houses = []

        # House are added in a circle around the position (0, 0)
        for i in range(d['HOUSE_NUMBER']):
            can_add_house = False

            while not can_add_house:
                if len(self.lst_houses) == 0:
                    can_add_house = True

                house_position = (
                    (self.hospital.radius + d['HOUSE_RADIUS'] + random.random() * 150) * cos(radians(360 * random.random())),
                    (self.hospital.radius + d['HOUSE_RADIUS'] + random.random() * 150) * sin(radians(360 * random.random()))
                )
                for house in self.lst_houses:
                    if dist(*house_position, *self.hospital.pos) > d['HOSPITAL_RADIUS'] + d['HOUSE_RADIUS'] + 5:
                        if dist(*house_position, *house.pos) > d['HOUSE_RADIUS']*2 + 5:
                            can_add_house = True
                        else:
                            can_add_house = False
                            break
                    else:
                        break

            self.lst_houses.append(House(pos=house_position))

        # the first particle is infected and is 20 years old
        #Houses are assigned randomly
        self.lst_particles = [Particle(infected=0, age=20, house=random.choice(self.lst_houses))]
        for i in range(1, pop_size):
            # HOSPITAL_CAPACITY doctors are chosen to be able to go in the hospital and houses
            if i >= pop_size - d["HOSPITAL_CAPACITY"]:
                self.lst_particles.append(Particle(house=random.choice(self.lst_houses), job="doc"))
            else:
                self.lst_particles.append(Particle(house=random.choice(self.lst_houses)))

        # stats to draw the graph at the end
        self.stats = {"healthy": {}, "infected": {}, "cured": {}, "sick": {}, "dead": {}}
        t.tracer(0, 0)
        t.ht()
        self.run(d)
        t.done()

    def run(self, d):
        infected = 1
        while infected > 0:
            self.compute_time()
            healthy, infected, sick, cured, dead = 0, 0, 0, 0, 0
            self.hospital.patients = sum([part.hospital for part in self.lst_particles])

            for i in range(len(self.lst_particles)):
                part1 = self.lst_particles[i]
                if part1.alive:
                    part1.update()
                for j in range(i+1, len(self.lst_particles)):
                    part2 = self.lst_particles[j]
                    # if 2 particles collide and one of them is infected, calculate the risk of transmission
                    # if one of them is protected, transmission probability is reduced, regardless of who is infected
                    if part1.alive and part2. alive and part1.check_collisions(part2):
                        # Detect collision and update directions
                        ParticleSystem.collision(part1, part2)
                        if (part1.is_contagious() or part2.is_contagious()) \
                                and random.random() <= d["TRANSMISSION_PROBABILITY"] \
                                * (1-d["PROTECTION_EFFICIENCY"]*max(part1.protection, part2.protection)):
                            part1.time_since_infected = max(0, part1.time_since_infected)
                            part2.time_since_infected = max(0, part2.time_since_infected)

                # House and quarantine
                # if in quarantine and outside the house, turn arround
                # if in hospital, ignored
                if self.quarantine and part1.job != "doc" and not part1.hospital:
                    x1, y1 = part1.pos
                    x2, y2 = part1.house.pos
                    if dist(x1, y1, x2, y2) > d["HOUSE_RADIUS"]:
                        part1.dir = (degrees(atan2(y1 - y2, x1 - x2)) + 180) % 360

                # Hospital and stuff
                if part1.is_sick():
                    if dist(*part1.pos) > self.hospital.radius:
                        # if hospitalised and outside, or need to be, go to the hospital
                        if part1.hospital:
                            part1.dir = (degrees(atan2(part1.pos[1], part1.pos[0]))+180) % 360
                            # if he finally joined the hospital, update the hospital state
                            self.hospital.patients += 1
                    if not part1.hospital and self.hospital.capacity > self.hospital.patients:
                        # Condition to prioritize elder people
                        # Explanation : if the number of infected is above the hospital capacity,
                        # we keep 20% of the capacity reserved for elder people
                        if infected >= self.hospital.capacity:
                            if self.hospital.patients + int(self.hospital.capacity * 0.2) == self.hospital.capacity:
                                if part1.age >= d['AGE_THRESHOLD_ELDER']:
                                    print('Elder guy prioritized')
                                    part1.hospital = True
                        else:
                            # Normal situation
                            part1.hospital = True
                # People are not allowed to go in the hospital unless :
                #  - there is quarantine so they can travel easier to their house
                #  - he's sick
                #  - he's a doctor
                if not self.quarantine and not part1.is_sick() and part1.job != "doc" \
                        and dist(*part1.pos) < self.hospital.radius:
                    part1.dir = degrees(atan2(part1.pos[1], part1.pos[0])) % 360

                # update protection after the hospital state has been updated
                part1.set_protection()

                # sick counter
                if part1.is_sick():
                    sick += 1

                # stat counters
                if part1.cured:
                    cured += 1
                elif not part1.alive:
                    dead += 1
                elif part1.time_since_infected >= 0:
                    infected += 1
                healthy = len(self.lst_particles) - (infected+cured+dead)

            # Append stats
            self.stats["healthy"][self.hours] = healthy
            self.stats["infected"][self.hours] = infected
            self.stats["sick"][self.hours] = sick
            self.stats["cured"][self.hours] = cured
            self.stats["dead"][self.hours] = dead

            # if quarantine criteria is reached, set up th quarantine (and save the start time)
            if not self.quarantine and sick >= d["QUARANTINE_THRESHOLD"]:
                self.quarantine = True
                self.quarantine_start = len(self.stats["healthy"])

            # draw graphics
            self.draw(d)

        # print the stats and show the graphes
        self.stats = pd.DataFrame(self.stats)
        #print(self.stats)
        self.stats.loc[:, ["healthy", "infected", "cured", "dead"]].plot.area()
        plt.axvline(self.quarantine_start, color="black")
        plt.xlabel('Time (hours)')
        plt.ylabel('Population')
        self.stats.loc[:, ["sick"]].plot.area()
        plt.axvline(self.quarantine_start, color="black")
        plt.axhline(d["HOSPITAL_CAPACITY"], color="black")
        plt.legend()
        plt.xlabel('time (hours)')
        plt.ylabel('Population')
        plt.show()

    def compute_time(self):
        self.hours = int(self.minutes/60)
        self.days = int(self.minutes/(24*60))
        self.minutes += 120

    def draw(self,d):
        # begin to clear turtle
        t.clear()

        # draw the frontiers
        w, h = d["WIDTH"]+d["PARTICLE_RADIUS"], d["HEIGHT"]+d["PARTICLE_RADIUS"]
        t.up()
        t.goto(w, h)
        t.down()
        t.color("black", "white")
        t.begin_fill()
        for x, y in ((-1, 1), (-1, -1), (1, -1), (1, 1)):
            t.goto(x*w, y*h)
        t.end_fill()

        # draw hospital and houses
        self.hospital.draw(d)
        for house in self.lst_houses:
            house.draw(d)

        # draw particles
        for part in self.lst_particles:
            t.up()
            t.goto(part.pos)
            t.down()
            if part.hospital:
                t.color("dark orange")
                t.dot(d["PARTICLE_RADIUS"]+7)
            if part.protection == 1:
                t.color("green")
                t.dot(d["PARTICLE_RADIUS"]+4)
            t.color(part.color)
            t.dot(d["PARTICLE_RADIUS"])

        t.up()
        t.color('black')
        #t.goto(-d['WIDTH'] / 1.4, d['HEIGHT'] / 1.5)
        t.goto(-d['WIDTH'] , d['HEIGHT']-d['HEIGHT']/10)
        t.down()
        t.write("Time : %s days, %s hours" % (self.days, self.hours%24), align=LEFT,
                font=("Arial", 15, "normal"))
        t.up()

        # update the screen because I've disabled the auto update (it speeds up the drawing)
        t.update()

    @staticmethod
    def collision(part1, part2):
        """Update direction of particles after the collision has been detected"""
        x1, y1 = part1.pos
        x2, y2 = part2.pos
        part1.dir = degrees(atan2(y1 - y2, x1 - x2)) % 360
        part2.dir = (part1.dir + 180) % 360


class House(object):
    def __init__(self, pos):
        self.pos = pos
        self.radius = d["HOUSE_RADIUS"]

    def draw(self,d):
        t.up()
        t.goto(self.pos[0], self.pos[1]-self.radius)
        t.seth(0)
        t.color("black")
        t.fillcolor("#97c1de")
        t.down()
        t.begin_fill()
        t.circle(self.radius)
        t.end_fill()


class Hospital(object):
    def __init__(self, capacity, radius):
        self.capacity = capacity
        self.patients = 0
        self.radius = radius
        self.pos = 0, 0

    def draw(self,d):
        t.up()
        t.goto(0, -self.radius)
        t.seth(0)
        t.color("#cc4141")
        t.fillcolor("#e85d5d")
        t.down()
        t.begin_fill()
        t.circle(self.radius)
        t.end_fill()
        self.draw_H()

    def draw_H(self):
        height = self.radius/3
        t.up()
        t.goto(-height/2, 0)
        t.seth(90)
        t.color("#999090")
        t.fillcolor("white")
        t.down()
        t.begin_fill()

        for i in range(2):
            t.forward(height / 2)
            t.right(90)
            t.forward(height/3)
            t.right(90)
            t.forward(height/3)
            t.left(90)
            t.forward(height/3)
            t.left(90)
            t.forward(height/3)
            t.right(90)
            t.forward(height/3)
            t.right(90)
            t.forward(height/2)
        t.end_fill()




class Particle(object):
    def __init__(self, house, infected=-1, age=random.randint(0, 100), job=""):
        # TODO some things are missing here
        self.age = age
        self.job = job
        self.house = house
        self.alive = True
        self.hospital = False
        self.cured = False
        self.time_since_infected = infected # -1 means not infected, 0 or more means infected
        # set the particle position in a square centered on its house
        x_h, y_h = self.house.pos
        x_h, y_h = int(x_h), int(y_h)
        self.pos = (random.randint(x_h-d["HOUSE_RADIUS"], x_h+d["HOUSE_RADIUS"]),
                    random.randint(y_h-d["HOUSE_RADIUS"], y_h+d["HOUSE_RADIUS"]))
        self.dir = random.randint(0, 360)
        self.velocity = random.random()*2+5  # random speed between 3 and 5
        self.color = ""
        self.set_color()
        self.protection = 0  # 0 is not protected, 1 is protected
        self.set_protection()

    def set_protection(self):
        """update the protection depending on the PROTECTION parameter and particle state"""
        if d["PROTECTION"] == 4 \
                or (d["PROTECTION"] == 3 and (self.job == "doc" or self.is_sick())) \
                or (d["PROTECTION"] == 2 and (self.job == "doc" or self.hospital)) \
                or (d["PROTECTION"] == 1 and self.job == "doc"):
            self.protection = 1
        else:
            self.protection = 0

    def death(self):
        """update self.alive state depending on self.age and self.hospital state"""
        # Random probability, if under this probability, subject dies
        random_probability = random.random()*100
        if self.hospital:
            random_probability *= 3
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
        """update the color"""
        if not self.alive:
            self.color = "light gray"
        elif self.cured:
            self.color = "green"
        elif self.time_since_infected >= 0:
            self.color = "red"
        else:
            self.color = "black"

    def update(self):
        """update a bunch of things about the particle"""
        self.check_boundary_collision()  # change direction if colliding a wall
        # update position
        x, y = self.pos
        x += cos(radians(self.dir))*self.velocity
        y += sin(radians(self.dir))*self.velocity
        self.pos = x, y

        # update illness state
        if self.is_contagious():
            self.time_since_infected += 1
            # if illness duration ends
            if self.time_since_infected > 400:
                self.death()
                # if self.death() didn't kill it, set it to cured
                if self.alive:
                    self.cured = True
                # as the illness is ended, don't stay in the hospital
                self.hospital = False
            # if sick and not in a hospital, the illness progresses faster
            elif self.time_since_infected > d["INCUBATION_PERIOD"] and not self.hospital:
                self.time_since_infected += 2

        self.set_color()

    def is_contagious(self):
        """if infected, is contagious"""
        return self.alive and self.time_since_infected >= 0 and not self.cured

    def is_sick(self):
        """if infected and incubation period is over, is sick"""
        return self.alive and self.time_since_infected >= d["INCUBATION_PERIOD"] and not self.cured

    def check_boundary_collision(self):
        """update direction after colliding a wall using where incidence angle = reflected angle"""
        x, y = self.pos
        if (x < -d["WIDTH"] and 90 < self.dir < 270) or (x > d["WIDTH"] and 90 < (180-self.dir) % 360 < 270):
            self.dir = (180-self.dir) % 360
        if (y < -d["HEIGHT"] and self.dir > 180) or (y > d["HEIGHT"] and self.dir < 180):
            self.dir = (-self.dir) % 360

    def check_collisions(self, other):
        """return True if other is colliding with self"""
        return dist(*self.pos, *other.pos) < d["PARTICLE_RADIUS"]


class Window(Frame):
    def __init__(self, 
                 master,
                 parameters,
                 title="Definition of the Parameters",
                 geometry="1100x550"):
        Frame.__init__(self, master)        
        self.master = master

        # widget can take all window
        self.pack(fill=BOTH, expand=1)
        
        # Give it a title
        master.wm_title(title)
        
        # Decide the geometry
        master.geometry(geometry)
        
        #Define the font
        appHighlightFont = font.Font(family='Arial', size=11)
        back='#bdc3af'
        charac='#150b04'
        self.configure(background=back)

        # create button, link it to clickExitButton()
        runButton = Button(self, text="Run", font=appHighlightFont, command=self.runButton, bg='green', fg='white')
        runButton.place(x=110, y=10)
        
        # Parameter Labels
        self.parameters = parameters
        
        # Create Entry Form And fill in parameters
        # Store in Dictionary so changes can be retrieved
        self.entryObjects = dict()
        for i,par in enumerate(self.parameters.keys()):
            # Extract Default valie
            defaultTextForEntry = self.parameters[par]
            
            # Generate and place label
            if par == "POPULATION":
                textForLabel=par[0]+par[1:len(par)].replace("_"," ").lower()+" size (Default: "+str(defaultTextForEntry)+ ")"
            elif par == "HEIGHT" or par == "WIDTH":
                textForLabel=par[0]+par[1:len(par)].replace("_"," ").lower()+" of the window (Default: "+str(defaultTextForEntry)+ ")"
            elif par == "PROTECTION":
                textForLabel=par[0]+par[1:len(par)].replace("_"," ").lower()+" (0: nobody, 1: doctors, 2: doctors and patients, 3: doctors and infected, 4: everybody)"
            elif par == "HOUSE_NUMBER":
                textForLabel="Number of houses (Default: "+str(defaultTextForEntry)+ ")"
            elif par == "QUARANTINE":
                textForLabel=par[0]+par[1:len(par)].replace("_"," ").lower()+" (True or False)"
            elif par == "QUARANTINE_THRESHOLD":
                textForLabel="Number of sick people required to trigger the beginning of the quarantine (Default: "+str(defaultTextForEntry)+ ")"
            elif par == "AGE_THRESHOLD_ELDER":
                textForLabel="Threshold to be considered as an elder (Default: "+str(defaultTextForEntry)+ ")"
            else:
                textForLabel=par[0]+par[1:len(par)].replace("_"," ").lower()+" (Default: "+str(defaultTextForEntry)+ ")"
            label = Label(self, text=textForLabel, font=appHighlightFont, bg=back, fg=charac)
            label.place(x=200,y=30*(i+2))
            
            # Generate and plac entry fields
            entry = Entry(self)
            entry.insert(0,defaultTextForEntry)
            entry.place(x=20,y=30*(i+2))
            self.entryObjects[par]=entry
                    
        # Launch and run the window
        master.mainloop()
            
    def runButton(self):
        d = self.retrieveParametersFromWindow()
        try:
            return ParticleSystem(d["POPULATION"], d)
        except:
            #print('pk la vi')
            self.master.destroy()
            pass
    
    def retrieveParametersFromWindow(self):
        parameters=dict()
        for par in self.entryObjects.keys():
            key = par
            entry = self.entryObjects[key]
            valueRaw = entry.get()
            if key == "QUARANTINE":
                if valueRaw == '0' or valueRaw.lower()=="false":
                    value = False
                else:
                    value = True
            elif key in ["TRANSMISSION_PROBABILITY", 
                         "HOSPITAL_CAPACITY", 
                         "PROTECTION_EFFICIENCY"]:
                value = float(valueRaw)
            else:
                value = int(valueRaw)
            parameters[key]=value
        return parameters
    

if __name__ == "__main__":
    app = Window(Tk(),d)
