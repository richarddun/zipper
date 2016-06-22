from kivy.app import App
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.uix.widget import Widget
#from kivy.metrics import sp
from kivy.clock import Clock
#from kivy.utils import platform

#import pytmx

class ZippyApp(App):
    def build(self):
        sprite = Player_Sprite(source='animation\/transparent\/walk_1.png')
        map = ZippyMap()
        map.add_widget(sprite)
        return map

class ZippyMap(Image):
    def __init__(self,**kwargs):
        super(ZippyMap,self).__init__(**kwargs)
        self.size = self.texture_size

class Player_Sprite(Image):
    def __init__(self,**kwargs):
        super(Player_Sprite,self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(None, self)

        if not self._keyboard:
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):

        self.animleft = Animation(x = self.x-30, y = self.y, duration=.06)
        self.animrigt = Animation(x = self.x+30, y = self.y, duration=.06)
        self.animup = Animation(x = self.x, y = self.y+30, duration = .06)
        self.animdown = Animation(x = self.x, y = self.y-30, duration = .06)
        self.animdowl = Animation(x = self.x-30, y = self.y-30, duration = .06)
        self.animdowr = Animation(x = self.x+30, y = self.y-30, duration = .06)
        self.animuple = Animation(x = self.x-30, y = self.y+30, duration = .06)
        self.anumupri = Animation(x = self.x+30, y = self.y+30, duration = .06)

        if keycode[1] == 'left' and self.x > 0:
            if keycode[1] == 'down':
                self.animdowl.start(self)
                self.x -= 30
                self.y += 30
            else:
                self.animleft.start(self)
                self.x -= 5
            print str(self.x)
        elif keycode[1] == 'right' and self.x < 500:
            self.animrigt.start(self)
            self.x += 5
            print str(self.x)
        elif keycode[1] == 'up':
            self.animup.start(self)
            self.y += 5
        elif keycode[1] == 'down':
            if self.y >= 5:
                self.animdown.start(self)
                self.y -= 5
        else:
            return False
        return True

ZippyApp().run()

