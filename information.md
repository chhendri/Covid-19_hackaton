# Sites links
* https://codevscovid19.devpost.com/
	- To register
* https://github.com/csamuelsm/covid19-simulations
	-  simulation of the covid-19 dissemination made with Processing and inspired by the 'Why outbreaks like coronavirus spread exponentially, and how to “flatten the curve”' article on the Washington Post and written by Harry Stevens
* https://processing.org/download/
	- Processing is a flexible software sketchbook and a language for learning how to code within the context of the visual arts. Since 2001, Processing has promoted software literacy within the visual arts and visual literacy within technology.
* https://www.nih.gov/health-information/coronavirus
	- The current state of the art on covid research can be bout on
*  https://www.supinfo.com/articles/single/4777-pymunk-moteur-physique-2d-vos-programmes-python
	- Simulations in Python

# Simulation Concept (Esteban)
* From the original simulation method
	- Random walks
	- Independence between spheres
	- Infection by contact
	- Change of direction after the contact (opposite direction)
	- No smaller closed blocks (representing closed environment such as home / institutions etc)
* Our simulation method
	- Dependence between certain spheres with some others
	- Directed walks (ex: work) AND random walks (hobbies)
	- BUT the walks are constrained by an environment (existence of « building » , creation of « roads »)
	- Infection by being next to someone else (no contact necessary) and depending on a certain probability
		+ We could maybe implement a chance distribution with contact higher chance and then decreasing chance with increasing distance
	- And I forgot to mention something important : in the base model, all spheres fully recover after a time t (based population = final population) but in our model we need to take into account the fact that people die (based population > final population). 
	- No change in direction after the infection
	- Creation of a sort of hospital with a fixed capacity? (Need to think on how it should work)
	- Disease growth rate curve displayed in the same time 
* What we need to determine:
	- The probability to get infected after a contact
	- The probability of death
	- Disease duration (at least an estimation)
	- The time during which a person can infect someone else
	- An average on how many people a patient infect during the first phase of the disease
* Our assumptions
	- Focused on a specific system / country or worldwide? (Health systems are different between countries)
	- The number of dependence between spheres (taking into account « family » , « work », « friends », « everyday routine activity »)
		+ We could maybe use graph theory to generate such kind of relationships 
* Pros
	- General simulation system that can be used later for another pandemic by changing some parameters
	- More accurate
* Cons
	- Computationally demanding ? (Need to create a map of size M, with a population of size P …)

# Features So Far
* Population of 100 (can be changed) in a rectangle area
* Each collision has a probability of 50% to transmit the virus (can also be changed)
* There is a hospital in the middle (red circle) with a capacity of 20 patients (20% of the population, can be changed)
* We begin with a 20-years-old infected, the others have random ages
* When two people collide, they go away in opposites directions
* People goes to the hospital when the incubation period is finished and there is room for them
* Once in the hospital, people heal faster with a lower probability of dying
* In the initial population, there are 40 doctors that are able to go in the hospital. Other healthy people are not allowed to go inside.
* Dead people are still visible but don't collide, don't move and don't transmit the virus

