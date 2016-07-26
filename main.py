from kivy.app import App
from kivy.core.window import Window, Keyboard
from kivy.uix.image import Image
from kivy.atlas import Atlas
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.vector import Vector
import tmx
from rect import Rect
from collections import defaultdict
from math import atan2, degrees, pi

keys = defaultdict(lambda: False)

class ZippyApp(App):
    def build(self):
        return ZippyGame()

class ZippyGame(Widget):
    def __init__(self, **kwargs):
        super(ZippyGame,self).__init__(**kwargs)
        tempscale = Window.height / 256.
        self.map = tmx.TileMapWidget(
            '\users\/richarddun\dropbox\project_alpha\zipper\Maps\prototype1\/16px-680x800-metal.tmx',
            Window.size,tempscale)
        spawn = self.map.map.layers['start'].find('spawn')[0]
        self.sprite = Player_Sprite((spawn.px,spawn.py),self.map)
        self.add_widget(self.map)
        self.map.add_widget(self.sprite)
        Clock.schedule_interval(self.update, 1.0/60.0)

    def update(self, *ignore):
        self.sprite.update()
        self.map.set_focus(*self.sprite.pos)

class params(object):
    def __init__(self):
        self.width, self.height = Window.size
        self.scale = self.height / 256.      # 21 tile size * 12

