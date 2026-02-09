from robot import * 
import random
import math

nb_robots = 0
debug = False

class Robot_player(Robot):
    
    team_name = "EX TOXIQUE"
    
    robot_id = -1
    iteration = 0
    memory = 0
    
    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
        
        self.genetic_weights = [
            0.92, 0.88, 0.95, 0.91,
            0.15, 0.72, -0.48, -0.69
        ]
        
        self.last_x = x_0
        self.last_y = y_0
        self.stuck_counter = 0
        
    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # Prétraitement des capteurs
        sensor_to_wall = []
        sensor_to_robot = []
        sensor_to_enemy = []
        sensor_to_teammate = []
        
        for i in range(8):
            sensor_val = float(sensors[i])
            view_type = int(sensor_view[i]) if sensor_view[i] is not None else 0
            team_val = str(sensor_team[i]) if sensor_team[i] is not None else "n/a"
            
            if view_type == 1:  # Mur
                sensor_to_wall.append(sensor_val)
                sensor_to_robot.append(1.0)
                sensor_to_enemy.append(1.0)
                sensor_to_teammate.append(1.0)
            elif view_type == 2:  # Robot
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensor_val)
                if team_val == str(self.team):
                    sensor_to_teammate.append(sensor_val)
                    sensor_to_enemy.append(1.0)
                else:
                    sensor_to_enemy.append(sensor_val)
                    sensor_to_teammate.append(1.0)
            else:  # Vide
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)
                sensor_to_enemy.append(1.0)
                sensor_to_teammate.append(1.0)
        
        # Détection de blocage
        if self.iteration % 50 == 0 and self.iteration > 0:
            try:
                dist_moved = math.sqrt((self.x - self.last_x)**2 + (self.y - self.last_y)**2)
                if dist_moved < 5.0:
                    self.stuck_counter += 1
                else:
                    self.stuck_counter = 0
            except:
                self.stuck_counter = 0
            self.last_x = self.x
            self.last_y = self.y
        
        # PRIORITÉ MAXIMALE: Déblocage
        if self.stuck_counter >= 3:
            self.memory = 40
            self.stuck_counter = 0
        
        if self.memory > 0:
            self.memory -= 1
            self.iteration += 1
            if self.memory > 30:
                return -0.9, 0.95, False  # FIX: Ajout du False
            elif self.memory > 20:
                return -0.9, -0.95, False  # FIX: Ajout du False
            else:
                return 0.95, 0.8, False  # FIX: Ajout du False
        
        # Comportement selon robot ID
        if self.robot_id == 0:
            translation, rotation = self._genetic_explorer(
                sensors, sensor_to_wall, sensor_to_enemy, sensor_to_teammate
            )
        elif self.robot_id == 1:
            translation, rotation = self._elite_wall_follower(
                sensors, sensor_to_wall, sensor_view
            )
        elif self.robot_id == 2:
            translation, rotation = self._aggressive_sweeper(
                sensors, sensor_to_wall, sensor_to_enemy, sensor_to_teammate
            )
        else:
            translation, rotation = self._tactical_explorer(
                sensors, sensor_to_wall, sensor_to_enemy, sensor_to_teammate
            )
        
        self.iteration += 1
        return translation, rotation, False
    
    def _genetic_explorer(self, sensors, sensor_to_wall, sensor_to_enemy, sensor_to_teammate):
        inputs = [
            1.0, 
            float(sensors[sensor_front_left]), 
            float(sensors[sensor_front]), 
            float(sensors[sensor_front_right])
        ]
        
        try:
            translation = math.tanh(sum(inputs[i] * self.genetic_weights[i] for i in range(4)))
            rotation = math.tanh(sum(inputs[i] * self.genetic_weights[i+4] for i in range(4)))
        except:
            translation = 0.8
            rotation = 0.0
        
        if sensor_to_enemy[sensor_front] < 0.6:
            translation += 0.35
        
        teammate_repulsion = 0.0
        for i in [sensor_front_left, sensor_left, sensor_front, sensor_front_right, sensor_right]:
            if sensor_to_teammate[i] < 0.5:
                if i in [sensor_front_left, sensor_left, sensor_rear_left]:
                    teammate_repulsion += 0.4
                else:
                    teammate_repulsion -= 0.4
        rotation += teammate_repulsion
        
        if all(s > 0.8 for s in sensor_to_wall[:4]) and self.iteration % 200 < 5:
            rotation += random.uniform(-0.3, 0.3)
        
        return translation, rotation
    
    def _elite_wall_follower(self, sensors, sensor_to_wall, sensor_view):
        if self.memory > 0:
            self.memory -= 1
            if self.memory > 22:
                return 0.15, 0.95
            elif self.memory > 12:
                return 0.3, 0.9
            else:
                return 0.5, 0.75
        
        wall_front = sensor_to_wall[sensor_front] < 0.55
        wall_front_left = sensor_to_wall[sensor_front_left] < 0.6
        wall_left = sensor_to_wall[sensor_left] < 0.45
        
        if wall_front:
            self.memory = 28
            return 0.2, 0.95
        
        if wall_left:
            if wall_front_left:
                return 0.75, -0.35
            elif sensor_to_wall[sensor_left] < 0.35:
                return 0.85, -0.15
            else:
                return 0.95, 0.05
        else:
            if sensor_to_wall[sensor_left] > 0.7:
                return 0.7, 0.6
            else:
                return 0.8, 0.3
    
    def _aggressive_sweeper(self, sensors, sensor_to_wall, sensor_to_enemy, sensor_to_teammate):
        translation = 1.0
        rotation = 0.0
        
        front_danger = 1.0 - sensor_to_wall[sensor_front]
        if front_danger > 0.3:
            translation -= front_danger * 1.2
            left_clear = sensor_to_wall[sensor_front_left]
            right_clear = sensor_to_wall[sensor_front_right]
            if left_clear > right_clear:
                rotation += 0.85
            else:
                rotation -= 0.85
        
        if sensor_to_wall[sensor_front_left] < 0.65:
            rotation -= 0.7
            translation *= 0.9
        if sensor_to_wall[sensor_front_right] < 0.65:
            rotation += 0.7
            translation *= 0.9
        
        if sensor_to_wall[sensor_left] < 0.5:
            rotation -= 0.45
        if sensor_to_wall[sensor_right] < 0.5:
            rotation += 0.45
        
        enemy_bonus = 0.0
        for i in range(8):
            if sensor_to_enemy[i] < 0.65:
                enemy_bonus += (1.0 - sensor_to_enemy[i]) * 0.15
        translation += min(enemy_bonus, 0.3)
        
        for i in range(8):
            if sensor_to_teammate[i] < 0.55:
                if i <= 3:
                    rotation -= 0.5
                else:
                    rotation += 0.5
                translation *= 0.85
        
        if self.iteration % 300 < 10:
            rotation += 0.4
        
        return translation, rotation
    
    def _tactical_explorer(self, sensors, sensor_to_wall, sensor_to_enemy, sensor_to_teammate):
        translation = 0.95
        rotation = -0.08
        
        if sensor_to_wall[sensor_front] < 0.65:
            danger = 1.0 - sensor_to_wall[sensor_front]
            translation -= danger * 1.0
            rotation += 0.75 * (1.5 - sensor_to_wall[sensor_front_right])
        
        if sensor_to_wall[sensor_front_left] < 0.6:
            rotation += 0.65
        if sensor_to_wall[sensor_front_right] < 0.6:
            rotation -= 0.5
        
        if sensor_to_wall[sensor_left] < 0.45:
            rotation += 0.5
        if sensor_to_wall[sensor_right] < 0.45:
            rotation -= 0.4
        
        phase = (self.iteration // 200) % 4
        
        if phase == 0:
            rotation += 0.2
        elif phase == 1:
            rotation -= 0.2
        elif phase == 2:
            translation = min(translation * 1.1, 1.0)
        else:
            if sensor_to_enemy[sensor_front] < 0.7:
                translation += 0.25
                rotation *= 0.5
        
        for i in range(8):
            if sensor_to_teammate[i] < 0.6:
                if i < 4:
                    rotation += 0.45
                else:
                    rotation -= 0.45
        
        if sensor_to_wall[sensor_rear] < 0.4:
            translation += 0.3
        
        return translation, rotation
