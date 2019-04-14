import pygame,math,random,Obj,Particle,numpy as np,matplotlib.path as mplPath
def point_distance(x1,y1,x2,y2):
	return (((x1-x2)**2)+((y1-y2)**2))**0.5
def point_direction(x1,y1,x2,y2):
	return math.atan2(y1 - y2, x1 - x2);

def tron(argument0):
	#this will convert any number to a number between 0 and 359, so -90 becomes 270
	#argument0 = first direction
	tt=float(argument0)
	while(tt>=math.pi*2):
		tt-=math.pi*2
	while(tt<0):
		tt+=math.pi*2
	return tt
def dir_tron(argument0,argument1,argument2):
	#argument0 = first direction
	#argument1 = direciton to move to
	#argument2 = will be the amount to turn
	face=tron(float(argument0));
	face_to=tron(float(argument1));

	if face<face_to:
		if face<face_to-math.pi:
			face-=argument2
		else:
			face+=argument2

	if face>face_to:
		if face>face_to+math.pi:
			face+=argument2
		else:
			face-=argument2
	if abs(face-face_to)<argument2:
		face=face_to
	return face


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
		self.r=7
		self.dir_change=120
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
				w.hit_bullet()
				self.destroy()

		#Check for collisions with the player
		if self.controller.player.dead==False and\
			point_distance(self.x,self.y,self.controller.player.x_center,self.controller.player.y_center)<15:
			self.controller.bpm+=self.damage
			for i in range(3):
				p=Particle.Particle(self.controller,self.x-math.cos(self.direction)*self.speed,self.y-math.sin(self.direction)*self.speed\
					,2,random.uniform(0,math.pi*2),random.uniform(0,2),self.color,60)
			self.destroy()

	def destroy(self,particles=True):
		Obj.Obj.destroy(self)
		if particles==True:
			'''
			for i in range(3):
				p=Particle.Particle(self.controller,self.x-math.cos(self.direction)*self.speed,self.y-math.sin(self.direction)*self.speed\
					,2,random.uniform(0,math.pi*2),random.uniform(0,2),self.color,60)
			'''

	def draw(self,screen):
		pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),self.r)
		pygame.draw.circle(screen,(min(255,self.color[0]+25),min(255,self.color[1]+25,min(255,self.color[2]+25)),255),(int(self.x),int(self.y)),self.r-4)
	def draw_shadow(self,screen):
		pygame.draw.circle(screen,(50,50,50),(int(self.x+2),int(self.y+2)),6)

class BulletHom(Bullet):
	def update(self):
		d=point_direction(self.x,self.y,self.controller.player.x_center,self.controller.player.y_center)+math.pi
		self.direction=dir_tron(self.direction,d,(0.01)*(self.controller.bpm/self.dir_change))
		
		self.xvel=math.cos(self.direction)*self.speed
		self.yvel=math.sin(self.direction)*self.speed


		if self.controller.player.dead==False and\
			point_distance(self.x,self.y,self.controller.player.x_center,self.controller.player.y_center)<25:
			self.controller.bpm+=self.damage
			self.destroy()


		Bullet.update(self)



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
				self.controller.play_sound(self.controller.shoot_shape)
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


