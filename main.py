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
        baselayer = ZippyBase()
        sprite = Player_Sprite(source='animation\/transparent\/walk_1.png')
        map = ZippyMap(source='maps\/prototype1\/basic16px-680x800_metal.png')
        baselayer.add_widget(map)
        map.add_widget(sprite)
        return baselayer

class ZippyBase(Widget):
    def __init__(self, **kwargs):
        super(ZippyBase,self).__init__(**kwargs)

class ZippyMap(Image):
    def __init__(self,**kwargs):
        super(ZippyMap,self).__init__(**kwargs)
        self.size = self.texture_size

class Player_Sprite(Image):
    def __init__(self,**kwargs):
        super(Player_Sprite,self).__init__(**kwargs)
        self.xval = 1
        self._keyboard = Window.request_keyboard(None, self)
        if not self._keyboard:#if the keyboard fails
            return
        self._keyboard.bind(on_key_down=self.on_keyboard_down)
        self.frametrigger = Clock.create_trigger(self.frametick)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        val = keycode[1]
        if val == 'left':
            if self.x > 0:
                self.xval -= 10
        elif val == 'right':
            self.xval += 10
        self.frametrigger()

    def frametick(self, *ignore):
        self.x = self.xval

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
