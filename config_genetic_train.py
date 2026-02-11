
import arenas


display_mode = 2  
arena = 1 
position = False 

display_welcome_message = False
verbose_minimal_progress = False
display_robot_stats = False
display_team_stats = False
display_tournament_results = False
display_time_stats = True


evaluations = 4500  
it_per_evaluation = 1000 
max_iterations = evaluations * it_per_evaluation + 1


import robot_genetic_train

def initialize_robots(arena_size=-1, particle_box=-1):
    """
    Robot d'optimisation génétique
    Position centrale pour exploration maximale
    """
    x_center = arena_size // 2 - particle_box / 2
    y_center = arena_size // 2 - particle_box / 2
    
    robots = []
    robots.append(
        robot_genetic_train.Robot_player(
            x_center, y_center, 0,
            name="Genetic Optimizer",
            team="Evolution",
            evaluations=evaluations,
            it_per_evaluation=it_per_evaluation
        )
    )
    
    return robots