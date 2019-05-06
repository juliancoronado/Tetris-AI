import copy

class GeneticAI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = []
        row = []
        for _ in range(0, self.width):
            row.append(0)
        for _ in range(0, self.height):
            self.board.append(row)

    def update_board(self, board):
        self.board = board

    @staticmethod
    def collision(board, stone, offset):
        off_x, off_y = offset
        for cy, row in enumerate(stone):
            for cx, cell in enumerate(row):
                try:
                    if cell and board[ cy + off_y ][ cx + off_x ]:
                        return True
                except IndexError:
                    return True
        return False

    @staticmethod
    def rotate_clockwise(shape):
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1) ]

    @staticmethod
    def best_move(board, stones, stone_idx, weights, level):
        best_rotation = None
        best_offset = None
        best_score = 0
        idx = copy.deepcopy(stone_idx)
        best_stone = stones[idx]
        shapes_rotation = { 4 : 4, 8 : 2, 12 : 2, 16 : 4, 20 : 4, 24 : 2, 28 : 1 }
        flat_piece = [val for sublist in best_stone for val in sublist]
        hashed_piece = sum(flat_piece)

        for rotation in range(0, shapes_rotation[hashed_piece]):
            for offset in range(0, board.width):
                result = board.drop(best_stone, offset, level)
                if not result is None:
                    score = None
                    if idx == len(stones) - 1 :
                        heuristics = board.heuristics()
                        score = sum([a * b for a, b in zip(heuristics, weights)])
                    else:
                        _, _, score = GeneticAI.best_move(board, stones, idx + 1, weights, 2)

                    if score > best_score or best_score is 0:
                        best_score = score
                        best_offset = offset
                        best_rotation = rotation
                board.revert_last_change(level)
            best_stone = GeneticAI.rotate_clockwise(best_stone)

        return best_offset, best_rotation, best_score

    @staticmethod
    def choose(initial_board, stone, next_stone, off_x, weights, parent):
        board = GeneticAI(len(initial_board[0]), len(initial_board))
        board.update_board(copy.deepcopy(initial_board))

        offset, rotation, _ = GeneticAI.best_move(board, [stone, next_stone], 0, weights, 1)
        moves = []

        offset = offset - off_x
        for _ in range(0, rotation):
            moves.append("UP")
        for _ in range(0, abs(offset)):
            if offset > 0:
                moves.append("RIGHT")
            else:
                moves.append("LEFT")
        parent.executes_moves(moves)

    def drop(self, stone, off_x, idx):
        if off_x + len(stone[0]) > self.width or off_x < 0:
            return None
        off_y = self.height
        for row_num in range(0, self.height):
            if GeneticAI.collision(self.board, stone, (off_x, row_num)):
                off_y = row_num
                break
        for row in range(0, len(stone[0])):
            for col in range(0, len(stone)):
                num = stone[col][row]
                if num > 0:
                    self.board[off_y -1 + col][off_x + row] = -idx
        return self

    def revert_last_change(self, idx):
        for row in range(0, len(self.board)):
            for col in range(0, len(self.board[row])):
                if self.board[row][col] == -idx:
                    self.board[row][col] = 0
        #self.board = [[0 if el == -idx else el for el in row] for row in self.board]

    def col_height(self, column):
        for i in range(0, self.height):
            if self.board[i][column] != 0:
                return self.height - i
        return 0

    def heights(self):
        result = []
        for i in range(0, self.width):
            result.append(self.col_height(i))
        return result

    def col_holes(self, column):
        total_holes = 0
        max_height = self.col_height(column)
        for height, line in enumerate(reversed(self.board)):
            if height > max_height: 
                break
            if line[column] == 0 and height < max_height:
                total_holes = total_holes + 1
        return total_holes

    def row_holes(self, row):
        total_holes = 0
        for index, value in enumerate(self.board[self.height -1 - row]):
            if value == 0 and self.col_height(index) > row:
                total_holes = total_holes + 1
        return total_holes

    def heuristics(self):
        heights = self.heights()
        return heights + [sum(heights)] + self.get_total_holes(heights) + self.bumpinesses(heights) + [self.complete_lines(), (max(heights) - min(heights)), max(heights), min(heights)]

    def complete_lines(self):
        lines = 0
        for i in range (0, self.height) :
            if 0 not in self.board[i]:
                lines = lines + 1
        return lines

    def bumpinesses(self, heights):
        bumps = []
        for i in range(0, len(heights) - 1):
            bumps.append(abs(heights[i] - heights[i + 1]))
        return bumps

    def get_total_holes(self, heights):
        total_holes = []
        for j in range(0, self.width) :
            holes = 0
            for i in range (0, self.height) :
                if self.board[i][j] == 0 and self.height - i < heights[j]:
                    holes = holes + 1
            total_holes.append(holes)
        return total_holes