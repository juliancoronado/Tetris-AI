import random, pygame, sys, math, json, threading

# Initial matrix
matrix = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

# To reset the matrix without cluttering code
clear_matrix = matrix

# List of tetris shapes
tetris_shapes = {
    'I': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
    'J': [[2,0,0], [2,2,2], [0,0,0]],
    'L': [[0,0,3], [3,3,3], [0,0,0]],
    'T': [[0,6,0], [6,6,6], [0,0,0]],
    'S': [[0,5,5], [5,5,0], [0,0,0]],
    'Z': [[7,7,0], [0,7,7], [0,0,0]],
    'O': [[4,4], [4,4]]
}

# Initialize the current tetris stone to be manipulated
current_stone = {
    'tetronimo': [None],
    'x_position': 0,
    'y_position': 0
}

# Base values
score = 0
moves_taken = 0
move_limit = 100
move_algorithm = []
population = 10
genomes = []
current_genome = -1
generation = 0

# Begin the program
def initialize_population():
    next_stone()
    set_stone()
    selection()

# SELECTION
def selection():
    global genomes
    global current_genome
    genomes = []
    for _ in range(0, population):
        genome = {
            'id': random.uniform(0, 1),
            'rows_cleared': random.uniform(0, 1) - 0.5,
            'height_weight': random.uniform(0, 1) - 0.5,
            'height_cumulative': random.uniform(0, 1) - 0.5,
            'height_relative': random.uniform(0, 1) - 0.5,
            'holes': random.uniform(0, 1) - 0.5,
            'roughness': random.uniform(0, 1) - 0.5,
            'fitness': -1
        }
        genomes.append(genome)
    evaluate_next_genome()

def evaluate_next_genome():
    global moves_taken
    global current_genome
    global genomes

    current_genome = current_genome + 1
    if current_genome == len(genomes):
        crossover()
    
    moves_taken = 0
    make_next_move()

# CROSSOVER
# new generation
def crossover():
    global current_genome
    global generation
    global genomes

    current_genome = 0
    generation = generation + 1
    reset_game()
    genomes = sorted(genomes, key = lambda k: k['fitness'], reverse=True)
    while (len(genomes) > (population / 2)):
        genomes.pop()
    total_fitness = 0
    for i in range(0, len(genomes)):
        total_fitness = total_fitness + genomes[i]['fitness']
    children = []
    children.append(genomes[0])
    while len(children) < population:
        children.append(mutate(random.choice(genomes), random.choice(genomes)))
    genomes = []
    genomes = genomes + children

# MUTATION
def mutate(parent1, parent2):
    child = {
        'id': random.uniform(0, 1),
        'rows_cleared': inherit(parent1['rows_cleared'], parent2['rows_cleared']),
        'height_weight': inherit(parent1['height_weight'], parent2['height_weight']),
        'height_cumulative': inherit(parent1['height_cumulative'], parent2['height_cumulative']),
        'height_relative': inherit(parent1['height_relative'], parent2['height_relative']),
        'holes': inherit(parent1['holes'], parent2['holes']),
        'roughness': inherit(parent1['roughness'], parent2['roughness']),
        'fitness': -1
    }
    mutation_rate = 0.05 # can be tuned to make it better
    mutation_step = 0.2  # interval to mutation rate

    # mutate each parameter
    if random.uniform(0, 1) < mutation_rate:
        child['rows_cleared'] = child['rows_cleared'] + random.uniform(0, 1) * mutation_step * 2
    if random.uniform(0, 1) < mutation_rate:
        child['height_weight'] = child['height_weight'] + random.uniform(0, 1) * mutation_step * 2
    if random.uniform(0, 1) < mutation_rate:
        child['height_cumulative'] = child['height_cumulative'] + random.uniform(0, 1) * mutation_step * 2
    if random.uniform(0, 1) < mutation_rate:
        child['height_relative'] = child['height_relative'] + random.uniform(0, 1) * mutation_step * 2
    if random.uniform(0, 1) < mutation_rate:
        child['holes'] = child['holes'] + random.uniform(0, 1) * mutation_step * 2
    if random.uniform(0, 1) < mutation_rate:
        child['roughness'] = child['roughness'] + random.uniform(0, 1) * mutation_step * 2
    return child

def inherit(parent1, parent2):
    if round(random.uniform(0, 1)) == 0:
        return parent1
    else:
        return parent2

