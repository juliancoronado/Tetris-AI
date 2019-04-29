#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Simple tetris implementation
# 
# Control keys:
# Down - Drop block faster
# Left/Right - Move block
# Up - Rotate block clockwise
# Esc - Quit game
# P - Pause game
# A - activate AI
#
# Have fun!

# Copyright (c) 2010 "Kevin Chabowski"<kevin@kch42.de>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This code has been modified by Team 7 for Wenlin Han's CPSC481 class and
# is used primarily for educational purposes. The team is composed of:
# Julian Coronado, Theresa Tanubrata, Alexander Truong, Ying Lin Wen

from random import randrange as rand, uniform
import pygame, sys, math, json, threading

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

# The configuration
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

tetris_shapes = {
    'I': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
    'J': [[2,0,0], [2,2,2], [0,0,0]],
    'L': [[0,0,3], [3,3,3], [0,0,0]],
    'O': [[4,4], [4,4]],
    'S': [[0,5,5], [5,5,0], [0,0,0]],
    'T': [[0,6,0], [6,6,6], [0,0,0]],
    'Z': [[7,7,0], [0,7,7], [0,0,0]]
}

'''
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
'''

random_seed = 1
current_shape = {
    'x': 0,
    'y': 0, 
    'shape': []
}
upcoming_shape = None

bag = []

score = 500

bag_index = 0

# GAME VALUES
score = 0
speed = 10
save_state = None
round_state = None
next_draw = True
moves_taken = 0
move_limit = 500
move_algorithm = []
inspect_move_selection = False

# LOCALSTORAGE - probably won't be needed
# storage = None

def storing(stringed_archive):
    storage = { 'archive': stringed_archive }

# GENETIC ALGO VALUES
# number of genomes
population = 50
genomes = []
current_genome = -1
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
    global save_state
    global round_state
    global speed

    archive['population_size'] = population
    next_shape()
    apply_shape()
    save_state = get_state()
    round_state = get_state()
    create_initial_population()
    # set_interval(loop, speed)
    update()


def get_state():
    global grid
    global current_shape
    global upcoming_shape
    global bag
    global bag_index
    global random_seed
#    global score

    state = {
        'grid': clone(grid),
        'current_shape': clone(current_shape),
        'upcoming_shape': clone(upcoming_shape),
        'bag': clone(bag),
        'bag_index': clone(bag_index),
        'random_seed': clone(random_seed)
        # score: clone(score)
    }
    return state

def load_state(state):
    global grid
    global current_shape
    global upcoming_shape
    global bag
    global bag_index
    global random_seed

    grid = clone(state['grid'])
    current_shape = clone(state['current_shape'])
    upcoming_shape = clone(state['upcoming_shape'])
    bag = clone(state['bag'])
    bag_index = clone(state['bag_index'])
    random_seed = clone(state['random_seed'])

    output()

def create_initial_population():
    global genomes
    global current_genome
    genomes = []
    for _ in range(0, population):
        genome = {
            'id': uniform(0, 1),
            'rows_cleared': uniform(0, 1) - 0.5,
            'height_weight': uniform(0, 1) - 0.5,
            'height_cumulative': uniform(0, 1) - 0.5,
            'height_relative': uniform(0, 1) - 0.5,
            'holes': uniform(0, 1) - 0.5,
            'roughness': uniform(0, 1) - 0.5,
            'fitness': -1
        }
        genomes.append(genome)
    evaluate_next_genome()

# SELECTION
def evaluate_next_genome():
    global moves_taken
    global current_genome
    global genomes
    global round_state
    global load_state

    current_genome = current_genome + 1
    if current_genome == len(genomes):
        evolve()
    
    load_state(round_state)
    moves_taken = 0
    make_next_move()


# CROSSOVER
# new generation
def evolve():
    global current_genome
    global generation
    global genomes
    global population
    global round_state
    global generation

    current_genome = 0
    generation = generation + 1

    reset_game()
    round_state = get_state()

    genomes = sorted(genomes, key = lambda k: k['fitness'], reverse=True) # CHECK THIS OUT THIS MAY NEED TO BE MODIFIED
    # archive['elites'].append(clone(genomes[0]))
    # print("Elite's fitness:", genomes[0].fitness)

    while (len(genomes) > (population / 2)):
        genomes.pop()
    
    total_fitness = 0
    for i in range(0, len(genomes)):
        total_fitness = total_fitness + genomes[i]['fitness']

    children = []
    children.append(clone(genomes[0]))

    while len(children) < population:
        children.append(make_child(get_random_genome(), get_random_genome()))
    
    genomes = []
    genomes = genomes + children
    
    # might not need these next 3 lines
    #archive['genomes'] = clone(genomes)
    #archive['current_generation'] = clone(gen)
    #storing(json.dumps(archive, separators=(',', ':')))

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
    global genomes
    return genomes[random_weight_num(0, len(genomes - 1))]

