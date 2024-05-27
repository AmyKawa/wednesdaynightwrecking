#prior to may 26th - sorry the file was corrupted, uploaded version is here now
# Block 4
# Amy Lee
# Game Design 12 Final Project

import pygame, sys, time, random, gc
from pygame.locals import *

# Setup stuff
screen = pygame.display.set_mode((1400, 830))
bgscreen = pygame.display.set_mode((1400, 830))
clock = pygame.time.Clock()
pygame.mixer.pre_init()
pygame.init()
pygame.event.set_allowed([QUIT])
pygame.display.set_caption('rhythmcore')

global curr_offset, activenotes, curr_value, tick, combo
combo = 0
acc_numerator = 0
curr_value = ''

def text(message, x, y, fontsize, r, g, b):
	# Pre: Reads message, the coordinates, fontsize and colors through rgb values
	# Post: Displays text on the Pygame window according to the parameters above
	font = pygame.font.Font('assets\\misc\\OMORI_GAME2.ttf', int(fontsize))
	string = font.render(message, False, (r,g,b))
	bgscreen.blit(string, (x, y))

def dialogue(message, name, ver, option1, option2):
	# Pre: Everytime u click on a title screen object
	# Post: It opens a dialogue box. there are 3 types, speaking, choice, and info. Speaking is when u click on a living being, choice is for objects that grant u a choice (ie leave game or stay)
	# and info is just a box with text on it, no choice or dialogue
	if ver == 'speaking':
		screen.blit(dialoguebox, (175, 320))
		text(name, 195, 500, 40, 255, 255, 255)
		text('(Press escape to OK)', 955, 780, 30, 255, 255, 255)
	if ver == 'choice':
		screen.blit(optionbox, (175, 320))
		text(option1, 880, 440, 40, 255, 255, 255)
		text(option2, 880, 470, 40, 255, 255, 255)
	if ver == 'info':
		screen.blit(infobox, (175, 320))
		text('(Press escape to OK)', 955, 780, 30, 255, 255, 255)
		if name == 'lightbulb':
			text('It\'s pitch black inside, you can\'t see a thing.', 195, 650, 50, 255, 255, 255)
	text(message, 195, 600, 50, 255, 255, 255)
		
	
def get_metadata(chart):
	# Pre: When a user mouses over a chart in menu
	# Post: Display metadata of a song as well as charter credits
	global metadata
	metadata = open('game\\' + chart + '.txt').read().replace('\n', '.').split('-')
	metadata = list(metadata[0].split('.'))
	metadata.pop(8)
	
	thumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\' + chart + '_thumb.png').convert_alpha()
	text(('Difficulty: ' + metadata[7]), 75, 400, 75, 255, 255, 255)
	text((metadata[3]), 30, 500, 50, 255, 255, 255)
	text(('By ' + metadata[2]), 30, 550, 50, 255, 255, 255)
	text(('Charted by ' + metadata[4]), 30, 600, 50, 255, 255, 255)
	text((metadata[5] + ', ' + metadata[6]), 30, 650, 50, 255, 255, 255)
	screen.blit(thumb, (100, 150))

class button:
	def __init__(self, text, x, y, w, h, size):
		# Pre: Reads the values that it's given in brackets
		# Post: Creates a button of those given values (position, size, text)
		self.rect = pygame.Rect(x, y, w, h)
		self.text = text
		self.size = size
		# ~ self.x_offset = x_offset
		self.mouse = False
		self.clicked = False
		self.font = pygame.font.Font('assets\\misc\\OMORI_GAME2.ttf', int(h))

	def draw(self):
		# Pre: Reads created button size, position and text
		# Post: Draws the button on the Pygame screen, also deals with mouseover display to change color when hovered over
		if self.mouse == True:
			get_metadata(self.text)
			#self.letter = self.font.render(self.text, True, (0,0,0))
			pygame.draw.rect(screen, (255, 255, 255), self.rect, 0, 15, 15)
			#screen.blit(self.letter, (self.rect.x, self.rect.y-2))
		else:
			#self.letter = self.font.render(self.text, True, (0, 0, 0))
			pygame.draw.rect(screen, (255,255,255), self.rect, 0, 15, 15)
			#screen.blit(self.letter, (self.rect.x, self.rect.y-2))

	def mouseover(self):
		# Pre: Gets the x and y coordinates of the mouse cursor
		# Post: If the mouse is on a coordinate where a button is, tells the code that the button has been moused over
		x , y = pygame.mouse.get_pos()
		if x >= self.rect.x and x < self.rect.x + self.size and y > self.rect.y and y < self.rect.y + self.size:
			self.mouse = True
		else:
			self.mouse = False
	
	def buttonclicked(self):
		global keydelay
		# Pre: Determines if the mouse button is down and if it's over a button
		# Post: Adds the letter/word value it clicked on to the list of either guessed letters or another variable to detect word
		global keydelay, sButtonInput
		pos = pygame.mouse.get_pos()
		letterclicked = 'placeholder'
		if self.rect.collidepoint(pos):
			self.mouse = True
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:# and keydelay > 10:
				self.clicked = True
				sButtonInput = self.text
				keydelay = 0
				print (sButtonInput)
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False
		else:
			self.mouse = False

