from robot import *
import random

# =============================================================================
# COMPORTEMENTS BRAITENBERG (Fonctions pures)
# =============================================================================

def cruise_braitenberg(sensors, walls, robot_id):
    """
    Comportement croisière : Avance vite avec légères variations aléatoires
    Type : Braitenberg avec composante exploratoire
    """
    translation = 1.0
    
    # Micro-ajustements selon murs lointains (Braitenberg)
    rotation = 0.0
    rotation -= walls[1] * 0.15  # Pousse à droite si mur à gauche
    rotation += walls[7] * 0.15  # Pousse à gauche si mur à droite
    
    # Variation aléatoire pour éviter trajectoires répétitives
    if random.random() < 0.2:
        rotation += random.uniform(-0.4, 0.4)
    
    return translation, rotation


def avoid_walls_braitenberg(sensors, walls):
    """
    Évitement de murs : Réaction proportionnelle Braitenberg classique
    Plus le mur est proche, plus on tourne fort
    """
    translation = 0.9
    
    # Braitenberg : somme pondérée des capteurs
    rotation = 0.0
    
    # Capteurs avant-gauche repoussent vers la droite (rotation négative)
    rotation -= walls[1] * 1.5  # Front-left
    rotation -= walls[2] * 0.8  # Left
    
    # Capteurs avant-droit repoussent vers la gauche (rotation positive)
    rotation += walls[7] * 1.5  # Front-right
    rotation += walls[6] * 0.8  # Right
    
    # Si mur vraiment devant, réaction forte
    if walls[0] > 0.5:
        translation = 0.5
        # Tourne du côté le plus libre
        left_space = sum(walls[1:4])
        right_space = sum(walls[5:8])
        rotation = -1.0 if left_space > right_space else 1.0
    
    return translation, rotation


def avoid_robots_braitenberg(sensors, robots):
    """
    Évitement de robots : Braitenberg répulsif fort
    Priorité haute car les robots bougent
    """
    # Force répulsive proportionnelle
    rotation = 0.0
    
    # Répulsion latérale
    rotation -= (robots[1] + robots[2]) * 2.0  # Gauche
    rotation += (robots[7] + robots[6]) * 2.0  # Droite
    
    # Si robot devant proche, urgence
    robot_front = max(robots[0], robots[1], robots[7])
    
    if robot_front > 0.6:
        translation = 0.0  # Stop
        # Tourne vers l'espace libre
        if robots[1] + robots[2] > robots[7] + robots[6]:
            rotation = -1.0
        else:
            rotation = 1.0
    elif robot_front > 0.3:
        translation = 0.6  # Ralentit
    else:
        translation = 1.0
    
    return translation, rotation


# =============================================================================
# COMPORTEMENTS SPÉCIALISÉS GAGNANTS
# =============================================================================

def diagonal_sweeper(sensors, walls):
    """
    ROBOT 0 : Explorateur rapide avec variations aléatoires fortes
    
    ✅ CORRIGÉ : Plus de rotation constante !
    Comportement purement réactif + variations aléatoires
    """
    translation = 1.0
    
    # BASE : Braitenberg pur (réaction aux murs)
    rotation = 0.0
    rotation -= walls[1] * 0.6  # Évite mur gauche-avant
    rotation += walls[7] * 0.6  # Évite mur droit-avant
    
    # VARIATION FORTE : Change souvent de direction
    # 30% de chance de variation forte à chaque step
    if random.random() < 0.3:
        # Choix aléatoire entre plusieurs comportements
        choice = random.random()
        
        if choice < 0.4:
            # Dérive légère
            rotation += random.uniform(-0.3, 0.3)
        elif choice < 0.7:
            # Virage moyen
            rotation += random.choice([-0.6, 0.6])
        else:
            # Virage fort
            rotation += random.choice([-0.9, 0.9])
    
    # ANTI-CERCLE : Si aucun mur proche, variation continue
    if max(walls) < 0.2:
        # En espace ouvert : variation aléatoire constante
        rotation += random.uniform(-0.4, 0.4)
    
    return translation, rotation