def random_weight_num(min, max):
    # returns a random number between 0 and max length of genomes
    return math.floor(math.pow(uniform(0, 1), 2) * (max - min + 1) + min) 

def random_choice(one, two):
    if round(uniform(0, 1)) == 0:
        return clone(one)
    else:
        return clone(two)

def make_next_move():
    global moves_taken
    global move_limit
    global next_draw
    global genomes

    moves_taken = moves_taken + 1

    if moves_taken > move_limit:
        genomes[current_genome]['fitness'] = clone(score)
        evaluate_next_genome()
    else:
        old_draw = clone(next_draw)
        next_draw = False
        possible_moves = get_all_possible_moves()
        last_state = get_state()
        next_shape()
        
        for i in range(0, len(possible_moves)):
            next_move = get_highest_rated_move(get_all_possible_moves())
            possible_moves[i]['rating'] = possible_moves[i]['rating'] + next_move['rating']
        
        load_state(last_state)
        move = get_highest_rated_move(possible_moves)

        for i in range(0, move['rotations']):
            rotate_shape()

        if move['translation'] < 0:
            for lefts in range(0, abs(move['translation'])):
                move_left()

        elif move['translation'] > 0:
            for rights in range(0, move['translation']):
                move_right()

        if (inspect_move_selection):
            move_algorithm = move['algorithm']
        
        next_draw = old_draw

        output()

        #update_score()
    
def get_all_possible_moves():
    global current_shape

    last_state = get_state()
    possible_moves = []
    possible_move_ratings = []
    iterations = 0

    for r in range(0, 4):
        oldX = []

        for t in range(-5, 6):
            iterations = iterations + 1
            load_state(last_state)

            for _ in range(0, r):
                rotate_shape()
            
            if t < 0:
                for _ in range(0, abs(t)):
                    move_left()
            elif t > 0:
                for _ in range(0, t):
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
                rating = rating + (algorithm['rows_cleared'] * genomes[current_genome]['rows_cleared'])
                rating = rating + (algorithm['height_weight'] * genomes[current_genome]['height_weight'])
                rating = rating + (algorithm['height_cumulative'] * genomes[current_genome]['height_cumulative'])
                rating = rating + (algorithm['height_relative'] * genomes[current_genome]['height_relative'])
                rating = rating + (algorithm['holes'] * genomes[current_genome]['holes'])
                rating = rating + (algorithm['roughness'] * genomes[current_genome]['roughness'])

                if move_down_results['lose']:
                    rating = rating - 500

                possible_moves.append({
                    'rotations': r,
                    'translation': t,
                    'rating': rating,
                    'algorithm': algorithm
                })

                oldX.append(current_shape['x'])
    load_state(last_state)
    return possible_moves

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
    return stringed_object

def contains(oldX, currentX):
    idx = len(oldX) - 1
    while idx >= 0 and len(oldX) != 0:
        if oldX[idx] == currentX:
            return True
        if idx != 0:
            idx = idx - 1
        else:
            break
    return False

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
    #update_score()

def move_down():
    global current_shape
    global grid

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
            reset_game()
        result['moved'] = False
    apply_shape()
    # score = score + 1
    # update_score()
    output()

    for i in range(0, len(grid)):
        print(grid[i])
        if i == 19:
            print('\n')

    name = input("PRESS ENTER")

    return result

def move_left():
    global current_shape
    global grid

    remove_shape()
    current_shape['x'] = current_shape['x'] - 1

    if collides(grid, current_shape) or current_shape['x'] < 0:
        current_shape['x'] = current_shape['x'] + 1
    apply_shape()

    for i in range(0, len(grid)):
        print(grid[i])
        if i == 19:
            print(grid[i], '\n')

def move_right():
    global current_shape
    global grid

    remove_shape()
    current_shape['x'] = current_shape['x'] + 1
    if collides(grid, current_shape):
        current_shape['x'] = current_shape['x'] - 1
    apply_shape()

    for i in range(0, len(grid)):
        print(grid[i])
        if i == 19:
            print(grid[i], '\n')

def clear_rows():
    global grid

    clear_rows_list = []
    for row in range(0, len(grid)):
        empty_spaces = False
        for col in range(0, len(grid[row])):
            if grid[row][col] == 0:
                empty_spaces = True
        if not empty_spaces:
            clear_rows_list.append(row)
    
    # score, can take out
    #if len(clear_rows_list) == 1:
    #    score = score + 400
    #elif len(clear_rows_list) == 2:
    #    score = score + 1000
    #elif len(clear_rows_list) == 3:
    #    score = score + 3000
    #elif len(clear_rows_list) == 4:
    #    score = score + 12000
    
    cleared_rows = clone(len(clear_rows_list))

    for i in range(len(clear_rows_list) - 1, -1, -1):
        grid.pop(clear_rows_list[i])

    while len(grid) < 20:
        grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    return cleared_rows