def make_next_move():
    global moves_taken
    global move_limit
    global genomes

    moves_taken = moves_taken + 1

    if moves_taken > move_limit:
        genomes[current_genome]['fitness'] = score
        evaluate_next_genome()
    else:
        possible_moves = get_all_possible_moves()
        next_stone()
        hai = input('press enter -- after getting all possible moves')
        
        for i in range(0, len(possible_moves)):
            next_move = highest_rating(get_all_possible_moves())
            possible_moves[i]['rating'] = possible_moves[i]['rating'] + next_move['rating']
        
        move = highest_rating(possible_moves)

        for i in range(0, move['rotations']):
            rotate_stone()

        if move['translation'] < 0:
            for _ in range(0, abs(move['translation'])):
                move_left()

        elif move['translation'] > 0:
            for _ in range(0, move['translation']):
                move_right()
    
def get_all_possible_moves():
    global current_stone
    possible_moves = []
    iterations = 0
    for r in range(0, 4):
        old_x_positions = []
        for t in range(-5, 6):
            iterations = iterations + 1
            for _ in range(0, r):
                rotate_stone()
            if t < 0:
                for _ in range(0, abs(t)):
                    move_left()
            elif t > 0:
                for _ in range(0, t):
                    move_right()
            
            if not contains(old_x_positions, current_stone['x_position']):
                drop_results = drop()
    
                while drop_results['moved']:
                    drop_results = drop()
                    
                output()
                hi = input('hello')
                algorithm = {
                    'rows_cleared': drop_results['rows_cleared'],
                    'height_weight': math.pow(get_height(), 1.5),
                    'height_cumulative': get_cumulative_height(),
                    'height_relative': get_relative_height(),
                    'holes': get_holes(),
                    'roughness': get_roughness(),
                    'ties': 0
                }
                rating = 0
                rating = rating + (algorithm['rows_cleared'] * genomes[current_genome]['rows_cleared'])
                rating = rating + (algorithm['height_weight'] * genomes[current_genome]['height_weight'])
                rating = rating + (algorithm['height_cumulative'] * genomes[current_genome]['height_cumulative'])
                rating = rating + (algorithm['height_relative'] * genomes[current_genome]['height_relative'])
                rating = rating + (algorithm['holes'] * genomes[current_genome]['holes'])
                rating = rating + (algorithm['roughness'] * genomes[current_genome]['roughness'])

                if drop_results['lose']:
                    reset_game()

                possible_moves.append({
                    'rotations': r,
                    'translation': t,
                    'rating': rating,
                    'algorithm': algorithm
                })

                old_x_positions.append(current_stone['x_position'])
    return possible_moves

def highest_rating(moves):
    max_rating = -100000000
    ties = []
    for i in range(0, len(moves)):
        if moves[i]['rating'] > max_rating:
            max_rating = moves[i]['rating']
            ties = [i]
        elif moves[i]['rating'] == max_rating:
            ties.append(i)
    move = moves[ties[0]]
    move['algorithm']['ties'] = len(ties)
    return move

def contains(old_x_positions, currentX):
    idx = len(old_x_positions) - 1
    while idx >= 0 and len(old_x_positions) != 0:
        if old_x_positions[idx] == currentX:
            return True
        if idx != 0:
            idx = idx - 1
        else:
            break
    return False

def drop():
    global current_stone
    global matrix
    global score

    result = {
        'lose': False,
        'moved': True,
        'rows_cleared': 0
    }

    remove_stone()
    current_stone['y_position'] = current_stone['y_position'] + 1

    if collides(matrix, current_stone):
        current_stone['y_position'] = current_stone['y_position'] - 1
        set_stone()
        next_stone()
        result['rows_cleared'] = clear_rows()
        if collides(matrix, current_stone):
            result['lose'] = True
        result['moved'] = False
    set_stone()
    score = score + 1
    return result

def move_left():
    global current_stone
    global matrix

    remove_stone()
    current_stone['x_position'] = current_stone['x_position'] - 1

    if collides(matrix, current_stone) or current_stone['x_position'] < 0:
        current_stone['x_position'] = current_stone['x_position'] + 1
    set_stone()

def move_right():
    global current_stone
    global matrix

    remove_stone()
    current_stone['x_position'] = current_stone['x_position'] + 1
    if collides(matrix, current_stone):
        current_stone['x_position'] = current_stone['x_position'] - 1
    set_stone()

