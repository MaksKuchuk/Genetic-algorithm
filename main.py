import pygame as pg
import random as rd
import math as mt
import copy
import time

rd.seed(time.time())

class Agent:
	 def __init__(self, xabs, yabs, steps, power, screen):
	 	self.xyabs = (xabs, yabs)
	 	self.xy = [0, 0]
	 	self.steps = steps
	 	self.moveV = [self.randNormV() for i in range(steps)]
	 	self.color = (rd.randint(0, 255), rd.randint(0, 255), rd.randint(0, 255))
	 	self.power = power
	 	self.screen = screen

	 	#Settings Percents
	 	self.mutOfVectors = 0.1
	 	self.selOfVectors = 0.3

	 def newAgent(self, ag):
	 	self.moveV = copy.deepcopy(ag.moveV)

	 def randNormV(self):
	 	x, y = rd.randint(-100, 100), rd.randint(-100, 100)
	 	l = mt.sqrt(x**2 + y**2)
	 	if abs(l) > 0.0001:
	 		return (x / l, y / l)
	 	else:
	 		return self.randNormV()

	 def mutRandNormV(self, v):
	 	p = (rd.random()*2 - 1 + v[0], rd.random()*2 - 1 + v[1])
	 	l = mt.sqrt(p[0]**2 + p[1]**2)
	 	return (p[0]/l, p[1]/l)

	 def mutate(self):
	 	for i in range(int(len(self.moveV) * self.mutOfVectors)):
	 		t = rd.randint(0, len(self.moveV)-1)
	 		self.moveV[t] = self.mutRandNormV(self.moveV[t])

	 def select(self, ag):
	 	for i in range(int(len(self.moveV) * self.selOfVectors)):
	 		t = rd.randint(0, len(self.moveV)-1)
	 		l = mt.sqrt((self.moveV[t][0] + ag.moveV[t][0])**2 + (self.moveV[t][1] + ag.moveV[t][1])**2)
	 		if abs(l) > 0.0001:
	 			self.moveV[t] = ((self.moveV[t][0] + ag.moveV[t][0]) / l, (self.moveV[t][1] + ag.moveV[t][1]) / l)

	 def succ(self):
	 	return mt.sqrt((self.xy[0])**2 + (self.xy[1])**2)

	 def step(self, step):
	 	self.xy[0] += self.moveV[step][0] * self.power
	 	self.xy[1] += self.moveV[step][1] * self.power

	 def draw(self):
	 	pg.draw.circle(self.screen, self.color, (self.xyabs[0], self.xyabs[1]), 1)
	 	pg.draw.circle(self.screen, self.color, (self.xyabs[0] + self.xy[0], self.xyabs[1] + self.xy[1]), 6)


class App:
	def __init__(self, amAgenX, amAgenY, amSteps, fps, res):
		self.res = res
		self.screen = pg.display.set_mode(res, pg.SCALED)
		self.clock = pg.time.Clock()
		self.genPS = 0
		self.fps = fps
		self.startTime = time.time()
		self.gen = 0
		self.average = 0
		self.best = 0
		self.gameSpeed = 1/4000
		self.localStep = 0
		self.appSpeed = 0.0001		
		self.power = 5
		self.steps = amSteps
		self.dt = 0
		self.maxRes = self.power * self.steps
		self.prev_time = pg.time.get_ticks()
		self.agents = [Agent(x, y, amSteps, self.power, self.screen) for x in range(int(res[0] / (amAgenX * 2)), res[0], int(res[0] / amAgenX)) for y in range(int(res[1]/(amAgenY * 2)), res[1], int(res[1]/amAgenY))]

		#Settings Percents
		self.mutOfAgents = 0.4
		self.selOfAgents = 0.25
		self.partForDeletion = 0.05


	def run(self):
		while True:
			self.clock.tick
			self.screen.fill('black')

			self.control()
				
			self.draw()
			pg.display.flip()

			[exit() for i in pg.event.get() if i.type == pg.QUIT]
			self.dt = self.delta_time()
			self.clock.tick(int(self.fps))
			pg.display.set_caption(f'{self.fps :.0f} Generation: {self.gen}   Average: {self.average :.0f}   Best: {self.best :.0f}   MaxRes: {self.maxRes :.0f}   GenInSec: {self.genPS :.0f}')

	def draw(self):
		for i in self.agents:
			i.draw()

	def step(self):
		if self.localStep < self.steps:
			for i in self.agents:
				i.step(self.localStep)
			self.localStep += 1
		else:
			self.best = self.getBest()
			self.average = self.getAverage()
			self.newGeneration()
			self.gen += 1
			self.localStep = 0

	def newGeneration(self):
		t = [(i, i.succ()) for i in self.agents]
		t = sorted(t, key=lambda x: x[1])

		ags = [i[0] for i in t]

		for i in range(len(ags)):
			if (len(ags) * self.partForDeletion) <= i:
				break
			ags[i].newAgent(ags[rd.randint(int(len(ags) * self.partForDeletion), len(ags)-1)])

		self.mutation(ags)
		self.selection(ags)

		for i in ags: i.xy = [0, 0]

		self.agents = ags

		self.genPS = 1/(time.time() - self.startTime)
		self.startTime = time.time()

	def getAverage(self):
		s = 0
		for i in self.agents: s += i.succ()
		return (s/len(self.agents))

	def getBest(self):
		s = -1
		for i in self.agents: 
			t = i.succ()
			if s < t: s = t
		return s

	def delta_time(self):
		time_now = pg.time.get_ticks() - self.prev_time
		self.prev_time = time_now
		return time_now

	def mutation(self, ags):
		for i in range(int(len(ags) * self.mutOfAgents)):
			ags[rd.randint(0, len(ags)-1)].mutate()

	def selection(self, ags):
		for i in range(int(len(ags) * self.selOfAgents)):
			ags[rd.randint(0, len(ags)-1)].select(ags[rd.randint(0, len(ags)-1)])

	def control(self):
		pressed_key = pg.key.get_pressed()
		if pressed_key[pg.K_w]:
			self.step()
		if pressed_key[pg.K_a]:
			self.fps -= self.dt * self.gameSpeed
		if pressed_key[pg.K_d]:
			self.fps += self.dt * self.gameSpeed


if __name__ == '__main__':
	xAgents = 10
	yAgents = 10
	steps = 30
	fps = 30
	app = App(xAgents, yAgents, steps, fps, (1280, 720))
	app.run()
