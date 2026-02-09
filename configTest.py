import arenas
import robot_longemur 

display_mode = 0
arena = 4
position = False 
max_iterations = 2000

verbose_minimal_progress = True
display_time_stats = True

def initialize_robots(arena_size=-1, particle_box=-1):
    x_init = 10 
    y_center = arena_size // 2
    robots = []
    robots.append(robot_longemur.Robot_player(x_init, y_center, 0, name="Bot_Test", team="A"))
    return robots # NE PAS OUBLIER CETTE LIGNE