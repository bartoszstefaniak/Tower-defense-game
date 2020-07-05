"""

This module contains classes:
    Turret which is resposible for drawing, managing turrets,
    Enemy which is resposible for drawing, managing enemies,
    Projectile which is resposible for drawing, managing projectiles,
    EnemySpawner which is resposible for creating new enemies,
    LevelState which is responsible for drawing UI, game logic and
    managing turrets, enemies, projectiles

"""


from state import State
from pygame import Rect
from pygame.surface import Surface
import pygame.locals as pgl
from pygame.draw import circle
from math import sqrt
from pygame.math import Vector2
from pygame import font
from button import Button


class LevelState(State):
    MOVABLE_TILES = [1, 3, 4]

    def __init__(self, screen, resource_manager):
        super().__init__("level")
        self.resource_manager = resource_manager
        self.startup(screen, "LEVEL 1")

    def startup(self, screen, level_name, reset=True):
        if reset is False:
            return
        self.screen = screen
        self.level_name = level_name
        self.level_data = self.resource_manager.level_data[self.level_name]
        self.BASICFONT = font.Font("resources/arial.ttf", 20)

        self.textures = self.resource_manager.scaled_textures

        (self.map_rect, self.panel_rect, self.stat_rect, self.turrets_rect,
         self.info_rect, self.button_rect) = self.prepare_areas()

        (self.map_surface, self.tiles,
         self.paths, self.spawn_point) = self.prepare_map()

        self.panel_surface = Surface(self.panel_rect.size)
        self.panel_surface.blit(self.textures["panel_background"],
                                (0, 0))

        self.enemies = []
        self.turrets = []
        self.projectiles = []
        self.buttons = []
        self.finished = False

        Turret.init(self.screen, self.turrets, self.enemies, self.projectiles,
                    self.resource_manager)

        Projectile.init(self.screen, self.resource_manager)

        Enemy.init(self.screen, self.paths, self.resource_manager)

        self.upgrade_button, self.sell_button = self.make_turret_buttons()
        self.current_turret = -1

        self.max_wave = self.level_data["waves"]
        self.health = self.level_data["health"]
        self.money = self.level_data["start_money"]

        self.next_wave_time = 0
        self.current_wave = 0
        self.speed_multiplier = 1

        self.enemy_spawner = EnemySpawner(screen, self.enemies,
                                          self.spawn_point)

        self.create_buttons()

    def draw(self):
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.map_surface, (0, 0))

        for enemy in self.enemies:
            enemy.draw()

        for turret in self.turrets:
            turret.draw()

        for projectile in self.projectiles:
            projectile.draw()

        self.screen.blit(self.panel_surface, self.panel_rect)
        self.draw_stats()
        self.describe_turret()

        for button in self.buttons:
            button.draw()

        if Turret.get_selected() is not None:
            self.upgrade_button.draw()
            self.sell_button.draw()

    def process_event(self, event):
        if event.type == pgl.MOUSEBUTTONUP:
            position = event.pos

            # Placing new turret
            if self.current_turret != -1:
                for tile_id in range(len(self.tiles)):
                    rect, available = self.tiles[tile_id]

                    if (available and rect.collidepoint(position) and
                       self.finished is False):

                        if self.money >= Turret.get_cost(self.current_turret):

                            turret = Turret.create_turret(rect.topleft,
                                                          self.current_turret,
                                                          tile_id)
                            self.turrets.append(turret)
                            self.tiles[tile_id][1] = False
                            self.money -= Turret.get_cost(self.current_turret)

        for turret in self.turrets:
            turret.process_event(event)

        for button in self.buttons:
            button.process_event(event)

        if Turret.get_selected() is not None:
            self.upgrade_button.process_event(event)
            self.sell_button.process_event(event)

    def update(self, dt):
        dt *= self.speed_multiplier

        if self.finished:
            dt = 0

        self.next_wave_time -= dt

        if self.next_wave_time <= 0 and self.current_wave < self.max_wave:
            self.current_wave += 1
            self.next_wave_time = (sqrt(self.current_wave) + 1.5 -
                                   5/self.current_wave)

            if self.current_wave <= self.max_wave:
                self.enemy_spawner.spawn_wave(self.current_wave)

        for turret in self.turrets:
            self.money -= turret.upgrades_cost
            turret.upgrades_cost = 0
            turret.update(dt)

        for projectile in self.projectiles:
            projectile.update(dt)

        for button in self.buttons:
            button.update()

        if Turret.get_selected() is not None:
            self.upgrade_button.update()
            self.sell_button.update()

        self.enemy_spawner.update(dt)

        self.alive_enemies = 0

        for enemy in self.enemies:
            if enemy.alive is True:
                self.alive_enemies += 1
            if enemy.used is False:
                if not enemy.alive and enemy.finished is False:
                    self.money += enemy.value
                    enemy.used = True
                elif enemy.finished:
                    self.health -= 1
                    enemy.used = True
            enemy.update(dt)

        # LEVEN WON
        if (self.finished is False and self.alive_enemies == 0 and
                self.current_wave == self.max_wave):
            for button in self.buttons:
                button.toggle_active()
            self.buttons.append(Button(self.screen, self.screen.get_rect(),
                                caption="Wygrałeś naciśnij aby wrócić do menu",
                                command=self.go_to_menu))
            self.finished = True

        # LEVEL LOST
        if (self.finished is False and self.health <= 0):
            for button in self.buttons:
                button.toggle_active()
            self.buttons.append(Button(self.screen, self.screen.get_rect(),
                                caption="Przegrałeś naciśnij aby wrócić \
                                         do menu",
                                command=self.go_to_menu))
            self.finished = True

    def go_to_menu(self):
        self.done = True
        self.next = "menu"

    def prepare_areas(self):
        map_rect = self.screen.get_rect()
        map_rect.width -= map_rect.width // 5

        panel_rect = self.screen.get_rect()
        panel_rect.width -= map_rect.width
        panel_rect.midleft = map_rect.midright

        stat_rect = panel_rect.copy()
        stat_rect.h = int(panel_rect.h * 0.15)

        turret_rect = panel_rect.copy()
        turret_rect.h = int(panel_rect.h * 0.3)
        turret_rect.top = stat_rect.bottom

        info_rect = panel_rect.copy()
        info_rect.h = int(panel_rect.h * 0.4)
        info_rect.top = turret_rect.bottom

        button_rect = panel_rect.copy()
        button_rect.h = int(panel_rect.h * 0.15)
        button_rect.top = info_rect.bottom

        return (map_rect, panel_rect, stat_rect, turret_rect,
                info_rect, button_rect)

    def prepare_map(self):
        map_surface = Surface(self.map_rect.size)
        # print(self.resource_manager.maps)
        tile_map = self.resource_manager.maps[self.level_name]

        tile_size = self.textures["tile0"].get_rect().w

        tile_list = []

        for row_idx, row in enumerate(tile_map):
            for column_idx, tile in enumerate(row):

                tile_rect = self.textures["tile" + str(tile)].get_rect().copy()
                tile_rect.topleft = (column_idx * tile_size,
                                     row_idx * tile_size)

                map_surface.blit(self.textures["tile" + str(tile)],
                                 tile_rect)

                if tile in [2]:
                    tile_list.append([tile_rect, True])

                elif tile == 1:
                    spawn_point = tile_rect.topleft
                    spawn_tile = (column_idx, row_idx)

                elif tile == 4:
                    end_tile = (column_idx, row_idx)

        paths = self.prepare_paths(tile_map, spawn_tile, end_tile)

        return map_surface, tile_list, paths, spawn_point

    # returns paths in form of (direction, length, end_tile topleft corner)
    def prepare_paths(self, tile_map, spawn_tile, end_tile):
        paths = []

        current_tile = spawn_tile
        previous_tile = spawn_tile

        DX = [0, 0, 1, -1]
        DY = [1, -1, 0, 0]

        map_height = len(tile_map)
        map_length = len(tile_map[0])
        tile_size = self.textures["tile0"].get_rect().w

        while current_tile != end_tile:
            direction = 0
            path_length = 0

            for move_type in range(4):
                nx = current_tile[0] + DX[move_type]
                ny = current_tile[1] + DY[move_type]

                if (0 <= nx < map_length and 0 <= ny < map_height and
                        (nx, ny) != previous_tile and
                        tile_map[ny][nx] in LevelState.MOVABLE_TILES):

                    direction = move_type
                    break

            while True:
                tmp_tile = (current_tile[0] + DX[direction],
                            current_tile[1] + DY[direction])

                if (0 <= tmp_tile[0] < map_length and
                        0 <= tmp_tile[1] < map_height and
                        tile_map[tmp_tile[1]][tmp_tile[0]] in
                        LevelState.MOVABLE_TILES):
                    previous_tile = current_tile
                    current_tile = tmp_tile
                    path_length += 1
                else:
                    break

            paths.append(((DX[direction], DY[direction]),
                          path_length * tile_size,
                          (current_tile[0] * tile_size,
                           current_tile[1] * tile_size)))
        return paths

    def draw_stats(self):
        white = (255, 255, 255)
        money_rect = self.stat_rect.copy()
        money_rect.h = 30
        money_rect.y += 10
        money_rect.w -= 20
        money_rect.x += 10

        health_rect = money_rect.copy()
        health_rect.y += 30

        wave_rect = health_rect.copy()
        wave_rect.y += 30

        money_text1 = self.BASICFONT.render("Monety", True, white)
        money_text2 = self.BASICFONT.render(str(self.money), True, white)

        health_text1 = self.BASICFONT.render("Życia", True, white)
        health_text2 = self.BASICFONT.render(str(self.health), True, white)

        wave_text1 = self.BASICFONT.render("Fala", True, white)
        wave_text2 = self.BASICFONT.render(str(self.current_wave), True, white)

        cost0 = self.BASICFONT.render(str(Turret.get_cost(0)), True, white)
        cost1 = self.BASICFONT.render(str(Turret.get_cost(1)), True, white)
        cost2 = self.BASICFONT.render(str(Turret.get_cost(2)), True, white)
        x, y = self.buttons[0].rect.midbottom
        y += 3
        self.screen.blit(cost0, cost0.get_rect(midtop=(x, y)))
        x, y = self.buttons[1].rect.midbottom
        y += 3
        self.screen.blit(cost1, cost1.get_rect(midtop=(x, y)))
        x, y = self.buttons[2].rect.midbottom
        y += 3
        self.screen.blit(cost2, cost2.get_rect(midtop=(x, y)))

        self.screen.blit(money_text1, money_text1.get_rect(
                         midleft=money_rect.midleft))
        self.screen.blit(money_text2, money_text2.get_rect(
                         midright=money_rect.midright))
        self.screen.blit(health_text1, health_text1.get_rect(
                         midleft=health_rect.midleft))
        self.screen.blit(health_text2, health_text2.get_rect(
                         midright=health_rect.midright))
        self.screen.blit(wave_text1, wave_text1.get_rect(
                         midleft=wave_rect.midleft))
        self.screen.blit(wave_text2, wave_text2.get_rect(
                         midright=wave_rect.midright))

    def create_buttons(self):
        x, y, w, h = self.turrets_rect
        self.buttons.append(Button(self.screen,
                            self.textures["turret0"].get_rect(
                                topleft=(x + 43 * 2+64, 28 + y)),
                            texture=[self.textures["turret0"]],
                            command=lambda: self.set_current_turret(
                                turre_type=0)))

        self.buttons.append(Button(self.screen,
                            self.textures["turret1"].get_rect(
                                topleft=(x + 43, 28 + y)),
                            texture=[self.textures["turret1"]],
                            command=lambda: self.set_current_turret(
                                turre_type=1)))

        self.buttons.append(Button(self.screen,
                            self.textures["turret2"].get_rect(
                                topleft=(x + 43, 2 * 34 + 60 + y)),
                            texture=[self.textures["turret2"]],
                            command=lambda: self.set_current_turret(
                                turre_type=2)))

        x, y, w, h = self.button_rect

        self.buttons.append(Button(self.screen,
                            self.textures["speed2"].get_rect(
                                midright=self.button_rect.midright),
                            texture=[self.textures["speed2"]],
                            command=lambda: self.set_speed_multiplier(2)))

        self.buttons.append(Button(self.screen,
                            self.textures["speed1"].get_rect(
                                midright=self.buttons[-1].rect.midleft),
                            texture=[self.textures["speed1"]],
                            command=lambda: self.set_speed_multiplier(1.5)))

        self.buttons.append(Button(self.screen,
                            self.textures["speed0"].get_rect(
                                midright=self.buttons[-1].rect.midleft),
                            texture=[self.textures["speed0"]],
                            command=lambda: self.set_speed_multiplier(1)))

        self.buttons.append(Button(self.screen,
                            self.textures["home"].get_rect(
                                midright=self.buttons[-1].rect.midleft),
                            texture=[self.textures["home"]],
                            command=self.go_to_menu))

    def describe_turret(self):
        selected_turret = Turret.get_selected()
        if selected_turret is None:
            return

        white = (255, 255, 255)

        self.upgrade_button.set_command(
            self.upgrade_decorator(selected_turret))
        self.sell_button.set_command(self.sell_turret, selected_turret)

        dmg_rect = self.info_rect.copy()
        dmg_rect.h = 30
        dmg_rect.y += 10
        dmg_rect.w -= 20
        dmg_rect.x += 10

        range_rect = dmg_rect.copy()
        range_rect.y += 30

        wave_rect = range_rect.copy()
        wave_rect.y += 30

        dmg_text1 = self.BASICFONT.render("Obrażenie", True, white)
        dmg_text2 = self.BASICFONT.render(str(selected_turret.dmg), True,
                                          white)

        range_text1 = self.BASICFONT.render("Zasięg", True, white)
        range_text2 = self.BASICFONT.render(str(selected_turret.range), True,
                                            white)

        wave_text1 = self.BASICFONT.render("Prędkość ataku", True, white)
        wave_text2 = self.BASICFONT.render(str(selected_turret.att_speed),
                                           True, white)

        upgrade_cost_text = self.BASICFONT.render(
                str(selected_turret.get_upgrade_cost()), True, white)

        upgrade_cost_rect = self.upgrade_button.rect.copy()
        upgrade_cost_rect.y += 50

        self.screen.blit(dmg_text1, dmg_text1.get_rect(
            midleft=dmg_rect.midleft))
        self.screen.blit(dmg_text2, dmg_text2.get_rect(
            midright=dmg_rect.midright))
        self.screen.blit(range_text1, range_text1.get_rect(
            midleft=range_rect.midleft))
        self.screen.blit(range_text2, range_text2.get_rect(
            midright=range_rect.midright))
        self.screen.blit(wave_text1, wave_text1.get_rect(
            midleft=wave_rect.midleft))
        self.screen.blit(wave_text2, wave_text2.get_rect(
            midright=wave_rect.midright))
        self.screen.blit(upgrade_cost_text, upgrade_cost_text.get_rect(
            center=upgrade_cost_rect.center))

    def make_turret_buttons(self):
        dmg_rect = self.info_rect.copy()
        dmg_rect.h = 30
        dmg_rect.y += 10
        dmg_rect.w -= 20
        dmg_rect.x += 10

        range_rect = dmg_rect.copy()
        range_rect.y += 30

        wave_rect = range_rect.copy()
        wave_rect.y += 30
        upgrade_rect_center = list(wave_rect.center)
        upgrade_rect_center[0] -= 60
        upgrade_rect_center[1] += 70

        delete_rect_center = upgrade_rect_center.copy()
        delete_rect_center[0] += 120

        upgrade_button = Button(self.screen, self.textures["upgrade_button"].
                                get_rect(center=upgrade_rect_center),
                                [self.textures["upgrade_button"]])

        sell_button = Button(self.screen, self.textures["sell_button"].
                             get_rect(center=delete_rect_center),
                             [self.textures["sell_button"]])

        return upgrade_button, sell_button

    def set_current_turret(self, turre_type=0):
        self.current_turret = turre_type

    def set_speed_multiplier(self, speed_multiplier):
        self.speed_multiplier = speed_multiplier

    def sell_turret(self, selected_turret):
        self.money += int(selected_turret.used_money * 0.4)

        self.tiles[selected_turret.tile_id][1] = True

        del(self.turrets[self.turrets.index(selected_turret)])

        Turret.selected_turret = None

    def upgrade_decorator(self, selected_turret):

        def upgrade_turret():
            if self.money >= selected_turret.get_upgrade_cost():
                selected_turret.upgrade()
        return upgrade_turret


