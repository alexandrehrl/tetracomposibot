from robot import *
import math
import random

class Robot_player(Robot):
    team_name = "Team Alpha" 
    robot_id = -1
    memory = 0 
    _counter = 0 

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        # On utilise une sécurité pour ne jamais dépasser l'ID 3
        self.robot_id = Robot_player._counter % 4 
        Robot_player._counter += 1
        super().__init__(x_0, y_0, theta_0, name="Alpha_"+str(self.robot_id), team=self.team_name)

    def behavior_avoid_all(self, sensors):
        translation = sensors[sensor_front] * 0.8
        rotation = (1.0 - sensors[sensor_front_left]) * (-1.0) + (1.0 - sensors[sensor_front_right]) * (1.0)
        return translation, rotation

    def behavior_optimized(self, sensors):
        w_t = [0.8, 0.1, 0.6, 0.1] 
        w_r = [0.0, 0.7, 0.0, -0.7]
        t = math.tanh(w_t[0] + w_t[1]*sensors[sensor_front_left] + w_t[2]*sensors[sensor_front] + w_t[3]*sensors[sensor_front_right])
        r = math.tanh(w_r[0] + w_r[1]*sensors[sensor_front_left] + w_r[2]*sensors[sensor_front] + w_r[3]*sensors[sensor_front_right])
        return t, r

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        if sensors[sensor_front] < 0.05:
            self.memory = 15 
        if self.memory > 0:
            self.memory -= 1
            return -0.6, 0.8, False
        if min(sensors[sensor_front], sensors[sensor_front_left], sensors[sensor_front_right]) < 0.2:
            t, r = self.behavior_avoid_all(sensors)
            return t, r, False
        t, r = self.behavior_optimized(sensors)
        return t, r, False