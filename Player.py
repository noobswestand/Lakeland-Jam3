import pygame,math,random,Obj,Particle

def point_distance(x1,y1,x2,y2):
	return (((x1-x2)**2)+((y1-y2)**2))**0.5
def point_direction(x1,y1,x2,y2):
	return math.atan2(y1 - y2, x1 - x2)
def clamp(my_value,min_value,max_value):
	return max(min(my_value, max_value), min_value)



class Player(Obj.Obj):
	def __init__(self,controller):
		Obj.Obj.__init__(self,controller)
		self.controller=controller
		self.x=0
		self.y=0
		self.x_center=0
		self.y_center=0
		self.xvel=0
		self.yvel=0
		self.dead=False

		self.pxy=[[self.x,self.y],[self.x,self.y],[self.x,self.y],[self.x,self.y],[self.x,self.y]]

		self.friction=.2
		self.onground=False
		self.color=(0, 128, 255)
		self.color2=(107, 181, 255)
		self.w=24
		self.h=24
		self.solid=True
		self.key_left=False
		self.key_right=False
		self.key_up=False
		self.key_down=False
		self.move_speed=2
	def move(self,xvel,yvel):
		self.xvel+=xvel
		self.yvel+=yvel
	def update(self):
		#Update previous positions
		self.pxy.pop(0)
		self.pxy.append([int(self.x),int(self.y)])

		#Controls
		pressed = pygame.key.get_pressed()
		self.key_left=pressed[pygame.K_a]
		self.key_right=pressed[pygame.K_d]
		self.key_up=pressed[pygame.K_w]
		self.key_down=pressed[pygame.K_s]

		#Movement
		'''
		if self.key_left==True: self.move(-self.move_speed,0)
		if self.key_right==True: self.move(self.move_speed,0)
		if self.key_up==True: self.move(0,-self.move_speed)
		if self.key_down==True: self.move(0,self.move_speed)
		'''
		x,y=pygame.mouse.get_pos()
		d=point_direction(x-self.w/2,y-self.w/2,self.x,self.y)
		self.xvel+=(math.cos(d)*self.move_speed)*1.5#*0.5
		self.yvel+=(math.sin(d)*self.move_speed)*1.5#*0.5

		#Collisions - Enemies
		for e in self.controller.enemies:
			if e.bbPath.contains_point((self.x,self.y)):
				d=point_direction(self.x,self.y,e.x,e.y)
				self.xvel+=math.cos(d)*5
				self.yvel+=math.sin(d)*5

		#Collisions - WALLS
		overlapbbox = (self.x-abs(self.xvel), self.y-abs(self.yvel),\
			self.x+self.w+abs(self.xvel), self.y+self.h+abs(self.yvel))
		walls = self.controller.wallTree.intersect(overlapbbox)
		self.collision(walls,True)



		
		#Motion
		if self.dead==False:
			self.x+=self.xvel
			self.y+=self.yvel
			self.xvel=clamp(self.xvel,-8,8)
			self.yvel=clamp(self.yvel,-8,8)
		else:
			self.x=-500
			self.y=-500
			self.x_center=-500
			self.y_center=-500
		#self.xvel=self.xvel*(1-self.friction)
		#self.yvel=self.yvel*(1-self.friction)


		#Death
		if self.controller.bpm>360:
			for i in range(20):
				p=Particle.Particle(self.controller,self.x_center,self.y_center\
				,7,random.uniform(0,math.pi*2),random.uniform(0,4),self.color,120)
			for i in range(20):
				p=Particle.Particle(self.controller,self.x_center,self.y_center\
				,4,random.uniform(0,math.pi*2),random.uniform(0,4),self.color2,120)
			self.destroy(False)
			self.dead=True
			self.controller.tick=30


	def draw(self,screen):
		r=self.w/2
		x=int(self.x+r)
		y=int(self.y+r)
		rr=[r/1.5,r/1.25,r,r/1.25,r/1.5]
		for i in range(len(self.pxy)):
			xx=self.pxy[i][0]+r
			yy=self.pxy[i][1]+r
			pygame.draw.circle(screen,self.color,(xx,yy),int(rr[i]))
			if i==(len(self.pxy)//2):
				self.x_center=xx
				self.y_center=yy

		r=self.w/3
		x=int(self.x+self.w/2)
		y=int(self.y+self.w/2)
		rr=[r/1.5,r/1.25,r,r/1.25,r/1.5]
		for i in range(len(self.pxy)):
			xx=self.pxy[i][0]+self.w/2
			yy=self.pxy[i][1]+self.w/2
			pygame.draw.circle(screen,self.color2,(xx,yy),int(rr[i]))
	def draw_shadow(self,screen):
		r=self.w/2
		x=int(self.x+r)
		y=int(self.y+r)
		rr=[r/1.5,r/1.25,r,r/1.25,r/1.5]
		for i in range(len(self.pxy)):
			xx=self.pxy[i][0]+r+3
			yy=self.pxy[i][1]+r+3
			pygame.draw.circle(screen,(50,50,50),(xx,yy),int(rr[i]))

