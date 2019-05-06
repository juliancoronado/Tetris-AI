# took out top comments bc they were distracting, sorry

from random import randrange as rand, uniform
import pygame, sys, math, json, random

grid = [
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0],
]

# game configuration
config = {
	'cell_size': 20,
	'cols': 10,
	'rows':	20,
	'delay': 750,
	'maxfps': 30
}

colors = [
(0, 0, 0),
(255, 0, 0),
(0, 150, 0),
(0, 0, 255),
(255, 120, 0),
(255, 255, 0),
(180, 0, 255),
(0, 220, 220)
]

current_shape = {
	'x': 0,
	'y': 0, 
	'shape': None
}

tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]]

moves_taken = 0
score = 0
move_limit = 100
bag_index = 0
bag = []
upcoming_shape = []

class AI:

	population_size = 50
	current_gen = 0
	curr_genome = 0
	elites = []
	genomes = []

	def __init__(self):
		self.next_shape()
		self.apply_shape()
		self.create_init_pop()

	def create_init_pop(self):
		# generates all the random values for each genome
		for i in range(0, self.population_size):
			genome = {
				'id': uniform(0, 1) - 0.5,
				'rows_cleared': uniform(0, 1) - 0.5,
				'height_weight': uniform(0, 1) - 0.5,
				'height_cumulative': uniform(0, 1) - 0.5,
				'height_relative': uniform(0, 1) - 0.5,
				'holes': uniform(0, 1) - 0.5,
				'roughness': uniform(0, 1) - 0.5,
				'fitness': -1
			}
			self.genomes.append(genome)
		self.evaluate_next_genome()

	def evaluate_next_genome(self):
		global moves_taken
		self.curr_genome = self.curr_genome + 1
		if self.curr_genome == len(self.genomes):
			self.evolve()
		moves_taken = 0
		self.make_next_move()
	
	def evolve(self):
		# nothing yet
		print("evolve() function has been called.")

	def make_next_move(self):
		global moves_taken, move_limit, score
		moves_taken = moves_taken + 1
		if moves_taken > move_limit:
			self.genomes[self.curr_genome]['fitness'] = score
			self.evaluate_next_genome()
		else:
			#TODO
			possible_moves = self.get_all_possible_moves()
	
	def get_all_possible_moves(self):
		print("get_all_possible_moves() function has been called.")
		possible_moves = []
		possible_move_ratings = []
		iterations = 0

		for rots in range(0, 4):
			oldX = []
			for t in range(-5, 5):
				iterations = iterations + 1

				for j in range(0, rots):
					self.rotate_shape()

				if (t < 0):
					for left in range(0, abs(t)):
						self.move_left()

				if not self.contains(oldX, current_shape['x']):
					move_down_results = self.move_down()

					while move_down_results['moved']:
						move_down_results = self.move_down()

					
	
	def rotate_shape(self):
		current_shape['shape'] = self.rotate(current_shape['shape'], 1)

	def rotate(self, shape, n):
		for t in range(0, n):
			shape = self.transpose(shape)
			for i in range(0, len(shape)):
				shape[i] = shape[i][::-1]
		return shape

	def transpose(self, s):
		transposed_array = [[s[j][i] for j in range(len(s))] for i in range(len(s[0]))]
		return transposed_array

	def remove_shape(self):
		for row in range(0, len(current_shape['shape'])):
			for col in range(0, len(current_shape['shape'][row])):
				if (current_shape['shape'][row][col] != 0):
					grid[current_shape['y'] + row][current_shape['x'] + col] = 0

	def next_shape(self):
		global bag_index, current_shape, grid, bag
		bag_index = bag_index + 1
		if (len(bag) == 0 or bag_index == len(bag)):
			self.generate_bag()
		if (bag_index == (len(bag) - 1)):
			current_shape['shape'] = random.choice(tetris_shapes)
		else:
			current_shape['shape'] = bag[bag_index + 1]

	def generate_bag(self):
		global bag, bag_index
		contents = ""
		for i in range(0, 7):
			t = random.choice(tetris_shapes)
			bag.append(t)
		bag_index = 0

	def apply_shape(self):
		for row in range(0, len(current_shape['shape'])):
			for col in range(0, len(current_shape['shape'][row])):
				if (current_shape['shape'][row][col] != 0):
					grid[current_shape['y'] + row][current_shape['x'] + col] = current_shape['shape'][row][col]

	def move_left(self):
		self.remove_shape()
		current_shape['x'] = current_shape['x'] - 1
		if self.collides():
			current_shape['x'] = current_shape['x'] + 1
		self.apply_shape()

	def collides(self):
		global grid, current_shape
		for row in range(0, len(current_shape['shape']) - 1):
			for col in range(0, len(current_shape['shape'][row]) - 1):
				if (current_shape['shape'][row][col] != 0):
					if (grid[current_shape['y'] + row] == None):
						return True
					elif (grid[current_shape['y'] + row][current_shape['x'] + col] == None):
						return True
					elif (grid[current_shape['y'] + row][current_shape['x'] + col] != 0):
						return True
		return False

	def move_down(self):
		global score
		result = {
			'lose': False,
			'moved': True,
			'rows_cleared': 0
		}
		
		self.remove_shape()
		current_shape['y'] = current_shape['y'] + 1

		if (self.collides()):
			current_shape['y'] = current_shape['y'] - 1
			self.apply_shape()
			self.next_shape()
			result['rows_cleared'] = self.clear_rows()
			if (self.collides()):
				result['lose'] = True
				self.reset_game()
			result['moved'] = False

		self.apply_shape()
		score = score + 100
		return result

	def contains(self, oldX, currentX):
		idx = len(oldX)
		while (idx > 0):
			if (oldX[idx] == currentX):
				return True
			idx = idx - 1
		return False

