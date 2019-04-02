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

	def destroy(self):
		Obj.Obj.destroy(self)
		self.controller.wallTree.remove(self,self.bbox)

	def draw(self,screen):
		if self.col==True:
			self.r+=(0-self.r)/10.0
			pygame.draw.rect(screen, self.getcolor(), pygame.Rect(self.getx()-int(self.r), self.gety()-int(self.r),\
				self.getw()+int(self.r*2), self.geth()+int(self.r*2)))
		else:
			pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.getx(), self.gety(),\
				self.getw(), self.geth()),1)
	
	
	def draw_shadow(self,screen):
		if self.col==True:
			pygame.draw.rect(screen, (50,50,50), pygame.Rect(self.getx()+5, self.gety()+5, self.getw(), self.geth()))

