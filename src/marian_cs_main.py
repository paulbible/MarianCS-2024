"""
    A simple game to have some fun and explore python programming.
    Author: Dr. Paul W. Bible, pbible@marian.edu

    Access: https://github.com/paulbible/MarianCS-2024
"""
import pygame
import sys
import math
from pygame.locals import *
from graph_tools import create_tile_graph, get_shortest_path


class Animation(object):
    def __init__(self, frames, duration, location):
        self.frames = frames
        self.duration = duration
        self.active = True
        self.start = pygame.time.get_ticks()
        self.location = location

    def reset(self):
        self.active = True
        self.start = pygame.time.get_ticks()

    def draw(self, surface):
        time_since = pygame.time.get_ticks() - self.start
        if time_since >= self.duration:
            self.active = False
        else:
            frame = int(time_since/(self.duration/len(self.frames)))
            surface.blit(self.frames[frame], self.location)


class Projectile(object):
    def __init__(self, location, direction, speed, frames, duration):
        self.location = location
        self.direction = direction
        self.speed = speed
        self.animation = Animation(frames, duration, location)

    def next_location(self, delta):
        return self.location + self.direction*delta* self.speed

    def update(self, location):
        self.location = location
        self.animation.location = location

    def draw(self, surface):
        self.animation.draw(surface)
        if not self.animation.active:
            self.animation.reset()


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
    explode_sound.set_volume(0.25)
    bg_image = pygame.image.load('../data/BlueTexture.png').convert()
    bg_image = pygame.transform.scale(bg_image, (win_width, win_height))
    # images
    wall_block = pygame.image.load('../data/mark_finish.png').convert_alpha()
    wall_block = pygame.transform.scale(wall_block, (grid_w, grid_h))
    robot_img = pygame.image.load('../data/robot/example.png').convert_alpha()
    robot_rect = robot_img.get_rect()
    robot_offset_x = robot_rect[2] / 2
    robot_offset_y = robot_rect[3] / 2

    # explosion animation
    explosion_sheet = pygame.image.load('../data/explosion.png').convert_alpha()
    explosion_frames = []
    for i in range(5):
        tile = explosion_sheet.subsurface(pygame.Rect(i*16, 0, 16, 16))
        explosion_frames.append(tile)

    explosions = []

    '''
    # print(explosion_sheet.get_rect())
    expl_timer = 0
    expl_max_milliseconds = 500
    frames = 5
    do_explode = False
    explode_location = (20, 20)
    '''

    enemy_sheet = pygame.image.load('../data/power-up.png').convert_alpha()
    print(enemy_sheet.get_rect())
    enemy1_frames = [enemy_sheet.subsurface(pygame.Rect(0, 0, 16, 16)),
                     enemy_sheet.subsurface(pygame.Rect(16, 0, 16, 16))]
    enemy2_frames = [enemy_sheet.subsurface(pygame.Rect(0, 16, 16, 16)),
                     enemy_sheet.subsurface(pygame.Rect(16, 16, 16, 16))]

    laser_sheet = pygame.image.load('../data/laser-bolts.png')
    laser1_frames = [laser_sheet.subsurface(pygame.Rect(0, 0, 16, 16)),
                     laser_sheet.subsurface(pygame.Rect(16, 0, 16, 16))]
    laser_offset = 8

    '''
        The Game Map
          To make creating maps easier, we use a simple text file to specify a tile map.
          The tile map is 10-by-10. 
          Every '#' creates a wall in the map and the player starts at the position marked
          with a 'p'. This just makes the map easy to create. You are not locked on only
          the grid locations.
          
          Example: given in the 'map.txt' file
    '''
    tile_map = load_map('../data/map.txt')
    # print_text_map(tile_map)
    start_row, start_col = player_start(tile_map)
    # print("Player starts a row:", start_row, " and column:", start_col)

    # a graph used by enemies to find the player
    graph = create_tile_graph('../data/map.txt')

    # convert the tile coordinates in row/column to game map x and y
    # place in the center of the grid tile (default, upper left corner)
    player_x = (start_col * grid_w) + grid_w / 2
    player_y = (start_row * grid_h) + grid_h / 2
    player_location = pygame.math.Vector2(player_x, player_y)

    player_speed = 0.25
    player_size = 25

    enemy_row, enemy_col = enemy_start(tile_map)
    enemy_x = (enemy_col * grid_w) + grid_w / 2
    enemy_y = (enemy_row * grid_h) + grid_h / 2
    enemy_location = pygame.math.Vector2(enemy_x, enemy_y)

    path = get_shortest_path(enemy_row, enemy_col, start_row, start_col, graph)
    print(path)


    # get a container for keys that are being pressed
    keys_pressed = []


    # physics / movement
    vector_up = pygame.math.Vector2(0, -1)
    vector_down = pygame.math.Vector2(0, 1)
    vector_left = pygame.math.Vector2(-1, 0)
    vector_right = pygame.math.Vector2(1, 0)


    # get the list of projectiles
    projectiles = []

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
        # get the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_direction = look_direction(player_location.x, player_location.y, mouse_x, mouse_y)
        angle = look_angle(player_location.x, player_location.y, mouse_x, mouse_y)

        for event in pygame.event.get():
            if event.type == QUIT:
                keep_playing = False
            elif event.type == MOUSEBUTTONDOWN:
                # print('mouse clicked', mouse_x, mouse_y)
                lazer_sound.play()
                p = Projectile(player_location, player_direction, 0.4, laser1_frames, 500)
                projectiles.append(p)

                # lazer_sound.play() # turn on later
            elif event.type == KEYDOWN:
                # print("key pressed")
                keys_pressed.append(event.key)
            elif event.type == KEYUP:
                # print("key released")
                keys_pressed.remove(event.key)



        ##### update game entities #####
        # update player
        player_velocity = pygame.math.Vector2(0, 0)
        if K_RIGHT in keys_pressed or K_d in keys_pressed:
            #player_x += speed
            player_velocity += vector_right

        if K_LEFT in keys_pressed or K_a in keys_pressed:
            #player_x -= speed
            player_velocity += vector_left

        if K_UP in keys_pressed or K_w in keys_pressed:
            #player_y -= speed
            player_velocity += vector_up

        if K_DOWN in keys_pressed or K_s in keys_pressed:
            #player_y += speed
            player_velocity += vector_down

        if player_velocity.length() > 0:
            player_velocity = player_velocity.normalize()
            new_location = player_location + player_velocity * delta_t * player_speed
        else:
            new_location = player_location

        if collide_wall(new_location, player_size, tile_map, grid_w, grid_h):
            # print('hit wall!!')
            pass
        elif is_inside_window(new_location, player_size, win_width, win_height):
            player_location = new_location


        # Update projectiles
        for projectile in projectiles:
            new_projectile_location = projectile.next_location(delta_t)
            distance = new_projectile_location.distance_to(enemy_location)
            if distance < 15:
                print('Enemy Hit!')
                explode_sound.play()

                # explode_location = (mouse_x, mouse_y)
                explosions.append(Animation(explosion_frames, 500, new_projectile_location))
                # reset the enemy location
                enemy_location = pygame.math.Vector2(enemy_x, enemy_y)
                projectiles.remove(projectile)

            # delete projectiles that go off the screen
            if not windowSurface.get_rect().collidepoint(new_projectile_location.x, new_projectile_location.y):
                # print('removing projectile')
                projectiles.remove(projectile)
            else:
                projectile.update(new_projectile_location)

            # delete projectiles that collide with a wall
            if collide_wall(new_projectile_location, 1, tile_map, grid_w, grid_h):
                projectiles.remove(projectile)
                new_projectile_location.x -= 4
                explosions.append(Animation(explosion_frames, 500, new_projectile_location))



        # update enemy
        enemy_row, enemy_col = vector_to_rc(enemy_location, grid_w, grid_h)
        goal_row, goal_col = vector_to_rc(player_location, grid_w, grid_h)
        # print(enemy_row, enemy_col)
        path = get_shortest_path(enemy_row, enemy_col, goal_row, goal_col , graph)
        # print(path)

        if len(path) > 1 and enemy_location.distance_to(player_location) > 100:
            target = pygame.math.Vector2(graph.get_vertex_xy(path[1], grid_w, grid_h))
        else:
            target = player_location

        direction = (target - enemy_location)

        if direction.length() > 0:
            enemy_to_player = (target - enemy_location).normalize()
            new_enemy_location = enemy_location + enemy_to_player * delta_t * (player_speed * 0.5)

            if collide_wall(new_enemy_location, 1, tile_map, grid_w, grid_h):
                # print('hit wall!!')
                pass
            elif is_inside_window(new_enemy_location, player_size/2, win_width, win_height):
                enemy_location = new_enemy_location

        if enemy_location.distance_to(player_location) < 25:
            print("Player hit, take damage")


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
        # blitRotate(windowSurface, robot_img, (player_x, player_y), (robot_offset_x, robot_offset_y), angle)
        blitRotate(windowSurface, robot_img, player_location, (robot_offset_x, robot_offset_y), angle)

        # draw projectiles
        for projectile in projectiles:
            projectile.draw(windowSurface)


        # draw explosions
        for exp in explosions:
            exp.draw(windowSurface)
            # deactivate explosions after their animation is over
            if not exp.active:
                explosions.remove(exp)

        # draw / animate enemy
        if int(pygame.time.get_ticks()/400) % 2 == 0:
            windowSurface.blit(enemy2_frames[0], (enemy_location.x - laser_offset, enemy_location.y - laser_offset))
        else:
            windowSurface.blit(enemy2_frames[1], (enemy_location.x - laser_offset, enemy_location.y - laser_offset))

        # Draw debug info
        # pygame.draw.line(windowSurface, BLACK, target, enemy_location)

        # draw the window onto the screen, the last drawing step.
        pygame.display.update()

        ##### post loop processing #####
        # delay to lock frame rate
        clock.tick(60)
        # calculate delta_t, important for physics / movement
        delta_t = pygame.time.get_ticks() - last_ticks
        # delta_t = delta_t/5
        last_ticks = pygame.time.get_ticks()

    # shut down Pygame
    pygame.quit()
    # end of the program (main function)
    print("Goodbye!")


