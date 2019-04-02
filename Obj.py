import pygame

class Obj():
	def __init__(self,controller):
		self.controller=controller
		self.x=0
		self.y=0
		self.color=(0,0,0)
		#add collision in this obj
		self.xvel=0
		self.yvel=0
		self.onGround=False
		self.w=16
		self.h=16
		self.solid=False
		self.controller.objs.append(self)
	def destroy(self):
		if self in self.controller.objs:
			self.controller.objs.remove(self)

	def getx(self):
		return self.x
	def gety(self):
		return self.y
	def getcolor(self):
		return self.color
	def getw(self):
		return self.w
	def geth(self):
		return self.h
	def getsolid(self):
		return self.solid
	def collision(self,walls,changeState=False):
		self.onground=False

		for i in walls:

			if self.x+self.xvel<i.x+i.w and self.xvel!=0\
			and self.x+self.w+self.xvel>i.x\
			and self.y<i.y+i.h and self.y+self.h>i.y:
				if self.x<i.x:
					self.x=i.x-self.w
				if self.x>i.x+i.w:
					self.x=i.x+i.w
				self.xvel=0
				if changeState==True:
					i.col=True
			
			if self.y+self.yvel<i.y+i.h and self.yvel!=0\
			and self.y+self.h+self.yvel>i.y\
			and self.x<i.x+i.w and self.x+self.w>i.x:
				if self.y>i.y+i.h:
					self.y=i.y+i.h
				if self.y<i.y:
					self.y=i.y-self.h
				self.yvel=0
				if changeState==True:
					i.col=True
			


	def draw(self,screen):
		pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx(), self.gety(), self.getw(), self.geth()))
	def draw_shadow(self,screen):
		return 0

	def update(self):
		return 0