class Turret:

    #           DMG  RANGE AS
    BASE_STATS = [(5, 400, 0.1),
                  (3, 200, 0.02),
                  (10, 700, 1)]

    UPGRADES = [(5, 30, 0.1),
                (5, 30, 0.1),
                (5, 30, 0.1)]

    UPGRADE_COST = [10, 20, 30]

    COST = [20, 50, 70]

    @staticmethod
    def init(screen, turrets, enemies, projectiles, resource_manager):
        Turret.screen = screen
        Turret.turrets = turrets
        Turret.enemies = enemies
        Turret.projectiles = projectiles
        Turret.resource_manager = resource_manager
        Turret.textures = resource_manager.scaled_textures
        Turret.selected_turret = None

    def __init__(self, rect_topleft, turret_type, tile_id):
        self.turret_type = turret_type
        self.turret_name = "turret" + str(turret_type)
        self.tile_id = tile_id

        self.dmg, self.range, self.att_speed = Turret.BASE_STATS[turret_type]
        self.cost = Turret.COST[turret_type]

        self.current_target = None

        self.texture = Turret.textures[self.turret_name].copy()
        self.texture_rect = self.texture.get_rect(topleft=rect_topleft)
        self.center = self.texture_rect.center
        self.attack_timeout = 0
        self.selected = True
        self.lvl = 1
        self.upgrades_cost = 0
        self.used_money = self.cost

    def draw_range(self):
        if self.selected:
            circle(Turret.screen, (255, 0, 0), self.center, self.range, 4)

    def draw(self):
        self.draw_range()
        Turret.screen.blit(self.texture, self.texture_rect)

    def shoot(self):

        if self.attack_timeout > 0:
            return

        self.current_target = self.update_target()

        if self.current_target is not None:
            self.projectiles.append(
                Projectile.create_projectile(self.center,
                                             self.turret_type,
                                             self.current_target, self.dmg))

        self.attack_timeout = self.att_speed

    def update_target(self):
        if self.current_target is None:
            return self.find_target()
        elif (self.current_target.alive is False or
                Turret.euclid_dist(self.center, self.current_target.center)
                > self.range):
            return self.find_target()
        return None

    def find_target(self):
        target = None
        distance = 1e9

        for enemy in Turret.enemies:
            if enemy.alive is False:
                continue

            tmp_dist = Turret.euclid_dist(self.center, enemy.center)

            if tmp_dist < distance and tmp_dist <= self.range:
                distance = tmp_dist
                target = enemy

        return target

    def update(self, dt):
        self.attack_timeout -= dt
        self.shoot()

    def upgrade(self):
        self.used_money += Turret.UPGRADE_COST[self.turret_type] * self.lvl
        self.upgrades_cost += Turret.UPGRADE_COST[self.turret_type] * self.lvl
        self.lvl += 1
        self.dmg += Turret.UPGRADES[self.turret_type][0]

    def process_event(self, event):
        if event.type == pgl.MOUSEBUTTONUP:
            if self.texture_rect.collidepoint(event.pos):
                current_select = self.selected
                for turret in self.turrets:
                    turret.selected = False

                self.selected = current_select ^ 1

                if self.selected:
                    Turret.selected_turret = self
                else:
                    Turret.selected_turret = None

    @staticmethod
    def create_turret(rect_topleft, turret_type, tile_id):
        return Turret(rect_topleft, turret_type, tile_id)

    @staticmethod
    def get_selected():
        return Turret.selected_turret

    @staticmethod
    def get_cost(turret_type):
        return Turret.COST[turret_type]

    def get_upgrade_cost(self):
        return Turret.UPGRADE_COST[self.turret_type] * self.lvl

    @staticmethod
    def euclid_dist(point, point2):
        return sqrt(((point[0] - point2[0])**2) + ((point[1] - point2[1])**2))


