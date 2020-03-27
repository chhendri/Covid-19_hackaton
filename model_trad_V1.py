
"""Source:     https://github.com/csamuelsm/covid19-simulations/blob/master/corona.pde   """



import random



contamined = 1
cured = 0
dead = 0
population = 500
healthy = 0

initial_population = population
initial_cases = contamined
num_contaminated = contamined
num_deaths = 0

# No idea what this uti means
num_uti = 0
num_hospital = 0
total_hospital = 0
num_saved = initial_population - num_contaminated
num_recuperating = 0

def ParticleSystem():
    healthy = population - contamined
    for i in range(contamined):

    for i in range(population-contamined):




class Particle:
    def __init__(self, position, velocity):
        # TODO some things are missing here
        d = 2
        t = 10
        age =
        death = 0
        time = 0
        necessary_time = random.randint(1800,3000)
        hospital = 0

    def Particle(self, pos, cat):
        position = pos
        velocity =
        cathegory = cat
        age = random.randint(10, 100)
        # Random probability, if under this probability, subject dies
        random_probability = random.uniform(0, 100)
        # Compute the probabilities of death for each condition
        if 10 <= age <= 19:
            if random_probability <= 0.02:
                death = 1
        elif 20 <= age <= 29:
            if random_probability <= 0.09:
                death = 1
        elif 30 <= age <= 39:
            if random_probability <= 0.18:
                death = 1
        elif 40 <= age <= 49:
            if random_probability <= 0.4:
                death = 1
        elif 50 <= age <= 59:
            if random_probability <= 1.3:
                death = 1
        elif 60 <= age <= 69:
            if random_probability <= 4.6:
                death = 1
        elif 70 <= age <= 79:
            if random_probability <= 9.8:
                death = 1
        else:
            if random_probability <= 18:
                death = 1

        prob = random.uniform(0, 100)
        if 0 <= prob <= 5:
            hospital = 2
        elif 5 < prob <= 20:
            hospital = 1


    # TODO run


    def update(self):
        position += velocity
        if cathegory == 1:
            time += 1
        if time > necessary_time:
            num_recuperating += 1
            cathegory = 2
            # TODO here compute velocity
            velocity =
            time = 0
        total_hospital = num_hospital + num_uti

    def display(self):
        if cathegory = 1 and hospital = 1:
            # TODO strokeweight
        elif cathegory = 1 and hospital = 2:
            # TODO strokeweight
        else:
            # TODO nostroke

        # TODO switch categhory
        # TODO ellipse


    def check_boundary_collision(self):
        # WARNING! HERE I ASSUME POSITION WILL BE GIVEN AS A TUPLE
        if position[0] > 0.7*width-(d/2):
            position[0] = 0.7 * width - (d / 2)
            velocity[0] *= -1
        elif position[0] < (d/2):
            position[0] = (d/2)
            velocity[0] *= -1
        elif position[1] > height - (d/2):
            position[1] = height - (d / 2)
            velocity[1] *= -1
        elif position[1] < (d/2):
            position[1] = (d / 2)
            velocity[1] *= -1

    def check_collisions(self, other):

        # TODO this first part about the distancevectors

        minDistance = (d / 2) + (other.d / 2)
        if distanceVectMag < minDistance:
            if cathegory == 1 and other.cathegory == 0:
                if other.death == 1:
                    other.cathegory = 3
                    num_deaths += 1
                else:
                    other.cathegory = 1
                    num_contaminated += 1
            elif cathegory == 0 and other.cathegory == 1:
                if death == 1:
                    cathegory = 3
                    num_deaths += 1
                else:
                    cathegory = 1
                    num_contaminated += 1

        """
        float theta  = distanceVect.heading();
        // precalculate trig values
        float sine = sin(theta);
        float cosine = cos(theta);
        """
        # TODO all the things with the velocity calculation



    def is_dead(self):
        True if cathegory == 3 else False

    class Particle_System:

        # TODO all the particlesystem part here

        def add_particle(self, cathegory):

            # TODO all of this addParticle

        def run(self):
            num_hospital = 0
            num_uti = 0

        # TODO run