def clear_rows():
    global matrix

    clear_rows_list = []
    for row in range(0, len(matrix)):
        empty_spaces = False
        for col in range(0, len(matrix[row])):
            if matrix[row][col] == 0:
                empty_spaces = True
        if not empty_spaces:
            clear_rows_list.append(row)
    
    if len(clear_rows_list) == 1:
       score = score + 400
    elif len(clear_rows_list) == 2:
       score = score + 1000
    elif len(clear_rows_list) == 3:
       score = score + 3000
    elif len(clear_rows_list) == 4:
       score = score + 12000
    
    cleared_rows = len(clear_rows_list)

    for i in range(len(clear_rows_list) - 1, -1, -1):
        matrix.pop(clear_rows_list[i])

    while len(matrix) < 20:
        matrix.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    return cleared_rows

def set_stone():
    global current_stone
    global matrix
    for row in range(0, len(current_stone['tetronimo'])):
        for col in range(0, len(current_stone['tetronimo'][row])):
            if current_stone['tetronimo'][row][col] != 0:
                matrix[current_stone['y_position'] + row][current_stone['x_position'] + col] = current_stone['tetronimo'][row][col]

def remove_stone():
    global current_stone
    global matrix
    for row in range(0, len(current_stone['tetronimo'])):
        for col in range(0, len(current_stone['tetronimo'][row])):
            if current_stone['tetronimo'][row][col] != 0:
                matrix[current_stone['y_position'] + row][current_stone['x_position'] + col] = 0

def rotate_stone():
    global current_stone
    global matrix
    remove_stone()
    current_stone['tetronimo'] = rotate(current_stone['tetronimo'], 1)
    if collides(matrix, current_stone):
        current_stone['tetronimo'] = rotate(current_stone['tetronimo'], 3)
    set_stone()

def next_stone():
    global current_stone
    current_stone['tetronimo'] = random.choice(list(tetris_shapes.values()))
    current_stone['x_position'] = math.floor(len(matrix[0]) / 2) - math.ceil(len(current_stone['tetronimo'][0]) / 2)
    current_stone['y_position'] = 0

def reset_game():
    global score
    global matrix
    global moves_taken
    score = 0
    print('You\'ve lost! Resetting the matrix. . .')
    matrix = clear_matrix
    moves_taken = 0
    next_stone()

def collides(matrix, this_shape):
    for row in range(0, len(this_shape['tetronimo'])):
        for col in range(0, len(this_shape['tetronimo'][row])):
            if this_shape['tetronimo'][row][col] != 0:
                try:
                    if (matrix[this_shape['y_position'] + row] == None) or (matrix[this_shape['y_position'] + row][this_shape['x_position'] + col] == None) or (matrix[this_shape['y_position'] + row][this_shape['x_position'] + col] != 0):
                        return True
                except IndexError:
                    return True
    return False

def rotate(matrix, times):
    for _ in range(0, times):
        matrix = transpose(matrix)
        for i in range(0, len(matrix)):
            matrix[i].reverse()
    return matrix

def transpose(array):
    transposed_array = [[array[j][i] for j in range(len(array))] for i in range(len(array[0]))]
    return transposed_array

def get_height():
    global matrix
    remove_stone()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[row])):
            if matrix[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    set_stone()
    return 20 - min(peaks)

def get_cumulative_height():
    global matrix
    remove_stone()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[row])):
            if matrix[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    total_height = 0
    for i in range(0, len(peaks)):
        total_height = total_height + 20 - peaks[i]
    set_stone()
    return total_height

def get_relative_height():
    remove_stone()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[row])):
            if matrix[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    set_stone()
    return max(peaks) - min(peaks)

def get_holes():
    global matrix
    remove_stone()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[row])):
            if matrix[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    holes = 0
    for x in range(0, len(peaks)):
        for y in range(peaks[x], len(matrix)):
            if matrix[y][x] == 0:
                holes = holes + 1
    set_stone()
    return holes

def get_roughness():
    remove_stone()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[row])):
            if matrix[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    roughness = 0
    differences = []
    for i in range(0, len(peaks) - 1):
        roughness = roughness + abs(peaks[i] - peaks[i + 1])
        differences.append(abs(peaks[i] - peaks[i + 1]))
    set_stone()
    return roughness

def output():
    global matrix
    for i in range(0, len(matrix)):
        if i == 0:
            print(matrix[i])
        else:
            print(matrix[i])

initialize_population()

'''
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
        global matrix
        board = matrix
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
'''