def vector_to_rc(location, grid_width, grid_height):
    r = int(location.y/grid_height)
    c = int(location.x/grid_width)
    return r, c


# check if the location is inside the window
def is_inside_window(location, size, window_width, window_height):
    if location.x < size or location.x > window_width - size:
        return False

    if location.y < size or location.y > window_height - size:
        return False

    return True


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


# find where the player should start
def enemy_start(tile_map):
    map_rows = len(tile_map)
    map_cols = len(tile_map[0])
    for i in range(map_rows):
        for j in range(map_cols):
            if tile_map[i][j] == 'e':
                return i, j


def look_direction(player_x, player_y, mouse_x, mouse_y):
    mouse_vector = pygame.math.Vector2(mouse_x, mouse_y)
    player_position_vector = pygame.math.Vector2(player_x, player_y)
    player_to_mouse_vector = (mouse_vector - player_position_vector).normalize()
    return player_to_mouse_vector


def look_angle(player_x, player_y, mouse_x, mouse_y):
    mouse_vector = pygame.math.Vector2(mouse_x, mouse_y)
    player_position_vector = pygame.math.Vector2(player_x, player_y)
    player_to_mouse_vector = (mouse_vector - player_position_vector).normalize()
    down_vector = pygame.math.Vector2(0, 1)
    angle = math.degrees(math.acos(player_to_mouse_vector.dot(down_vector)))

    if player_x > mouse_x:
        angle = -1.0 * angle

    return angle


def collide_wall(position, radius, tile_map, grid_width, grid_height):
    map_rows = len(tile_map)
    map_cols = len(tile_map[0])
    for r in range(map_rows):
        for c in range(map_cols):
            if tile_map[r][c] == '#':
                rect = pygame.Rect(c*grid_width, r*grid_height, grid_width, grid_height)
                if collide_circle_rect(position, radius, rect):
                    return True
    return False




# detect if a circle and rectangle collide / intersect
# http://www.jeffreythompson.org/collision-detection/circle-rect.php
def collide_circle_rect(point, radius, rect):
    #  assume point is a pygame.math.Vector2
    rect_x, rect_y, width, height = rect

    test_x = point.x
    test_y = point.y

    if point.x < rect_x:
        test_x = rect_x
    elif point.x > rect_x + width:
        test_x = rect_x + width

    if point.y < rect_y:
        test_y = rect_y
    elif point.y > rect_y + height:
        test_y = rect_y + height

    dist_x = point.x - test_x
    dist_y = point.y - test_y
    distance = math.sqrt(dist_x**2 + dist_y**2)
    if distance <= radius:
        return True
    else:
        return False


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
