# Configuration pour entraînement génétique Paint Wars

import arenas

# ========== AFFICHAGE ==========

display_mode = 2  # 2 = très rapide (pas d'affichage) pour entraînement
arena = 1  # Arène 1 (classic) pour entraînement
position = False 

display_welcome_message = False
verbose_minimal_progress = False
display_robot_stats = False
display_team_stats = False
display_tournament_results = False
display_time_stats = True

# ========== OPTIMISATION ==========

evaluations = 4500  # 500 générations × 3 conditions = 1500 évaluations
it_per_evaluation = 1000  # 400 itérations par évaluation
max_iterations = evaluations * it_per_evaluation + 1

# ========== INITIALISATION ==========

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