class Enemy:

    # HP SPEED VALUE
    BASE_STATS = [(10, 700, 3),
                  (5, 1000, 3),
                  (60, 500, 3)]

    UPGRADES = [(2), (5), (5)]

    @staticmethod
    def init(screen, paths, resource_manager):
        Enemy.screen = screen
        Enemy.paths = paths
        Enemy.resource_manager = resource_manager
        Enemy.textures = resource_manager.scaled_textures

    def __init__(self, rect_topleft, enemy_type, wave):
        self.enemy_type = enemy_type
        self.enemy_name = "enemy" + str(enemy_type)

        self.path_id = 0
        self.passed_distance = 0

        self.hp, self.speed, self.value = Enemy.BASE_STATS[enemy_type]
        self.hp += (wave - 1) * Enemy.UPGRADES[enemy_type]
        self.alive = True
        self.finished = False
        self.used = False

        self.texture = Enemy.textures[self.enemy_name].copy()
        self.texture_rect = self.texture.get_rect(topleft=rect_topleft)
        self.center = list(self.texture_rect.center)

    def draw(self):
        if self.alive is True:
            Enemy.screen.blit(self.texture, self.texture_rect)

    def update(self, dt):

        if self.hp <= 0:
            self.alive = False
            return

        left_distance = dt * self.speed

        if self.path_id == len(Enemy.paths):
            return None

        direction, distance, end_point = Enemy.paths[self.path_id]

        if left_distance + self.passed_distance <= distance:
            self.center[0] += direction[0] * left_distance
            self.center[1] += direction[1] * left_distance
            self.passed_distance += left_distance
            self.texture_rect.center = tuple(self.center)
        else:
            left_distance -= distance - self.passed_distance

            self.texture_rect.topleft = end_point
            self.center = list(self.texture_rect.center)

            self.path_id += 1
            self.passed_distance = 0

            if self.path_id == len(Enemy.paths):
                self.alive = False
                self.finished = True
                return None

            direction, distance, end_point = Enemy.paths[self.path_id]

            self.center[0] += direction[0] * left_distance
            self.center[1] += direction[1] * left_distance
            self.passed_distance += left_distance
            self.texture_rect.center = tuple(self.center)

    def get_hit(self, dmg):
        self.hp -= dmg

    @staticmethod
    def create_enemy(rect_topleft, enemy_type, wave):
        return Enemy(rect_topleft, enemy_type, wave)


