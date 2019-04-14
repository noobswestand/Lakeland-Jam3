import pygame,math,os,struct,time
import Wall,Network,Enemy
from pyqtree import Index
from Constants import enemyList,wallList

class Game():
	def __init__(self):
		pygame.init()
		pygame.font.init()
		self.font = pygame.font.SysFont('Comic Sans MS', 15)
		self.resolution=(1280,720)
		self.screen = pygame.display.set_mode(self.resolution)
		self.running = True
		self.clock = pygame.time.Clock()
		#Engine
		self.objs=[]
		self.beat_go=False

		#QuadTree Collisions
		self.wallTree = Index(bbox=(0, 0, 10000, 10000))
		self.walls=[]

		#Loading+Saving
		self.buffer=Network.Buff()

		self.enemies=[]

		self.player_x=500
		self.player_y=500

		self.type=0
		self.type2=0

		self.type_name=[[],[]]
		self.type_name[0]=["Normal","Inverse","Breakable","Breakable2"]
		self.type_name[1]=["Triangle","Rectangle","Pentagon","Hexagon","Targeter","Spinner","Plus","Plus2",\
		"Rhombus","Trap"]

		self.loaded=False

	def run(self):
		while self.running:

			
			for event in pygame.event.get():
				#Closing the game
				if event.type == pygame.QUIT:
						self.running = False
						pygame.quit()
						return 0
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 4:#UP
						if self.type==0:#Wall scroll
							x,y=pygame.mouse.get_pos()
							x=int(math.floor(float(x)/32.0)*32)
							y=int(math.floor(float(y)/32.0)*32)
							self.type2+=1
							if self.type2>=len(self.type_name[0]):
								self.type2=0

						if self.type==1:#Enemies Scroll
							x,y=pygame.mouse.get_pos()
							x=int(math.floor(float(x)/32.0)*32)
							y=int(math.floor(float(y)/32.0)*32)
							rot=False
							for w in self.enemies:
								if w.x==x and w.y==y:
									w.r-=math.pi/16
									w.update(False)
									rot=True
									break
							if rot==False:
								self.type2+=1
								if self.type2>=len(self.type_name[1]):
									self.type2=0


					elif event.button == 5:#DOWN
						if self.type==0:#Wall scroll
							x,y=pygame.mouse.get_pos()
							x=int(math.floor(float(x)/32.0)*32)
							y=int(math.floor(float(y)/32.0)*32)
							self.type2-=1
							if self.type2<0:
								self.type2=len(self.type_name[0])-1

						if self.type==1:#Enemies Scroll
							x,y=pygame.mouse.get_pos()
							x=int(math.floor(float(x)/32.0)*32)
							y=int(math.floor(float(y)/32.0)*32)
							rot=False
							for w in self.enemies:
								if w.x==x and w.y==y:
									w.r+=math.pi/16
									w.update(False)
									rot=True
									break

							if rot==False:
								self.type2-=1
								if self.type2<0:
									self.type2=len(self.type_name[1])-1

			#Change the placement states
			if pygame.key.get_pressed()[pygame.K_1]:
				self.type=0
				self.type2=0
			if pygame.key.get_pressed()[pygame.K_2]:
				self.type=1
				self.type2=0

			#Closing the game
			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				self.running = False
				pygame.quit()
				return 0


			#Loading
			if pygame.key.get_pressed()[pygame.K_LCTRL] and self.loaded==False:
				self.loaded=True
				for w in self.walls:
					w.destroy()
					del w
				del self.walls
				self.walls=[]
				with open("save.data","rb") as file:
					self.buffer.Buffer=file.read()
					a=self.buffer.readshort()
					for i in range(a):#WALLS
						_type=self.buffer.readbyte()
						x=self.buffer.readshort()
						y=self.buffer.readshort()
						w=self.buffer.readshort()
						h=self.buffer.readshort()
						c=[0,0,0]
						c[0]=self.buffer.readbyte()
						c[1]=self.buffer.readbyte()
						c[2]=self.buffer.readbyte()
						wall=None
						wall=wallList[_type](self,x,y,w,h,(c[0],c[1],c[2]))
						wall.done=True
						self.walls.append(wall)
					self.player_x=self.buffer.readshort()
					self.player_y=self.buffer.readshort()
					a=self.buffer.readshort()
					for i in range(a):#ENEMIES
						x=self.buffer.readshort()
						y=self.buffer.readshort()
						_type=self.buffer.readbyte()
						r=self.buffer.readdouble()
						beat=self.buffer.readbyte()
						beatoff=self.buffer.readbyte()
						w=enemyList[_type](self,x,y)
						w.r=r
						w.beat_mod=beat
						w.beat_mod_off=beatoff
						w.update(False)


					
			#Saving
			if pygame.key.get_pressed()[pygame.K_SPACE]:
				try:
					os.remove("save.data")
				except:
					pass
				self.buffer.clearbuffer()
				self.buffer.writeshort(len(self.walls))
				for w in self.walls:
					self.buffer.writebyte(w.type)
					self.buffer.writeshort(w.x)
					self.buffer.writeshort(w.y)
					self.buffer.writeshort(w.w)
					self.buffer.writeshort(w.h)
					self.buffer.writebyte(w.color[0])
					self.buffer.writebyte(w.color[1])
					self.buffer.writebyte(w.color[2])
				self.buffer.writeshort(self.player_x)
				self.buffer.writeshort(self.player_y)
				self.buffer.writeshort(len(self.enemies))
				for w in self.enemies:
					self.buffer.writeshort(w.x)
					self.buffer.writeshort(w.y)
					self.buffer.writebyte(w.type)
					#print("rot",w.r)
					self.buffer.writedouble(float(w.r))

					self.buffer.writebyte(w.beat_mod)
					self.buffer.writebyte(w.beat_mod_off)
				
				types = ''.join(self.buffer.BufferWriteT)
				bstr=struct.pack("="+types,*self.buffer.BufferWrite)
				try:
					with open("save.data",'wb') as file:
						file.write(bstr)
					print("Saved")
				except:
					pass

			###########WALLS###########
			if self.type==0:
				#Add
				if pygame.mouse.get_pressed()[0]==True:
					x,y=pygame.mouse.get_pos()
					x=int(math.floor(float(x)/32.0)*32)
					y=int(math.floor(float(y)/32.0)*32)
					add=True
					for w in self.walls:
						if w.x==x and w.y==y:
							add=False
							break
					if add==True:
						w=wallList[self.type2](self,x,y,32,32)
						w.done=True
						self.walls.append(w)
				#Remove
				if pygame.mouse.get_pressed()[2]==True:
					x,y=pygame.mouse.get_pos()
					x=int(math.floor(float(x)/32.0)*32)
					y=int(math.floor(float(y)/32.0)*32)
					for w in self.walls:
						if w.x==x and w.y==y:
							self.walls.remove(w)
							w.destroy()
							break
				#Move player
				if pygame.mouse.get_pressed()[1]==True:
					x,y=pygame.mouse.get_pos()
					self.player_x=int(math.floor(float(x)/32.0)*32)
					self.player_y=int(math.floor(float(y)/32.0)*32)
			
			###########ENEMIES###########
			if self.type==1:
				#Add
				if pygame.mouse.get_pressed()[0]==True:
					x,y=pygame.mouse.get_pos()
					x=int(math.floor(float(x)/32.0)*32)
					y=int(math.floor(float(y)/32.0)*32)
					add=True
					for w in self.enemies:
						if w.x==x and w.y==y and w.r==0:
							add=False
							break
					if add==True:
						w=enemyList[self.type2](self,x,y)
						w.update(False)
				#Remove
				if pygame.mouse.get_pressed()[2]==True:
					x,y=pygame.mouse.get_pos()
					x=int(math.floor(float(x)/32.0)*32)
					y=int(math.floor(float(y)/32.0)*32)
					for w in self.enemies:
						if w.x==x and w.y==y:
							w.destroy()
							break
			



			#Clear the screen
			pygame.display.flip()
			self.screen.fill((0,0,0))

			#Update the objects
			'''
			for i in self.objs:
				i.update()
			'''

			#Draw the objects
			for i in self.objs:
				i.draw_shadow(self.screen)
			for i in self.objs:
				i.draw(self.screen)

			#PLAYER
			pygame.draw.circle(self.screen,(0, 128, 255),(self.player_x,self.player_y),12)

			#GUI
			if self.type==0:
				textsurface = self.font.render('Walls'+str(
					self.type2)+":"+str(self.type_name[0][self.type2]) + ' PLAYER', False, (255,255,255))
				self.screen.blit(textsurface,(0,0))
			if self.type==1:
				textsurface = self.font.render('Enemies: '+str(self.type2)+":"+str(self.type_name[1][self.type2]), False, (255,255,255))
				self.screen.blit(textsurface,(0,0))


			#Tick 60 frames per second
			self.clock.tick(60)


game=Game()
game.run()