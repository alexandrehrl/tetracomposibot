# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Alexandre Hurel 21231339
#  Prénom Nom No_étudiant/e : Mayes Haddab 21206341
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import *
import random

nb_robots = 0

#Principe du code : 
#On a implémenté plusieurs comportements de différentes manières (braitenberg modifié, subsomption et arbre de décision (priorité))
#On a 3 robots qui ont de la subsomption pour choisir entre ces comportements
#On a 1 robot qui est purement génétique (optimisé à l'aide d'un fichier externe)
#Tous les robots suivent un ordre de priorité qu'on définit plus bas, mais ont tous un trait de personnalité différent (comportement plus présent)

#IMPORTANT POUR JUSTIFIER QUE CES COMPORTEMENTS SONT BRAITENBERG : 
#ligne 461 : rotation = max(-1.0, min(1.0, rotation))
#on a aussi inversé les valeurs des senseurs pour des valeurs qui nous sont plus "naturelles" :
# 1 pour danger, 0 pour pas de danger    

# COMPORTEMENTS BRAITENBERG

def cruise_braitenberg(sensor_to_wall):
    """
    comportement croisière, vitesse optimale, virages le moins serrés possible pour ne pas perdre de la vitesse
    implémentation braitenberg légèrement modifié
    """
    translation = 1.0 #vitesse opti
    
    rotation = 0.0
    rotation -= sensor_to_wall[sensor_front_left] * 0.15 #petit virage à droite
    rotation += sensor_to_wall[sensor_front_right] * 0.15 #petit virage à gauche
    
    # Variation aléatoire pour éviter trajectoires répétitives, donc couvrir un maximum de terrain
    #Avec une proba de 20%, on change légèrement la trajectoire de 0.4 (+ ou -)
    if random.random() < 0.2:
        rotation += random.uniform(-0.4, 0.4)
    
    return translation, rotation


def avoid_walls_braitenberg(sensor_to_wall):
    """
    comportement pour éviter les murs
    implémentation braitenberg légèrement modifié
    """
    translation = 0.9 #légèrement sous la vitesse opti pour tourner de manière plus serrée, on a trouvé cette valeur experimentalement
    
    rotation = 0.0 #de base rotation à 0 pour être droit par rapport au mur qui pose problème
    
    rotation -= sensor_to_wall[sensor_front_left] * 1.5 #on tourne beaucoup à droite en prévention du mur devant à gauche
    rotation -= sensor_to_wall[sensor_left] * 0.8 #on tourne moins à droite en fonction d'à quel point on est proche du mur juste à gauche
    
    rotation += sensor_to_wall[sensor_front_right] * 1.5 
    rotation += sensor_to_wall[sensor_right] * 0.8
    
    # réaction forte si mur devant
    if sensor_to_wall[sensor_front] > 0.5:
        translation = 0.5
        # tourner du côté le plus libre, on a 2 variables d'espace pour comparer l'espace libre qu'on a à gauche et à droite, et on tourne en fonction
        left_space = sensor_to_wall[sensor_front_left] + sensor_to_wall[sensor_left] + sensor_to_wall[sensor_rear_left]
        right_space = sensor_to_wall[sensor_front_right] + sensor_to_wall[sensor_right] + sensor_to_wall[sensor_rear_right]
        rotation = -1.0 if left_space > right_space else 1.0
    
    return translation, rotation


def avoid_robots_braitenberg(sensors, sensor_to_robot):
    """
    comportement pour éviter les robots, alliés comme ennemis pour survivre
    implémentation braitenberg légèrement modifiée
    """
    #on se remet droit
    rotation = 0.0
    
    rotation -= (sensor_to_robot[sensor_front_left] + sensor_to_robot[sensor_left]) * 2.0 #tourner à droite
    rotation += (sensor_to_robot[sensor_front_right] + sensor_to_robot[sensor_right]) * 2.0 #tourner à gauche
    
    # réaction forte si robot devant
    robot_front = max(sensor_to_robot[sensor_front], sensor_to_robot[sensor_front_left], sensor_to_robot[sensor_front_right])
    
    #subsomption sur plusieurs cas pour ne pas être bloqué si 2 robots arrivent en même temps.
    if robot_front > 0.6:
        translation = 0.0
        if sensor_to_robot[sensor_front_left] + sensor_to_robot[sensor_left] > sensor_to_robot[sensor_front_right] + sensor_to_robot[sensor_right]:
            rotation = -1.0
        else:
            rotation = 1.0
    elif robot_front > 0.3:
        translation = 0.6
    else:
        translation = 1.0
    
    return translation, rotation


# COMPORTEMENTS "trait de caractère""


