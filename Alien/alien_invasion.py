import sys

import pygame
from pygame.sprite import Group

from setting import Setting
from ship import Ship
from alien import Alien
from game_stats import GameStats
import game_functions as gf

def run_game():
    pygame.init()
    ai_setting = Setting()
    screen = pygame.display.set_mode((
        ai_setting.screen_width,
        ai_setting.screen_height
    ))
    pygame.display.set_caption("Alien Invasion")

    #创建一个用于储存游戏统计信息的实例
    stats = GameStats(ai_setting)

    #创建一艘飞船 一个子弹编组和一个外星人编组
    ship = Ship(ai_setting, screen)
    bullets = Group()
    aliens = Group()
    #创建外星人群
    gf.create_fleet(ai_setting, screen, ship, aliens)
    

    while True:

        gf.check_events(ai_setting, screen, ship, bullets)
        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_setting, screen, ship, aliens, bullets)
            gf.update_aliens(ai_setting, stats, screen, ship, aliens, bullets)
        gf.update_screen(ai_setting, screen, ship, aliens, bullets)

run_game()