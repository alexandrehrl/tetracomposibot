from robot import *
import math
import random

class Robot_player(Robot):
    team_name = "Team Beta" 
    robot_id = -1
    memory = 0 
    _counter = 0 

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        self.robot_id = Robot_player._counter % 4 
        Robot_player._counter += 1
        super().__init__(x_0, y_0, theta_0, name="Beta_"+str(self.robot_id), team=self.team_name)

    def behavior_avoid_all(self, sensors):
        translation = sensors[sensor_front] * 0.7
        rotation = (1.0 - sensors[sensor_front_left]) * (-1.2) + (1.0 - sensors[sensor_front_right]) * (1.2)
        return translation, rotation

    def behavior_hunt(self, sensors, sensor_view, sensor_team):
        for i in range(8):
            if sensor_view[i] == 2 and sensor_team[i] != self.team_name:
                return 1.0, (0.5 if i < 4 else -0.5)
        return None

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        if sensors[sensor_front] < 0.05:
            self.memory = 20 
        if self.memory > 0:
            self.memory -= 1
            return -0.5, -0.9, False
        target = self.behavior_hunt(sensors, sensor_view, sensor_team)
        if target:
            t, r = target
            return t, r, False
        t, r = self.behavior_avoid_all(sensors)
        r += (random.random() - 0.5) * 0.3 
        return t, r, False