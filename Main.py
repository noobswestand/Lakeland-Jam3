import pygame,Player,Wall,Enemy,random,Network
from pyqtree import Index


class Game():
	def __init__(self):
		#Setup game window
		pygame.init()
		self.resolution=(1280,720)
		self.screen = pygame.display.set_mode(self.resolution)
		self.running = True
		self.clock = pygame.time.Clock()
		self.buffer=Network.Buff()

		#Setup game vars
		self.view_x=0
		self.view_y=0
		self.view_w,self.view_h=self.resolution
		self.room_width,self.room_height=self.resolution

		self.background=(201, 193, 108)

		#Music - all music is 120 BPM
		pygame.mixer.music.load('assets/music/level0.wav')
		pygame.mixer.music.play(-1)

		#Engine
		self.objs=[]
		self.enemies=[]
		#QuadTree Collisions
		self.wallTree = Index(bbox=(0, 0, 10000, 10000))
		self.walls=[]

		#Setup objects
		self.player=Player.Player(self)
		self.player.x,self.player.y=(self.resolution[0]/2,self.resolution[1]/2)


		#Setup game vars
		self.bpm=240
		self.beat=0
		self.beat_go=False
		self.level=1
		self.load_level(self.level)

		


	def load_level(self,lvl):
		for w in self.walls:
			w.destroy()
			del w
		del self.walls
		self.walls=[]
		with open("assets/levels/"+str(lvl)+".data","r") as file:
			self.buffer.Buffer=file.read()
			a=self.buffer.readshort()
			for i in range(a):#WALLS
				x=self.buffer.readshort()
				y=self.buffer.readshort()
				w=self.buffer.readshort()
				h=self.buffer.readshort()
				c=[0,0,0]
				c[0]=self.buffer.readbyte()
				c[1]=self.buffer.readbyte()
				c[2]=self.buffer.readbyte()
				w=Wall.Wall(self,x,y,w,h,(c[0],c[1],c[2]))
				self.walls.append(w)
			self.player.x=self.buffer.readshort()
			self.player.y=self.buffer.readshort()
			self.player.xvel=0
			self.player.yvel=0
			a=self.buffer.readshort()
			for i in range(a):#ENEMIES
				x=self.buffer.readshort()
				y=self.buffer.readshort()
				_type=self.buffer.readbyte()
				r=self.buffer.readshort()
				beat=self.buffer.readbyte()
				beatoff=self.buffer.readbyte()
				if _type==0:
					w=Enemy.Triangle(self,x,y)
				if _type==1:
					w=Enemy.Rectangle(self,x,y)
				if _type==2:
					w=Enemy.Pentagon(self,x,y)
				if _type==3:
					w=Enemy.Hexagon(self,x,y)
				w.r=r
				w.beat_mod=beat
				w.beat_mod_off=beatoff


	def run(self):
		while self.running:

			#Closing the game
			for event in pygame.event.get():
					if event.type == pygame.QUIT:
							self.running = False
							pygame.quit()
							return 0
			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				self.running = False
				pygame.quit()
				return 0


			#Clear the screen
			pygame.display.flip()
			self.screen.fill(self.background)

			#Update the objects
			for i in self.objs:
				i.update()

			#Draw the objects
			for i in self.objs:
				i.draw_shadow(self.screen)
			for i in self.objs:
				i.draw(self.screen)

			#Draw the GUI


			#Game Logic
			self.beat+=self.bpm/60
			if self.beat>=60:
				self.beat-=60
				self.beat_go=True
			else:
				self.beat_go=False

			complete=True
			for w in self.walls:
				if w.col==False:
					complete=False
					break
			if complete==True:
				self.level+=1
				self.load_level(self.level)



			#Tick 60 frames per second
			self.clock.tick(60)
				
game=Game()
game.run()