def diagonal_sweeper(sensor_to_wall):
    """
    balayage aléatoire + fort que le comportement croisière de base
    implémentation semi braitenbeg semi subsomption
    """
    translation = 1.0
    #tourner à chaque mur
    rotation = 0.0
    rotation -= sensor_to_wall[sensor_front_left] * 0.6
    rotation += sensor_to_wall[sensor_front_right] * 0.6
    
    #probabilité de 30% de changer de trajectoire sans forcément rencontrer de mur
    if random.random() < 0.3:
        choice = random.random()
        #une fois dans ces 30%, on a les probabilités suivante : 
        #40% de chance de tourner faiblement
        #30% de chance de tourner modéremment
        #30% de chance de tourner fortement
        if choice < 0.4:
            rotation += random.uniform(-0.3, 0.3)
        elif choice < 0.7:
            rotation += random.choice([-0.6, 0.6])
        else:
            rotation += random.choice([-0.9, 0.9])
    
    # nécessaire pour ne pas faire de cercle
    # on s'assure de tourner si on est proche d'un mur (max_wall prend tous les murs)
    max_wall = max(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right], 
                   sensor_to_wall[sensor_left], sensor_to_wall[sensor_right], 
                   sensor_to_wall[sensor_rear_left], sensor_to_wall[sensor_rear_right], sensor_to_wall[sensor_rear])
    if max_wall < 0.2:
        rotation += random.uniform(-0.4, 0.4)
    
    return translation, rotation


def wall_hugger_with_gap_detection(sensors, sensor_to_wall):
    """
    Idéalement, ce comportement suit les murs et repère les trous à 90 degrés, en pratique ce n'est pas trop le cas
    N'est pas assez haut dans la priorité pour avoir un réel impact dans l'arene 3 par exemple
    """
    translation = 1.0
    
    wall_left = sensor_to_wall[sensor_left]
    wall_front_left = sensor_to_wall[sensor_front_left]
    wall_front = sensor_to_wall[sensor_front]
    
    # Détection de trou (uniquement à gauche car robot va forcément tourner sur lui même et être dans ce cas (grâce à not système de débloquage))
    gap_detected = (wall_left < 0.15 and wall_front_left < 0.2 and wall_front < 0.3)
    
    if gap_detected:
        rotation = 0.9
        translation = 1.0
    
    elif wall_left > 0.1:
        target_distance = 0.2
        current_distance = 1.0 - sensors[sensor_left]
        error = current_distance - target_distance
        
        rotation = error * -2.0
        
        if wall_front > 0.5:
            rotation = -0.9
            translation = 0.7
    
    else:
        translation = 1.0
        rotation = 0.5
    
    return translation, rotation


def enemy_chaser_braitenberg(sensor_to_enemy):
    """
    LOVEBOT version braitenberg vraiment modifiée
    On utilise les puissances de 10 pour faire des énormes virages
    """
    
    enemy_front = sensor_to_enemy[sensor_front]
    enemy_front_left = sensor_to_enemy[sensor_front_left]
    enemy_front_right = sensor_to_enemy[sensor_front_right]
    
    #translation trouvée experimentalement (être lent de base pour ajuster sa trajectoire puis rattraper son ennemi)
    translation = 0.1 + 0.4 * (enemy_front**2 + enemy_front_left**2 + enemy_front_right**2)
    
    # attraction exponentielle (puissance de 2 fonctionnait aussi, mais 10 donne des réactions plus sensible)
    rotation = (enemy_front_left**10) * 1.0 + (enemy_front_right**10) * (-1.0)
    
    rotation = max(-1.0, min(1.0, rotation))
    
    return translation, rotation


def genetic_braitenberg(sensors):
    """
    robot génétique implémenté grâce aux fichiers config_genetic_train.py et robot_genetic_train.py
    avec une fonction score qui s'assure de tourner le moins possible pour ne pas perdre de vitesse.
    """
    # Paramètres optimaux après une grosse session d'entrainement
    param = [0.8, -0.6, 0.4, -0.3,0.2, -0.2, 0.5, -0.5,0.9, 0.7]
    
    rotation = 0.0
    rotation += sensors[sensor_front] * param[0]
    rotation += sensors[sensor_front_left] * param[1]
    rotation += sensors[sensor_front_right] * param[2]
    rotation += sensors[sensor_left] * param[3]
    rotation += sensors[sensor_right] * param[4]
    rotation += sensors[sensor_rear_left] * param[5]
    rotation += sensors[sensor_rear_right] * param[6]
    rotation += sensors[sensor_rear] * param[7]
    
    rotation *= param[9]
    translation = param[8]
    
    rotation = max(-1.0, min(1.0, rotation))
    
    return translation, rotation