class note:
	def __init__(self, lane, startms):
		# Pre: Creating a new note in the chart
		# Post: Grabs information from .txt file and turns it into a tuple that my code can interpret
		self.startms = startms
		if lane == 64:
			self.x = 475
		elif lane == 192:
			self.x = 600
		elif lane == 320:
			self.x = 725
		elif lane == 448:
			self.x = 850
		
		self.y = -336
		self.complete = False
		self.fall_too_far = False
	
	global accuracies
	# Pre (all 4 hit functions): When the player hits one of their keybinds
	# Post (all 4 hit functions): Looks at offset it's supposed to be played at (super perfect) and gets current offset (ms) that it's at currently, subtracts it to figure out accuracy depending on how
	# close the player is to the real offset
	def hitD(self):
		global acc_numerator, misscounter, curr_value, tick, combo
		value = ''
		try:
			if len(lane1) > 0:
				if int(lane1[0][1]) - curr_offset <= 120 and int(lane1[0][1]) - curr_offset >= -80:
					if int(lane1[0][1]) - curr_offset <= 120 and int(lane1[0][1]) - curr_offset >= 81 or int(lane1[0][1]) - curr_offset >= -80 and int(lane1[0][1]) - curr_offset <= -61:
						value = 'okay'
						acc_numerator += 0.5
					elif int(lane1[0][1]) - curr_offset <= 80 and int(lane1[0][1]) - curr_offset >= 41 or int(lane1[0][1]) - curr_offset >= -60 and int(lane1[0][1]) - curr_offset <= -41:
						value = 'great'
						acc_numerator += 0.75
					elif int(lane1[0][1]) - curr_offset <= 40 and int(lane1[0][1]) - curr_offset >= -40:
						value = 'perfect'
						acc_numerator += 1.0
					pygame.mixer.Sound.play(hitnormal)
					curr_value = value
					tick = 0
					combo += 1
					accuracies.append(value)
					lane1.pop(0)
					self.complete = True
		except:
			print ('hitD: list empty')

	def hitF(self):
		global acc_numerator, misscounter, curr_value, tick, combo
		value = ''
		try:
			if len(lane2) > 0:
				if int(lane2[0][1]) - curr_offset <= 120 and int(lane2[0][1]) - curr_offset >= -80:
					if int(lane2[0][1]) - curr_offset <= 120 and int(lane2[0][1]) - curr_offset >= 81 or int(lane2[0][1]) - curr_offset >= -80 and int(lane2[0][1]) - curr_offset <= -61:
						value = 'okay'
						acc_numerator += 0.5
					elif int(lane2[0][1]) - curr_offset <= 80 and int(lane2[0][1]) - curr_offset >= 41 or int(lane2[0][1]) - curr_offset >= -60 and int(lane2[0][1]) - curr_offset <= -41:
						value = 'great'
						acc_numerator += 0.75
					elif int(lane2[0][1]) - curr_offset <= 40 and int(lane2[0][1]) - curr_offset >= -40:
						value = 'perfect'
						acc_numerator += 1.0
					pygame.mixer.Sound.play(hitnormal)
					accuracies.append(value)
					curr_value = value
					tick = 0
					combo += 1
					lane2.pop(0)
					self.complete = True
		except:
			print ('hitF: list empty')
		
	def hitJ(self):
		global acc_numerator, misscounter, curr_value, tick, combo
		value = ''
		try:
			if len(lane3) > 0:
				if int(lane3[0][1]) - curr_offset <= 120 and int(lane3[0][1]) - curr_offset >= -80:
					if int(lane3[0][1]) - curr_offset <= 120 and int(lane3[0][1]) - curr_offset >= 81 or int(lane3[0][1]) - curr_offset >= -80 and int(lane3[0][1]) - curr_offset <= -61:
						value = 'okay'
						acc_numerator += 0.5
					elif int(lane3[0][1]) - curr_offset <= 80 and int(lane3[0][1]) - curr_offset >= 41 or int(lane3[0][1]) - curr_offset >= -60 and int(lane3[0][1]) - curr_offset <= -41:
						value = 'great'
						acc_numerator += 0.75
					elif int(lane3[0][1]) - curr_offset <= 40 and int(lane3[0][1]) - curr_offset >= -40:
						value = 'perfect'
						acc_numerator += 1.0
					pygame.mixer.Sound.play(hitnormal)
					accuracies.append(value)
					curr_value = value
					tick = 0
					combo += 1
					lane3.pop(0)
					self.complete = True
		except:
			print ('hitJ: list empty')

	def hitK(self):
		global acc_numerator, misscounter, curr_value, tick, combo
		value = ''
		try:
			if len(lane4) > 0:
				if int(lane4[0][1]) - curr_offset <= 120 and int(lane4[0][1]) - curr_offset >= -80:
					if int(lane4[0][1]) - curr_offset <= 120 and int(lane4[0][1]) - curr_offset >= 81 or int(lane4[0][1]) - curr_offset >= -80 and int(lane4[0][1]) - curr_offset <= -61:
						value = 'okay'
						acc_numerator += 0.5
					elif int(lane4[0][1]) - curr_offset <= 80 and int(lane4[0][1]) - curr_offset >= 41 or int(lane4[0][1]) - curr_offset >= -60 and int(lane4[0][1]) - curr_offset <= -41:
						value = 'great'
						acc_numerator += 0.75
					elif int(lane4[0][1]) - curr_offset <= 40 and int(lane4[0][1]) - curr_offset >= -40:
						value = 'perfect'
						acc_numerator += 1.0
					pygame.mixer.Sound.play(hitnormal)
					accuracies.append(value)
					curr_value = value
					tick = 0
					combo += 1
					lane4.pop(0)
					self.complete = True
		except:
			print ('hitK: list empty')
		
	def fall(self, y):
		# Pre: As the game is playing
		# Post: notes will fall from the top to the bottom of the screen until it goes too low, then deletes itself
		global misscounter
		self.y += y
		if self.x == 475:
			bgscreen.blit(leftarrow, (self.x, self.y))
		if self.x == 600:
			bgscreen.blit(uparrow, (self.x, self.y))
		if self.x == 725:
			bgscreen.blit(downarrow, (self.x, self.y))
		if self.x == 850:
			bgscreen.blit(rightarrow, (self.x, self.y))
		
		if self.y > 750:
			self.fall_too_far = True
				
	# Pre (all 4 miss functions): Always running while a game is in session
	# Post (all 4 miss functions): If the offset differnce between actual offset and current offset, it counts as a miss (the player didn't hit the note in time). Note will delete itself to reduce lag
	def checkmissD(self):
		global misscounter, curr_value, tick, combo
		if len(lane1) > 0:
			if int(lane1[0][1]) - curr_offset < -80:
				lane1.pop(0)
				curr_value = 'miss'
				tick = 0
				combo = 0
				misscounter += 1
				self.complete = True
	
	def checkmissF(self):
		global misscounter, curr_value, tick, combo
		if len(lane2) > 0:
			if int(lane2[0][1]) - curr_offset < -80:
				lane2.pop(0)
				curr_value = 'miss'
				tick = 0
				combo = 0
				misscounter += 1
				self.complete = True
	
	def checkmissJ(self):
		global misscounter, curr_value, tick, combo
		if len(lane3) > 0:
			if int(lane3[0][1]) - curr_offset < -80:
				lane3.pop(0)
				curr_value = 'miss'
				tick = 0
				combo = 0
				misscounter += 1
				self.complete = True
	
	def checkmissK(self):
		global misscounter, curr_value, tick, combo
		if len(lane4) > 0:
			if int(lane4[0][1]) - curr_offset < -80:
				lane4.pop(0)
				curr_value = 'miss'
				tick = 0
				combo = 0
				misscounter += 1
				self.complete = True
			
