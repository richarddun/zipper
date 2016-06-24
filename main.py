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
        map = ZippyMap(source='maps\/prototype1\/basic16px-680x800_metal.png')
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
        Clock.schedule_interval(self.update, 1.0/60.0)
        Clock.schedule_interval(self.updatewalk1, .2)
        Clock.schedule_interval(self.updatewalk2, .2a)
    def update(self, *ignore):
        dx = 0
        if keys.get(Keyboard.keycodes['spacebar']) and self.resting:
            self.dy = 9 * params.scale
            self.resting = False
        elif keys.get(Keyboard.keycodes['left']):
            dx -= 2 * params.scale
        elif keys.get(Keyboard.keycodes['right']):
            dx += 2 * params.scale
        self.x += dx

    def updatewalk1(self, *ignore):
        if keys.get(Keyboard.keycodes['left']):
            self.texture = self.images['walk_2_left']
        elif keys.get(Keyboard.keycodes['right']):
            self.texture = self.images['walk_2_right']

    def updatewalk2(self, *ignore):
         if keys.get(Keyboard.keycodes['left']):
            self.texture = self.images['walk_1_left']
         elif keys.get(Keyboard.keycodes['right']):
            self.texture = self.images['walk_1_right']

params = params()

if __name__ == '__main__':
    def on_key_down(window, keycode, *rest):
        keys[keycode] = True
    def on_key_up(window, keycode, *rest):
        keys[keycode] = False
    Window.bind(on_key_down=on_key_down, on_key_up=on_key_up)
    ZippyApp().run()

        #leaving this here for later...
        #self.animleft = Animation(x = self.x-30, y = self.y, duration=.06)
        #self.animrigt = Animation(x = self.x+30, y = self.y, duration=.06)
        #self.animup = Animation(x = self.x, y = self.y+30, duration = .06)
        #self.animdown = Animation(x = self.x, y = self.y-30, duration = .06)
        #self.animdowl = Animation(x = self.x-30, y = self.y-30, duration = .06)
        #self.animdowr = Animation(x = self.x+30, y = self.y-30, duration = .06)
        #self.animuple = Animation(x = self.x-30, y = self.y+30, duration = .06)
        #self.anumupri = Animation(x = self.x+30, y = self.y+30, duration = .06)
