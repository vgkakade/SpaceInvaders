import pygame
import os
import time
import random

#font for the test to be used in pygame
pygame.font.init()

WIDTH, HEIGHT = 650, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Ship:
	COOLDOWN = 10
	"""docstring for Ship"""
	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0   #waite berfore shooting another laser

	def draw(self, window):  #location to draw
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cool_down()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cool_down(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0:		#if counter is 0 create laser
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()


class Laser():
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not(self.y <= height and self.y >= 0)

	def collision(self, obj):
		return collide(self, obj)

class Player(Ship):
	def __init__(self, x, y, health=100):
		#calling player __init__ method
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)	#take image and mask it (tell where pixes is present or absent)
		self.max_health = health	

	def move_lasers(self, vel, objs):
		self.cool_down()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)	

	def draw(self, window):
		super().draw(window)
		self.health_bar(window)

	def health_bar(self, window):
		pygame.draw.rect(window, (255,0,0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0,255,0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
		

class Enemy(Ship):
	COLOR_MAP = {
		"red": (RED_SPACE_SHIP, RED_LASER),
		"green": (GREEN_SPACE_SHIP, GREEN_LASER),
		"blue": (BLUE_SPACE_SHIP, BLUE_LASER)
	}

	def __init__(self, x ,y,color, health=100):
		super().__init__(x,y,health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0:		#if counter is 0 create laser
			laser = Laser(self.x-15, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1 


def collide(obj1, obj2):	#check if px of noth objects overlap (collide) with each other
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None

def main():
	run = True
	FPS = 60
	level = 0
	lives = 5
	clock = pygame.time.Clock()
	lost = False
	lost_count = 0
	main_font = pygame.font.SysFont("comicsans", 50)
	lost_font = pygame.font.SysFont("comicsans", 60)
	player_vel = 5 #speed of movement when key pressed

	enemies = [] #store where enemies
	wave_length = 5
	enemy_vel = 1   #1px speed
	laser_vel = 5

	player = Player(200,540)

	#draws everything on the screen
	def redraw_window():
		#redraw for every FPS
		WIN.blit(BG ,(0, 0))   #take background at top left
    	#draw text to screen
		lives_label = main_font.render(f"Lives: {lives}", 1, (0, 255, 0))
		level_label = main_font.render(f"Level: {level}", 1, (0, 255, 0))

		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)

		if lost:
			lost_label = lost_font.render("You Lost !!", 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))  #text at center
		
		pygame.display.update()

	while run:
		clock.tick(FPS)

		redraw_window()
		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:		#show msg fro 5 seconds
				run = False
			else:
				continue
		
		if len(enemies) == 0:			#after end of enemies
			level +=1		#increase level of game
			wave_length +=5	#no. of enemies is 5 each time

			for i in range(wave_length):
				#make enemy appear at different positions using random
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(["red","blue","green"]))
				enemies.append(enemy)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

	    #know if key pressed
		keys = pygame.key.get_pressed()
		#if a i.e left
		if keys[pygame.K_a] and player.x - player_vel > 0:
			player.x -= player_vel
		if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
			player.x += player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 10 < HEIGHT:
			player.y +=player_vel
		if keys[pygame.K_w] and player.y - player_vel > 0:	#check for window border
			player.y -= player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:   #create copy of list
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2*60) == 1:
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)

			elif enemy.y + enemy.get_height() > HEIGHT:		#check if enemy is out of screen and decrease life
				lives -= 1
				enemies.remove(enemy)

		player.move_lasers(-laser_vel, enemies)

def main_menu():
	title_font = pygame.font.SysFont("comicsans", 70)
	run = True
	while run:
		WIN.blit(BG, (0,0))
		title_label = title_font.render("Press the mouse to begin...", 1 , (255,255,255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()

	pygame.quit()

main_menu()