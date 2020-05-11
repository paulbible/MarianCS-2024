"""
    A simple game to have some fun and explore python programming.
    Author: Dr. Paul W. Bible, pbible@marian.edu

    Access: https://github.com/paulbible/MarianCS-2024
"""
import pygame
import sys
import math
from pygame.locals import *


def main():
    # set up the mixer, pygame, and the game clock
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.init()

    # Timing, these variables help keep up with times and timers
    clock = pygame.time.Clock()
    last_ticks = pygame.time.get_ticks()  # starter tick
    delta_t = 0

    # create some colors in RGB, range 0 - 255
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # set up the game window
    # set up the window
    # x,y  ... -> ... width height
    win_width = 900
    win_height = 900
    grid_w = int(win_width/10)
    grid_h = int(win_height/10)
    windowSurface = pygame.display.set_mode((win_width, win_height), 0, 32)
    pygame.display.set_caption('Maraian CS Game Demo')

    # load some game assets, images and sounds
    # sounds
    lazer_sound = pygame.mixer.Sound("../data/sound/lazer1.wav")
    explode_sound = pygame.mixer.Sound("../data/sound/explode1.wav")
    bg_image = pygame.image.load('../data/BlueTexture.png').convert()
    bg_image = pygame.transform.scale(bg_image, (win_width, win_height))
    # images
    wall_block = pygame.image.load('../data/mark_finish.png').convert_alpha()
    wall_block = pygame.transform.scale(wall_block, (grid_w, grid_h))
    robot_img = pygame.image.load('../data/robot/example.png').convert_alpha()
    robot_rect = robot_img.get_rect()
    robot_offset_x = robot_rect[2] / 2
    robot_offset_y = robot_rect[3] / 2

    '''
        The Game Map
          To make creating maps easier, we use a simple text file to specify a tile map.
          The tile mape is 10-by-10. 
          Every '#' creates a wall in the map and the player starts at the position marked
          with a 'p'. This just makes the map easy to create. You are not locked on only
          the grid locations.
          
          Example: given in the 'map.txt' file
    '''
    tile_map = load_map('../data/map.txt')
    print_text_map(tile_map)
    start_row, start_col = player_start(tile_map)
    print("Player starts a row:", start_row, " and column:", start_col)

    # convert the tile coordinates in row/column to game map x and y
    # place in the center of the grid tile (default, upper left corner)
    player_x = (start_col * grid_w) + grid_w / 2
    player_y = (start_row * grid_h) + grid_h / 2


    '''
        The Main Game Loop
        This loop keeps processing data until the game is quit.
        The process goes:
        1) handle any events (key presses etc.)
        2) update game entities (collisions, game actions)
        3) Draw everything onto the screen.
        4) post processing (calculate timings etc.)
    '''
    keep_playing = True
    while keep_playing:
        ##### 1) Handle events #####
        for event in pygame.event.get():
            if event.type == QUIT:
                keep_playing = False
            elif event.type == MOUSEBUTTONDOWN:
                print('mouse clicked')
                lazer_sound.play() # turn on later
            elif event.type == KEYDOWN:
                print("key pressed")
                if event.key == K_RIGHT or event.key == K_d:
                    player_x += 5
            elif event.type == KEYUP:
                print("key released")

        # get the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = look_angle(player_x, player_y, mouse_x, mouse_y)

        ##### update game entities #####
        # TODO


        ##### Draw #####
        # draw background, do this first
        windowSurface.blit(bg_image, (0, 0))

        # draw walls
        for r in range(len(tile_map)):
            for c in range(len(tile_map[0])):
                # for each position in the grid, check it is a wall.
                if tile_map[r][c] == '#':
                    # draw the wall at that location
                    windowSurface.blit(wall_block, (c*grid_w, r*grid_h))

        # draw the player, but rotated to face the mouse
        blitRotate(windowSurface, robot_img, (player_x, player_y), (robot_offset_x, robot_offset_y), angle)




        # draw the window onto the screen, the last drawing step.
        pygame.display.update()

        ##### post loop processing #####
        # delay to lock frame rate
        clock.tick(60)
        # calculate delta_t, important for physics / movement
        delta_t = pygame.time.get_ticks() - last_ticks
        last_ticks = pygame.time.get_ticks()

    # shut down Pygame
    pygame.quit()
    # end of the program (main function)
    print("Goodbye!")


# load the map and return a table (matrix) of characters
def load_map(filename):
    tile_map = []
    with open(filename, 'r') as f:
        for i in range(10):
            line = f.readline()
            if line:
                tile_map.append(line[:10])
    return tile_map


# print out the characters in the map representation
def print_text_map(tile_map):
    for row in tile_map:
        print(row)


# find where the player should start
def player_start(tile_map):
    map_rows = len(tile_map)
    map_cols = len(tile_map[0])
    for i in range(map_rows):
        for j in range(map_cols):
            if tile_map[i][j] == 'p':
                return i, j


def look_angle(player_x, player_y, mouse_x, mouse_y):
    mouse_vector = pygame.math.Vector2(mouse_x, mouse_y)
    player_position_vector = pygame.math.Vector2(player_x, player_y)
    player_to_mouse_vector = (mouse_vector - player_position_vector).normalize()
    down_vector = pygame.math.Vector2(0, 1)
    angle = math.degrees(math.acos(player_to_mouse_vector.dot(down_vector)))

    if player_x > mouse_x:
        angle = -1.0 * angle

    return angle


# Rotate an image around it's center. Lets the robot look at your mouse.
# code from https://stackoverflow.com/a/54714144/2912901
def blitRotate(surf, image, pos, originPos, angle):

    # calcaulate the axis aligned bounding box of the rotated image
    w, h       = image.get_size()
    box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot
    pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (pos[0] - originPos[0] + min_box[0] - pivot_move[0], pos[1] - originPos[1] - max_box[1] + pivot_move[1])

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)

    # rotate and blit the image
    surf.blit(rotated_image, origin)

    # draw rectangle around the image
    # pygame.draw.rect (surf, (255, 0, 0), (*origin, *rotated_image.get_size()),2)

# call main to run the program
main()
