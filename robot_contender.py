from robot import *
import math
import random

nb_robots = 0

class Robot_player(Robot):

    team_name = "team 67" # Nom de l'équipe
    robot_id = -1
    memory = 0 # Unique entier autorisé pour la mémoire

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots % 4 
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Bot_"+str(self.robot_id), team=self.team_name)

    # --- COMPORTEMENTS DE BASE ---

    def behavior_avoid_all(self, sensors):
        """ Évitement d'obstacles classique """
        translation = sensors[sensor_front] * 0.8
        rotation = (1.0 - sensors[sensor_front_left]) * (-1.0) + (1.0 - sensors[sensor_front_right]) * (1.0)
        return translation, rotation

    def behavior_follow_wall(self, sensors):
        """ Longement de mur """
        translation = 0.7
        rotation = (sensors[sensor_left] - 0.5) * 2.0
        return translation, rotation

    def behavior_optimized(self, sensors):
        """ Comportement avec poids type Perceptron """
        w_t = [0.8, 0.1, 0.6, 0.1] 
        w_r = [0.0, 0.7, 0.0, -0.7]
        
        t = math.tanh(w_t[0] + w_t[1]*sensors[sensor_front_left] + w_t[2]*sensors[sensor_front] + w_t[3]*sensors[sensor_front_right])
        r = math.tanh(w_r[0] + w_r[1]*sensors[sensor_front_left] + w_r[2]*sensors[sensor_front] + w_r[3]*sensors[sensor_front_right])
        return t, r

    def behavior_hunt_enemy(self, sensors, sensor_view, sensor_team):
        """ Se dirige vers l'ennemi (LoveBot vers robots adverses) """
        for i in range(8):
            if sensor_view[i] == 2 and sensor_team[i] != self.team_name:
                translation = 1.0
                rotation = 0.5 if i < 4 else -0.5
                return translation, rotation
        return None

    # --- ARCHITECTURE DE SUBSOMPTION CORRIGÉE ---

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # 1. Gestion du blocage (Mémoire)
        if sensors[sensor_front] < 0.05:
            self.memory = 15 

        if self.memory > 0:
            self.memory -= 1
            return -0.6, 0.8, False # ON AJOUTE 'False' ICI

        # 2. Évitement d'urgence
        if min(sensors[sensor_front], sensors[sensor_front_left], sensors[sensor_front_right]) < 0.2:
            t, r = self.behavior_avoid_all(sensors)
            return t, r, False # ON AJOUTE 'False' ICI

        # 3. Spécialisation par ID
        
        if self.robot_id == 0:
            t, r = self.behavior_optimized(sensors)
            return t, r, False

        elif self.robot_id == 1:
            hunt = self.behavior_hunt_enemy(sensors, sensor_view, sensor_team)
            if hunt: 
                t, r = hunt
                return t, r, False
            
        elif self.robot_id == 2:
            if sensors[sensor_left] < 0.5 or sensors[sensor_right] < 0.5:
                t, r = self.behavior_follow_wall(sensors)
                return t, r, False

        # 4. Exploration par défaut
        t, r = self.behavior_avoid_all(sensors)
        r += (random.random() - 0.5) * 0.2 
        return t, r, False # TOUJOURS 3 VALEURS