class animate:
	def __init__(self, basename, x, y, scalex, scaley, framemult, framecount, extension, alpha):
		# Pre: Reads parameters entered by user
		# Post: Creates an animation with the correct images and frames
		
		# --Doesn't limit how many frames you use (before i limited it to 3), creates the animation and appends it to a list--
		# --framemult will append the exact same image x amount of times to prevent the animation from happening so fast u can't even see it--
		self.x = x
		self.y = y
		self.framemult = framemult
		pngs = []
		for x in range(framecount):
			pngs.append('assets\\images\\ui\\twinkle\\'+ basename + ' (' + str(x+1) + ').' + extension)
		self.animation = []
		self.frame = 0
		for frame in pngs:
			# ~ for x in range(framemult):
			yes = pygame.transform.scale(pygame.image.load(frame).convert_alpha(), (scalex, scaley))
			yes.set_alpha(alpha)
			self.animation.append(yes)

	def execute(self):#, x, y):
		global tick
		# Pre: Takes information from the __init__ function
		# Post: Displays the animation at the correct x and y coordinates with that information (such as images)
		bgscreen.blit(self.animation[self.frame],(self.x, self.y))
		if tick % self.framemult == 0:
			self.frame += 1
		if self.frame == len(self.animation):
			self.frame = 0

class whitespace: 
	def __init__(self, furniture, x, endx, y, endy):
		# Pre: Start game
		# Post: Creates all the objects you see in the title screen
		if furniture == 'door':
			self.regular = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\door.png').convert_alpha(), (100, 125))
			self.hovered = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\door.png').convert_alpha(), (150, 175))
		elif furniture == 'tissue':
			self.regular = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\tissuebox.png').convert_alpha(), (130,120))
			self.hovered = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\tissuebox.png').convert_alpha(), (180,170))
		elif furniture == 'laptop':
			self.regular = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\laptop.png').convert_alpha(), (110,100))
			self.hovered = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\laptop.png').convert_alpha(), (160,150))
		elif furniture == 'sketchbook':
			self.regular = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\sketchbook.png').convert_alpha(), (100, 90))
			self.hovered = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\sketchbook.png').convert_alpha(), (150, 140))
		elif furniture == 'cat':
			self.regular = animate('mewo', 200, 600, 200, 150, 35, 2, 'png', 2000)
		elif furniture == 'lightbulb':
			self.regular = animate('lightbulb', 800, -50, 150, 400, 7, 3, 'png', 2000)
		
		self.type = furniture
		self.x = x
		self.endx = endx
		self.y = y
		self.endy = endy
		self.mouse = False
		
	def hover(self):
		# Pre: Gets the x and y coordinates of the mouse cursor
		# Post: If the mouse is on a coordinate where a button is, tells the code that the button has been moused over
		x , y = pygame.mouse.get_pos()
		if self.type in {'door', 'tissue', 'laptop', 'sketchbook'}:
			if x in range(self.x, self.endx) and y in range(self.y, self.endy):
				self.mouse = True
			else:
				self.mouse = False
		else:
			if self.type == 'cat':
				if x in range(self.x, self.endx + 75) and y in range(self.y+10, self.endy+10):
					self.mouse = True
				else:
					self.mouse = False
			elif self.type == 'lightbulb':
				if x in range(self.x+20, self.endx+20) and y in range(self.y+250, self.endy+275):
					self.mouse = True
				else:
					self.mouse = False
		
	def clicked(self):
		# Pre: Hovering over and object and clicking on it
		# Post: Sets the corresponding clicked variable to True, which indicates an object has been clicked
		global sketchbookclicked, doorclicked, laptopclicked, catclicked, lightbulbclicked, tissueclicked, sketchbook_page, tick, mewowowo
		if self.mouse == True and pygame.mouse.get_pressed()[0] == 1 and keydelay > 10:
			if self.type == 'cat':
				pygame.mixer.Sound.play(meowing_sound)
			else:
				pygame.mixer.Sound.play(select)
			if self.type == 'door':
				doorclicked = True
			elif self.type == 'laptop':
				laptopclicked = True
			elif self.type == 'cat':
				tick = 0
				if tick < 1 and catclicked == False:
					mewowowo = random.choice(mewo_dialogue)
				catclicked = True
			elif self.type == 'lightbulb':
				lightbulbclicked = True
			elif self.type == 'tissue':
				tissueclicked = True
			elif self.type == 'sketchbook':
				sketchbook_page = 0
				sketchbookclicked = True
	
	def draw(self):
		# Pre: Start game
		# Post: Draws the objects on the menu. If it's being hovered over, make it bigger slightly
		if self.type in {'door', 'tissue', 'laptop', 'sketchbook'}:
			if self.mouse == True:
				screen.blit(self.hovered, (self.x - 20, self.y - 20))
			else:
				screen.blit(self.regular, (self.x, self.y))
		else:
			self.regular.execute()
	
def loadmap(chart):
	# Pre: When the player clicks on a song to play
	# Post: Loads map with corresponding text file and splits data into necessary lists for gameplay
	global real_REAL_mapdata, curr_song

	mapdata = open('game\\' + chart + '.txt').read().replace('\n', '.').split('-')
	mapdata = list(mapdata[1].split('.'))

	mapdata.pop(0)
	mapdata.pop(0)

	real_mapdata = []
	real_REAL_mapdata = []

	for thingy in mapdata:
		real_mapdata.append(thingy.split(','))

	for yes in real_mapdata:
		real_REAL_mapdata.append(yes)

	global lane1, lane2, lane3, lane4

	lane1 = []
	lane2 = []
	lane3 = []
	lane4 = []
	# Append everything into 4 separate lanes, that way each individual lane can be evaluated for more accuracy
	for datas in real_REAL_mapdata:
		if int(datas[0]) == 64:
			lane1.append(datas)
		if int(datas[0]) == 192:
			lane2.append(datas)
		if int(datas[0]) == 320:
			lane3.append(datas)
		if int(datas[0]) == 448:
			lane4.append(datas)

def buttondisplay(button):
	# Pre: Reads button that user entered
	# Post: Draws the button on screen and adds its mouseover and buttonclicked properties
	button.draw()
	button.mouseover()
	button.buttonclicked()