class Player_Sprite(Image):
    def __init__(self,pos,mapz,**kwargs):
        super(Player_Sprite,self).__init__(pos=pos, size=(193,81),*kwargs)
        self.mov_images = Atlas("animation\/movement\/animatlas.atlas")
        self.atk_images = Atlas("animation\/attack/atk.atlas")
        self.spe_images = Atlas("animation\/special\/specatlas.atlas")
        self.map = mapz
        self.texture = self.mov_images['walk_1_right']
        self.moving_right = False
        self.resting = True
        self.moving_left = False
        self.movyval = 0
        self.suspended = 0
        self.jumping = False
        self.prevdir = 'right'
        self.atkcounter = 0
        self.touching = False
        self.perma_x = self.map.map.view_w / 2
        self.perma_y = self.map.map.view_y / 2
        self.skew_x_touch, self.skew_y_touch = 0,0
        self.zipping = False
        self.sticking = False
        self.coldir = 'n'

    def orientation(self, touch):
        """
        :param touch:
        receive Kivy touch location, find difference between touch and
        current self.position.  Calculate angle, display an image based
        on the angle
        :return:
        none
        """
        self.skew_x_touch = self.map.map.viewport.bottomleft[0] + touch.pos[0]
        self.skew_y_touch = self.map.map.viewport.bottomleft[1] + touch.pos[1]
        self.touch_skew = (self.skew_x_touch, self.skew_y_touch)
        # Above skew_x and skew_y track the x/y touch positions, plus the position of the current viewport
        # to aid in finding the 'true' touch value as expressed with reference to the full map.
        self.delta_x = self.skew_x_touch - self.new.center[0]
        self.delta_y = self.skew_y_touch - self.new.center[1]
        self.bearing = atan2(self.delta_y, self.delta_x) * 180 / pi

    def prep_zip(self, touch):
        self.touching = True
        if not self.zipping:
            self.orientation(touch)
            self.origin = Vector(*self.new.center)
            self.target = Vector(*self.touch_skew)
            self.tgetdir = self.target - self.origin
            self.movedir = self.tgetdir.normalize()

    def on_touch_down(self, touch):
        self.prep_zip(touch)

    def on_touch_move(self, touch):
        self.prep_zip(touch)

    def on_touch_up(self, touch):
        self.touching = False
        self.coldir = 'n'

    def atk(self,dt):
        if self.prevdir == 'left':
            if self.atkcounter < 10:
                self.texture = self.atk_images['attack2_l']
                self.atkcounter += 1
            #self.texture = self.atk_images['attack3_l']
        elif self.prevdir == 'right':
            if self.atkcounter < 10:
                self.texture = self.atk_images['attack2_r']
                self.atkcounter += 1
             #self.texture = self.atk_images['attack2_r']

    def zip(self):
        self.x += self.movedir.x * (40*params.scale)
        self.y += self.movedir.y * (40*params.scale)
        self.coldir = 'n'
        if self.move_or_collide():
            self.zipping = False
        else:
            self.zipping = True

    def update(self, *ignore):
        if (self.touching or self.sticking) or (self.zipping):
            if self.coldir == 't' or self.coldir == 'n':
                if self.bearing >= 0 and self.bearing <= 30:
                    self.texture = self.spe_images['special_r_1']
                elif self.bearing > 30 and self.bearing <= 60:
                    self.texture = self.spe_images['special_r_2']
                elif self.bearing > 60 and self.bearing <= 90:
                    self.texture = self.spe_images['special_r_3']
                elif self.bearing > 90 and self.bearing <= 120:
                    self.texture = self.spe_images['special_l_3']
                elif self.bearing > 120 and self.bearing <= 150:
                    self.texture = self.spe_images['special_l_2']
                elif self.bearing > 150 and self.bearing <= 180:
                    self.texture = self.spe_images['special_l_1']
            elif self.coldir == 'b':
                if self.bearing <= 0 and self.bearing >= -30:
                    self.texture = self.spe_images['special_r_1_u']
                elif self.bearing < -30 and self.bearing >= -60:
                    self.texture = self.spe_images['special_r_2_u']
                elif self.bearing < -60 and self.bearing >= -90:
                    self.texture = self.spe_images['special_r_3_u']
                elif self.bearing < -90 and self.bearing >= -120:
                    self.texture = self.spe_images['special_l_3_u']
                elif self.bearing < -120 and self.bearing >= -150:
                    self.texture = self.spe_images['special_l_2_u']
                elif self.bearing < -150 and self.bearing >= -180:
                    self.texture = self.spe_images['special_l_1_u']
            if (keys.get(Keyboard.keycodes['z']) or self.zipping):
                self.resting = True
                self.zip()

            if keys.get(Keyboard.keycodes['c']):
                self.resting = False

        else:
            self.dx, self.dy = 0, 0
            if keys.get(Keyboard.keycodes['right']):
                self.prevdir = 'right'
            if keys.get(Keyboard.keycodes['left']):
                self.prevdir = 'left'
            self.last = Rect(self.pos[0]+(self.width*.42),self.pos[1], (self.size[0]/6), self.size[1])
            if keys.get(Keyboard.keycodes['x']):
                Clock.schedule_once(self.atk)
            if not keys.get(Keyboard.keycodes['x']):
                self.atkcounter = 0

            if keys.get(Keyboard.keycodes['spacebar']) and self.resting:
                if self.moving_right:
                    self.texture = self.mov_images['walk_2_right']
                elif self.moving_left:
                    self.texture = self.mov_images['walk_2_left']
                self.jumping = True
                self.resting = False
                self.dy = 5 * params.scale
            elif keys.get(Keyboard.keycodes['spacebar']) and self.jumping:
                if self.movyval > 20:
                    self.jumping = False
                    self.movyval = 0
                    if self.moving_right:
                        self.texture = self.mov_images['walk_2_right']
                    elif self.moving_left:
                        self.texture = self.mov_images['walk_2_left']
                    self.dy -= 6 * params.scale
                else:
                    if self.moving_right:
                        self.texture = self.mov_images['jump_r']
                    elif self.moving_left:
                        self.texture = self.mov_images['jump_l']
                    self.dy = 5 * params.scale
                    self.movyval += .5
            if self.jumping and not keys.get(Keyboard.keycodes['spacebar']):
                self.jumping = False
                self.movyval = 0
            if not self.jumping:
                if self.moving_right:
                    self.texture = self.mov_images['walk_2_right']
                    self.dy -= 6 * params.scale
                elif self.moving_left:
                    self.texture = self.mov_images['walk_2_left']
                    self.dy -= 6 * params.scale
                else:
                    self.dy -= 6 * params.scale
            if keys.get(Keyboard.keycodes['left']) or keys.get(Keyboard.keycodes['a']) and not \
                    keys.get(Keyboard.keycodes['right']):
                self.dx -= 5 * params.scale
                self.moving_left = True
                self.moving_right = False
            elif keys.get(Keyboard.keycodes['right']) or keys.get(Keyboard.keycodes['d']) and not \
                    keys.get(Keyboard.keycodes['left']):
                self.dx += 5 * params.scale
                self.moving_right = True
                self.moving_left = False
            elif keys.get(Keyboard.keycodes['right']) or keys.get(Keyboard.keycodes['d']) and \
                    keys.get(Keyboard.keycodes['left']) or keys.get(Keyboard.keycodes['a']):
                self.moving_left, self.moving_right = False,False
            elif not self.jumping and not (keys.get(Keyboard.keycodes['right']) and (keys.get(Keyboard.keycodes['left']))):
                if self.moving_left and self.resting:
                    self.texture = self.mov_images['walk_1_left']
                    self.moving_left = False
                elif self.moving_right and self.resting:
                    self.texture = self.mov_images['walk_1_right']
                    self.moving_right = False
                else:
                    if self.prevdir == 'left':
                       self.texture = self.mov_images['walk_1_left']
                    elif self.prevdir == 'right':
                        self.texture = self.mov_images['walk_1_right']
            if self.moving_left:
                if self.jumping:
                    self.texture = self.mov_images['jump_l']
                else:
                    self.texture = self.mov_images['walk_2_left']
            if self.moving_right:
                if self.jumping:
                    self.texture = self.mov_images['jump_r']
                else:
                    self.texture = self.mov_images['walk_2_right']
            if not self.zipping:
                self.x += self.dx
                self.y += self.dy
                self.move_or_collide()

    def move_or_collide(self):
        blocked = False
        self.new = Rect(self.pos[0]+(self.width*.42), self.pos[1], (self.size[0]/6), self.size[1])
        """Rect instantiated with x set to where character drawing is, relative to the
         overall width of the image (5/12 (42%) of the image, 1/6 wide) for more precise
         collision as the character drawing is centered within a larger transparent image"""
        for cell in self.map.map.layers['blocker'].collide(self.new, 'blocker'):
            blocker = cell['blocker']
            if 't' in blocker and self.last.bottom >= cell.top and self.new.bottom < cell.top:
                self.resting = True
                self.new.bottom = cell.top
                self.dy = 0
                self.coldir = 't'
                blocked = True
            if 'b' in blocker and self.last.top <= cell.bottom and self.new.top > cell.bottom:
                self.new.top = cell.bottom
                self.dy = 0
                self.coldir = 'b'
                blocked = True
            if 'l' in blocker and self.last.right <= cell.left and self.new.right > cell.left:
                self.new.right = cell.left-1  # 1 pixel for padding, to prevent corner sticking
                self.coldir = 'l'
                blocked = True
            if 'r' in blocker and self.last.left >= cell.right and self.new.left < cell.right:
                self.new.left = cell.right+1  # 1 pixel for padding, to prevent corner sticking
                self.coldir = 'r'
                blocked = True
            self.pos = self.new.bottomleft[0]-self.width*.42, self.new.bottomleft[1]
            self.posref = self.pos
        if blocked == True:
            return True
        else:
            return False

params = params()

if __name__ == '__main__':
    def on_key_down(window, keycode, *rest):
        keys[keycode] = True
    def on_key_up(window, keycode, *rest):
        keys[keycode] = False

    Window.bind(on_key_down=on_key_down, on_key_up=on_key_up)
    ZippyApp().run()