def apply_shape():
    global current_shape
    global grid

    for row in range(0, len(current_shape['shape'])):
        for col in range(0, len(current_shape['shape'][row])):
            if current_shape['shape'][row][col] != 0:
                grid[current_shape['y'] + row][current_shape['x'] + col] = current_shape['shape'][row][col]

def remove_shape():
    global current_shape
    global grid

    for row in range(0, len(current_shape['shape'])):
        for col in range(0, len(current_shape['shape'][row])):
            if current_shape['shape'][row][col] != 0:
                grid[current_shape['y'] + row][current_shape['x'] + col] = 0

def rotate_shape():
    global current_shape
    global grid

    remove_shape()
    current_shape['shape'] = rotate(current_shape['shape'], 1)
    if collides(grid, current_shape):
        current_shape['shape'] = rotate(current_shape['shape'], 3)
    apply_shape()

def next_shape():
    global grid
    global bag
    global bag_index
    global random_seed
    global tetris_shapes
    global current_shape
    global upcoming_shape

    bag_index = bag_index + 1
    if len(bag) == 0 or bag_index == len(bag):
        generate_bag()
    if bag_index == (len(bag) - 1):
        previous_seed = random_seed
        upcoming_shape = tetris_shapes[random_key(tetris_shapes)]
        random_seed = previous_seed
    else:
        upcoming_shape = tetris_shapes[bag[bag_index + 1]]
    
    current_shape['shape'] = tetris_shapes[bag[bag_index]]
    current_shape['x'] = math.floor(len(grid[0]) / 2) - math.ceil(len(current_shape['shape'][0]) / 2)
    current_shape['y'] = 0

def generate_bag():
    global bag
    global tetris_shapes
    global bag_index
    bag = [None, None, None, None, None, None, None]
    contents = ""
    for i in range(0, 7):
        tetronimo = random_key(tetris_shapes)
        while (contents.find(tetronimo) != -1):
            tetronimo = random_key(tetris_shapes)
        bag[i] = tetronimo
        contents = contents + tetronimo
    bag_index = 0

def random_key(obj):
    global random_seed

    list_shapes = []

    for key in obj.keys():
        list_shapes.append(key)

    random_seed = (random_seed * 9301 + 49297) % 233280
    random = random_seed / 233280
    idx = math.floor(random * len(list_shapes))
    return list_shapes[idx]

def reset_game():
    # score = 0
    global grid
    global moves_taken

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

def collides(grid, this_shape):
    for row in range(0, len(this_shape['shape'])):
        for col in range(0, len(this_shape['shape'][row])):
            if this_shape['shape'][row][col] != 0:
                try:
                    if (grid[this_shape['y'] + row] == None) or (grid[this_shape['y'] + row][this_shape['x'] + col] == None) or (grid[this_shape['y'] + row][this_shape['x'] + col] != 0):
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
    global grid
    remove_shape()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(grid)):
        for col in range(0, len(grid[row])):
            if grid[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    apply_shape()
    return 20 - min(peaks)

def get_cumulative_height():
    global grid
    remove_shape()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(grid)):
        for col in range(0, len(grid[row])):
            if grid[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    total_height = 0
    for i in range(0, len(peaks)):
        total_height = total_height + 20 - peaks[i]
    apply_shape()
    return total_height

def get_relative_height():
    remove_shape()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(grid)):
        for col in range(0, len(grid[row])):
            if grid[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    apply_shape()
    return max(peaks) - min(peaks)

def get_holes():
    global grid
    remove_shape()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(grid)):
        for col in range(0, len(grid[row])):
            if grid[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    holes = 0
    for x in range(0, len(peaks)):
        for y in range(peaks[x], len(grid)):
            if grid[y][x] == 0:
                holes = holes + 1
    apply_shape()
    return holes

def get_roughness():
    remove_shape()
    peaks = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    for row in range(0, len(grid)):
        for col in range(0, len(grid[row])):
            if grid[row][col] != 0 and peaks[col] == 20:
                peaks[col] = row
    roughness = 0
    differences = []
    for i in range(0, len(peaks) - 1):
        roughness = roughness + abs(peaks[i] - peaks[i + 1])
        differences.append(abs(peaks[i] - peaks[i + 1]))
    apply_shape()
    return roughness

def output():
    global next_draw
    global grid
    if next_draw:
        for i in range(0, len(grid)):
            if i == 0:
                print(grid[i])
            else:
                print('\n')
                print(grid[i])

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def loop():
    update()
    #set_interval(loop, speed)

initialize_population()
