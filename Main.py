import pygame,Player,Wall,Enemy,random,Network,threading
from pyqtree import Index
from Constants import enemyList,wallList

from pydub import AudioSegment
from pydub.playback import play


class Game():
	def __init__(self):
		#Setup game window
		pygame.init()
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=256)
		self.resolution=(1280,720)
		self.screen = pygame.display.set_mode(self.resolution)
		self.running = True
		self.clock = pygame.time.Clock()
		self.buffer=Network.Buff()

		self.tick=60

		#Setup game vars
		self.view_x=0
		self.view_y=0
		self.view_w,self.view_h=self.resolution
		self.room_width,self.room_height=self.resolution

		self.background=(201, 193, 108)
		self.font = pygame.font.SysFont('Comic Sans MS', 24)
		self.font2 = pygame.font.SysFont('Comic Sans MS', 56)


		#Music - all music is 120 BPM
		pygame.mixer.music.load('assets/music/level0.wav')
		pygame.mixer.music.play(-1)

		#Sounds
		self.channels=[]
		pygame.mixer.set_num_channels(15)
		for i in range(pygame.mixer.get_num_channels()):
			self.channels.append(pygame.mixer.Channel(i))


		self.wall_collide = AudioSegment.from_wav("assets/sound/wallNormal.wav")
		self.wall_break = AudioSegment.from_wav("assets/sound/wallBreak.wav")
		#self.wall_collide=[]
		#self.load_sound(self.wall_collide,'assets/sound/wallNormal.wav')
		#self.wall_break=[]
		#self.load_sound(self.wall_break,'assets/sound/wallBreak.wav')

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
		self.bpm=120
		self.bpm_start=self.bpm
		self.beat=0
		self.beat_go=False
		self.level=5
		#self.load_level(self.level)
		self.death_count=0
		self.win=False

		self.menu=True



	def play_sound(self,sound):
		t = threading.Thread(target=play,args=(sound,))
		t.start()

	def load_level(self,lvl):
		for w in self.walls:
			w.destroy()
		for i in range(15):
			for i in self.objs:
				if i!=self.player:
					if isinstance(i,Enemy.Bullet):
						i.destroy(False)
					else:
						i.destroy()
		filter(lambda a: a != self.player, self.objs)
		del self.walls
		self.walls=[]
		with open("assets/levels/"+str(lvl)+".data","r") as file:
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
				wall=wallList[_type](self,x,y,w,h)#,(c[0],c[1],c[2])
				self.walls.append(wall)
			self.player.x=self.buffer.readshort()
			self.player.y=self.buffer.readshort()
			self.player.xvel=0
			self.player.yvel=0
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

	def draw_death(self):
		surface=pygame.Surface((self.room_width,self.room_height))
		surface.set_alpha(128)
		pygame.draw.rect(surface,(0,0,0),(0,0,self.room_width,self.room_height))
		textsurface = self.font2.render("Your heart exploded", False, (255,255,255))
		textsurface2 = self.font2.render("Your heart exploded", False, (0,0,0))
		text_rect  = textsurface.get_rect(center=(self.room_width/2,self.room_height/2))
		text_rect2  = textsurface2.get_rect(center=(self.room_width/2-2,self.room_height/2-2))

		textsurface3 = self.font.render("Press any key to continue", False, (255,255,255))
		textsurface4 = self.font.render("Press any key to continue", False, (0,0,0))
		text_rect3  = textsurface3.get_rect(center=(self.room_width/2,self.room_height/2+50))
		text_rect4  = textsurface4.get_rect(center=(self.room_width/2+2,self.room_height/2+50+2))

		w=textsurface.get_rect().width
		self.screen.blit(surface, (0,0))
		self.screen.blit(textsurface2,text_rect)
		self.screen.blit(textsurface,text_rect2)
		self.screen.blit(textsurface4,text_rect4)
		self.screen.blit(textsurface3,text_rect3)

		pressed = pygame.key.get_pressed()
		if True in pressed:
			self.player.dead=False
			self.player.create()
			self.bpm=self.bpm_start
			self.load_level(self.level)
			self.tick=60
			self.death_count+=1

	def draw_win(self):
		surface=pygame.Surface((self.room_width,self.room_height))
		surface.set_alpha(128)
		pygame.draw.rect(surface,(0,0,0),(0,0,self.room_width,self.room_height))
		self.screen.blit(surface, (0,0))


		textsurface = self.font2.render("Your heart survived.  You win", False, (255,255,255))
		textsurface2 = self.font2.render("Your heart survived.  You win", False, (0,0,0))
		text_rect  = textsurface.get_rect(center=(self.room_width/2,self.room_height/2))
		text_rect2  = textsurface2.get_rect(center=(self.room_width/2-2,self.room_height/2-2))
		self.screen.blit(textsurface2,text_rect)
		self.screen.blit(textsurface,text_rect2)

		if self.death_count>0:
			textsurface3 = self.font.render("(not really - you died "+str(self.death_count)+" times)", False, (255,255,255))
			textsurface4 = self.font.render("(not really - you died "+str(self.death_count)+" times)", False, (0,0,0))
			text_rect3  = textsurface3.get_rect(center=(self.room_width/2,self.room_height/2+50))
			text_rect4  = textsurface4.get_rect(center=(self.room_width/2-2,self.room_height/2+50-2))
			self.screen.blit(textsurface4,text_rect4)
			self.screen.blit(textsurface3,text_rect3)

		textsurface3 = self.font.render("Final resting heart beat: "+str(self.bpm), False, (255,255,255))
		textsurface4 = self.font.render("Final resting heart beat: "+str(self.bpm), False, (0,0,0))
		text_rect3  = textsurface3.get_rect(center=(self.room_width/2,self.room_height/2+100))
		text_rect4  = textsurface4.get_rect(center=(self.room_width/2+2,self.room_height/2+100+2))
		self.screen.blit(textsurface4,text_rect4)
		self.screen.blit(textsurface3,text_rect3)

	def draw_menu(self):
		if self.player.dead==False:#Deactivate the player
			self.player.destroy(False)
			self.dead=True

		surface=pygame.Surface((self.room_width,self.room_height))
		surface.set_alpha(128)
		pygame.draw.rect(surface,(0,0,0),(0,0,self.room_width,self.room_height))
		self.screen.blit(surface, (0,0))


		#Play button
		ww=150
		hh=60
		xx=(self.room_width/2)-ww/2
		yy=(self.room_height/2)-hh/2
		pygame.draw.rect(self.screen,(155,155,155),(xx,yy,ww,hh))

		text = self.font.render("Play", False, (255,255,255))
		text_rect  = text.get_rect(center=(self.room_width/2+2,self.room_height/2))
		self.screen.blit(text, text_rect)

		xy=pygame.mouse.get_pos()
		if xy[0]>xx and xy[1]>yy and xy[0]<xx+ww and xy[1]<yy+hh:
			pygame.draw.rect(self.screen,(255,255,255),(xx,yy,ww,hh),3)
			if pygame.mouse.get_pressed()[0]==True:
				self.player.dead=False
				self.player.create()
				self.bpm=self.bpm_start
				self.load_level(self.level)
				self.tick=60
				self.menu=False


		#Quit button
		ww=100
		hh=60
		xx=(self.room_width/2)-ww/2
		yy=(self.room_height/2)-hh/2+100
		pygame.draw.rect(self.screen,(155,155,155),(xx,yy,ww,hh))
		
		text = self.font.render("Quit", False, (255,255,255))
		text_rect  = text.get_rect(center=(self.room_width/2+2,self.room_height/2+100))
		self.screen.blit(text, text_rect)

		if xy[0]>xx and xy[1]>yy and xy[0]<xx+ww and xy[1]<yy+hh:
			pygame.draw.rect(self.screen,(255,255,255),(xx,yy,ww,hh),3)
			if pygame.mouse.get_pressed()[0]==True:
				self.running = False
				pygame.quit()

		




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
			if pygame.key.get_pressed()[pygame.K_a]:
				self.play_sound(self.wall_break)


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
			textsurface = self.font.render("BPM: "+str(self.bpm), False, (255,255,255))
			textsurface2 = self.font.render("BPM: "+str(self.bpm), False, (0,0,0))
			self.screen.blit(textsurface2,(2,2))
			self.screen.blit(textsurface,(0,0))


			if self.menu==True:
				self.draw_menu()

			if self.player.dead==True and self.menu==False:
				self.draw_death()
			if self.win==True:
				self.draw_win()


			

			#Game Logic
			self.beat+=self.bpm/60
			if self.beat>=60:
				self.beat-=60
				self.beat_go=True
			else:
				self.beat_go=False

			#Check if you completed the level
			complete=True
			if self.win==True:
				complete=False
			if self.menu==True:
				complete=False
			for w in self.walls:
				if w.done==False:
					complete=False
					break
			if complete==True:#Load the next one
				self.level+=1
				try:
					self.load_level(self.level)
				except:
					self.win=True



			#Tick 60 frames per second
			self.clock.tick(self.tick)
				
game=Game()
game.run()