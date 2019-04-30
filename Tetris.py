# took out top comments bc they were distracting, sorry

from random import randrange as rand, uniform
import pygame, sys, math, json

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
	 [7, 7]]
]

random_seed = 1
current_shape = {
	'x': 0,
	'y': 0, 
	'shape': None
}

bag = []
bag_index = 0
score = 500

# GAME VALUES
score = 0
speed = 500
save_state = None
round_state = None
next_draw = True
moves_taken = 0
move_limit = 500
move_algorithm = []
inspect_move_selection = False

# LOCALSTORAGE - probably won't be needed
storage = None

def storing(stringed_archive):
	storage = { 'archive': stringed_archive }

# GENETIC ALGO VALUES
# number of genomes
population = 50
genomes = []
current_genome = 0
generation = 0
archive = {
	'population_size': 0,
	'current_generation': 0,
	'elites': [], # fittest genomes that we define
	'genomes': [] # all genomes
}

mutation_rate = 0.05 # can be tuned to make it better
mutation_step = 0.2  # interval to mutation rate

def initialize_population():
	archive['population_size'] = population
	next_shape()
	apply_shape()
	create_initial_population()

# SELECTION
def evaluate_next_genome():
	global current_genome
	current_genome = current_genome + 1
	if current_genome == len(genomes):
		evolve()
	# load_state(round_state)
	moves_taken = 0
	make_next_move()

def create_initial_population():
	genomes = []
	for i in range(0, population):
		genome = {
			'id': uniform(0, 1),
			'rows_cleared': uniform(0, 1) - 0.5,
			'height_weight': uniform(0, 1) - 0.5,
			'height_cumulative': uniform(0, 1) - 0.5,
			'height_relative': uniform(0, 1) - 0.5,
			'holes': uniform(0, 1) - 0.5,
			'roughness': uniform(0, 1) - 0.5
		}
		genomes.append(genome)
	evaluate_next_genome()

# CROSSOVER
# new generation
def evolve():
	global generation
	global current_genome
	current_genome = 0
	generation = generation + 1
	genomes = sorted(g_nomes, key = lambda k: k['fitness'])
	archive['elites'].append(clone(genomes[0]))
	print("Elite's fitness:", genomes[0].fitness)

	while len(genomes) > (population / 2):
		genomes.pop()
	
	total_fitness = 0
	for i in range(0, len(genomes)):
		total_fitness = total_fitness + genomes[i].fitness

	children = []
	children.append(genomes[0])
	while len(children) < population:
		children.append(make_child(get_random_genome(), get_random_genome()))
	
	genomes = []
	genomes = genomes + children
	archive['genomes'] = clone(genomes)
	acrhive['current_generation'] = clone(gen)

	storing(json.dumps(archive, separators=(',', ':')))

# MUTATION
def make_child(parent1, parent2):
	# inherit from first parent or second parent randomly
	child = {
		'id': uniform(0, 1),
		'rows_cleared': random_choice(parent1['rows_cleared'], parent2['rows_cleared']),
		'height_weight': random_choice(parent1['height_weight'], parent2['height_weight']),
		'height_cumulative': random_choice(parent1['height_cumulative'], parent2['height_cumulative']),
		'height_relative': random_choice(parent1['height_relative'], parent2['height_relative']),
		'holes': random_choice(parent1['holes'], parent2['holes']),
		'roughness': random_choice(parent1['roughness'], parent2['roughness']),
		'fitness': -1
	}

	# mutate each parameter
	if uniform(0, 1) < mutation_rate:
		child['rows_cleared'] = child['rows_cleared'] + uniform(0, 1) * mutation_step * 2 - mutation_step
	if uniform(0, 1) < mutation_rate:
		child['height_weight'] = child['height_weight'] + uniform(0, 1) * mutation_step * 2 - mutation_step
	if uniform(0, 1) < mutation_rate:
		child['height_cumulative'] = child['height_cumulative'] + uniform(0, 1) * mutation_step * 2 - mutation_step
	if uniform(0, 1) < mutation_rate:
		child['height_relative'] = child['height_relative'] + uniform(0, 1) * mutation_step * 2 - mutation_step
	if uniform(0, 1) < mutation_rate:
		child['holes'] = child['holes'] + uniform(0, 1) * mutation_step * 2 - mutation_step
	if uniform(0, 1) < mutation_rate:
		child['roughness'] = child['roughness'] + uniform(0, 1) * mutation_step * 2 - mutation_step

	return child

def get_random_genome():
	return genomes[random_weight_num(0, len(genomes - 1))]

def random_weight_num(min, max):
	return math.floor(math.pow(uniform(0, 1), 2) * (max - min + 1) + min)

def random_choice(one, two):
	if round(uniform(0, 1)) == 0:
		return clone(one)
	else:
		return clone(two)

