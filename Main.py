import pygame,Player,Wall,Enemy,random,Network,threading
from pyqtree import Index
from Constants import enemyList,wallList

from pydub import AudioSegment
from pydub.playback import play


class Game():
	def __init__(self):
		#Setup game window
		pygame.init()
		pygame.display.init()
		self.resolution=(1280,720)
		self.screen = pygame.display.set_mode(self.resolution)
		self.screen_slow = pygame.Surface(self.resolution)
		self.screen_slow_shadow = pygame.Surface(self.resolution)
		self.screen_slow.set_colorkey((0,0,0))
		self.screen_slow_shadow.set_colorkey((0,0,0))
		self.screen_update=False

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
		pygame.mixer.music.load('assets/music/level.mp3')

		#Sounds
		self.channels=[]
		pygame.mixer.set_num_channels(15)
		for i in range(pygame.mixer.get_num_channels()):
			self.channels.append(pygame.mixer.Channel(i))

		self.wall_collide = AudioSegment.from_wav("assets/sound/wallNormal.wav")
		self.wall_break = AudioSegment.from_wav("assets/sound/wallBreak.wav")
		self.wall_hit = AudioSegment.from_wav("assets/sound/wallHit.wav")
		self.wall_hit_bullet = AudioSegment.from_wav("assets/sound/wallBulletHit.wav")

		self.shoot_spinner= AudioSegment.from_wav("assets/sound/shoot_spinner.wav")
		self.shoot_shape = AudioSegment.from_wav("assets/sound/shoot_shape.wav")

		#Engine
		self.objs=[]
		self.enemies=[]
		#QuadTree Collisions
		self.wallTree = Index(bbox=(0, 0, 10000, 10000))
		self.walls=[]

		#GUI
		self.gui_heart=[(0,1),(0.5,1.25),(1,1),(1.15,0.5),(1.1,0.5),(0,-1),\
			(0,-1),(-1.1,0.5),(-1.15,0.5),(-1,1),(-0.5,1.25),(0,1)]
		self.gui_heart_size=1


		#Setup objects
		self.player=Player.Player(self)
		self.player.x,self.player.y=(self.resolution[0]/2,self.resolution[1]/2)


		#Setup game vars
		self.bpm=120
		self.bpm_start=self.bpm
		self.beat=0
		self.beat_go=False
		self.level=0
		self.level_begin=False
		self.level_final=8
		#self.load_level(self.level)
		self.death_count=0
		self.win=False

		self.menu=True



	def play_sound(self,sound,frame_rate=None):
		if frame_rate==None:
			frame_rate=sound.frame_rate
		new_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': int(frame_rate)})
		t = threading.Thread(target=play,args=(new_sound,))
		t.start()

	def load_level(self,lvl):
		self.level_begin=True

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
		with open("assets/levels/"+str(lvl)+".data","rb") as file:
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
			self.player.x_center=self.player.x
			self.player.y=self.buffer.readshort()
			self.player.y_center=self.player.y
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
				pygame.mixer.music.play(-1)


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

	def draw_start(self):
		surface=pygame.Surface((self.room_width,self.room_height))
		surface.set_alpha(128)
		pygame.draw.rect(surface,(0,0,0),(0,0,self.room_width,self.room_height))
		self.screen.blit(surface, (0,0))

		surface2=pygame.Surface((100,100))
		surface2.set_colorkey((0,0,0))
		surface2.set_alpha(164)
		pygame.draw.circle(surface2,(255,255,255),(50,50),45)
		self.screen.blit(surface2, (self.player.x_center-50,self.player.y_center-50))

		text = self.font.render("Put mouse here ->", False, (255,255,255))
		self.screen.blit(text, (self.player.x_center-250,self.player.y_center-15))
		
		xy=pygame.mouse.get_pos()
		if ((xy[0]-self.player.x_center)**2 + (xy[1]-self.player.y_center)**2)**0.5<50:
			self.level_begin=False



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


			###################Clear the screen##################
			pygame.display.flip()
			self.screen.fill(self.background)

			
			if self.level_begin==False:

				###################Update the objects##################
				for i in self.objs:
					i.update()

				###################Draw the objects##################
				for i in self.objs:
					if i.draw_normal==True:
						i.draw_shadow(self.screen)

				if self.win==False:
					self.screen.blit(self.screen_slow_shadow,(0,0))

				for i in self.objs:
					if i.draw_normal==True:
						i.draw(self.screen)

				###################DRAW NON UPDATING OBJECTS##################
				
				if self.screen_update==True:
					self.screen_slow.fill(pygame.Color(0,0,0,0))
					self.screen_slow_shadow.fill(pygame.Color(0,0,0,0))

					for i in self.objs:
						if i.draw_normal==False:
							i.draw_shadow(self.screen_slow_shadow)
					for i in self.objs:
						if i.draw_normal==False:
							i.draw(self.screen_slow)
					self.screen_update=False
				if self.win==False:
					self.screen.blit(self.screen_slow,(0,0))
				
				

			##################Draw the GUI##################
			textsurface = self.font.render("BPM: "+str(self.bpm), False, (255,255,255))
			textsurface2 = self.font.render("BPM: "+str(self.bpm), False, (0,0,0))
			self.screen.blit(textsurface2,(2,2))
			self.screen.blit(textsurface,(0,0))

			if self.beat_go==True:
				self.gui_heart_size+=1

			self.gui_heart_size+=(1.0-self.gui_heart_size)/5.0
			l=list(self.gui_heart)
			for i in range(len(l)):
				l[i]=list(l[i])
				l[i][0]=l[i][0]*25*self.gui_heart_size+75
				l[i][1]=l[i][1]*-25*self.gui_heart_size+75
			pygame.draw.polygon(self.screen,(0,0,0),tuple(l))
			l=list(self.gui_heart)
			for i in range(len(l)):
				l[i]=list(l[i])
				l[i][0]=l[i][0]*25*self.gui_heart_size*((float(480-self.bpm)/360.0))+75
				l[i][1]=l[i][1]*-25*self.gui_heart_size*((float(480-self.bpm)/360.0))+75
			pygame.draw.polygon(self.screen,(255,0,0),tuple(l))

			#Restart button
			if self.menu==False and self.player.dead==False and self.win==False:
				xy=pygame.mouse.get_pos()
				ww=150
				hh=25
				xx=(self.room_width)-ww-15
				yy=(self.room_height)-hh-15
				pygame.draw.rect(self.screen,(155,155,155),(xx,yy,ww,hh))
				
				text = self.font.render("Restart Level", False, (255,255,255))
				text_rect  = text.get_rect(center=(self.room_width-ww/2-15,self.room_height-hh-5))
				self.screen.blit(text, text_rect)

				if xy[0]>xx and xy[1]>yy and xy[0]<xx+ww and xy[1]<yy+hh:
					pygame.draw.rect(self.screen,(255,255,255),(xx,yy,ww,hh),3)
					if pygame.mouse.get_pressed()[0]==True:
						self.load_level(self.level)


			if self.level_begin==True:
				self.draw_start()

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
			if self.level==self.level_final:
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