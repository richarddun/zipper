from kivy.app import App
from kivy.core.window import Window, Keyboard
from kivy.uix.image import Image
from kivy.atlas import Atlas
from kivy.animation import Animation
from kivy.uix.widget import Widget
#from kivy.metrics import sp
from kivy.clock import Clock
#from kivy.utils import platform
#import pytmx
from collections import defaultdict

keys = defaultdict(lambda: False)

class ZippyApp(App):
    def build(self):
        baselayer = ZippyBase()
        sprite = Player_Sprite(source='animation\/transparent\/walk_1.png')
        map = ZippyMap(source='maps\/prototype1\/basic16px-680x800_metal.png',allow_stretch=True)
        baselayer.add_widget(map)
        map.add_widget(sprite)
        return baselayer

class ZippyBase(Widget):
    def __init__(self, **kwargs):
        super(ZippyBase,self).__init__(**kwargs)

class params(object):
    def __init__(self):
        self.width, self.height = Window.size
        self.scale = self.height / 252.      # 21 tile size * 12

class ZippyMap(Image):
    def __init__(self,**kwargs):
        super(ZippyMap,self).__init__(**kwargs)
        self.size = self.texture_size

class Player_Sprite(Image):
    def __init__(self,**kwargs):
        super(Player_Sprite,self).__init__(**kwargs)

        self.images = Atlas('animation/animatlas/myatlas.atlas')
        self.texture = self.images['walk_1_right']
        self.rightick = 0
        self.leftick = 0
        self.moving_right = False
        self.resting = True
        self.moving_left = False
        self.maxjump = 10 * params.scale
        self.jumping = False
        Clock.schedule_interval(self.update, 1.0/60.0)

    def update(self, *ignore):
        dx,self.dy = 0,0

        if keys.get(Keyboard.keycodes['spacebar']) and self.resting:
            self.jumping = True
            self.resting = False
            self.dy = 2 * params.scale
        elif keys.get(Keyboard.keycodes['spacebar']) and self.jumping:
            self.dy = 2 * params.scale
        elif self.jumping and not keys.get(Keyboard.keycodes['spacebar']):
            self.jumping = False
        elif self.jumping == False and self.y > 0:
            self.dy -= 3 * params.scale
        elif self.jumping == False and self.y <= 0:
            self.resting = True
        if keys.get(Keyboard.keycodes['left']) and not keys.get(Keyboard.keycodes['right']):
            dx -= 4 * params.scale
            self.moving_left = True
            self.moving_right = False
        elif keys.get(Keyboard.keycodes['right']) and not keys.get(Keyboard.keycodes['left']):
            dx += 4 * params.scale
            self.moving_right = True
            self.moving_left = False
        elif (keys.get(Keyboard.keycodes['right']) and (keys.get(Keyboard.keycodes['left']))):
            self.moving_left, self.moving_right = False,False
        elif not self.jumping and not (keys.get(Keyboard.keycodes['right']) and (keys.get(Keyboard.keycodes['left']))):
            if self.moving_left:
                self.texture = self.images['walk_1_left']
                self.moving_left = False
            elif self.moving_right:
                self.texture = self.images['walk_1_right']
                self.moving_right = False

        if self.moving_left:
            self.texture = self.images['walk_2_left']
        if self.moving_right:
            self.texture = self.images['walk_2_right']


        self.x += dx
        self.y += self.dy

params = params()

if __name__ == '__main__':
    def on_key_down(window, keycode, *rest):
        keys[keycode] = True
    def on_key_up(window, keycode, *rest):
        keys[keycode] = False
    Window.bind(on_key_down=on_key_down, on_key_up=on_key_up)
    ZippyApp().run()