########################################################################################################################
########################################################################################################################

class Tetris:
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.width = 400
		self.height = 400
		
		self.screen = pygame.display.set_mode((self.width, self.height))
		# we do not need mouse move events, so they are blocked
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		self.init_game()
	
	def new_stone(self):
		global moves_taken
		moves_taken = moves_taken + 1
		self.stone = tetris_shapes[rand(len(tetris_shapes))]
		self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
		self.stone_y = 0
		
		if self.check_collision(self.board,
						   self.stone,
						   (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = self.new_board()
		self.new_stone()

	def check_collision(self, board, shape, offset):
		off_x, off_y = offset
		for cy, row in enumerate(shape):
			for cx, cell in enumerate(row):
				try:
					if cell and board[ cy + off_y ][ cx + off_x ]:
						return True
				except IndexError:
					return True
		return False
	
	def new_board(self):
		board = [[0 for x in range(config['cols'])] for y in range(config['rows']) ]
		board += [[1 for x in range(config['cols'])]]
		return board

	def right_msg(self, msg, off_x, off_y):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.SysFont('Arial', 15).render(
					line, False, (255,255,255), (105, 105, 105))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x = 300
			msgim_center_y = 300
		
			self.screen.blit(msg_image, (220 + off_x, 300 + off_y))

	def join_matrixes(self, mat1, mat2, mat2_off):
		off_x, off_y = mat2_off
		for cy, row in enumerate(mat2):
			for cx, val in enumerate(row):
				mat1[cy+off_y-1][cx+off_x] += val
		return mat1
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.SysFont('Arial', 20).render(
					line, False, (0, 0, 0), (255, 255, 0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					rect = pygame.Rect(	(off_x+x) * config['cell_size'], (off_y+y) * config['cell_size'],
						config['cell_size'], config['cell_size'])
					pygame.draw.rect(self.screen, colors[val], rect, 0)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > config['cols'] - len(self.stone[0]):
				new_x = config['cols'] - len(self.stone[0])
			if not self.check_collision(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x

	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()

	def begin_ai(self):
		self.ai = not self.ai
		player = AI()

	def remove_row(self, board, row):
		global score
		score = score + 100
		del board[row]
		return [[0 for i in range(config['cols'])]] + board
	
	def drop(self):
		if (not self.gameover and not self.paused):
			self.stone_y += 1
			if self.check_collision(self.board,
							   self.stone,
							   (self.stone_x, self.stone_y)):
				self.board = self.join_matrixes(
				  self.board,
				  self.stone,
				  (self.stone_x, self.stone_y))
				self.new_stone()
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = self.remove_row(
							  self.board, i)
							break
					else:
						break
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = self.rotate_clockwise(self.stone)
			if not self.check_collision(self.board,
								   new_stone,
								   (self.stone_x, self.stone_y)):
				self.stone = new_stone

	def rotate_clockwise(self, shape):
		return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1) ]
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	def run(self):
		global moves_taken
		global score
		key_actions = {
			'ESCAPE':	self.quit,
			# im not entirely sure what "lambda"
			# does here but if i remove it the game breaks
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		self.drop,
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'a': 		self.begin_ai,
			'SPACE':	self.start_game
		}

		self.ai = False
		self.gameover = False
		self.paused = False
		
		pygame.time.set_timer(pygame.USEREVENT + 1, config['delay'])
		clock = pygame.time.Clock()
		while 1:
			rect1 = pygame.Rect(0, 0, 200, 400)
			rect2 = pygame.Rect(200, 0, 200, 400)
			self.screen.fill((0 , 0, 0), rect1)
			self.screen.fill((105, 105, 105), rect2)
			if self.gameover:
				self.center_msg("""Game Over! Press space to continue""")
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
					self.right_msg("Genome Values: ", 0, -120)
					self.right_msg("Generation: ", 15, -105)
					self.right_msg("Genome #: ", 15, -90)
					self.right_msg("Fitness: ", 15, -75)
					self.right_msg("Example Val: ", 15, -60)
					self.right_msg("[A] Toggle AI", 0, -15)
					self.right_msg("Moves Taken: " + str(moves_taken), 0, 0)
					if (self.ai):
						self.right_msg("AI: On", 0, 15)
					else:
						self.right_msg("AI: Off", 0, 15)
					self.right_msg("Score: " + str(score), 0, 30)
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop()
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_"
						+key):
							key_actions[key]()
					
			clock.tick(config['maxfps'])

if __name__ == '__main__':
	game = Tetris()

game.run()