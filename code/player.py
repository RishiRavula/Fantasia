from typing import Any
import pygame 
from settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups, obstacle_sprites, create_attack, despawn_attack):
		super().__init__(groups)
		self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-8,-26)

		# import animations
		self.import_player_assets()
		self.status = 'down'
		self.frame_index = 0
		self.animation_speed = 0.15
		# movement
		self.direction = pygame.math.Vector2(0,0)
		self.speed = 5
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None
		self.obstacle_sprites = obstacle_sprites

		#weapon
		self.create_attack = create_attack
		self.weapon_index = 0
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.despawn_attack = despawn_attack
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 200



	
	def import_player_assets(self):
		player_path = './graphics/player/'
		self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
			'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
			'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []}
		for animation in self.animations.keys():
			full_path = player_path + animation
			self.animations[animation] = import_folder(full_path)
		
		
	def get_input(self):
		if not self.attacking:
			keys = pygame.key.get_pressed()
			#Move input
			if keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.status = 'left'
			elif keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.status = 'right'
			else:
				self.direction.x = 0
			if keys[pygame.K_UP]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0
			
			#attack input
			if keys[pygame.K_SPACE] and not self.attacking:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack()
				
				
				
			#magic input
			if keys[pygame.K_LCTRL] and not self.attacking:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
			
			#weapon input
			if keys[pygame.K_TAB] and self.can_switch_weapon:
				self.can_switch_weapon = False
				self.weapon_switch_time = pygame.time.get_ticks()
				self.weapon_index += 1
				if self.weapon_index >= len(weapon_data):
					self.weapon_index = 0
				self.weapon = list(weapon_data.keys())[self.weapon_index]
				
			
			
	
	def get_status(self):
		#idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not'attack' in self.status:
				self.status = self.status + '_idle'
		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				# remove the idle status if the player is attacking
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','')
				self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack','')
	
		
	def move(self,speed):
		if self.direction.magnitude() != 0:
			self.direction.normalize_ip()


		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')

		self.rect.center = self.hitbox.center

	def cooldown(self):
		current_time = pygame.time.get_ticks()
		# attack cooldown
		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False
				self.despawn_attack()

		# weapon switch cooldown
		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True
				

	def collision(self, dir):
		if dir == 'horizontal':
			for sprite in self.obstacle_sprites:
				if self.hitbox.colliderect(sprite.hitbox):
					if self.direction.x > 0:
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0:
						self.hitbox.left = sprite.hitbox.right
			
		if dir == 'vertical':
			for sprite in self.obstacle_sprites:
				if self.hitbox.colliderect(sprite.hitbox):
					if self.direction.y > 0:
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0:
						self.hitbox.top = sprite.hitbox.bottom

	def animate(self):
		animation = self.animations[self.status]
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

	def update(self):
		self.get_input()
		self.cooldown()
		self.get_status()
		self.animate()
		self.move(self.speed)