class Projectile:

    BASE_SPEED = [2500, 2500, 2500]

    @staticmethod
    def init(screen, resource_manager):
        Projectile.screen = screen
        Projectile.resource_manager = resource_manager
        Projectile.textures = resource_manager.scaled_textures

    def __init__(self, rect_center, projectile_type, target, dmg):

        self.projectile_type = projectile_type
        self.projectile_name = "projectile" + str(projectile_type)

        self.speed = Projectile.BASE_SPEED[projectile_type]
        self.alive = True

        self.texture = Projectile.textures[self.projectile_name].copy()
        self.texture_rect = self.texture.get_rect(center=rect_center)
        self.center = list(self.texture_rect.center)
        self.target = target
        self.dmg = dmg

        self.direction = self.get_direction()

    def draw(self):
        if self.alive:
            Projectile.screen.blit(self.texture, self.texture_rect)

    def update(self, dt):
        if self.alive is False:
            return
        if self.target.alive is False:
            self.alive = False
            return

        self.direction = self.get_direction()
        current_distance = Turret.euclid_dist(self.center, self.target.center)

        if current_distance <= 15:
            self.alive = False
            self.target.get_hit(self.dmg)
        else:
            self.center[0] += dt * self.speed * self.direction[0]
            self.center[1] += dt * self.speed * self.direction[1]
            self.texture_rect.center = self.center

    def get_direction(self):
        direction = Vector2(self.target.center[0] - self.center[0],
                            self.target.center[1] - self.center[1])

        try:
            direction = direction.normalize()
            return direction
        except ValueError:
            return Vector2(0, 0)

    @staticmethod
    def create_projectile(rect_center, projectile_type, target, dmg):
        return Projectile(rect_center, projectile_type, target, dmg)


