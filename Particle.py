import pygame,math,Obj

class Particle(Obj.Obj):
	def __init__(self,controller,x,y,r,direction,speed,color,life):
		Obj.Obj.__init__(self,controller)
		self.controller=controller
		self.x=x
		self.y=y
		self.r=r
		self.direction=direction
		self.speed=speed
		self.w=1
		self.h=1

		self.xvel=math.cos(self.direction)*self.speed
		self.yvel=math.sin(self.direction)*self.speed

		self.color=color
		self.life=life
		self.life_max=life

		self.surface=pygame.Surface((r*2,r*2))
		self.surface.set_colorkey((0,0,0))
		self.drawn=False
		self.friction=.02
	def update(self):
		self.surface.set_alpha(int((float(self.life)/float(self.life_max))*255))
		self.life-=1
		if self.life<=0:
			self.destroy()

		if self.x<0 or self.x>self.controller.room_width or self.y<0 or self.y>self.controller.room_height:
			self.destroy()
		#Collisions
		overlapbbox = (self.x-abs(self.speed), self.y-abs(self.speed),\
			self.x+self.w+abs(self.speed), self.y+self.h+abs(self.speed))
		walls = self.controller.wallTree.intersect(overlapbbox)
		self.collision(walls)


		self.x+=self.xvel
		self.y+=self.yvel
		self.xvel=self.xvel*(1-self.friction)
		self.yvel=self.yvel*(1-self.friction)
		#self.x+=math.cos(self.direction)*self.speed
		#self.y+=math.sin(self.direction)*self.speed
				

	def draw(self,screen):
		if self.drawn==False:
			self.drawn=True
			pygame.draw.circle(self.surface,self.color,(self.r,self.r),self.r)

		screen.blit(self.surface, (int(self.x),int(self.y)))
