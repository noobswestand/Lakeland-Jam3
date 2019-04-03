import pygame,Obj

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

	def destroy(self):
		Obj.Obj.destroy(self)
		self.controller.wallTree.remove(self,self.bbox)
	

class WallNormal(Wall):
	def __init__(self,controller,x,y,w,h,color=(183, 183, 183)):
		Wall.__init__(self,controller,x,y,w,h,color)
		self.type=0
		self.col=True
		self.col_bullet=False

	def collide(self):
		self.done=True
		self.col_bullet=True

	def draw(self,screen):
		if self.done==True:
			self.r+=(0-self.r)/10.0
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
				self.getw()+int(self.r*2), self.geth()+int(self.r*2)))
		else:
			pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()),1)
	def draw_shadow(self,screen):
		if self.done==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))


class WallInverse(Wall):
	def __init__(self,controller,x,y,w,h,color=(50,50,50)):
		Wall.__init__(self,controller,x,y,w,h,color)
		self.type=1
		self.col=True
		self.col_bullet=True
		self.r=0.0

	def collide(self):
		self.col=False
		self.col_bullet=False
		self.done=True
		
	def draw(self,screen):
		if self.col==False:
			self.r+=(-float(self.w)/2.0-self.r)/10.0
			pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
				self.getw()+int(self.r*2), self.geth()+int(self.r*2)),1)
		else:
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()))

	def draw_shadow(self,screen):
		if self.col==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))