def make_next_move():
	global moves_taken
	moves_taken = moves_taken + 1
	if moves_taken > move_limit:
		genomes[current_genome]['fitness'] = clone(score)
		evaluate_next_genome()
	else:
		global next_draw
		old_draw = clone(next_draw)
		next_draw = False
		possible_moves = get_all_possible_moves()
		next_shape()
		
		for i in range(0, possible_moves):
			next_move = get_highest_rated_move(get_all_possible_moves())
			possible_moves[i]['rating'] = possible_moves[i]['rating'] + next_move['rating']
		
		load_state(last_state)
		move = get_highest_rated_move(possible_moves)
		
		for i in range(0, move['rotations']):
			rotate_shape()

		if move['translation'] < 0:
			for lefts in range(0, math.fabs(move['translation'])):
				move_left()
		elif move['translation'] > 0:
			for rights in range(0, move['translation']):
				move_right()

		if (inspect_move_selection):
			move_algorithm = move['algorithm']
		
		next_draw = old_draw

		output()

		update_score()
	
def get_all_possible_moves():
	possible_moves = []
	possible_move_ratings = []
	iterations = 0
	for rotations in range(0, 4):
		oldX = []
		for t in range(-5, 6):
			iterations = iterations + 1
			# load_state(last_state)

			for j in range(0, rotations):
				rotate_shape()
			
			if t < 0:
				for left in range(0, abs(t)):
					move_left()
			elif t > 0:
				for right in range(0, t):
					move_right()
			
			if not contains(oldX, current_shape['x']):
				move_down_results = move_down()
				
				while move_down_results['moved']:
					move_down_results = move_down()
				
				algorithm = {
					'rows_cleared': move_down_results['rows_cleared'],
					'height_weight': math.pow(get_height(), 1.5),
					'height_cumulative': get_cumulative_height(),
					'height_relative': get_relative_height(),
					'holes': get_holes(), # this getter not done TODO
					'roughness': get_roughness()
				}

				rating = 0
				rating = rating + algorithm['rows_cleared'] * genomes[current_genome]['rows_cleared']
				rating = rating + algorithm['height_weight'] * genomes[current_genome]['height_weight']
				rating = rating + algorithm['height_cumulative'] * genomes[current_genome]['height_cumulative']
				rating = rating + algorithm['height_relative'] * genomes[current_genome]['height_relative']
				rating = rating + algorithm['holes'] * genomes[current_genome]['holes']
				rating = rating + algorithm['roughness'] * genomes[current_genome]['roughness']

				if move_down_results['lose']:
					rating = rating - 500

				possible_moves.append({
					'rotations': rotations,
					'translation': t,
					'rating': rating,
					'algorithm': algorithm
				})

				oldX.append(current_shape['x'])

def get_highest_rated_move(moves):
	max_rating = -100000000
	max_move = -1
	ties = []

	for i in range(0, len(moves)):
		if moves[i]['rating'] > max_rating:
			max_rating = moves[i]['rating']
			max_move = i
			ties = [i]
		elif moves[i]['rating'] == max_rating:
			ties.append(i)
	
	move = moves[ties[0]]
	move['algorithm']['ties'] = len(ties)
	return move

def clone(stringed_object):
	return json.dumps(archive, separators=(',', ':'))

def contains(oldX, currentX):
	idx = len(oldX)
	while idx >= 0:
		if oldX[idx] == currentX:
			return True
		idx = idx - 1
	return false

def update():
	if current_genome != -1:
		results = move_down()
		if not results['moved']:
			if results['lose']:
				genomes[current_genome]['fitness'] = clone(score)
				evaluate_next_genome()
			else:
				make_next_move()
	else:
		move_down()
	output()
	update_score()

def move_down():
	result = {
		'lose': False,
		'moved': True,
		'rows_cleared': 0
	}

	remove_shape()
	current_shape['y'] = current_shape['y'] + 1
	
	if collides(grid, current_shape):
		current_shape['y'] = current_shape['y'] - 1
		apply_shape()
		next_shape()
		result['rows_cleared'] = clear_rows()
		if collides(grid, current_shape):
			result['lose'] = True
			#reset_game()
		result['moved'] = False
	apply_shape()
	score = score + 1
	update_score()
	output()
	return result

def move_left():
	remove_shape()
	current_shape['x'] = current_shape['x'] - 1
	if collides(grid, current_shape):
		current_shape['x'] = current_shape['x'] + 1
	apply_shape()

def move_right():
	remove_shape()
	current_shape['x'] = current_shape['x'] + 1
	if collides(grid, current_shape):
		current_shape['x'] = current_shape['x'] - 1
	apply_shape()

def clear_rows():
	clear_rows_list = []
	for row in range(0, len(grid)):
		empty_spaces = False
		for col in range(0, len(grid[row])):
			if grid[row][col] == 0:
				empty_spaces = True
		if not empty_spaces:
			clear_rows_list.append(row)
	
	# score, can take out
	if len(clear_rows_list) == 1:
		score = score + 400
	elif len(clear_rows_list) == 2:
		score = score + 1000
	elif len(clear_rows_list) == 3:
		score = score + 3000
	elif len(clear_rows_list) == 4:
		score = score + 12000
	
	cleared_rows = clone(len(clear_rows_list))

	for i in range(len(clear_rows_list) - 1, -1, -1):
		grid.pop(clear_rows_list[i])

	while len(grid) < 20:
		grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

	return clear_rows_list

