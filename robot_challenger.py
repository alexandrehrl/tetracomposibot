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

        # Principe du code : 
        # On a implémenté plusieurs comportements de différentes manières (braitenberg modifié, subsomption et arbre de décision (priorité))
        # On a 3 robots qui ont de la subsomption pour choisir entre ces comportements
        # On a 1 robot qui est purement génétique (optimisé à l'aide d'un fichier externe)
        # Tous les robots suivent un ordre de priorité qu'on définit plus bas, mais ont tous un trait de personnalité différent.

        # IMPORTANT POUR JUSTIFIER QUE CES COMPORTEMENTS SONT BRAITENBERG : 
        # ligne 461 (originale) : rotation = max(-1.0, min(1.0, rotation))
        # on a aussi inversé les valeurs des senseurs pour des valeurs qui nous sont plus "naturelles" :
        # sensor_to_wall : 1 = danger
        # sensor_to_robot : 1 = danger
        # sensor_to_ennemy : 1 = danger
        # sensors : 0 = danger

        # --- COMPORTEMENTS BRAITENBERG ---

        def cruise_braitenberg(sensor_to_wall):
            """
            comportement croisière, vitesse optimale.
            implémentation braitenberg légèrement modifié
            """
            translation = 1.0 # vitesse opti
            
            rotation = 0.0
            rotation -= sensor_to_wall[sensor_front_left] * 0.15 #petit virage au maximum pour garder la vitesse (mode croisière)
            rotation += sensor_to_wall[sensor_front_right] * 0.15 
            
            # Variation aléatoire pour éviter trajectoires répétitives
            if random.random() < 0.2:
                rotation += random.uniform(-0.4, 0.4)
            
            return translation, rotation

        def avoid_walls_braitenberg(sensor_to_wall):
            """
            comportement pour éviter les murs.
            implémentation braitenberg légèrement modifié
            """
            translation = 0.9 
            rotation = 0.0 
            
            rotation -= sensor_to_wall[sensor_front_left] * 1.5 
            rotation -= sensor_to_wall[sensor_left] * 0.8 
            
            rotation += sensor_to_wall[sensor_front_right] * 1.5 
            rotation += sensor_to_wall[sensor_right] * 0.8
            
            # réaction forte si mur devant
            if sensor_to_wall[sensor_front] > 0.5:
                translation = 0.5
                # comparer l'espace libre à gauche et à droite (senseurs inversés ici, donc on cherche la valeur min)
                left_space = sensor_to_wall[sensor_front_left] + sensor_to_wall[sensor_left] + sensor_to_wall[sensor_rear_left]
                right_space = sensor_to_wall[sensor_front_right] + sensor_to_wall[sensor_right] + sensor_to_wall[sensor_rear_right]
                rotation = -1.0 if left_space > right_space else 1.0
            
            return translation, rotation

        def avoid_robots_braitenberg(sensors, sensor_to_robot):
            """
            comportement pour éviter les robots.
            """
            rotation = 0.0
            
            rotation -= (sensor_to_robot[sensor_front_left] + sensor_to_robot[sensor_left]) * 2.0 
            rotation += (sensor_to_robot[sensor_front_right] + sensor_to_robot[sensor_right]) * 2.0 
            
            # réaction forte si robot devant (senseur inversé)
            robot_front = max(sensor_to_robot[sensor_front], sensor_to_robot[sensor_front_left], sensor_to_robot[sensor_front_right])
            
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

        # --- COMPORTEMENTS "trait de caractère" ---

        def diagonal_sweeper(sensor_to_wall):
            """
            balayage aléatoire + fort que le comportement croisière.
            """
            translation = 1.0
            rotation = 0.0
            rotation -= sensor_to_wall[sensor_front_left] * 0.6
            rotation += sensor_to_wall[sensor_front_right] * 0.6
            
            # probabilité de 30% de changer de trajectoire
            if random.random() < 0.3:
                choice = random.random()
                if choice < 0.4:
                    rotation += random.uniform(-0.3, 0.3)
                elif choice < 0.7:
                    rotation += random.choice([-0.6, 0.6])
                else:
                    rotation += random.choice([-0.9, 0.9])
            
            # nécessaire pour ne pas faire de cercle (senseurs inversés)
            # si il y a un mur (donc max_wall = 1) on laisse mur avoider éviter, sinon on tourne de manière aléatoire
            max_wall = max(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right], 
                           sensor_to_wall[sensor_left], sensor_to_wall[sensor_right], 
                           sensor_to_wall[sensor_rear_left], sensor_to_wall[sensor_rear_right], sensor_to_wall[sensor_rear])
            if max_wall < 0.2:
                rotation += random.uniform(-0.4, 0.4)
            
            return translation, rotation

        def wall_hugger_with_gap_detection(sensors, sensor_to_wall):
            """
            Suit les murs et repère les trous, pas aussi efficace que souhaité
            """
            translation = 1.0
            
            wall_left = sensor_to_wall[sensor_left]
            wall_front_left = sensor_to_wall[sensor_front_left]
            wall_front = sensor_to_wall[sensor_front]
            
            # Détection de trou (senseurs inversés)
            # on a besoin juste de détecter à gauche car si on détecte les 2 en même temps, le robot ne prendra jamais de décision (il va zigzaguer et ne jamais prendre le virage)
            #le robot viendra éventuellement dans le même tunnel dans le sens inversé auquel cas la droite sera vérifiée dans tous les cas
            gap_detected = (wall_left < 0.15 and wall_front_left < 0.2 and wall_front < 0.3)
            
            if gap_detected:
                rotation = 0.9
                translation = 1.0
            
            elif wall_left > 0.1:
                target_distance = 0.2 
                # calcul l'erreur pour tourner de manière adaptative
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
            LOVEBOT version braitenberg modifiée.
            """
            
            enemy_front = sensor_to_enemy[sensor_front]
            enemy_front_left = sensor_to_enemy[sensor_front_left]
            enemy_front_right = sensor_to_enemy[sensor_front_right]
            
            #vitesse lente puis on additionne en fonction de la distance quadratique pour "rattraper" l'ennemi
            translation = 0.1 + 0.4 * (enemy_front**2 + enemy_front_left**2 + enemy_front_right**2)
            
            # attraction exponentielle 
            rotation = (enemy_front_left**10) * 1.0 + (enemy_front_right**10) * (-1.0)
            
            rotation = max(-1.0, min(1.0, rotation))
            
            return translation, rotation

        def genetic_braitenberg(sensors):
            """
            robot génétique optimisé grace à genetic_log.csv avec les fichiers config_genetic_train.py robot_genetic_train.py
            """
            # Paramètres optimaux
            param = [-0.1602,0.0299,0.9529,0.9400,-0.7794,-0.7607,-0.4079,-0.2086,0.6709,0.2895,-0.2284,-1.0000]
            
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

        # --- COMPORTEMENTS DE DETECTION DE SITUATION ET DEBLOQUAGE ---

        def tunnel_navigation(sensors, sensor_to_wall):
            """
            cette fonction sert à naviguer dans le tunnel une fois qu'on sait qu'on est dedans
            c'est une implémentation par subsomption
            """
            wall_front = sensor_to_wall[sensor_front]
            wall_front_left = sensor_to_wall[sensor_front_left]
            wall_front_right = sensor_to_wall[sensor_front_right]
            wall_left = sensor_to_wall[sensor_left]
            wall_right = sensor_to_wall[sensor_right]
            
            # Détecte virage à 90° (valeurs inversées : >0.45 = mur proche)
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
            Comportement de débloquage (Double utilisation de memory expliquée plus tard)
            """
            # On met memory à 1000 quand on est bloqué
            # On récupère l'étape de la séquence (memory > 1000)
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

        # --- DÉTECTION DE SITUATIONS ---

        def detect_tunnel(sensors, sensor_to_wall):
            """
            détecteur de tunnel, renvoie true si 3 conditions respectées, sinon non
            """
            #tunnel de l'arene 4 par exemple
            front_clear = sensor_to_wall[sensor_front] < 0.3
            corners_occupied = (sensor_to_wall[sensor_front_left] > 0.25 or sensor_to_wall[sensor_front_right] > 0.25)
            # inversion manuelle de sensors ici pour obtenir la pression latérale
            #on a besoin de la pression pour savoir de quel côté commencer le "zigzag"
            #sensors pas inversé, on prend tous les sensors pour ne pas "rentrer" quand il y a un ennemi
            side_pressure = (1.0 - sensors[sensor_left]) + (1.0 - sensors[sensor_right])
            #side pressure vaut 2 quand confiné dans un tunnel de largeur 1
            return front_clear and corners_occupied and side_pressure > 0.6

        def detect_confined_space(sensor_to_wall):
            """
            différence entre tunnel et endroit "confiné"
            """
            obstacles_count = 0
            for i in range(8):
                if sensor_to_wall[i] > 0.3:
                    obstacles_count += 1
            return obstacles_count >= 4

        # --- ARCHITECTURE DE SUBSOMPTION ---

        def subsumption_architecture(robot_id, sensors, sensor_to_wall, sensor_to_robot, sensor_to_enemy, memory):
            """
            Architecture de subsomption pour définir les priorités des robots
            """
            #on renvoie un string pour le debuggage, on le laisse au cas ou on en a besoin à nouveau
            # PRIORITÉ 1 : DÉBLOCAGE
            if memory >= 1000:
                return unstuck_behavior(memory), "UNSTUCK"
            
            # PRIORITÉ 2 : TUNNEL
            if detect_tunnel(sensors, sensor_to_wall):
                return tunnel_navigation(sensors, sensor_to_wall), "TUNNEL"
            
            # PRIORITÉ 3 : ÉVITEMENT ROBOTS
            if robot_id % 4 != 2:
                enemy_any = max(sensor_to_enemy)
                if enemy_any > 0.25:
                    return avoid_robots_braitenberg(sensors, sensor_to_enemy), "AVOID_ENEMY"
            
            # PRIORITÉ 4 : ÉVITEMENT MURS PROCHES
            wall_front_critical = max(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right]) > 0.6 
            if wall_front_critical:
                return avoid_walls_braitenberg(sensor_to_wall), "AVOID_WALL"
            
            # PRIORITÉ 5 : COMPORTEMENTS SPÉCIALISÉS
            
            if robot_id % 4 == 0:
                return diagonal_sweeper(sensor_to_wall), "EXPLORER"
            
            elif robot_id % 4 == 1:
                # Attention : genetic_braitenberg prend 'sensors' (NON inversé)
                return genetic_braitenberg(sensors), "GENETIC"
            
            elif robot_id % 4 == 2:
                enemy_any = max(sensor_to_enemy)
                if enemy_any > 0.1:
                    return enemy_chaser_braitenberg(sensor_to_enemy), "ENEMY_CHASE"
                else:
                    return cruise_braitenberg(sensor_to_wall), "CRUISE"
            
            else:  # robot_id % 4 == 3
                return wall_hugger_with_gap_detection(sensors, sensor_to_wall), "WALL_GAP"

