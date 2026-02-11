# Configuration file.

import arenas

# general -- first three parameters can be overwritten with command-line arguments (cf. "python tetracomposibot.py --help")

display_mode = 0
arena = 3
position = False 
max_iterations = 1000 #401*500

# affichage

display_welcome_message = False
verbose_minimal_progress = True # display iterations
display_robot_stats = False
display_team_stats = False
display_tournament_results = False
display_time_stats = True

# initialization : create and place robots at initial positions (returns a list containing the robots)

import robot_dumb
import robot_braitenberg_avoider
import robot_braitenberg_loveWall
import robot_braitenberg_loveBot
import robot_braitenberg_hateWall
import robot_challenger
import robot_braitenberg_hateBot


def initialize_robots(arena_size=-1, particle_box=-1): # particle_box: size of the robot enclosed in a square
    x_center = arena_size // 2 - particle_box / 2
    y_center = arena_size // 2 - particle_box / 2
    global position
    #x_center = arena_size // 2 - particle_box / 2
    #y_center = arena_size // 2 - particle_box / 2
    x_init_pos = []
    if position == False:
        x_init_pos = [4,93]
        orientation_champion = 0
        orientation_challenger = 180
    else:
        x_init_pos = [93,4]
        orientation_champion = 180
        orientation_challenger = 0
    robots = []
    for i in range(4):
        robots.append(robot_challenger.Robot_player(x_init_pos[0], arena_size//2-16+i*8, orientation_champion, name="", team="final"))
    return robots
