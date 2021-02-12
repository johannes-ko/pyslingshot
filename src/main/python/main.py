# pylint: disable=import-error, no-name-in-module, unused-wildcard-import
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon, QImage, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QTimer,QDateTime, QPoint, QPointF, QLineF, QRect
from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys
import numpy as np
import random

from planet import Planet
from ship import Ship
from bullet import Bullet
from const import *

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "PySlingshot"
        self.top= 50
        self.left= 150
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        self.out_zoom = False

        self.planets = []
        self.ships = []
        self.active_ship_id = 0
        self.bullet = None
        self.bullet_time = None
        self.bullet_lines = []
        self.control_key_pressed = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.physicsUpdate)

        for _ in range(N_SHIPS):
            self.ships.append(Ship(0,0))
        
        self.generate_world()

        self.draw_bg()
        self.InitWindow()

    def generate_world(self):
        n_planets = random.randint(MIN_PLANETS, MAX_PLANETS)
        planets = []

        for _ in range(n_planets):
            found_option = False
            while not found_option:
                found_option = True
                size = random.randint(MIN_PLANET_SIZE, MAX_PLANET_SIZE)
                x = random.randint(PLANET_PADDING+size, WINDOW_WIDTH-PLANET_PADDING-size)
                y = random.randint(PLANET_PADDING+size, WINDOW_HEIGHT-PLANET_PADDING-size)

                for planet in planets:
                    if np.sqrt((x-planet.x)**2 + (y-planet.y)**2) < size + planet.size + PLANET_PADDING:
                        found_option = False

            planets.append(Planet(x, y, size)) 

        for i in range(N_SHIPS):
            found_option = False
            world_build_try = 0
            while not found_option:
                found_option = True
                x = random.randint(PLANET_PADDING+size, WINDOW_WIDTH-PLANET_SHIP_PADDING-size)
                y = random.randint(PLANET_PADDING+size, WINDOW_HEIGHT-PLANET_SHIP_PADDING-size)

                for planet in planets:
                    if np.sqrt((x-planet.x)**2 + (y-planet.y)**2) < planet.size + PLANET_SHIP_PADDING:
                        found_option = False
                for ship in self.ships[:i]:
                    if np.sqrt((x-ship.x)**2 + (y-ship.y)**2) < SHIP_SHIP_PADDING:
                        found_option = False
                world_build_try += 1
                if world_build_try > 50:
                    self.generate_world()
                    return

            self.ships[i].x = x
            self.ships[i].y = y 

        self.planets = planets
    

    def draw_bg(self):
        global appctxt
        image_path_outer = appctxt.get_resource("outer.png")
        image_path_inner = appctxt.get_resource("inner.png")

        if self.out_zoom:
            oImage = QImage(image_path_outer)
        else:
            oImage = QImage(image_path_inner)
        sImage = oImage.scaled(QSize(WINDOW_WIDTH,WINDOW_WIDTH))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))                        
        self.setPalette(palette)

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def keyPressEvent(self, event):
        ship = self.ships[self.active_ship_id]
        if event.key() == Qt.Key_Left:
            ship.rotate_left(self.control_key_pressed)
        elif event.key() == Qt.Key_Right:
            ship.rotate_right(self.control_key_pressed)
        elif event.key() == Qt.Key_Up:
            ship.increase_power(self.control_key_pressed)
        elif event.key() == Qt.Key_Down:
            ship.decrease_power(self.control_key_pressed)
        elif event.key() == Qt.Key_Space:
            if self.bullet is None:
                self.shoot()
        elif event.key() == Qt.Key_Control:
            self.control_key_pressed = True
        self.update()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.control_key_pressed = False

    def paintEvent(self, event):
        scale = ZOOM_OUT_SCALE if self.out_zoom else 1
        x_offset = WINDOW_WIDTH*(1-ZOOM_OUT_SCALE)/2 if self.out_zoom else 0
        y_offset = WINDOW_HEIGHT*(1-ZOOM_OUT_SCALE)/2 if self.out_zoom else 0
        offset_point = QPoint(x_offset, y_offset)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.out_zoom:
            for bullet_line in self.bullet_lines[:-len(self.ships)]:
                if len(bullet_line) > 0:
                    painter.setPen(QPen(QColor(255, 255, 255, 60),  1, Qt.SolidLine))
                    painter.drawPolyline(*bullet_line)
            for bullet_line in self.bullet_lines[-len(self.ships):]:
                if len(bullet_line) > 0:
                    painter.setPen(QPen(QColor(255, 255, 255, 160),  1, Qt.SolidLine))
                    painter.drawPolyline(*bullet_line)
            

        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.white,  5, Qt.SolidLine))

        for planet in self.planets:
            painter.drawEllipse((planet.x-planet.size/2)*scale+x_offset, (planet.y-planet.size/2)*scale+y_offset, planet.size*scale, planet.size*scale)
        
        painter.setPen(QPen(Qt.white,  1, Qt.SolidLine))
        for ship in self.ships:
            line = QLineF(*ship.get_line_coordinates(scale))
            line.translate(offset_point)
            painter.drawLine(line)
        
        for i, ship in enumerate(self.ships):
            painter.setBrush(PLAYER_COLORS[i])
            painter.setPen(QPen(PLAYER_COLORS[i],  5, Qt.SolidLine))

            polygon = QPolygon(ship.get_coordinates(scale))
            polygon.translate(offset_point)
            painter.drawPolygon(polygon)

        if self.bullet is not None:
            painter.setPen(QPen(Qt.white,  5, Qt.SolidLine))
            painter.drawPoint(QPointF(self.bullet.x, self.bullet.y)*scale+offset_point)

        if self.out_zoom:
            painter.setPen(QPen(QColor(255, 255, 255, 100),  1, Qt.SolidLine))
            painter.setBrush(False)
            painter.drawRect(x_offset, y_offset, WINDOW_WIDTH*ZOOM_OUT_SCALE, WINDOW_HEIGHT*ZOOM_OUT_SCALE)

        if self.bullet_time is not None:
            painter.setPen(QPen(Qt.white,  5, Qt.SolidLine))
            painter.drawText(QPoint(WINDOW_WIDTH-30,20), str(self.bullet_time))

        for i, ship in enumerate(self.ships):
            painter.setPen(QPen(PLAYER_COLORS[i],  5, Qt.SolidLine))
            painter.drawText(QPoint(10,20+20*i), str(ship.points))


    def shoot(self):
        self.bullet_lines.append([])
        ship = self.ships[self.active_ship_id]
        self.bullet = Bullet(ship.x, ship.y, ship.d, ship.power)
        self.bullet_time = 0
        self.timer.start(TIMER_SPEED)

    def physicsUpdate(self):
        terminate = self.bullet.update(self.planets, self.ships)
        self.bullet_lines[-1].append(QPoint(self.bullet.x, self.bullet.y))

        if self.bullet.x < 0 or self.bullet.x > WINDOW_WIDTH or self.bullet.y < 0 or self.bullet.y > WINDOW_HEIGHT:
            if not self.out_zoom:
                self.out_zoom = True
                self.draw_bg()
        else:
            if self.out_zoom:
                self.out_zoom = False
                self.draw_bg()

        self.bullet_time += 1
        self.update()

        if self.bullet_time > TIME_LIMIT:
            terminate = True
        if terminate:
            if self.bullet.ship_hit_id is not None:
                points = int((POWER_MAX*1.1-self.ships[self.active_ship_id].power)*10)
                if not self.bullet.ship_hit_id == self.active_ship_id:
                    self.ships[self.active_ship_id].points += points
                else:
                    self.ships[self.active_ship_id].points -= points
                self.generate_world()
                self.bullet_lines = []

            self.bullet = None
            self.bullet_time = None
            self.timer.stop()
            self.active_ship_id += 1
            self.active_ship_id = self.active_ship_id%len(self.ships)
            self.out_zoom = False
            self.draw_bg()

appctxt = ApplicationContext()

App = QApplication(sys.argv)
window = Window()


exit_code = appctxt.app.exec_()
sys.exit(App.exec())