def apply_shape():
	for row in range(0, len(current_shape['shape'])):
		for col in range(0, len(current_shape['shape'][row])):
			if current_shape['shape'][row][col] != 0:
				grid[current_shape['y'] + row][current_shape['y'] + col] = current_shape['shape'][row][col]

def remove_shape():
	for row in range(0, len(current_shape['shape'])):
		for col in range(0, len(current_shape['shape'][row])):
			if current_shape['shape'][row][col] != 0:
				grid[current_shape['y'] + row][current_shape['y'] + col] = 0

def next_shape():
	global bag_index
	bag_index = bag_index + 1
	if len(bag) == 0 or bag_index == len(bag):
		generate_bag()
	if bag_index == (len(bag) - 1):
		previous_seed = random_seed
		upcoming_shape = random_property(tetris_shapes)
		random_seed = previous_seed
	else:
		upcoming_shape = tetris_shapes[bag[bag_index + 1]]
	current_shape['shape'] = tetris_shapes[bag[bag_index]]
	current_shape['x'] = math.floor(len(grid[0]) / 2) - math.ceil(len(current_shape[0]) / 2)
	current_shape['y'] = 0

def generate_bag():
	bag = []
	contents = ""
	for i in range(0, 7):
		tetronimo = tetris_shapes[rand(0, 7)]
		while(contents.index(tetronimo) != -1):
			tetronimo = random_key(tetronimo)
		bag[i] = tetronimo
		contents = contents + tetronimo
	bag_index = 0

def reset_game():
	score = 0
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
		[0,0,0,0,0,0,0,0,0,0]
	]
	moves_taken = 0
	generate_bag()
	next_shape()

def collides(grid, tetronimos):
	for row in range(0, len(tetronimos['shape'])):
		for col in range(0, len(tetronimos['shape'][row])):
			if tetronimos['shape'][row][col] != 0:
				if grid[tetronimos['y'] + row] == None or grid[tetronimos['y'] + row][tetronimos['x'] + col] == None or grid[tetronimos['y'] + row][tetronimos['x'] + col] != 0:
					return True
	return False

def rotate(matrix, times):
	for t in range(0, times):
		matrix = transpose(matrix)
		for i in range(0, len(matrix)):
			matrix[i].reverse()
	return matrix

def transpose(array):
	transposed_array = [[array[j][i] for j in range(len(array))] for i in range(len(array[0]))]
	return transposed_array

def rotate_clockwise(shape):
	return [[shape[y][x]
			for y in range(len(shape))]
		for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False	

# TODO
def get_holes():
	remove_shape()
	peaks = [20, 20, 20, 20, 20, 20, 20, 20]
	for row in range(0, len(grid)):
		for col in range(0, len(grid[row])):
			if (grid[row][col] != 0 and peaks[col] == 20):
				peaks[col] = row

	holes = 0
	for x in range(0, len(peaks)):
		for y in (0, len(grid)):
			if (grid[y][x] == 0):
				holes = holes + 1

	apply_shape()
	print("This is from the get_holes function: ")
	print(holes)
	return holes

def remove_row(board, row):
	del board[row]
	return [[0 for i in range(config['cols'])]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1][cx+off_x] += val
	return mat1

def new_board():
	board = [[0 for x in range(config['cols'])]
			for y in range(config['rows']) ]
	board += [[1 for x in range(config['cols'])]]
	return board

class TetrisApp(object):
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
		
		if check_collision(self.board,
						   self.stone,
						   (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_stone()

	def right_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.Font(
				pygame.font.get_default_font(), 12).render(
					line, False, (255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x = 300
			msgim_center_y = 300
		
			self.screen.blit(msg_image, (300, 300))
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.Font(
				pygame.font.get_default_font(), 12).render(
					line, False, (255,255,255), (0,0,0))
		
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
			if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()

	def begin_ai(self):
		initialize_population()
	
	def drop(self):
		if (not self.gameover and not self.paused):
			self.stone_y += 1
			if check_collision(self.board,
							   self.stone,
							   (self.stone_x, self.stone_y)):
				self.board = join_matrixes(
				  self.board,
				  self.stone,
				  (self.stone_x, self.stone_y))
				self.new_stone()
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(
							  self.board, i)
							break
					else:
						break
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board,
								   new_stone,
								   (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	def run(self):
		global moves_taken
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		self.drop,
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'a': 		self.begin_ai,
			'SPACE':	self.start_game
		}

		self.gameover = False
		self.paused = False
		
		pygame.time.set_timer(pygame.USEREVENT + 1, config['delay'])
		clock = pygame.time.Clock()
		while 1:
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over! Press space to continue""")
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
					self.right_msg("Moves Taken: " + str(moves_taken))
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
	App = TetrisApp()
App.run()