# COMPORTEMENTS DE DETECTION DE SITUATION ET DEBLOQUAGE


def tunnel_navigation(sensors, sensor_to_wall):
    """
    gestion de navigation dans tunnel (couloir de largeur inférieur à 2 taille du robot) et de virage à 90degrés
    """
    wall_front = sensor_to_wall[sensor_front]
    wall_front_left = sensor_to_wall[sensor_front_left]
    wall_front_right = sensor_to_wall[sensor_front_right]
    wall_left = sensor_to_wall[sensor_left]
    wall_right = sensor_to_wall[sensor_right]
    
    # Détecte virage à 90°
    if wall_front > 0.45:
        #détermine la direction du virage
        opening_left = wall_front_left < 0.35 and wall_front_right > 0.5
        opening_right = wall_front_right < 0.35 and wall_front_left > 0.5
        #coef de 0.6 trouvé experimentalement
        left_score = wall_front_left + wall_left * 0.6
        right_score = wall_front_right + wall_right * 0.6
        score_diff = abs(left_score - right_score)
        #score_diff c'est la distance par rapport au "début du virage que l'on doit effectuer"
        
        #disjonction des cas en fonction de virage à gauche, à droite
        if opening_left or (score_diff > 0.35 and left_score < right_score):
            rotation = 1.0
            translation = 0.6
        
        elif opening_right or (score_diff > 0.35 and right_score < left_score):
            rotation = -1.0
            translation = 0.6
        
        elif score_diff < 0.25:
            if wall_left < wall_right - 0.12:
                rotation = 1.0
                translation = -0.7
            elif wall_right < wall_left - 0.12:
                rotation = -1.0
                translation = -0.7
            else:
                rotation = random.choice([-1.0, 1.0])
                translation = -0.8
        
        else:
            if left_score < right_score - 0.2:
                rotation = 0.9
                translation = 0.65
            else:
                rotation = -0.9
                translation = 0.65
    
    #mouvement zigzag pour avancer dans les tunnels et ne pas être constamment bloqué, car capteur front est en diagonale par rapport à la direction du robot
    else:
        left_pressure = wall_front_left + wall_left
        right_pressure = wall_front_right + wall_right
        error = left_pressure - right_pressure
        rotation = error * -1.0
        translation = 1.0
        
        if wall_front > 0.25:
            translation = 0.85
    
    return translation, rotation


def unstuck_behavior(memory):
    """
    comportement de débloquage quasiment 100% efficace en 3 phases grâce à memory
    """
    seq = memory - 1000
    
    if seq < 20:
        translation = 0.0
        rotation = random.choice([-1.0, 1.0])
    elif seq < 40:
        translation = -0.95
        rotation = random.choice([-1.0, -0.7, 0.7, 1.0])
    elif seq < 55:
        translation = 1.0
        rotation = random.uniform(-0.3, 0.3)
    else:
        translation = 1.0
        rotation = 0.0
    
    return translation, rotation


# =============================================================================
# DÉTECTION DE SITUATIONS
# =============================================================================

def detect_tunnel(sensors, sensor_to_wall):
    """
    Détecte un tunnel étroit
    """
    front_clear = sensor_to_wall[sensor_front] < 0.3
    corners_occupied = (sensor_to_wall[sensor_front_left] > 0.25 or sensor_to_wall[sensor_front_right] > 0.25)
    side_pressure = (1.0 - sensors[sensor_left]) + (1.0 - sensors[sensor_right])
    
    return front_clear and corners_occupied and side_pressure > 0.6


def detect_confined_space(sensor_to_wall):
    """
    Détecte espace confiné (risque de blocage)
    """
    obstacles_count = 0
    for i in range(8):
        if sensor_to_wall[i] > 0.3:
            obstacles_count += 1
    return obstacles_count >= 4


# =============================================================================
# ARCHITECTURE DE SUBSOMPTION
# =============================================================================