class Targeter(Enemy):
	def init(self):
		self.type=4
		self.color2=(155,155,155)
		self.damage=2
		self.r=0
		self.raduis=50
		self.sides=20
		self.step=0
		#Construct the poly
		self.poly=[]
		for i in range(self.sides):
			self.poly.append(((math.cos(self.r+(i*2*math.pi)/self.sides)),\
				(math.sin(self.r+(i*2*math.pi)/self.sides))))
		self.bbPath=None
		self.poly2=[]


	def update(self,move=True):
		self.step+=1

		self.raduis+=(50-self.raduis)/5.0
		
		#See if we have line of sight to the player
		if move==True:
			collide=False
			x=self.x
			y=self.y
			d=point_direction(self.x,self.y,self.controller.player.x_center,self.controller.player.y_center)+math.pi
			xvel=math.cos(d)*15
			yvel=math.sin(d)*15
			for i in range(50):
				x+=xvel
				y+=yvel

				#pygame.draw.circle(self.controller.screen,(255,255,255),(int(x),int(y)),15)

				if x<0 or x>self.controller.room_width or y<0 or y>self.controller.room_height:
					collide=False
					break
				#Check if collide with player
				if point_distance(x,y,self.controller.player.x_center,self.controller.player.y_center)<24:
					collide=False
					break
				#Collisions
				overlapbbox = (x-15, y-15,x+15, y+15)
				walls = self.controller.wallTree.intersect(overlapbbox)
				for w in walls:
					if w.col_bullet==True and x>w.x and x<w.x+w.w\
					and y>w.y and y<w.y+w.h:
						collide=True
				if collide==True:
					break;
			if collide==False:
				self.r=dir_tron(self.r,d,(0.01)*(self.controller.bpm/120))

				#Fire!
				if self.step%5==0:
					if (dir_tron(self.r,d,math.pi/8)==d or dir_tron(self.r,d,math.pi/8)==d+math.pi*2):
						self.controller.play_sound(self.controller.shoot_spinner-5.0,self.controller.shoot_spinner.frame_rate*random.uniform(0.5,1.0))
						Bullet(self.controller,self ,int(self.x+math.cos(self.r)*self.raduis),int(self.y+math.sin(self.r)*self.raduis),self.damage,self.r,5,self.color)



		#Construct target thing
		self.poly2=[]
		self.poly2.append(
			(math.cos(self.r-(math.pi/16)),
			math.sin(self.r-(math.pi/16))))
		self.poly2.append(
			(math.cos(self.r+(math.pi/16)),
			math.sin(self.r+(math.pi/16))))
		self.poly2.append((0,0))

	def draw(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			#print(l[i][0],l[i][0]*self.raduis)
			l[i][0]=l[i][0]*self.raduis+self.x
			l[i][1]=l[i][1]*self.raduis+self.y
		pygame.draw.polygon(screen,self.color,tuple(l))
		if self.bbPath==None:
			self.bbPath=mplPath.Path(np.array(l))
		l=list(self.poly2)
		for i in range(len(l)):
			l[i]=list(l[i])
			#print(l[i][0],l[i][0]*self.raduis)
			l[i][0]=l[i][0]*self.raduis+self.x
			l[i][1]=l[i][1]*self.raduis+self.y
		pygame.draw.polygon(screen,self.color2,tuple(l))
	def draw_shadow(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			l[i][0]=l[i][0]*self.raduis+5+self.x
			l[i][1]=l[i][1]*self.raduis+5+self.y
		pygame.draw.polygon(screen,(50,50,50),tuple(l))
		

class Spinner(Enemy):
	def init(self):
		self.type=5
		self.color2=(255,255,255)
		self.damage=2
		self.r=0
		self.raduis=50
		self.sides=20
		self.step=0
		#Construct the poly
		self.poly=[]
		for i in range(self.sides):
			self.poly.append(((math.cos(self.r+(i*2*math.pi)/self.sides)),\
				(math.sin(self.r+(i*2*math.pi)/self.sides))))
		self.bbPath=mplPath.Path(np.array(self.poly))
		self.poly2=[]


	def update(self,move=True):
		self.step+=1

		self.raduis+=(50-self.raduis)/5.0
		
		#See if we have line of sight to the player
		if move==True:
			self.r+=math.pi/120
			#Fire!
			if self.step%3==0:
				self.controller.play_sound(self.controller.shoot_spinner-5.0,self.controller.shoot_spinner.frame_rate*random.uniform(0.5,1.0))
				Bullet(self.controller,self ,int(self.x+math.cos(self.r)*self.raduis),int(self.y+math.sin(self.r)*self.raduis),self.damage,self.r,5,self.color)



		#Construct target thing
		self.poly2=[]
		self.poly2.append(
			(math.cos(self.r-(math.pi/16)),
			math.sin(self.r-(math.pi/16))))
		self.poly2.append(
			(math.cos(self.r+(math.pi/16)),
			math.sin(self.r+(math.pi/16))))
		self.poly2.append((0,0))

	def draw(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			#print(l[i][0],l[i][0]*self.raduis)
			l[i][0]=l[i][0]*self.raduis+self.x
			l[i][1]=l[i][1]*self.raduis+self.y
		pygame.draw.polygon(screen,self.color,tuple(l))
		l=list(self.poly2)
		for i in range(len(l)):
			l[i]=list(l[i])
			#print(l[i][0],l[i][0]*self.raduis)
			l[i][0]=l[i][0]*self.raduis+self.x
			l[i][1]=l[i][1]*self.raduis+self.y
		pygame.draw.polygon(screen,self.color2,tuple(l))
	def draw_shadow(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			l[i][0]=l[i][0]*self.raduis+5+self.x
			l[i][1]=l[i][1]*self.raduis+5+self.y
		pygame.draw.polygon(screen,(50,50,50),tuple(l))
		

class Plus(Enemy):
	def init(self):
		self.type=6
		self.damage=2
		self.r=0
		self.raduis=50
		self.sides=20
		self.step=0
		self.fire=0
		#Construct the poly
		self.poly=[(-0.5,1.5),(0.5,1.5),(0.5,0.5),(1.5,0.5),(1.5,-0.5),(0.5,-0.5),\
		(0.5,-1.5),(-0.5,-1.5),(-0.5,-0.5),(-1.5,-0.5),(-1.5,-0.5),(-1.5,0.5),(-0.5,0.5),(-0.5,1.5)]
		self.bbPath=mplPath.Path(np.array(self.poly))


	def update(self,move=True):
		self.raduis+=(50-self.raduis)/5.0
		
		#See if we have line of sight to the player
		if move==True:
			self.step+=1
			self.fire+=self.controller.bpm

			self.r+=math.pi/120

			#Fire!
			if self.fire>1080:
				self.fire-=1080
				self.controller.play_sound(self.controller.shoot_spinner-5.0,self.controller.shoot_spinner.frame_rate*random.uniform(0.5,1.0))
				Bullet(self.controller,self ,int(self.x+math.cos(self.r)*self.raduis*1.5),int(self.y+math.sin(self.r)*self.raduis*1.5),self.damage,self.r,5,self.color)
				Bullet(self.controller,self ,int(self.x+math.cos(self.r+math.pi/2)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi/2)*self.raduis*1.5),self.damage,self.r+math.pi/2,5,self.color)
				Bullet(self.controller,self ,int(self.x+math.cos(self.r+math.pi)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi)*self.raduis*1.5),self.damage,self.r+math.pi,5,self.color)
				Bullet(self.controller,self ,int(self.x+math.cos(self.r+math.pi*3/2)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi*3/2)*self.raduis*1.5),self.damage,self.r+math.pi*3/2,5,self.color)



	def draw(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])

			xy=np.matmul([[math.cos(self.r),-math.sin(self.r)],[math.sin(self.r),math.cos(self.r)]],[l[i][0],l[i][1]])
			xy=np.matmul([[self.raduis,0],[0,self.raduis]],xy)
			l[i][0]=xy[0]+self.x
			l[i][1]=xy[1]+self.y

		self.bbPath=mplPath.Path(np.array(l))
		pygame.draw.polygon(screen,self.color,tuple(l))
	def draw_shadow(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			xy=np.matmul([[math.cos(self.r),-math.sin(self.r)],[math.sin(self.r),math.cos(self.r)]],[l[i][0],l[i][1]])
			xy=np.matmul([[self.raduis,0],[0,self.raduis]],xy)
			l[i][0]=xy[0]+self.x+5
			l[i][1]=xy[1]+self.y+5
		pygame.draw.polygon(screen,(50,50,50),tuple(l))


class Plus2(Enemy):
	def init(self):
		self.type=7
		self.damage=2
		self.r=0
		self.raduis=50
		self.sides=20
		self.step=0
		self.fire=0
		self.fire2=0
		self.fire3=0
		#Construct the poly
		self.poly=[(-0.5,1.5),(0.5,1.5),(0.5,0.5),(1.5,0.5),(1.5,-0.5),(0.5,-0.5),\
		(0.5,-1.5),(-0.5,-1.5),(-0.5,-0.5),(-1.5,-0.5),(-1.5,-0.5),(-1.5,0.5),(-0.5,0.5),(-0.5,1.5)]
		self.bbPath=mplPath.Path(np.array(self.poly))


	def update(self,move=True):
		self.raduis+=(50-self.raduis)/5.0
		
		#See if we have line of sight to the player
		if move==True:
			self.step+=1
			self.fire+=self.controller.bpm

			self.r+=math.pi/120

			#Fire!
			if self.fire>540:
				self.fire-=540
				self.fire2+=1
				if self.fire2>10:
					self.fire2=0
					self.fire3+=1
					if self.fire3>3:
						self.fire3=0
				self.controller.play_sound(self.controller.shoot_spinner-5.0,self.controller.shoot_spinner.frame_rate*random.uniform(0.5,1.0))
				if self.fire3==0:
					Bullet(self.controller,self ,int(self.x+math.cos(self.r)*self.raduis*1.5),int(self.y+math.sin(self.r)*self.raduis*1.5),self.damage,self.r,5,self.color)
				if self.fire3==1:
					Bullet(self.controller,self ,int(self.x+math.cos(self.r+math.pi/2)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi/2)*self.raduis*1.5),self.damage,self.r+math.pi/2,5,self.color)
				if self.fire3==2:
					Bullet(self.controller,self ,int(self.x+math.cos(self.r+math.pi)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi)*self.raduis*1.5),self.damage,self.r+math.pi,5,self.color)
				if self.fire3==3:
					Bullet(self.controller,self ,int(self.x+math.cos(self.r+math.pi*3/2)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi*3/2)*self.raduis*1.5),self.damage,self.r+math.pi*3/2,5,self.color)



	def draw(self,screen):
		l=list(self.poly)
		xy=np.matmul(l,[[-math.sin(self.r),math.cos(self.r)],[math.cos(self.r),math.sin(self.r)]])
		xy=np.matmul(xy,[[self.raduis,0],[0,self.raduis]])
		for i in range(len(l)):
			l[i]=list(l[i])
			l[i][0]=xy[i][0]+self.x
			l[i][1]=xy[i][1]+self.y

		self.bbPath=mplPath.Path(np.array(l))
		pygame.draw.polygon(screen,self.color,tuple(l))
	def draw_shadow(self,screen):
		l=list(self.poly)
		xy=np.matmul(l,[[-math.sin(self.r),math.cos(self.r)],[math.cos(self.r),math.sin(self.r)]])
		xy=np.matmul(xy,[[self.raduis,0],[0,self.raduis]])
		for i in range(len(l)):
			l[i]=list(l[i])
			l[i][0]=xy[i][0]+self.x+5
			l[i][1]=xy[i][1]+self.y+5
		pygame.draw.polygon(screen,(50,50,50),tuple(l))