def list_buttondisplay(buttonlist):
	# Pre: Reads list that user entered
	# Post: Draws all buttons in the list on screen and adds its mouseover and buttonclicked properties
	for button in range(len(buttonlist)):
		buttonlist[button].draw()
		buttonlist[button].mouseover()
		buttonlist[button].buttonclicked()

def create_buttons():
	# Pre: Before the game starts
	# Post: Creates all buttons in the game
	global songbuttons_1, how2playbutton
	songlist = ['uwa-so-holiday', 'sleepwalking', 'rhythm-hell', 'push-and-shove', 'luminescence', 'sing-sing-red-indigo', 'bison-charge', 'attractor-dimension', 'what']
	songbuttons_1 = []
	buttonx = 550
	buttony = 10
	for song in songlist:
		currkey = (button(song, buttonx, buttony, 200, 200, 200))
		songbuttons_1.append(currkey)
		buttonx += 300
		if song == 'rhythm-hell':
			buttonx = 550
			buttony = 310
		if song == 'sing-sing-red-indigo':
			buttonx = 550
			buttony = 610
	
	how2playbutton = button('instructions', 900, 700, 100, 50, 100)

def load_animations():
	# Pre: Starting the game up
	# Post: Creates 4 animations and appends them to the same list. This is pushing the limits of pygame and actually freezes the whole application until it's complete lol
	global animations
	animations = [animate('image', 0, 0, 1400, 850, 5, 11, 'jpg', 100), animate('pixel', 0, 0, 1400, 850, 3, 50, 'jpg', 100), animate('laptop', 0, 0, 1400, 850, 5, 6, 'jpg', 100), animate('catfe', 0, 0, 1400, 850, 5, 16, 'jpg', 100)]

def sketchbook_text(page):
	# min 680 X right page, 260 X left page [top]
	# 575 max Y 
	# 125 Y
	if page == 0:
		text('Wednesday Night Wrecking', 680, 125, 25, 0, 0, 0)
		text('Developed with Python 3.7.9, Pygame 2.1.0', 680, 150, 25, 0, 0, 0)
		text('By Amy', 680, 175, 25, 0, 0, 0)
		text('Press ESCAPE to close', 680, 550, 25, 0, 0, 0)
		text('Use arrow keys to navigate the sketchbook', 680, 575, 25, 0, 0, 0)
	elif page == 1:
		text('this page is for a quick story of how it began', 260, 125, 25, 0, 0, 0)
		text('So my friend Tim told me to make a rhythm', 260, 200, 25, 0, 0, 0)
		text('game with OMORI gacha as a joke until I told', 260, 225, 25, 0, 0, 0)
		text('my dad and he didn\'t take it as a joke and', 260, 250, 25, 0, 0, 0)
		text('now here we are. Of course I still had to', 260, 275, 25, 0, 0, 0)
		text('add OMORI :)', 260, 300, 25, 0, 0, 0)
		text('"he who goes to bed with itchy bum wakes up', 680, 550, 25, 0, 0, 0)
		text('with stinky finger" - Chris Turoy', 680, 575, 25, 0, 0, 0)
	elif page == 4:
		text('"Sometimes when I close my eyes, I can\'t see"', 680, 110, 25, 0, 0, 0)
		text('- Andrew Pawlak', 780, 135, 25, 0, 0, 0)
	elif page == 7:
		text('"Hi"', 665, 100, 390, 0, 0, 0)
		text('- Ben Newington', 780, 560, 25, 0, 0, 0)
	elif page == 12:
		text('Special Thanks:', 320, 150, 50, 0, 0, 0)
		text('Chris :)', 360, 200, 25, 0, 0, 0)
		text('My dad :)', 360, 225, 25, 0, 0, 0)
		text('Ryax', 360, 275, 25, 0, 0, 0)
		text('HimitsuHiketsu', 360, 300, 25, 0, 0, 0)
		text('Ucitysm', 360, 325, 25, 0, 0, 0)
		text('Zembonics', 360, 350, 25, 0, 0, 0)
		text('AddGore', 360, 375, 25, 0, 0, 0)
		text('Rushiliations', 360, 400, 25, 0, 0, 0)
		
# ~~~~~~~~Image creation~~~~~~~~
uparrow = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\up.png').convert_alpha(), (100,100))
downarrow = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\down.png').convert_alpha(), (100,100))
leftarrow = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\left.png').convert_alpha(), (100,100))
rightarrow = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\right.png').convert_alpha(), (100,100))

hitpf = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\judgements\\hitpf.png').convert_alpha(), (250,75))
hitgr = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\judgements\\hitgr.png').convert_alpha(), (250,75))
hitok = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\judgements\\hitok.png').convert_alpha(), (250,75))
hitmiss = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\judgements\\miss.png').convert_alpha(), (250,75))
comboflash = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\flash.png').convert_alpha(), (1400, 850))

omoriBG = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\omoricore_bg.jpg').convert(), (1400,850))
menuoverlay = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\menu.png').convert_alpha(), (1400,850))
omoriBG.set_alpha(200)

# white space
menu_animations = [animate('omori_neutral', 550, 200, 200, 500, 4, 9, 'png', 2000), animate('omori_angry', 500, 200, 250, 500, 4, 11, 'png', 2000), animate('omori_manic', 500, 200, 350, 500, 2, 28, 'png', 2000), animate('omori_furious', 500, 200, 275, 520, 4, 14, 'png', 2000)]

