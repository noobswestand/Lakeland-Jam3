import pygame,Obj,Particle,random,math

class Wall(Obj.Obj):
	def __init__(self,controller,x,y,w,h,color=(91, 91, 91)):
		Obj.Obj.__init__(self,controller)
		self.controller=controller
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		self.color=color
		self.bbox=(self.x,self.y,self.x+self.w,self.y+self.h)
		self.solid=True
		self.r=15.0
		self.controller.wallTree.insert(self, self.bbox)#Insert into the quad tree
		self.col=False
		self.done=False
		self.draw_normal=False
		self.controller.screen_update=True

	def destroy(self):
		Obj.Obj.destroy(self)
		self.controller.wallTree.remove(self,self.bbox)

	def hit_bullet(self):
		self.controller.play_sound(self.controller.wall_hit_bullet)
	

class WallNormal(Wall):
	def __init__(self,controller,x,y,w,h,color=(45, 94, 255)):
		Wall.__init__(self,controller,x,y,w,h,color)
		self.type=0
		self.col=True
		self.col_bullet=False
		self.draw_update=60

	def collide(self):
		if self.done==False:
			self.done=True
			self.col_bullet=True
			self.controller.play_sound(self.controller.wall_collide)
			self.controller.screen_update=True
			self.draw_normal=True

	def draw(self,screen):
		if self.done==True:
			self.r+=(0-self.r)/10.0
			self.draw_update-=1
			if self.draw_update<=0:
				self.draw_normal=False
				self.controller.screen_update=True
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
				self.getw()+int(self.r*2), self.geth()+int(self.r*2)))
		else:
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()),1)
	def draw_shadow(self,screen):
		if self.done==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))


class WallInverse(Wall):
	def __init__(self,controller,x,y,w,h,color=(255, 80, 45)):#
		Wall.__init__(self,controller,x,y,w,h,color)
		self.type=1
		self.col=True
		self.col_bullet=True
		self.r=0.0
		self.draw_self=60

	def collide(self):
		if self.col==True:
			self.col=False
			self.col_bullet=False
			self.done=True
			self.controller.play_sound(self.controller.wall_collide)
			self.controller.screen_update=True
			self.draw_normal=True
		
	def draw(self,screen):
		if self.col==False:
			self.r+=(-float(self.w)/2.0-self.r)/10.0
			self.draw_self-=1
			if self.draw_self>0:
				pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
					self.getw()+int(self.r*2), self.geth()+int(self.r*2)),1)
		else:
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()))

	def draw_shadow(self,screen):
		if self.col==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))


class WallBreak(Wall):
	def __init__(self,controller,x,y,w,h,color=(43, 195, 255)):
		Wall.__init__(self,controller,x,y,w,h,color)
		self.type=2
		self.col=True
		self.col_bullet=False
		self.health=0
		self.cooldown=0
		self.draw_update=60

	def collide(self):
		if self.done==False and self.cooldown<=0:
			self.done=True
			self.col_bullet=True
			self.health=5
			self.cooldown=60
			self.controller.play_sound(self.controller.wall_collide)
			self.controller.screen_update=True
			self.draw_normal=True
			self.draw_update=60
		
	def draw(self,screen):
		self.cooldown-=1
		if self.done==True:

			self.draw_update-=1
			if self.draw_update<=0:
				self.draw_normal=False
				self.controller.screen_update=True

			self.r+=(0-self.r)/10.0
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
				self.getw()+int(self.r*2), self.geth()+int(self.r*2)))
		else:
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()),1)
	def draw_shadow(self,screen):
		if self.done==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))

	def hit_bullet(self):
		self.controller.play_sound(self.controller.wall_hit_bullet)
		self.health-=1
		if self.health<=0:
			self.r=15.0
			self.col_bullet=False
			self.done=False
			self.controller.play_sound(self.controller.wall_break)
			for i in range(10):
				p=Particle.Particle(self.controller,self.x+random.uniform(0,self.getw()),self.y+random.uniform(0,self.geth())\
					,5,random.uniform(0,math.pi*2),random.uniform(0,2),self.color,60)



class WallBreak2(Wall):
	def __init__(self,controller,x,y,w,h,color=(255, 146, 45)):
		Wall.__init__(self,controller,x,y,w,h,color)
		self.type=3
		self.col=True
		self.col_bullet=True
		self.health=0
		self.cooldown=0
		self.step=0
		self.colFrame=0
		self.draw_update=60
		self.draw_normal=True

	def collide(self):
		pass
		
	def draw(self,screen):
		self.cooldown-=1
		self.step+=1

		self.draw_update-=1
		if self.draw_update<=0:
			self.draw_normal=False
			self.controller.screen_update=True

		if self.col==True:
			self.r+=(0-self.r)/10.0
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
				self.getw()+int(self.r*2), self.geth()+int(self.r*2)))
		else:
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()),1)
	def draw_shadow(self,screen):
		if self.col==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))

	def hit_bullet(self):

		self.controller.play_sound(self.controller.wall_hit_bullet)
		self.health-=1
		if self.health<=0:
			self.draw_update=60
			self.draw_normal=True
			self.controller.screen_update=True

			self.r=15.0
			self.col_bullet=False
			self.done=True
			self.col=False
			self.controller.play_sound(self.controller.wall_break)
			for i in range(10):
				p=Particle.Particle(self.controller,self.x+random.uniform(0,self.getw()),self.y+random.uniform(0,self.geth())\
					,5,random.uniform(0,math.pi*2),random.uniform(0,2),self.color,60)