#----------------------------------------------------------------------------------------------------
        # LOGIQUE PRINCIPALE DU STEP
   
        #inversion senseurs comme prévenu auparavant
        
        sensor_to_wall = []
        sensor_to_robot = []
        
        for i in range(8):
            if sensor_view[i] == 1:
                sensor_to_wall.append(1.0 - sensors[i]) # (senseur inversé)
                sensor_to_robot.append(0.0)
            elif sensor_view[i] == 2:
                sensor_to_wall.append(0.0)
                sensor_to_robot.append(1.0 - sensors[i]) # (senseur inversé)
            else:
                sensor_to_wall.append(0.0)
                sensor_to_robot.append(0.0)
        
        # Filtre pour les ennemis uniquement (senseur inversé)
        # Note: on utilise self.team_name ici
        sensor_to_enemy = []
        for i in range(8):
            if sensor_view[i] == 2 and sensor_team[i] != self.team_name:
                sensor_to_enemy.append(1.0 - sensors[i])
            else:
                sensor_to_enemy.append(0.0)
        
        # détection bloquage et gestion mémoire
        
        in_tunnel = detect_tunnel(sensors, sensor_to_wall)
        confined = detect_confined_space(sensor_to_wall)
        
        # max car valeurs inversées : on cherche le mur/robot le plus proche (valeur la plus haute)
        wall_front = max(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right])
        robot_front = max(sensor_to_robot[sensor_front], sensor_to_robot[sensor_front_left], sensor_to_robot[sensor_front_right])
        

        # IMPORTANT :         # EXPLICATION DE L'UTILISATION DE self.memory
        # La variable memory a deux usages différents selon sa valeur :

        #    COMPTEUR DE DANGER (Valeurs < 1000) :
        #    On incrémente memory progressivement si le robot est dans une situation de blocage potentiel
        #    (face à un mur, espace confiné, dans un L, rate un virage, coincé contre un robot). Si la situation se maintient, memory augmente jusqu'au seuil critique (50).
        #    Si la voie est libre, memory diminue.
        
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
        
        #    MEMORY POUR DÉBLOCAGE (Valeurs >= 1000) :
        #    Si le compteur dépasse 50, on déclenche le mode "UNSTUCK" en sautant directement à 1000.
        #    Ensuite, memory sert de compteur d'étape pour jouer une séquence prédéfinie dans unstuck_behavior (reculer, tourner, avancer) d'où les 3 séquences
        
        if self.memory > 50 and self.memory < 1000:
            self.memory = 1000

        # architecture
        # Appel de la fonction locale avec les attributs de l'instance (self.robot_id, self.memory)
        (translation, rotation), state = subsumption_architecture(
            self.robot_id, sensors, sensor_to_wall, sensor_to_robot, sensor_to_enemy, self.memory
        )
        
        #l'incrémentation pendant la séquence de déblocage
        if self.memory >= 1000:
            self.memory += 1
            if self.memory >= 1055: # Fin de la séquence
                self.memory = 0
        
        # Limite rotation finale pour le moteur
        rotation = max(-1.0, min(1.0, rotation))
        
        return translation, rotation, False