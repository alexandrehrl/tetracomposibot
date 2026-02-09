from robot import *
import math
import random

class Robot_player(Robot):
    team_name = "testtesttesttest" # Nom de l'équipe
    robot_id = -1
    memory = 0 # Entier unique pour gérer le déblocage
    _count = 0 

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        # Attribution robuste de l'ID (0-3) pour chaque équipe
        self.robot_id = Robot_player._count % 4 
        Robot_player._count += 1
        super().__init__(x_0, y_0, theta_0, name="Bot_"+str(self.robot_id), team=self.team_name)

    # --- COMPORTEMENTS SPÉCIALISÉS ---

    def behavior_high_speed(self, sensors):
        """ Optimisé par AG (TP2) : Vitesse maximale et évitement fluide """
        # Poids favorisant la ligne droite (biais élevé) et réaction latérale
        w_t = [0.9, 0.1, 0.8, 0.1] 
        w_r = [0.0, 0.7, 0.0, -0.7]
        t = math.tanh(w_t[0] + w_t[1]*sensors[sensor_front_left] + w_t[2]*sensors[sensor_front] + w_t[3]*sensors[sensor_front_right])
        r = math.tanh(w_r[0] + w_r[1]*sensors[sensor_front_left] + w_r[2]*sensors[sensor_front] + w_r[3]*sensors[sensor_front_right])
        return t, r

    def behavior_wall_hugging(self, sensors):
        """ Suit le mur gauche pour nettoyer les bords (TP1) """
        translation = 0.8
        # Maintient le mur à une distance cible de 0.45
        rotation = (sensors[sensor_left] - 0.45) * 2.2
        return translation, rotation

    def behavior_sabotage(self, sensors, sensor_view, sensor_team):
        """ Traque l'ennemi pour voler ses cases (LoveBot agressif) """
        for i in range(8):
            if sensor_view[i] == 2 and sensor_team[i] != self.team_name:
                return 1.0, (0.5 if i < 4 else -0.5)
        return None

    # --- ARCHITECTURE DE SUBSOMPTION (PRIORITÉS) ---

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # 1. PRIORITÉ ABSOLUE : Anti-blocage (Mémoire)
        # Si coincé face à un mur (distance < 0.05), on active la manoeuvre de secours
        if sensors[sensor_front] < 0.05 and self.memory == 0:
            self.memory = 15 # Nombre de pas pour reculer/pivoter

        if self.memory > 0:
            self.memory -= 1
            return -0.6, 0.9, False # Recul tournant

        # 2. PRIORITÉ ÉVITEMENT : Sécurité immédiate
        if min(sensors[sensor_front], sensors[sensor_front_left], sensors[sensor_front_right]) < 0.15:
            # Évitement Braitenberg classique
            t = sensors[sensor_front] * 0.4
            r = (1.0 - sensors[sensor_front_left]) * -1.2 + (1.0 - sensors[sensor_front_right]) * 1.2
            return t, r, False

        # 3. PRIORITÉ MISSION : Rôles spécifiques
        
        if self.robot_id == 3: # Le Saboteur
            hunt = self.behavior_sabotage(sensors, sensor_view, sensor_team)
            if hunt: return hunt[0], hunt[1], False

        if self.robot_id == 2: # Le Nettoyeur de Murs
            if sensors[sensor_left] < 0.6 or sensors[sensor_right] < 0.6:
                t, r = self.behavior_wall_hugging(sensors)
                return t, r, False

        # 4. PRIORITÉ BASSE : Couverture AG (Par défaut)
        t, r = self.behavior_high_speed(sensors)
        
        # Ajout de bruit pour le Robot 1 afin de diversifier les trajectoires
        if self.robot_id == 1:
            r += (random.random() - 0.5) * 0.3

        return t, r, False