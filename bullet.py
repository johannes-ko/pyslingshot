# pylint: disable=import-error, no-name-in-module, unused-wildcard-import

from PyQt5.QtCore import Qt, QPoint
import numpy as np
from const import *


class Bullet:
    def __init__(self, x, y, d, power):
        self.x = x
        self.y = y
        self.dx = power * np.sin(d)
        self.dy = power * np.cos(d)
        self.ship_hit_id = None

    def update(self, planets, ships):
        for planet in planets:
            r2 = (self.x-planet.x)**2 + (self.y-planet.y)**2
            r = np.sqrt(r2)
            direction_x = (planet.x-self.x) / r
            direction_y = (planet.y-self.y) / r

            G = GRAVITATION_CONSTANT * planet.size / r2
            self.dx += direction_x * G
            self.dy += direction_y * G

            if r < planet.size/2:
                return True

        self.x += self.dx * SPEED_FACTOR
        self.y += self.dy * SPEED_FACTOR

        for i, ship in enumerate(ships):
            if ship.get_shape().containsPoint(QPoint(self.x, self.y), Qt.OddEvenFill):
                self.ship_hit_id = i
                return True

        return False
