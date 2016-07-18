from kivy.app import App
from kivy.core.window import Window, Keyboard
from kivy.uix.image import Image
from kivy.atlas import Atlas
from kivy.uix.widget import Widget
from kivy.clock import Clock
import tmx
from rect import Rect
from collections import defaultdict

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

    def update(self, *ignore):
        dx, self.dy = 0, 0
        # last = Rect(*(self.pos + self.size))
        if keys.get(Keyboard.keycodes['right']):
            self.prevdir = 'right'
        if keys.get(Keyboard.keycodes['left']):
            self.prevdir = 'left'
        last = Rect(self.pos[0]+(self.width*.42),self.pos[1], (self.size[0]/6), self.size[1])
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
            dx -= 5 * params.scale
            self.moving_left = True
            self.moving_right = False
        elif keys.get(Keyboard.keycodes['right']) or keys.get(Keyboard.keycodes['d']) and not \
                keys.get(Keyboard.keycodes['left']):
            dx += 5 * params.scale
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
        self.x += dx
        self.y += self.dy
        # new = Rect(*(self.pos + self.size))
        new = Rect(self.pos[0]+(self.width*.42), self.pos[1], (self.size[0]/6), self.size[1])
        """Rect instantiated with x set to where character drawing is, relative to the
         overall width of the image (5/12 (42%) of the image, 1/6 wide) for more precise
         collision as the character drawing is centered within a larger transparent image"""
        for cell in self.map.map.layers['blocker'].collide(new, 'blocker'):
            blocker = cell['blocker']
            if 't' in blocker and last.bottom >= cell.top and new.bottom < cell.top:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blocker and last.top <= cell.bottom and new.top > cell.bottom:
                new.top = cell.bottom
                self.dy = 0
                self.suspended = 0
            if 'l' in blocker and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left-1  # 1 pixel for padding, to prevent corner sticking
            if 'r' in blocker and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right+1  # 1 pixel for padding, to prevent corner sticking
        self.pos = new.bottomleft[0]-self.width*.42, new.bottomleft[1]

params = params()

if __name__ == '__main__':
    def on_key_down(window, keycode, *rest):
        keys[keycode] = True
    def on_key_up(window, keycode, *rest):
        keys[keycode] = False
    Window.bind(on_key_down=on_key_down, on_key_up=on_key_up)
    ZippyApp().run()

