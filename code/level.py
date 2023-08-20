import pygame 
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import Weapon

class Level:
	def __init__(self):

		# get the display surface 
		self.display_surface = pygame.display.get_surface()

		# sprite group setup
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		#attack sprites
		self.current_attack = None

		# sprite setup
		self.create_map()

	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
			'grass' : import_csv_layout('./map/map_Grass.csv'),
			'object': import_csv_layout('./map/map_Objects.csv'),
		}

		graphics = {
			'grass': import_folder('./graphics/grass/'),
			'object': import_folder('./graphics/objects/'),

		}
		print(graphics['grass'])

		for style, layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites], 'invisible')
						if style == 'grass':
							# random image of grass
							rand_grass_img = choice(graphics['grass'])
							Tile((x,y),[self.visible_sprites, self.obstacle_sprites], 'grass', rand_grass_img)
						if style == 'object':
							surf = graphics['object'][int(col)]
							Tile((x,y),[self.visible_sprites, self.obstacle_sprites], 'object', surf)
							
		self.player = Player((2000,1430),[self.visible_sprites], self.obstacle_sprites, self.create_attack, self.despawn_attack)

	
	
	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites])

	def despawn_attack(self):
		if self.current_attack:
			self.current_attack.kill()
			self.current_attack = None


	def run(self):
		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
		debug(self.player.direction)

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_screen_width = self.display_surface.get_size()[0] // 2
		self.half_screen_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2(0,0)

		#floor generation
		self.floor_surface = pygame.image.load('./graphics/tilemap/ground.png').convert()
		self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))

	def custom_draw(self, player):
		self.offset.x = (player.rect.centerx - self.half_screen_width)
		self.offset.y = (player.rect.centery - self.half_screen_height)

		self.display_surface.blit(self.floor_surface, self.floor_rect.topleft - self.offset)
		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)