tutorials = [animate('slide1key', 0, 0, 1400, 850, 15, 2, 'png', 2000), animate('slide2key', 0, 0, 1400, 850, 5, 46, 'png', 2000)]
logobounce = animate('logo', 965, 0, 450, 450, 25, 2, 'png', 2000)
loading_screens = [(pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\journey_of_two.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\twin_switch.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\sleep_princess.jpg').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\genesis_ending.jpg').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\riliane.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\bad_father.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\happy_twins.jpg').convert_alpha(), (1400, 850)))]
combobursts = [(pygame.transform.scale(pygame.image.load('assets\\images\\skin\\comboburst_e.png').convert_alpha(), (450,400))), (pygame.transform.scale(pygame.image.load('assets\\images\\skin\\comboburst_r.png').convert_alpha(), (450,400))), (pygame.transform.scale(pygame.image.load('assets\\images\\skin\\comboburst_n.png').convert_alpha(), (450,400))), (pygame.transform.scale(pygame.image.load('assets\\images\\skin\\comboburst_t.png').convert_alpha(), (450,400)))]

dialoguebox = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\talkingdialoguebox.png').convert_alpha(), (1000,500))
optionbox = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\optionbox.png').convert_alpha(), (1000,500))
infobox = pygame.transform.scale(pygame.image.load('assets\\images\\ui\\informationbox.png').convert_alpha(), (1000,500))
doormenu = pygame.image.load('assets\\images\\ui\\doormenu.png').convert_alpha()

attractorthumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\attractor-dimension_thumb.png').convert_alpha()
bisonthumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\bison-charge_thumb.png').convert_alpha()
luminescencethumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\luminescence_thumb.png').convert_alpha()
pushandshovethumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\push-and-shove_thumb.png').convert_alpha()
rhythmhellthumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\rhythm-hell_thumb.png').convert_alpha()
singsingredthumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\sing-sing-red-indigo_thumb.png').convert_alpha()
sleepwalkingthumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\sleepwalking_thumb.png').convert_alpha()
uwasothumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\uwa-so-holiday_thumb.png').convert_alpha()
whatthumb = pygame.image.load('assets\\images\\cover_art\\thumbs\\what_thumb.png').convert_alpha()

drawings = []
for aaaa in range(13):
	draw = pygame.image.load('assets\\images\\ui\\sketchbook\\' + str(aaaa+1) + '.png').convert_alpha()
	drawings.append(draw)

print (drawings)
# Perfect rectangle = transform scale (x, x*1.618)
stageleft =(pygame.image.load('assets\\images\\skin\\stage-left.png').convert_alpha())
notepad = pygame.transform.scale(pygame.image.load('assets\\images\\skin\\notepad.jpg').convert_alpha(), (250, 405))

# ~~~~~~~~Audio Creation~~~~~~~~
pygame.mixer.music.load('assets\\audio\\music\\menu\\white_space.mp3')
hitnormal = pygame.mixer.Sound('assets\\audio\\sfx\\soft-hitnormal.wav')
no = pygame.mixer.Sound('assets\\audio\\sfx\\deny.ogg')
select = pygame.mixer.Sound('assets\\audio\\sfx\\select.ogg')

meowing_sound = pygame.mixer.Sound('assets\\audio\\sfx\\meow.mp3')
pageflip = pygame.mixer.Sound('assets\\audio\\sfx\\page_turn.ogg')

pygame.mixer.Sound.set_volume(hitnormal, 0.2)
pygame.mixer.Sound.set_volume(meowing_sound, 1.0)
pygame.mixer.Sound.set_volume(select, 1.0)
# ~~~~~~~~Variable Creation~~~~~~~~
animations = []  
sButtonInput = ''
RightClickInput = ''
tick = 0
curr_offset = 0
y = 20
real_REAL_mapdata = []
metadata = ''
song = ''
UI = 'title'
load_msg = ['wednesday night wrecking?', 'how are u', 'hi mr blake', '4. this note is in an intimate relationship with my sister. can you believe it? a single note, capable of destroying familial ties', 'there is no i in birthday', 'take Water', 'F minor is the best musical key', 'thanks a lot for being so cool', 'Don\'t forget to forget who you are', 'Don\'t sell your soul. Be.', 'Flies are 100 percent iron', 'tip: subscribe to me on youtube', 'do i get an extra mark for my cursive handwriting?', 'this is an open ended question, how could i possibly get this wrong?', 'do i get an extra mark for writing the date?', 'Survive him', 'we have a word in our world called confidence. spelt "K-O-N... fidence"', 'this game is on life support pygame\'s memory is so small', 'extra cringe extra probation', 'buy your own car today!', 'jazz for ur soul', 't spin quad??', 'hm fs. ys. pak hm fs. ys. pak.', 'Knights of the Zodiac ft many Youtubers', 'We love being down double digits <3'] #'Play Circle Square Triangle by Christopher-handsome-parry-santa-true today!']
tipx = 670
combotrack = 100
burst_timer = 2000
keydelay = 0
tutorial_screen = 0
comboburst = random.choice(combobursts)
menuA = random.choice(menu_animations)
burst = False
create_buttons()
mewowowo = ''

# x , x + 100, y , y + 125
whitespacedoor = whitespace('door', 400, 500, 200, 325)
mewo = whitespace('cat', 200, 300, 600, 725)
lightbulb = whitespace('lightbulb', 800, 900, -50, 50)
laptop = whitespace('laptop', 410, 510, 380, 505)
sketchbook = whitespace('sketchbook', 810, 910, 380, 505)
tissuebox = whitespace('tissue', 1000, 1100, 600, 725)

omori_dialogue = ['...', 'I have to tell you something.', 'PIZZA DELIVERY!!']
mewo_dialogue = ['Meow? (Waiting for something to happen?)', 'Meow? (When is mom coming back?)', 'Meow? (Not much to do around here, is there?)', 'Meow? (Are you looking for a way out?)']
curr_animation = ''
doorclicked = False
sketchbookclicked = False
laptopclicked = False
catclicked = False
lightbulbclicked = False
tissueclicked = False

omoriclicked = False
sketchbook_page = 0
pygame.mixer.music.play(-1)

# Game Loop
rungame = True
while rungame:
	
	screen.fill((0,0,0))
	mousex, mousey = pygame.mouse.get_pos()
	keys = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			rungame = False	
	

	if UI == 'title':
		# Visuals
		screen.fill((255,255,255))
		pygame.draw.line(screen, (0,0,0), (425 , 400), (900, 400), 4)
		pygame.draw.line(screen, (0,0,0), (425 , 400), (125, 725), 6)
		pygame.draw.line(screen, (0,0,0), (900 , 400), (1200, 725), 6)
		pygame.draw.line(screen, (0,0,0), (125 , 725), (1200, 725), 8)
		pygame.draw.line(screen, (255,255,255), (825, 400), (900, 400), 4)
		
		# Title assets and properties
		whitespacedoor.draw(), whitespacedoor.hover(), whitespacedoor.clicked()
		mewo.draw(), mewo.hover(), mewo.clicked()
		lightbulb.draw(), lightbulb.hover(), lightbulb.clicked()
		sketchbook.draw(), sketchbook.hover(), sketchbook.clicked()
		tissuebox.draw(), tissuebox.hover(), tissuebox.clicked()
		laptop.draw(), laptop.hover(), laptop.clicked()
		menuA.execute()


		#---Title assets---
		if doorclicked == True:
			UI = 'door'
		# Instructions screen
		if laptopclicked == True:
			keydelay = 0
			UI = 'instructions'
			doorclicked, sketchbookclicked, catclicked, lightbulbclicked, tissueclicked = False, False, False, False, False
		# meow... (generates random dialogue for the cat to say...), meow. (this has no function.)
		if catclicked == True:
			dialogue(mewowowo, 'MEWO', 'speaking', None, None)
			if mewowowo == 'Meow? (Are you looking for a way out?)':
				text('Meow... (There always is one... but...)', 195, 650, 50, 255, 255, 255)
			doorclicked, sketchbookclicked, laptopclicked, lightbulbclicked, tissueclicked = False, False, False, False, False
		# Credits and a place for me to share my thoughts. you can look through 13 pages of random and weird drawings. if u try to flip more pages than there are, it prevents u
		if sketchbookclicked == True:
			screen.blit(drawings[sketchbook_page], (250, 100))
			sketchbook_text(sketchbook_page)
			doorclicked, laptopclicked, catclicked, lightbulbclicked, tissueclicked = False, False, False, False, False
			if keys[pygame.K_RIGHT] and keydelay > 10 or keys[pygame.K_LEFT] and keydelay > 1:
				tick = 0
				if keys[pygame.K_RIGHT] and sketchbook_page != 12:
					pygame.mixer.Sound.play(pageflip)
					if tick < 1:
						sketchbook_page += 1
				elif keys[pygame.K_RIGHT] and sketchbook_page == 12:
					pygame.mixer.Sound.play(no)
				if keys[pygame.K_LEFT] and sketchbook_page != 0:
					pygame.mixer.Sound.play(pageflip)
					if tick < 1:
						sketchbook_page -= 1
				elif keys[pygame.K_LEFT] and sketchbook_page == 0:
					pygame.mixer.Sound.play(no)
		# Random dialogue, this has no function
		if lightbulbclicked == True:
			dialogue('A lightbulb hangs from the ceiling, wherever it is.', 'lightbulb', 'info', None, None)
			doorclicked, laptopclicked, catclicked, sketchbookclicked, tissueclicked = False, False, False, False, False
		# Quit game
		if tissueclicked == True:
			dialogue('A tissue box for wiping your sorrows away. Quit game?', None, 'choice', 'ENTER : QUIT', 'ESCAPE : DO NOTHING')
			doorclicked, laptopclicked, catclicked, lightbulbclicked, sketchbookclicked = False, False, False, False, False
			if keys[pygame.K_RETURN]:
				rungame = False
		# Dialogue. This has no function
		if omoriclicked == True:
			doorclicked, laptopclicked, catclicked, sketchbookclicked, tissueclicked, lightbulbclicked = False, False, False, False, False, False
			dialogue(omoli, 'OMORI', 'speaking', None, None)
		
		# Detect if mouse is hovering and clicking on Omori
		if mousex in range(531, 777) and mousey in range(196, 362) and pygame.mouse.get_pressed()[0] == 1 and omoriclicked == False:
			tick = 0
			if tick < 1:
				omoli = random.choice(omori_dialogue)
			omoriclicked = True
		
		# In order to help this menu run smoother with less glitches, this code must be implemented
		if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
			tick = 0
		if tick < 1:
			keydelay = 0
		if pygame.mouse.get_pressed()[0] == 1:
			keydelay = 0
		
		# Reset (quits whatever object the player is interacting with)
		if keys[pygame.K_ESCAPE]:
			doorclicked, laptopclicked, catclicked, lightbulbclicked, sketchbookclicked, tissueclicked, omoriclicked = False, False, False, False, False, False, False
	
	if UI == 'door':
		# Door to enter game is here
		screen.fill((255,255,255))
		screen.blit(doormenu, (40, -130))
		text('ENTER : START GAME', 900, 450, 50, 255, 255, 255)
		text('ESCAPE : DO NOTHING', 900, 480, 50, 255, 255, 255)
		# Sets up and chooses the random loading image and text
		if keys[pygame.K_RETURN]:
			# Load into game
			tick = 0
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()
			pygame.mixer.music.load('assets\\audio\\music\\menu\\stardust_dusting.mp3')
			pygame.mixer.music.play(-1)
			loadimg = random.choice(loading_screens)
			loadimg.set_alpha(100)
			tip_of_the_day = random.choice(load_msg)
			for aaaa in range(len(tip_of_the_day)):
				tipx -= 8
			bgscreen.fill((0,0,0))
			UI = 'loading_screen'
		# Go back
		elif keys[pygame.K_ESCAPE]:
			UI = 'title'
			menuA = random.choice(menu_animations)
			doorclicked, laptopclicked, catclicked, lightbulbclicked, sketchbookclicked, tissueclicked = False, False, False, False, False, False
	
	if UI == 'loading_screen':
		# Loading visuals
		bgscreen.blit(loadimg, (0,0))
		text('Loading...', 600, 400, 50, 255, 255, 255)
		text(tip_of_the_day, tipx, 450, 50, 255, 255, 255)
		if animations == [] or animations == None:
			# This is the real loading, it only occurs when animations are wiped (the only thing it loads is animations), it actually freezes the game
			if tick >= 2:
				load_animations()
				curr_animation = random.choice(animations)
				tick = 0
				pending_return = True
				esc_down = False
				UI = 'menu'
		else:
			# This is a fake load. It waits for x frames to pass before moving on but nothing is actually loading
			if tick >= 75:
				curr_animation = random.choice(animations)
				tick = 0
				UI = 'menu'
	
	# Instructions screen. Very efficient right?
	elif UI == 'instructions':
		screen.fill((0,0,0))
		if tutorial_screen <= 1:
			tutorials[tutorial_screen].execute()
		text("HOW TO PLAY", 600, 50, 50, 255, 255, 255)
		text("do u like my high quality gifs", 950, 50, 30, 255, 255, 255)
		text("Press enter to continue...", 500, 750, 50, 255, 255, 255)
		
		if tutorial_screen == 0:
			text("these are your keybinds! (Q W END PGDOWN)", 350, 650, 50, 255, 255, 255)
		elif tutorial_screen == 1:
			text("Click the keys to the corresponding lanes on time", 550, 650, 50, 255, 255, 255)
		elif tutorial_screen == 2:
			text("Additional tips:", 600, 100, 50, 255, 255, 255)
			text("- Hitnormal support (a soft drum sound) plays when you hit notes. You can", 50, 200, 45, 255, 255, 255)
			text(" use this audible feedback to tell if you\'re too early or too late", 50, 240, 45, 255, 255, 255)
			text("- There is also live visual feedback that is very helpful!!", 50, 300, 45, 255, 255, 255)
			text("- Every multiple of 100 will flash a comboburst, it\'s not a jumpscare, it\'s", 50, 360, 45, 255, 255, 255)
			text(" supposed to be encouraging (so you know you\'re getting combo!)", 50, 400, 45, 255, 255, 255)
			text("- Don\'t play to get better, you\'ll just ragequit all the time and hate the game,", 50, 460, 45, 255, 255, 255)
			text(" instead, just play for enjoyment and improvement will naturally come without effort :D", 50, 500, 45, 255, 255, 255)
			text("- Just try your best, rhythm games are not easy unless you have experience :)", 50, 560, 45, 255, 255, 255)
		if keys[pygame.K_RETURN] and keydelay >= 15:
			keydelay = 0
			tutorial_screen += 1
			if tutorial_screen == 3:
				tipx = 670
				menuA = random.choice(menu_animations)
				tutorial_screen = 0
				doorclicked = False
				laptopclicked = False
				UI = 'title'
				
	elif UI == 'menu':
		# Visuals
		curr_animation.execute()
		pygame.draw.line(screen, (255,255,255), (450 , 0), (450, 830), 4)
		list_buttondisplay(songbuttons_1)
		bgscreen.blit(uwasothumb, (550, 10))
		bgscreen.blit(sleepwalkingthumb, (850, 10))
		bgscreen.blit(rhythmhellthumb, (1150, 10))
		bgscreen.blit(pushandshovethumb, (550, 310))
		bgscreen.blit(luminescencethumb, (850, 310))
		bgscreen.blit(singsingredthumb, (1150, 310))
		bgscreen.blit(bisonthumb, (550, 610))
		bgscreen.blit(attractorthumb, (850, 610))
		bgscreen.blit(whatthumb, (1150, 610))
		
		# Waits until a button is clicked and then sends the player to the game loading screen
		if sButtonInput != '':
			song = sButtonInput
			tick = 0
			UI = 'loading'
		
		# Conditions to let the player return to title
		if tick == 1:
			pending_return = True
			esc_down = False
		
		# Return to title
		if keys[pygame.K_ESCAPE] and keydelay >= 20:
			esc_down = True
		
		text('Press ESC to return to title', 30, 750, 40, 255, 255, 255)
		
		# Return to title part 2, resets music and chooses random animation for Omori
		if esc_down == True and pending_return == True:
			dialogue('Would you like to return to WHITE SPACE?', None, 'choice', 'ENTER : YES', 'BACKSPACE : NO')
			if keys[pygame.K_BACKSPACE]:
				pending_return = False
				tick = 0
			elif keys[pygame.K_RETURN]:	
				tipx = 670
				doorclicked = False
				menuA = random.choice(menu_animations)
				pygame.mixer.music.stop()
				pygame.mixer.music.unload()
				pygame.mixer.music.load('assets\\audio\\music\\menu\\white_space.mp3')
				pygame.mixer.music.play(-1)
				UI = 'title'
		
	elif UI == 'loading':
		# Visuals
		text("Get ready!", 600, 400, 50, 255, 255, 255)
		pygame.mixer.music.stop()
		# The code below happens instantaneously, so I set a visual delay of 50 frames before the loading happens
		if tick >= 50:
			loadmap(song)
			activenotes = []
			keyupD = True
			keyupF = True
			keyupJ = True
			keyupK = True
			totalnotes = 0
			perfectcounter = 0
			greatcounter = 0
			okaycounter = 0
			misscounter = 0
			accuracies = []
			acc_numerator = 0
			curr_value = ''
			pygame.mixer.music.unload()
			pygame.mixer.music.load('assets\\audio\\music\\' + song + '.mp3')
			pygame.mixer.music.play()
			sButtonInput = ''
			mapbg = pygame.transform.scale(pygame.image.load('assets\\images\\cover_art\\' + song + '.jpg').convert_alpha(), (1400, 850))
			mapbg.set_alpha(100)
			comboflash.set_alpha(0)
			tick = 0
			combotrack = 100
			del loading_screens[:]
			del animations[:]
			combo = 0
			maxcombo = 0
			start = int(time.time() * 1000)
			UI = 'game'
		
	elif UI == 'game':
		
		# Grabbing the time in milliseconds of how long has passed since starting the game
		end = int(time.time() * 1000)
		curr_offset = int(end - start)

		# Displays and visuals
		bgscreen.blit(mapbg, (0, 0))
		bgscreen.blit(comboflash, (0, 0))
		bgscreen.blit(stageleft,(280,575))
		bgscreen.blit(stageleft,(280,395))
		bgscreen.blit(stageleft,(280,215))
		bgscreen.blit(stageleft,(280,35))
		pygame.draw.rect(bgscreen, (0,0,0), (450, 0, 550, 1000))
		bgscreen.blit(leftarrow,(475,575))
		bgscreen.blit(uparrow,(600,575))
		bgscreen.blit(downarrow,(725,575))
		bgscreen.blit(rightarrow,(850,575)) # 575 OLD
		bgscreen.blit(notepad,(50,225))
		
		# Quit mid match
		if keys[pygame.K_ESCAPE]:
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()
			pygame.mixer.music.load('assets\\audio\\music\\menu\\stardust_dusting.mp3')
			pygame.mixer.music.play(-1)
			keydelay = 0
			loading_screens = [(pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\journey_of_two.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\twin_switch.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\sleep_princess.jpg').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\genesis_ending.jpg').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\riliane.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\bad_father.png').convert_alpha(), (1400, 850)))]
			tipx = 670
			loadimg = random.choice(loading_screens)
			loadimg.set_alpha(100)
			tip_of_the_day = random.choice(load_msg)
			for aaaa in range(len(tip_of_the_day)):
				tipx -= 8
			bgscreen.fill((0,0,0))
			tick = 0
			UI = 'loading_screen'
		
		# Display combo and Accuracy in percentage
		if totalnotes == 0:
			text('Accuracy: 100.0%', 75, 350, 35, 0, 0, 0)
		else:
			text(('Accuracy: ' + str(round((acc_numerator/(totalnotes)) * 100,2)) + '%'), 75, 350, 35, 0, 0, 0)
		text('Combo: x' + str(combo), 75, 400, 40, 0, 0, 0)
		
		# Stores highest combo in new variable for results screen
		if combo > maxcombo:
			maxcombo = combo
		
		# Note fall detection
		if len(real_REAL_mapdata) > 0:
			if int(real_REAL_mapdata[0][1]) - curr_offset >= 780 and int(real_REAL_mapdata[0][1]) - curr_offset <= 800:
				activenotes.append(note(int(real_REAL_mapdata[0][0]), int(real_REAL_mapdata[0][2])))
				real_REAL_mapdata.pop(0)
		# D = q
		# F = w
		# J = end
		# K = pagedown
		# i know i'm confusing
		
		# To work around pygame's key detection pressing (only allows a key down action to happen for one frame)
		if keys[pygame.K_q] == False:
			keyupD = True
		if keys[pygame.K_w] == False:
			keyupF = True
		if keys[pygame.K_END] == False:
			keyupJ = True
		if keys[pygame.K_PAGEDOWN] == False:
			keyupK = True
		
		# Notes will fall, be checked for miss, check for hit here, and delete once completed. The core of the gameplay
		for notes in activenotes:
			notes.fall(y)
			#notes.checkmiss()
			notes.checkmissD()
			notes.checkmissF()
			notes.checkmissJ()
			notes.checkmissK()
			if keyupD == True:
				if keys[pygame.K_q]:
					notes.hitD()
					keyupD = False
			if keyupF == True:
				if keys[pygame.K_w]:
					notes.hitF()
					keyupF = False
			if keyupJ == True:
				if keys[pygame.K_END]:
					notes.hitJ()
					keyupJ = False
			if keyupK == True:
				if keys[pygame.K_PAGEDOWN]:
					notes.hitK()
					keyupK = False
			if activenotes[0].complete == True or activenotes[0].fall_too_far == True:
				totalnotes += 1
				activenotes.pop(0)
				del notes
		
		# Visual accuracy display. Only lets the latest accuracy display for 15 frames so it's not clogging up emptier spaces in the gameplay
		if curr_value != '':
			if tick <= 15:
				if curr_value == 'perfect':
					bgscreen.blit(hitpf, (580,300))
				if curr_value == 'great':
					bgscreen.blit(hitgr, (580,300))
				if curr_value == 'okay':
					bgscreen.blit(hitok, (580,300))
				if curr_value == 'miss':
					combotrack = 100
					bgscreen.blit(hitmiss, (580,300))
		
		# Combo burst (the photo that flashes briefly when u get a combo that is a multiple of 100
		# Bc pygame is weird there was a lot of workaround to ensure stuff doesn't happen too fast or for an unintended amount of frames
		if combo / combotrack == 1:
			burst_timer = 180
			tick = 0
			burst = True
		if burst == True:
			bgscreen.blit(comboburst, (930, 200))
			comboflash.set_alpha(burst_timer - 175)
			comboburst.set_alpha(burst_timer)	
			if burst_timer <= 0:
				combotrack += 100
				comboburst = random.choice(combobursts)
				burst = False
				
		# When song complete, go to results screen
		if curr_offset >= int(metadata[1]):
			UI = 'results'
	elif UI == 'results':
		# Displays and accuracy breakdown
		bgscreen.blit(mapbg, (0, 0))
		text(('Perfects: ' + str(accuracies.count('perfect'))), 100, 200, 50, 255, 255, 255)
		text(('Greats: ' + str(accuracies.count('great'))), 100, 250, 50, 255, 255, 255)
		text(('Okay: ' + str(accuracies.count('okay'))), 100, 300, 50, 255, 255, 255)
		text(('Miss: ' + str(misscounter)), 100, 350, 50, 255, 255, 255)
		
		# Accuracy
		display_acc = round((acc_numerator/totalnotes) * 100,2)
		text(str(display_acc) + '%', 100, 400, 50, 255, 255, 255)
		
		# Grade based on accuracy. I'm sure there's a better way to do this, right?
		if display_acc == 100.0:
			text(('SS'), 400, 350, 200, 255, 255, 255)
		elif display_acc >= 95.0 and display_acc <= 99.99:
			text(('S'), 400, 350, 200, 255, 255, 255)
		elif display_acc >= 90.0 and display_acc <= 94.99:
			text(('A'), 400, 350, 200, 255, 255, 255)
		elif display_acc >= 81.0 and display_acc <= 89.99:
			text(('B'), 400, 350, 200, 255, 255, 255)
		elif display_acc >= 73.0 and display_acc <= 80.99:
			text(('C'), 400, 350, 200, 255, 255, 255)
		elif display_acc <= 72.99:
			text(('D'), 400, 350, 200, 255, 255, 255)
		
		# Display combo
		text('Max Combo: x' + str(maxcombo), 100, 450, 50, 255, 255, 255)
		
		# Full combo if no miss round
		if misscounter == 0:
			text('full combo wtf!!!!', 800, 200, 50, 255, 255, 255)
		
		text('press escape to return to menu', 600, 500, 50, 255, 255, 255)
		
		# Return to menu and resetting music
		if keys[pygame.K_ESCAPE]:
			keydelay = 0
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()
			pygame.mixer.music.load('assets\\audio\\music\\menu\\stardust_dusting.mp3')
			pygame.mixer.music.play(-1)
			loading_screens = [(pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\journey_of_two.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\twin_switch.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\sleep_princess.jpg').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\genesis_ending.jpg').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\riliane.png').convert_alpha(), (1400, 850))), (pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\bad_father.png').convert_alpha(), (1400, 850))),(pygame.transform.scale(pygame.image.load('assets\\images\\ui\\load\\happy_twins.jpg').convert_alpha(), (1400, 850)))]
			tipx = 670
			loadimg = random.choice(loading_screens)
			loadimg.set_alpha(100)
			tip_of_the_day = random.choice(load_msg)
			for aaaa in range(len(tip_of_the_day)):
				tipx -= 8
			bgscreen.fill((0,0,0))
			tick = 0
			UI = 'loading_screen'
	
	# Free up memory for less lag, garbage collect anything that isn't being actively used
	gc.collect()
	# Timers
	keydelay += 1
	burst_timer -= 5
	tick += 1
	pygame.display.update()
	clock.tick(60)
pygame.quit()
