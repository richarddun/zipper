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
        self.map = tmx.TileMapWidget('\users\/richarddun\dropbox\project_alpha\zipper\Maps\prototype1\/16px-680x800-metal.tmx',Window.size,tempscale)
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
        self.scale = self.height / 252.      # 21 tile size * 12

class Player_Sprite(Image):
    def __init__(self,pos,mapz,**kwargs):
        super(Player_Sprite,self).__init__(pos=pos,**kwargs)  #size=(145,80),
        self.mov_images = Atlas('animation/dup/dupdup/zipperanimatlas.atlas')
        self.map = mapz
        self.texture = self.mov_images['walk_1_right']
        self.moving_right = False
        self.resting = True
        self.moving_left = False
        self.movyval = 0
        self.suspended = 0
        self.jumping = False


    def update(self, *ignore):
        dx,self.dy = 0,0
        last = Rect(*(self.pos + self.size))#Rect(self.pos[0]+(self.width*.25),self.pos[1], (self.size[0]*.47), self.size[1])
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
        if keys.get(Keyboard.keycodes['left']) and not keys.get(Keyboard.keycodes['right']):
            dx -= 5 * params.scale
            self.moving_left = True
            self.moving_right = False
        elif keys.get(Keyboard.keycodes['right']) and not keys.get(Keyboard.keycodes['left']):
            dx += 5 * params.scale
            self.moving_right = True
            self.moving_left = False
        elif (keys.get(Keyboard.keycodes['right']) and (keys.get(Keyboard.keycodes['left']))):
            self.moving_left, self.moving_right = False,False
        elif not self.jumping and not (keys.get(Keyboard.keycodes['right']) and (keys.get(Keyboard.keycodes['left']))):
            if self.moving_left and self.resting:
                self.texture = self.mov_images['walk_1_left']
                self.moving_left = False
            elif self.moving_right and self.resting:
                self.texture = self.mov_images['walk_1_right']
                self.moving_right = False
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
        new = Rect(*(self.pos + self.size))
        #new=Rect(self.pos[0]+(self.width*.25),self.pos[1], (self.size[0]*.47), self.size[1])
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
                new.right = cell.left-1
            if 'r' in blocker and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right+1

        self.pos = new.bottomleft#[0]-self.width*.25, new.bottomleft[1]

params = params()

if __name__ == '__main__':
    def on_key_down(window, keycode, *rest):
        keys[keycode] = True
    def on_key_up(window, keycode, *rest):
        keys[keycode] = False
    Window.bind(on_key_down=on_key_down, on_key_up=on_key_up)
    ZippyApp().run()

