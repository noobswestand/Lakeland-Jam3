import pygame,math,random,Obj,Particle,numpy as np,matplotlib.path as mplPath
def point_distance(x1,y1,x2,y2):
	return (((x1-x2)**2)+((y1-y2)**2))**0.5
def point_direction(x1,y1,x2,y2):
	return math.atan2(y1 - y2, x1 - x2);


class Enemy(Obj.Obj):
	def __init__(self,controller,x,y,beat_mod=1,beat_mod_off=0):
		Obj.Obj.__init__(self,controller)
		self.controller=controller
		self.controller.enemies.append(self)
		self.color=(173, 10, 70)
		self.x=x
		self.y=y
		self.poly=((0,0),(0,0))
		self.beat=0
		self.beat_mod=beat_mod
		self.beat_mod_off=beat_mod_off

		self.init()
		self.bbPath=mplPath.Path(np.array(self.poly))
	def init(self):
		raise NotImplementedError("Must override init2")
	def destroy(self):
		Obj.Obj.destroy(self)
		self.controller.enemies.remove(self)

	def draw(self,screen):
		pygame.draw.polygon(screen,self.color,self.poly)
	def draw_shadow(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			l[i][0]+=5
			l[i][1]+=5
		pygame.draw.polygon(screen,(50,50,50),tuple(l))

class Bullet(Obj.Obj):
	def __init__(self,controller,owner,x,y,damage,direction,speed,color):
		Obj.Obj.__init__(self,controller)
		self.controller=controller
		self.owner=owner
		self.x=x
		self.y=y
		self.damage=damage
		self.direction=direction
		self.speed=speed
		self.color=color
		self.xvel=math.cos(self.direction)*self.speed
		self.yvel=math.sin(self.direction)*self.speed
	def update(self):
		self.x+=self.xvel
		self.y+=self.yvel
		if self.x<0 or self.x>self.controller.room_width or self.y<0 or self.y>self.controller.room_height:
			self.destroy()
		#Collisions
		overlapbbox = (self.x-abs(self.speed), self.y-abs(self.speed),\
			self.x+self.w+abs(self.speed), self.y+self.h+abs(self.speed))
		walls = self.controller.wallTree.intersect(overlapbbox)
		for w in walls:
			if w.col_bullet==True and self.x>w.x and self.x<w.x+w.w\
			and self.y>w.y and self.y<w.y+w.h:
				self.destroy()

		#Check for collisions with the player
		if point_distance(self.x,self.y,self.controller.player.x_center,self.controller.player.y_center)<15:
			self.controller.bpm+=self.damage
			self.destroy()

	def destroy(self):
		Obj.Obj.destroy(self)
		for i in range(3):
			p=Particle.Particle(self.controller,self.x-math.cos(self.direction)*self.speed,self.y-math.sin(self.direction)*self.speed\
				,2,random.uniform(0,math.pi*2),random.uniform(0,2),self.color,60)
		


	def draw(self,screen):
		pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),7)
		pygame.draw.circle(screen,(min(255,self.color[0]+25),min(255,self.color[1]+25,min(255,self.color[2]+25)),255),(int(self.x),int(self.y)),3)
	def draw_shadow(self,screen):
		pygame.draw.circle(screen,(50,50,50),(int(self.x+2),int(self.y+2)),6)

class Shape(Enemy):
	def init(self):
		self.r=0
		self.raduis=50
		self.step=0
		self.damage=5

	def update(self,move=True):
		#Rotate
		if move==True:
			self.r+=math.pi/60

		self.raduis+=(50-self.raduis)/5.0

		#Shooting
		if self.controller.beat_go==True:
			self.beat+=1
			if (self.beat+self.beat_mod_off)%self.beat_mod==0:
				self.raduis+=15
				for i in range(self.sides):
					x,y=(self.x+(math.cos(self.r+(i*2*math.pi)/self.sides)*self.raduis),\
						self.y+(math.sin(self.r+(i*2*math.pi)/self.sides)*self.raduis))
					d=point_direction(self.x,self.y,x,y)+math.pi
					Bullet(self.controller,self,x,y,self.damage,d,5,self.color)


		#Construct the poly
		self.poly=[]
		for i in range(self.sides):
			self.poly.append((self.x+(math.cos(self.r+(i*2*math.pi)/self.sides)*self.raduis),\
				self.y+(math.sin(self.r+(i*2*math.pi)/self.sides)*self.raduis)))
		self.bbPath=mplPath.Path(np.array(self.poly))

class Triangle(Shape):
	def init(self):
		Shape.init(self)
		self.sides=3
		self.type=0

class Rectangle(Shape):
	def init(self):
		Shape.init(self)
		self.sides=4
		self.type=1

class Pentagon(Shape):
	def init(self):
		Shape.init(self)
		self.sides=5
		self.type=2

class Hexagon(Shape):
	def init(self):
		Shape.init(self)
		self.sides=6
		self.type=3