def wall_hugger_with_gap_detection(sensors, walls):
    """
    ROBOT 3 : Suit mur GAUCHE + Détecte et rentre dans les TROUS
    """
    translation = 1.0
    
    wall_left = walls[2]
    wall_front_left = walls[1]
    wall_front = walls[0]
    
    # Détection gap améliorée
    gap_detected = (wall_left < 0.15 and wall_front_left < 0.2 and wall_front < 0.3)
    
    if gap_detected:
        rotation = 0.9
        translation = 1.0
    
    elif wall_left > 0.1:
        target_distance = 0.2
        current_distance = 1.0 - sensors[2]
        error = current_distance - target_distance
        
        rotation = error * -2.0
        
        if wall_front > 0.5:
            rotation = -0.9
            translation = 0.7
    
    else:
        # Pas de mur à gauche : cherche un mur
        translation = 1.0
        rotation = 0.5  # Tourne légèrement à gauche pour trouver mur
    
    return translation, rotation


def perpendicular_bouncer(sensors, walls):
    """
    ROBOT 2 : Rebondit sur les murs avec direction intelligente
    """
    translation = 1.0
    
    wall_front = walls[0]
    wall_front_left = walls[1]
    wall_front_right = walls[7]
    
    # Si obstacle proche : rebond intelligent
    if wall_front > 0.5 or wall_front_left > 0.6 or wall_front_right > 0.6:
        # Compare espaces disponibles
        left_space = walls[1] + walls[2]
        right_space = walls[7] + walls[6]
        
        if left_space > right_space + 0.2:
            rotation = 0.9  # Plus d'espace à gauche
        elif right_space > left_space + 0.2:
            rotation = -0.9  # Plus d'espace à droite
        else:
            # Espaces similaires : choix aléatoire
            rotation = random.choice([-1.0, 1.0])
        
        translation = 0.6
    
    else:
        # Pas d'obstacle : légers ajustements Braitenberg
        rotation = 0.0
        rotation -= walls[1] * 0.4
        rotation += walls[7] * 0.4
        
        # Variation aléatoire
        if random.random() < 0.1:
            rotation += random.uniform(-0.3, 0.3)
    
    return translation, rotation


def genetic_braitenberg(sensors):
    """
    ROBOT 1 : Comportement avec poids OPTIMISÉS par algorithme génétique
    
    ⚙️ PROCÉDURE D'ENTRAÎNEMENT :
    1. Lance : python tetracomposibot.py config_genetic_train
    2. Attends ~10-15 minutes (500 générations × 3 conditions × 400 itérations)
    3. À la fin, copie les paramètres affichés ci-dessous
    4. Remplace la liste 'param' par les valeurs optimales
    
    📊 FONCTION DE SCORE (entraînement) :
    - 70% Couverture (cellules visitées × 10)
    - 20% Vitesse (translation effective × 100)
    - 10% Efficacité (vitesse × (1 - rotation))
    
    🎯 RÉSULTAT ATTENDU : Score > 1500 sur arène 1
    """
    import math
    
    # ⚠️⚠️⚠️ REMPLACE PAR LES PARAMÈTRES OPTIMAUX APRÈS ENTRAÎNEMENT ⚠️⚠️⚠️
    param = [1.000, 0.932, 0.121, -0.006, -0.074, -0.532, -0.719, -0.676, 1.000, -0.283, 1.000, 0.652]
    # ⚠️⚠️⚠️ FIN DES PARAMÈTRES À REMPLACER ⚠️⚠️⚠️
    
    # Agrégation des capteurs
    avant = (sensors[0] + sensors[1] + sensors[7]) / 3.0
    cotes = (sensors[2] + sensors[6]) / 2.0
    asymetrie = sensors[6] - sensors[2]
    asymetrie_avant = sensors[7] - sensors[1]
    
    # TRANSLATION (normalisé 0.6 à 1.0)
    translation = 0.6 + 0.4 * math.tanh(
        param[0] + 
        param[1] * avant +
        param[2] * cotes +
        param[3] * sensors[4]  # rear
    )
    
    # ROTATION (normalisé -1.0 à 1.0)
    rotation = math.tanh(
        param[4] + 
        param[5] * asymetrie +
        param[6] * asymetrie_avant +
        param[7] * avant +
        param[8] * sensors[3] +  # rear-left
        param[9] * sensors[5]    # rear-right
    )
    
    # ANTI-BLOCAGE : Force rotation si obstacle proche
    if avant < 0.15:
        rotation += param[10] * 2.0
        translation *= param[11] * 0.5
    
    # Clamp rotation
    rotation = max(-1.0, min(1.0, rotation))
    
    return translation, rotation


# =============================================================================
# COMPORTEMENTS DE BASE
# =============================================================================