class EnemySpawner:

    def __init__(self, screen, enemies, spawn_tile):
        self.screen = screen
        self.enemies = enemies
        self.spawn_tile = spawn_tile
        self.wave_number = 0
        self.formulas = [
            lambda x: x,
            lambda x: x - 5 if x > 6 else 0,
            lambda x: x - 9 if x > 10 else 0
        ]
        self.spawn_numbers = [0, 0, 0]

    def spawn_wave(self, wave_number):
        self.wave_number += 1
        self.spawn_numbers[0] += self.formulas[0](wave_number)
        self.spawn_numbers[1] += self.formulas[1](wave_number)
        self.spawn_numbers[2] += self.formulas[2](wave_number)

    def update(self, dt):
        for enemy_type, number in enumerate(self.spawn_numbers):
            if number != 0:
                if len(self.enemies):
                    previous_rect = self.enemies[-1].texture_rect
                    if previous_rect.colliderect(Rect(*self.spawn_tile,
                                                 64, 64)):
                        return
                    else:
                        self.spawn_numbers[enemy_type] -= 1
                        self.enemies.append(Enemy(self.spawn_tile, enemy_type,
                                                  self.wave_number))
                        return
                else:
                    self.spawn_numbers[enemy_type] -= 1
                    self.enemies.append(Enemy(self.spawn_tile, enemy_type,
                                        self.wave_number))
                    return
            self.spawninig_done = True
