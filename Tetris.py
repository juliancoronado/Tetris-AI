# took out top comments bc they were distracting, sorry

from random import randrange as rand, uniform
from GeneticAI import GeneticAI as ai
import pygame, sys, math, json, random

# game configuration
config = {
    'cell_size': 20,
    'cols': 10,
    'rows':	20,
    'delay': 50,
    'maxfps': 100
}

colors = [
    (0, 0, 0),
    (255, 0, 255),
    (0, 255, 255),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (0, 125, 255),
    (255, 0, 0)
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

moves_taken = 0
score = 0

class TetrisApp(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = 400
        self.height = 400
        self.total_stones = 0
        self.upcoming_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.init_game()
    
    def new_stone(self):
        self.stone = tetris_shapes[rand(len(tetris_shapes))]
        self.upcoming_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
        self.stone_y = 0
        self.total_stones = self.total_stones + 1
        if self.check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
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
        return board

    # def right_msg(self, msg, off_x, off_y):
    #     for _, line in enumerate(msg.splitlines()):
    #         msg_image =  pygame.font.SysFont('Arial', 15).render(
    #                 line, False, (255,255,255), (105, 105, 105))
        
    #         msgim_center_x, msgim_center_y = msg_image.get_size()
    #         msgim_center_x = 300
    #         msgim_center_y = 300
        
    #         self.screen.blit(msg_image, (220 + off_x, 300 + off_y))

    def join_matrixes(self, mat1, mat2, mat2_off):
        off_x, off_y = mat2_off
        for cy, row in enumerate(mat2):
            for cx, val in enumerate(row):
                mat1[cy+off_y-1][cx+off_x] += val
        return mat1
    
    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image =  pygame.font.SysFont('Arial', 20).render(line, False, (0, 0, 0), (255, 255, 0))
        
            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2
        
            self.screen.blit(msg_image, (self.width // 2-msgim_center_x, self.height // 2-msgim_center_y+i*22))
    
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

    def remove_row(self, board, row):
        global score
        score = score + 100
        del board[row]
        return [[0 for i in range(config['cols'])]] + board
    
    def drop(self):
        if (not self.gameover and not self.paused):
            self.stone_y += 1
            if self.check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = self.join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
                self.new_stone()
                while True:
                    for i, row in enumerate(self.board):
                        if 0 not in row:
                            self.board = self.remove_row(self.board, i)
                            break
                    else:
                        break
    
    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = self.rotate_clockwise(self.stone)
            if not self.check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def rotate_clockwise(self, shape):
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1) ]
    
    def toggle_pause(self):
        self.paused = not self.paused
    
    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def executes_moves(self, moves):
        key_actions = {
        'ESCAPE':    self.quit,
        'LEFT':        lambda: self.move(-1),
        'RIGHT':    lambda: self.move(+1),
        'DOWN':        lambda: self.drop(),
        'UP':        self.rotate_stone,
        'p':        self.toggle_pause,
        'SPACE':    self.start_game
        }
        for action in moves:
            key_actions[action]()
    
    def run(self):
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
                self.center_msg("""Game Over!""")
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    self.draw_matrix(self.board, (0,0))
                    self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
                    # self.right_msg("Genome Values: ", 0, -120)
                    # self.right_msg("Generation: ", 15, -105)
                    # self.right_msg("Genome #: ", 15, -90)
                    # self.right_msg("Fitness: ", 15, -75)
                    # self.right_msg("Example Val: ", 15, -60)
                    # self.right_msg("Moves Taken: " + str(moves_taken), 0, 0)
                    # self.right_msg("Score: " + str(score), 0, 30)
            pygame.display.update()

            weights = [0.39357083734159515, -1.8961941343266449, -5.107694873375318, -3.6314963941589093, -2.9262681134021786, -2.146136640641482, -7.204192964669836, -3.476853402227247, -6.813002842291903, 4.152001386170861, -21.131715861293525, -10.181622180279133, -5.351108175564556, -2.6888972099986956, -2.684925769670947, -4.504495386829769, -7.4527302422826, -6.3489634714511505, -4.701455626343827, -10.502314845278828, 0.6969259450910086, -4.483319180395864, -2.471375907554622, -6.245643268054767, -1.899364785170105, -5.3416512085013395, -4.072687054171711, -5.936652569831475, -2.3140398163110643, -4.842883337741306, 17.677262456993276, -4.42668539845469, -6.8954976464473585, 4.481308299774875]
            ai.choose(self.board, self.stone, self.upcoming_stone, self.stone_x, weights, self)
            
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT+1:
                    self.drop()
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == eval("pygame.K_p"):
                        self.toggle_pause()
                    
            clock.tick(config['maxfps'])

if __name__ == '__main__':
    App = TetrisApp()
App.run()