# pylint: disable=import-error, no-name-in-module, unused-wildcard-import

from PyQt5.QtCore import QPointF, QPoint
from PyQt5.QtGui import QPolygon
import numpy as np
from const import *

class Ship:
    def __init__(self, x, y, d=0):
        self.x = x
        self.y = y
        self.d = d
        self.points = 0
        self.power = DEFAULT_POWER
        self.r = None
        self.update_r()

    def get_coordinates(self, scale):
        points = []
        points.append(QPoint(*np.matmul(self.r, [-0.5, -1])*SHIP_DISPLAY_SIZE*scale))
        points.append(QPoint(*np.matmul(self.r, [0, 0])*SHIP_DISPLAY_SIZE*scale))
        points.append(QPoint(*np.matmul(self.r, [0.5, -1])*SHIP_DISPLAY_SIZE*scale))
        points.append(QPoint(*np.matmul(self.r, [0, -0.6])*SHIP_DISPLAY_SIZE*scale))
        
        return self._move_points_to_center(points, scale)

    def get_shape(self):
        return QPolygon(self.get_coordinates(1))

    def get_line_coordinates(self, scale):
        points = []
        points.append(QPointF(0,0))
        points.append(QPointF(*np.matmul(self.r, [0, 1])*self.power*POWER_DISPLAY_FACTOR*scale))
        return self._move_points_to_center(points, scale)

    def update_r(self):
        self.r = np.array([[np.cos(self.d), np.sin(self.d)], [-np.sin(self.d), np.cos(self.d)]])

    def _move_points_to_center(self, points, scale):
        for point in points:
            point += QPoint(self.x*scale, self.y*scale)
        return points

    def rotate_left(self, is_control):
        step = KEY_ROTATION_CONTROL if is_control else KEY_ROTATION
        self.d += step
        self.update_r()

    def rotate_right(self, is_control):
        step = KEY_ROTATION_CONTROL if is_control else KEY_ROTATION
        self.d -= step
        self.update_r()

    def increase_power(self, is_control):
        step = KEY_POWER_STEP_CONTROL if is_control else KEY_POWER_STEP
        if self.power < POWER_MAX:
            self.power += step

    def decrease_power(self, is_control):
        step = KEY_POWER_STEP_CONTROL if is_control else KEY_POWER_STEP
        if self.power > KEY_POWER_STEP:
            self.power -= step


