#!/usr/bin/env python
#-*- coding: utf8 -*-

from animations import BulletExplosion, FullSizeExplosion
from stuff_on_map import *
import ai
import math
import random


class World (object):

    def __init__(self, game_map, players, texture_loader):
        self.players = players
        self.map = game_map
        self.texture_loader = texture_loader
        self._drawables = []
        self.enemies = []
        self.ai = ai.ZombieDriver(self)
        self.enemies_killed = 0
        self.enemeis_to_kill = 20
        self.un_flags = []

        self._bullets = pygame.sprite.RenderUpdates()
        self._visible_terrain = pygame.sprite.RenderUpdates()
        self._all_unpassable = pygame.sprite.RenderUpdates()
        self._all_passable = pygame.sprite.RenderUpdates()
        self._movable = pygame.sprite.RenderUpdates()
        self._animations = pygame.sprite.RenderUpdates()

    def init(self):
        for player in self.players:
            self._movable.add(player.tank)
        self._visible_terrain.add(*[self.map.objects + self.map.unpassable +
                self.map.un_flags + self.map.passable])
        self._all_unpassable.add(*[self.map.objects + self.map.unpassable +
                self.map.limits_guard + self.map.un_flags])
        self._all_passable.add(*self.map.passable)
        self.map.render.set_background(self._visible_terrain)
        for flag in self.map.un_flags:
            self.un_flags.append(flag)

    def get_end_game_stats(self):
        return _("Enemies killed: %d / %d") % (self.enemies_killed, self.enemeis_to_kill)

    def tick_only_animations(self, deltat, events):
        '''
            Progress the currently active animations and nothing else.
        '''
        self.map.render.clear([self._movable, self._bullets, self._animations])
        for anim in self._animations:
            if anim.finished:
                self._animations.remove(anim)
        self._animations.update(deltat)
        self._drawables = [self._movable, self._bullets, self._animations]

    def tick(self, deltat, events):
        '''
            Progresses the game world forward. This includes moving the game objects, processing
            events from players, trying for collisions and checking the game objectives.
        '''
        if self.enemies_killed >= self.enemeis_to_kill:
            return GAME_WON

        bullets = self._bullets
        unpassable = self._all_unpassable

        self.map.render.clear([bullets, self._movable, self._animations])
        for anim in self._animations:
            if anim.finished:
                self._animations.remove(anim)
        self._animations.update(deltat)

        players_tanks = []
        alive_enemies = len(self.enemies)

        if alive_enemies < 6 and random.randint(0, 100) < 0.05 and \
                (self.enemies_killed + alive_enemies) < self.enemeis_to_kill:
            self.spawn_enemy()

        for player in self.players:
            player.process_events(events)
            if player.tank is None:
                continue
            players_tanks.append(player.tank)
            bullets.add(*player.tank.bullets)

        if len(players_tanks) < 1:
            return GAME_OVER

        self.ai.tick(deltat, self.enemies)

        for enemy in self.enemies:
            bullets.add(*enemy.bullets)

        tanks = pygame.sprite.RenderUpdates(*(players_tanks + self.enemies))

        bullet_stoppers = players_tanks + self.map.objects + self.enemies + \
            bullets.sprites() + self.map.limits_guard + self.map.un_flags
        bullet_stoppers = pygame.sprite.Group(bullet_stoppers)

        collisions = pygame.sprite.groupcollide(bullets, bullet_stoppers, False, False)

        for bullet in collisions:
            collided_with = collisions[bullet]
            if len(collided_with) == 1 and bullet in collided_with:
                continue
            if bullet.owner is not None:
                bullet.owner.bullets.remove(bullet)
            bullet.explode_sound()
            bullets.remove(bullet)

            non_self = None
            for obj in collided_with:
                if obj is bullet:
                    continue
                non_self = obj

            ex, ey = bullet.rect.center
            if bullet.direction == DIRECTION_LEFT:
                ex = non_self.rect.centerx + non_self.rect.width * 0.5
            if bullet.direction == DIRECTION_RIGHT:
                ex = non_self.rect.centerx - non_self.rect.width * 0.5
            if bullet.direction == DIRECTION_UP:
                ey = non_self.rect.centery + non_self.rect.height * 0.5
            if bullet.direction == DIRECTION_DOWN:
                ey = non_self.rect.centery - non_self.rect.height * 0.5
            explosion_animation = BulletExplosion((ex, ey))
            self._animations.add(explosion_animation)

            for collided in collided_with:
                if collided == bullet:
                    continue
                if isinstance(collided, UnFlag):
                    self.map.un_flags.remove(collided)
                    self._visible_terrain.remove(collided)
                    self.map.render.set_background(self._visible_terrain)
                    explosion_animation = FullSizeExplosion(collided.rect.center)
                    self._animations.add(explosion_animation)
                    return GAME_OVER
                if not isinstance(collided, BasicTank):
                    continue
                if collided is bullet.owner:
                    continue

                if not collided.is_player and not bullet.is_player_bullet:
                    continue

                for orphan in collided.bullets:
                    orphan.owner = None

                self._movable.remove(collided)
                explosion_animation = FullSizeExplosion(collided.rect.center)
                self._animations.add(explosion_animation)

                if isinstance(collided, EnemyTank):
                    self.enemies.remove(collided)
                    collided.stop()
                    collided.explode_sound()
                    self.enemies_killed += 1
                if isinstance(collided, Tank):
                    tanks.remove(collided)
                    collided.stop()
                    for player in self.players:
                        if player.tank is collided:
                            player.tank.explode_sound()
                            player.tank = None

        bullets.update(deltat)

        for tank in tanks:
            other_tanks = [t for t in tanks if t != tank]
            previously_collided = pygame.sprite.spritecollide(tank, other_tanks, False, False)

            tank.update(deltat)

            collision = pygame.sprite.spritecollideany(tank, unpassable)

            if collision is not None:
                tank.undo()
                continue

            others = pygame.sprite.spritecollide(tank, other_tanks, False, False)
            if len(others) < 1:
                continue

            for other in others:
                if other not in previously_collided:
                    tank.undo()
                    break

                dist = math.sqrt(
                    abs(tank.rect.centerx - other.rect.centerx) ** 2 +
                    abs(tank.rect.centery - other.rect.centery) ** 2
                )

                if dist < self.map.scaled_box_size * 0.75:
                    tank.undo()
                    break


        self._drawables = [self._movable, bullets, self._animations]
        return GAME_CONTINUE

    def active_animations_count(self):
        return len(self._animations)

    def spawn_enemy(self):
        player_objects = []
        for player in self.players:
            if player.tank is None:
                continue
            player_objects.append(player.tank)
            player_objects += player.tank.bullets

        for i in range(10):
            index = random.randint(0, len(self.map.enemy_starts) - 1)
            position = self.map.enemy_starts[index]
            new_enemy = EnemyTank(position, self.texture_loader)
            collisions = pygame.sprite.groupcollide(
                [new_enemy],
                self._movable,
                False,
                False
            )
            if len(collisions):
                # we should not spawn an enemy on top of an other enemy
                continue
            self._movable.add(new_enemy)
            self.enemies.append(new_enemy)
            break

    def get_drawables(self):
        return self._drawables

    def objects_at(self, coords):
        return []