def tunnel_navigation(sensors, walls):
    """
    Navigation dans tunnels étroits + virages 90°
    """
    wall_front = walls[0]
    wall_front_left = walls[1]
    wall_front_right = walls[7]
    wall_left = walls[2]
    wall_right = walls[6]
    
    # Détecte virage à 90°
    if wall_front > 0.45:
        opening_left = wall_front_left < 0.35 and wall_front_right > 0.5
        opening_right = wall_front_right < 0.35 and wall_front_left > 0.5
        
        left_score = wall_front_left + wall_left * 0.6
        right_score = wall_front_right + wall_right * 0.6
        score_diff = abs(left_score - right_score)
        
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
    Séquence de déblocage en 3 phases
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

def detect_tunnel(sensors, walls):
    """
    Détecte un tunnel étroit
    """
    front_clear = walls[0] < 0.3
    corners_occupied = (walls[1] > 0.25 or walls[7] > 0.25)
    side_pressure = (1.0 - sensors[2]) + (1.0 - sensors[6])
    
    return front_clear and corners_occupied and side_pressure > 0.6


def detect_confined_space(walls):
    """
    Détecte espace confiné (risque de blocage)
    """
    obstacles_count = sum(1 for w in walls if w > 0.3)
    return obstacles_count >= 4


# =============================================================================
# ARCHITECTURE DE SUBSOMPTION
# =============================================================================

def subsumption_architecture(robot_id, sensors, walls, robots, memory):
    """
    Architecture de subsomption : priorité décroissante
    """
    
    # PRIORITÉ 1 : DÉBLOCAGE
    if memory >= 1000:
        return unstuck_behavior(memory), "UNSTUCK"
    
    # PRIORITÉ 2 : TUNNEL (avec gestion virages 90° améliorée)
    if detect_tunnel(sensors, walls):
        return tunnel_navigation(sensors, walls), "TUNNEL"
    
    # PRIORITÉ 3 : ÉVITEMENT ROBOTS
    robot_any = max(robots)
    if robot_any > 0.25:
        return avoid_robots_braitenberg(sensors, robots), "AVOID_ROBOT"
    
    # PRIORITÉ 4 : ÉVITEMENT MURS PROCHES
    wall_front_critical = max(walls[0], walls[1], walls[7]) > 0.6
    if wall_front_critical:
        return avoid_walls_braitenberg(sensors, walls), "AVOID_WALL"
    
    # PRIORITÉ 5 : COMPORTEMENTS SPÉCIALISÉS PAR ROBOT
    
    if robot_id % 4 == 0:
        # ROBOT 0 : Explorateur rapide (CORRIGÉ - plus de cercles !)
        return diagonal_sweeper(sensors, walls), "EXPLORER"
    
    elif robot_id % 4 == 1:
        # ROBOT 1 : Comportement GÉNÉTIQUE
        return genetic_braitenberg(sensors), "GENETIC"
    
    elif robot_id % 4 == 2:
        # ROBOT 2 : Bouncer perpendiculaire
        return perpendicular_bouncer(sensors, walls), "BOUNCER"
    
    else:  # robot_id % 4 == 3
        # ROBOT 3 : Wall hugger avec détection gaps
        return wall_hugger_with_gap_detection(sensors, walls), "WALL_GAP"


# =============================================================================
# CLASSE ROBOT
# =============================================================================

class Robot_player(Robot):
    team_name = "Hybrid_Final_Fixed"
    
    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        super().__init__(x_0, y_0, theta_0, name, team)
        self.memory = 0

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # ========== PRÉTRAITEMENT SENSEURS ==========
        
        val = [(1.0 - x) for x in sensors]
        
        walls = [0.0] * 8
        robots = [0.0] * 8
        
        for i in range(8):
            if sensor_view[i] == 1:
                walls[i] = val[i]
            elif sensor_view[i] == 2:
                robots[i] = val[i]
        
        # ========== MONITORING BLOCAGE ==========
        
        in_tunnel = detect_tunnel(sensors, walls)
        confined = detect_confined_space(walls)
        
        wall_front = max(walls[0], walls[1], walls[7])
        robot_front = max(robots[0], robots[1], robots[7])
        
        # Incrémentation memory
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
        
        # Trigger déblocage
        if self.memory > 50 and self.memory < 1000:
            self.memory = 1000
        
        # ========== ARCHITECTURE DE SUBSOMPTION ==========
        
        (translation, rotation), state = subsumption_architecture(
            self.id, sensors, walls, robots, self.memory
        )
        
        # Incrémentation memory si en déblocage
        if self.memory >= 1000:
            self.memory += 1
            if self.memory >= 1055:
                self.memory = 0
        
        # Limite rotation
        rotation = max(-1.0, min(1.0, rotation))
        
        return translation, rotation, False