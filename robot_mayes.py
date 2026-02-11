from robot import * 
import math

nb_robots = 0

class Robot_player(Robot):
    team_name = "Champion"
    robot_id = -1
    iteration = 0
    
    # Meilleurs paramètres trouvés
    param =[0.85, 1, 0.94, -1, -0.06, 0.26, -0.69, 0.4, 0.01, -0.39, -1, -0.42]

    
    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=400):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
    
    def reset(self):
        super().reset()
    
    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # Détection des zones
        avant = (sensors[sensor_front] + sensors[sensor_front_left] + sensors[sensor_front_right]) / 3.0
        cotes = (sensors[sensor_left] + sensors[sensor_right]) / 2.0
        asymetrie = sensors[sensor_right] - sensors[sensor_left]
        asymetrie_avant = sensors[sensor_front_right] - sensors[sensor_front_left]
        
        # TRANSLATION : toujours rapide
        translation = 0.6 + 0.4 * math.tanh(
            self.param[0] + 
            self.param[1] * avant +
            self.param[2] * cotes +
            self.param[3] * sensors[sensor_rear]
        )
        
        # ROTATION : évitement fluide
        rotation = math.tanh(
            self.param[4] + 
            self.param[5] * asymetrie +
            self.param[6] * asymetrie_avant +
            self.param[7] * avant +
            self.param[8] * sensors[sensor_rear_left] +
            self.param[9] * sensors[sensor_rear_right]
        )
        
        # Anti-blocage : si très proche d'un mur, force la rotation
        if avant < 0.15:
            rotation += self.param[10] * 2.0
            translation *= self.param[11] * 0.5
        
        # Limite rotation
        rotation = max(-0.8, min(0.8, rotation))
        
        self.iteration += 1
        return translation, rotation, False