def subsumption_architecture(robot_id, sensors, sensor_to_wall, sensor_to_robot, sensor_to_enemy, memory):
    """
    Architecture de subsomption afin de créer un arbre de priorité
    sensor to ennemy fonctionne différemment du reste des sensors, il vaut 1 si ennemi présent (on envoit dans la fonction 1 - sensor[i] plus tard)
    """
    #On a utilisé le string en return pour le débuggage, on le laisse au cas ou on en a encore besoin
    # PRIORITÉ 1 : DÉBLOCAGE
    if memory >= 1000:
        return unstuck_behavior(memory), "UNSTUCK"
    
    # PRIORITÉ 2 : TUNNEL
    if detect_tunnel(sensors, sensor_to_wall):
        return tunnel_navigation(sensors, sensor_to_wall), "TUNNEL"
    
    # PRIORITÉ 3 : ÉVITEMENT ROBOTS (sauf robot 2 qui chassent)
    if robot_id % 4 != 2:
        enemy_any = max(sensor_to_enemy)
        if enemy_any > 0.25:
            return avoid_robots_braitenberg(sensors, sensor_to_enemy), "AVOID_ENEMY"
    
    # PRIORITÉ 4 : ÉVITEMENT MURS PROCHES
    wall_front_critical = max(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right]) > 0.6 #0.6 experimental pour avoir le temps de tourner
    if wall_front_critical:
        return avoid_walls_braitenberg(sensor_to_wall), "AVOID_WALL"
    
    # PRIORITÉ 5 : COMPORTEMENTS SPÉCIALISÉS PAR ROBOT
    
    if robot_id % 4 == 0:
        return diagonal_sweeper(sensor_to_wall), "EXPLORER"
    
    elif robot_id % 4 == 1:
        return genetic_braitenberg(sensors), "GENETIC"
    
    elif robot_id % 4 == 2:
        # CHASSEUR : si ennemi détecté chasse, sinon croisiere braitenberg
        enemy_any = max(sensor_to_enemy)
        if enemy_any > 0.1:
            return enemy_chaser_braitenberg(sensor_to_enemy), "ENEMY_CHASE"
        else:
            return cruise_braitenberg(sensor_to_wall), "CRUISE"
    
    else:  # robot_id % 4 == 3
        return wall_hugger_with_gap_detection(sensors, sensor_to_wall), "WALL_GAP"


# =============================================================================
# CLASSE ROBOT
# =============================================================================

class Robot_player(Robot):
    team_name = "Toyota Yaris"
    robot_id = -1
    
    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Robot " + str(self.robot_id), team=self.team_name)
        self.memory = 0

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        #on a inversé les valeurs des senseurs pour des valeurs qui nous sont plus "naturelles" :
        # 1 pour danger, 0 pour pas de danger        
        sensor_to_wall = []
        sensor_to_robot = []
        
        for i in range(8):
            if sensor_view[i] == 1:
                sensor_to_wall.append(1.0 - sensors[i]) #inversion de valeur
                sensor_to_robot.append(0.0)
            elif sensor_view[i] == 2:
                sensor_to_wall.append(0.0)
                sensor_to_robot.append(1.0 - sensors[i]) #inversion de valeur
            else:
                sensor_to_wall.append(0.0)
                sensor_to_robot.append(0.0)
        
        # on filtre les robots ennemis
        sensor_to_enemy = []
        for i in range(8):
            if sensor_view[i] == 2 and sensor_team[i] != self.team_name:
                sensor_to_enemy.append(1.0 - sensors[i])
            else:
                sensor_to_enemy.append(0.0)
        
        # détecter bloquage
        
        in_tunnel = detect_tunnel(sensors, sensor_to_wall)
        confined = detect_confined_space(sensor_to_wall)
        
        wall_front = max(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right])
        #max vu qu'on a inversé pour les murs
        robot_front = max(sensor_to_robot[sensor_front], sensor_to_robot[sensor_front_left], sensor_to_robot[sensor_front_right])
        
        # FONCTIONNEMENT MEMOIRE
        # compter les dangers
        if not in_tunnel:
            if confined or wall_front > 0.5 or robot_front > 0.6:
                self.memory += 2
            elif wall_front > 0.3:
                self.memory += 1
            else:
                self.memory = max(0, self.memory - 1)
        else:
            stuck_in_corner = (wall_front > 0.6 and confined)
            stuck_by_robot = (robot_front > 0.7)
            
            if stuck_in_corner or stuck_by_robot:
                self.memory += 2
            elif wall_front > 0.4:
                self.memory += 1
            else:
                self.memory = max(0, self.memory - 1)
        
        # Trigger le déblocage en mettant memory à 1000 (parce que sinon memory n'atteint jamais 1000 naturellement )
        if self.memory > 50 and self.memory < 1000:
            self.memory = 1000
        
        #appliquer la subsomption
        
        (translation, rotation), state = subsumption_architecture(
            self.robot_id, sensors, sensor_to_wall, sensor_to_robot, sensor_to_enemy, self.memory
        )
        
        # incrémenter  memory pour débloquage
        if self.memory >= 1000:
            self.memory += 1
            if self.memory >= 1055:
                self.memory = 0
        
        # Limite rotation
        rotation = max(-1.0, min(1.0, rotation))
        
        return translation, rotation, False