class Rhombus(Enemy):
	def init(self):
		self.type=8
		self.damage=2
		self.r=0
		self.ro=-999
		self.raduis=50
		self.sides=20
		self.step=0
		self.fire=0
		self.rr=0
		#Construct the poly
		self.poly=[(0,1.5),(1,0),(0,-1.5),(-1,0)]
		self.bbPath=mplPath.Path(np.array(self.poly))


	def update(self,move=True):
		self.raduis+=(50-self.raduis)/5.0
		
		#See if we have line of sight to the player
		if move==True:
			self.step+=1
			self.fire+=self.controller.bpm
			if self.ro==-999:
				self.ro=self.r

			if self.rr==0:
				self.r+=math.pi/120
				if self.r>math.pi/6+self.ro:
					self.rr=1
			if self.rr==1:
				self.r-=math.pi/120
				if self.r<-math.pi/6+self.ro:
					self.rr=0



			#Fire!
			if self.fire>1080*2:
				self.fire-=1080*2
				self.controller.play_sound(self.controller.shoot_spinner-5.0,self.controller.shoot_spinner.frame_rate*random.uniform(0.5,0.75))
				BulletHom(self.controller,self ,int(self.x+math.cos(self.r+math.pi/2)*self.raduis*1.5),int(self.y+math.sin(self.r+math.pi/2)*self.raduis*1.5),self.damage,self.r+math.pi/2,9,(244, 212, 66))
				BulletHom(self.controller,self ,int(self.x+math.cos(self.r-math.pi/2)*self.raduis*1.5),int(self.y+math.sin(self.r-math.pi/2)*self.raduis*1.5),self.damage,self.r-math.pi/2,9,(244, 212, 66))

				


	def draw(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])

			xy=np.matmul([[math.cos(self.r),-math.sin(self.r)],[math.sin(self.r),math.cos(self.r)]],[l[i][0],l[i][1]])
			xy=np.matmul([[self.raduis,0],[0,self.raduis]],xy)
			l[i][0]=xy[0]+self.x
			l[i][1]=xy[1]+self.y

		self.bbPath=mplPath.Path(np.array(l))
		pygame.draw.polygon(screen,self.color,tuple(l))
	def draw_shadow(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			xy=np.matmul([[math.cos(self.r),-math.sin(self.r)],[math.sin(self.r),math.cos(self.r)]],[l[i][0],l[i][1]])
			xy=np.matmul([[self.raduis,0],[0,self.raduis]],xy)
			l[i][0]=xy[0]+self.x+5
			l[i][1]=xy[1]+self.y+5
		pygame.draw.polygon(screen,(50,50,50),tuple(l))


class Trap(Enemy):
	def init(self):
		self.type=9
		self.damage=2
		self.r=0
		self.raduis=50
		self.sides=20
		self.step=0
		self.fire=0
		#Construct the poly
		self.poly=[(-1,0),(1,0),(0.5,1),(-0.5,1)]
		self.bbPath=mplPath.Path(np.array(self.poly))


	def update(self,move=True):
		self.raduis+=(50-self.raduis)/5.0
		
		#See if we have line of sight to the player
		if move==True:
			self.step+=1
			self.fire+=self.controller.bpm
			
			#self.r=dir_tron(self.r,d,(0.01)*(self.controller.bpm/120))

			#Fire!
			if self.fire>1080:
				self.fire=0
				self.raduis+=5
				self.controller.play_sound(self.controller.shoot_spinner-5.0,self.controller.shoot_spinner.frame_rate*0.5)
				b=BulletHom(self.controller,self ,int(self.x+math.cos(self.r+math.pi/2)*self.raduis),int(self.y+math.sin(self.r+math.pi/2)*self.raduis),self.damage,self.r+math.pi/2,random.uniform(5,10),(244, 212, 66))
				b.r=12
				b.dir_change=random.randint(50,90)
				


	def draw(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])

			xy=np.matmul([[math.cos(self.r),-math.sin(self.r)],[math.sin(self.r),math.cos(self.r)]],[l[i][0],l[i][1]])
			xy=np.matmul([[self.raduis,0],[0,self.raduis]],xy)
			l[i][0]=xy[0]+self.x
			l[i][1]=xy[1]+self.y

		self.bbPath=mplPath.Path(np.array(l))
		pygame.draw.polygon(screen,self.color,tuple(l))
	def draw_shadow(self,screen):
		l=list(self.poly)
		for i in range(len(l)):
			l[i]=list(l[i])
			xy=np.matmul([[math.cos(self.r),-math.sin(self.r)],[math.sin(self.r),math.cos(self.r)]],[l[i][0],l[i][1]])
			xy=np.matmul([[self.raduis,0],[0,self.raduis]],xy)
			l[i][0]=xy[0]+self.x+5
			l[i][1]=xy[1]+self.y+5
		pygame.draw.polygon(screen,(50,50,50),tuple(l))


class Boss(Enemy):
	def init(self):
		self.step=0
		self.poly=[(-2,-1),(-2,1),(0,1),(0,1.5),(2.5,0),(0,-1.5),(0,-1),(-2,-1)]
		self.bbPath=mplPath.Path(np.array(self.poly))

	def step(self):
		if move==True:
			self.step+=1

			self.r+=math.pi/120
	def draw(self):
		pass
