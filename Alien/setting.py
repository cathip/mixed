class Setting():

    def __init__(self):
        
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        #飞船的设置
        self.ship_speed_factor = 1.5
        self.ship_limit = 3

        #子弹设置
        self.bullet_speed_factor = 3
        self.bullet_width = 10
        self.bullet_height = 30
        self.bullet_color = 245, 192, 10
        self.bullet_allowed = 30

        #外星人设置
        self.alien_speed_factor = 1
        self.fleet_drop_speed = 50
        #fleet_direction  1表示右移 -1表示左移
        self.fleet_direction = 1