import pdb
import sys
from kivy.app import App
from kivy.core.window import Window, Keyboard
from kivy.uix.image import Image
from kivy.atlas import Atlas
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.vector import Vector
import tmx
from rect import Rect
from collections import defaultdict
from math import atan2, degrees, pi

keys = defaultdict(lambda: False)
sys.setrecursionlimit(10000)

class ZippyApp(App):
    def build(self):
        return ZippyGame()

class ZippyGame(Widget):
    def __init__(self, **kwargs):
        super(ZippyGame,self).__init__(**kwargs)
        tempscale = Window.height / 256.
        self.map = tmx.TileMapWidget(
            'Maps\prototype1\/16px-680x800-metal.tmx',
            Window.size,tempscale)
        spawn = self.map.map.layers['start'].find('spawn')[0]
        self.pb = ProgressBar()
        self.pb.value = 500
        self.sprite = Player_Sprite((spawn.px,spawn.py),self.map)
        self.add_widget(self.map)
        self.map.add_widget(self.sprite)
        Clock.schedule_interval(self.update, 1.0/60.0)

    def update(self, *ignore):
        self.sprite.update()
        self.map.set_focus(*self.sprite.pos)

class params(object):
    """
    Initialise some useful parameters for scaling
    """
    def __init__(self):
        self.width, self.height = Window.size
        self.scale = self.height / 256.      # 21 tile size * 12

class Player_Sprite(Image):
    def __init__(self,pos,mapz,**kwargs):
        super(Player_Sprite,self).__init__(pos=pos,size=(195,164),*kwargs)
        #  (pos=pos, size=(192,81),*kwargs)
        self.mov_images = Atlas("animation\/movement\/animatlas.atlas")
        self.atk_images = Atlas("animation\/attack/atk.atlas")
        self.spe_images = Atlas("animation\/special\/specatlas.atlas")
        self.wall_images = Atlas("animation\/special\/wall_anim\/wall.atlas")
        self.animage = Atlas("animation\/effects\/arrow.atlas")
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
        current self.position.  Calculate angle, to later display an image based
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
        """
        helper method to pre-compute the vector and angle based on mouse pointer relation to sprite
        when mouse is clicked and held (and moved)
        :param touch: takes kivy touch as input
        :return: none
        """
        self.touching = True
        if not self.zipping:
            self.orientation(touch)
            self.origin = Vector(*self.new.center)  #self.new.center
            self.target = Vector(*self.touch_skew)
            self.tgetdir = self.target - self.origin
            self.movedir = self.tgetdir.normalize()
            #print str(self.bearing)
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
            elif self.coldir == 'r':
                if self.bearing <= 90 and self.bearing > 60:
                    self.texture = self.wall_images['special_lside_1']
                elif self.bearing <= 60 and self.bearing > 30:
                    self.texture = self.wall_images['special_lside_2']
                elif self.bearing <= 30 and self.bearing >0:
                    self.texture = self.wall_images['special_lside_3']
                elif self.bearing <= 0 and self.bearing > -30:
                    self.texture = self.wall_images['special_lside_4']
                elif self.bearing <= -30 and self.bearing > -60:
                    self.texture = self.wall_images['special_lside_5']
                elif self.bearing <= -60 and self.bearing > -90:
                    self.texture = self.wall_images['special_lside_5']  # need to add one more sprite for straight down
            elif self.coldir == 'l':
                if self.bearing >= 90 and self.bearing < 120:
                    self.texture = self.wall_images['special_rside_1']
                elif self.bearing >= 120 and self.bearing < 150 :
                    self.texture = self.wall_images['special_rside_2']
                elif self.bearing >= 150 and self.bearing < 180:
                    self.texture = self.wall_images['special_rside_3']
                elif self.bearing > -180 and self.bearing < -150:
                    self.texture = self.wall_images['special_rside_4']
                elif self.bearing >= -150 and self.bearing < -120:
                    self.texture = self.wall_images['special_rside_5']
                elif self.bearing >= -120 and self.bearing < -90:
                    self.texture = self.wall_images['special_rside_5']

    def on_touch_down(self, touch):
        """
        kivy on_touch_down handle, to fire prep_zip when mouse button is pressed
        :param touch: kivy touch input
        :return: none
        """
        self.prep_zip(touch)

    def on_touch_move(self, touch):
        """
        kivy on_touch_move handle, to fire prep_zip when mouse button is pressed and mouse is moved
        :param touch: kivy touch input
        :return: none
        """
        self.prep_zip(touch)

    def on_touch_up(self, touch):
        """
        kivy on_touch_up handle, to clear prep_zip values and cease action when mouse is released
        :param touch: kivy touch input
        :return: none
        """
        self.touching = False
        self.coldir = 'n'
        self.zip()

    def atk(self,dt):
        """
        method to trigger animation for attack with main weapon
        :param dt: delta-time (unused at present)
        :return: none
        """
        if self.prevdir == 'left':
            self.texture = self.atk_images['attack2_l']
        elif self.prevdir == 'right':
            self.texture = self.atk_images['attack2_r']

    def consider_collide(self,pushx,pushy):
        """
        method to recursively find the point on a straight line where a collision occurs with
        tile object containing collision properties (t,b,l,r : top, bottom, left, right)
        Updates an Rect instance value with the x,y location at the point of collision for
        later use.  Uses recursion instead of iteration because endpoint is not known prior to
        calling the method.

        :param pushx: normalised vector describing the direction to move, already pre-computed by the touch angle
        plus the touch location
        :param pushy: normalised vector describing the direction to move, already pre-computed by the touch angle
        plus the touch location
        :return: always returns None
        """
        self.plotrect = Rect((self.pos[0]+(self.width*.42))+pushx,(self.pos[1]+(self.height*.35))+pushy,
                             self.size[0]*.16, self.size[1]*.29)
        numnum = len(self.map.map.layers['blocker'].collide(self.plotrect, 'blocker'))
        if numnum >= 1:
            return None
        pushx += self.movedir.x
        pushy += self.movedir.y
        self.consider_collide(pushx,pushy)

    def zip(self):
        """
        method to move sprite image along movedir, previously computed by prep_zip.
        also checks for collision with objects
        :return: none
        """
        self.consider_collide(self.movedir.x,self.movedir.y)
        za_collide_point = Vector(self.plotrect.center)  # Zero Aligned collide point
        za_origin = Vector(self.new.center)  # Zero Aligned origin
        asa_collider = za_collide_point - za_origin  # Need the length of the true vector before normalisation
        sa_collider = asa_collider.normalize()  # Now normalise for use in iteration later
        #len_to_collide = int(round(asa_collider.length()))
        len_to_collide = 200  # Arbitrary number
        self.texture = self.animage['arrow']
        for index,coltick in enumerate(xrange(1, len_to_collide)):
            self.texture = self.animage['arrow']
            lastRect = Rect(self.pos[0]+(self.width*.42)+(sa_collider[0]*index), self.pos[1]+(self.height*.35)
                            +(sa_collider[1]*index),(self.size[0]*.16), self.size[1]*.29)
            #  In brief :
            #  Rect with bottomleft x value of sprite x position, plus 42% of the image width (image is small within
            #  transparent larger image) plus sa_collider[0] - x value of normalised vector direction to collide point
            #  multiplied by index to ensure the 'lastRect' is always 1 iteration behind the 'newRect'
            #  Next values supplied to Rect are for y location, similar logic
            #  Further values relate to the height/width of the rect instance which should envelope the inner
            #  sprite drawing.  For the purposes of this calculation that's not so important.
            newRect = Rect(self.pos[0]+(self.width*.42)+(sa_collider[0]*coltick), self.pos[1]+(self.height*.35)
                            +(sa_collider[1]*coltick),(self.size[0]*.16), self.size[1]*.29)
            #  Multiply by coltick for newRect to ensure it's always 1 step ahead of lastRect

            if self.move_or_collide(Rect1=newRect, Rect2=lastRect):
                break
        self.pos = newRect.bottomleft[0]-self.width*.42, newRect.bottomleft[1]-self.height*.35
        self.posref = self.pos

    def update(self, *ignore):
        """
        main update method, handles character movement logic and animation updates
        :param ignore: unused, reserved for future use
        :return: none
        """
        if (self.touching or self.sticking) or (self.zipping):
            if keys.get(Keyboard.keycodes['c']):
                self.resting = False
        else:
            self.dx, self.dy = 0, 0
            self.last = Rect(self.pos[0]+(self.width*.42),self.pos[1]+(self.height*.35), (self.size[0]*.16),
                             self.size[1]*.29)

            if keys.get(Keyboard.keycodes['left']) and not keys.get(Keyboard.keycodes['right']):
                self.dx -= 5 * params.scale
                self.moving_left = True
                self.moving_right = False
                self.texture = self.mov_images['walk_2_left'] if not self.jumping else self.mov_images['jump_l']
                self.prevdir = 'left'

            elif keys.get(Keyboard.keycodes['right']) and not keys.get(Keyboard.keycodes['left']):
                self.dx += 5 * params.scale
                self.moving_right = True
                self.moving_left = False
                self.texture = self.mov_images['walk_2_right'] if not self.jumping else self.mov_images['jump_r']
                self.prevdir = 'right'

            elif keys.get(Keyboard.keycodes['right']) and keys.get(Keyboard.keycodes['left']):
                self.moving_left, self.moving_right = False,False

            if not self.jumping and self.resting:
                if not keys.get(Keyboard.keycodes['right']) and not keys.get(Keyboard.keycodes['left']):
                    self.texture = self.mov_images['walk_1_left'] if self.prevdir == 'left' \
                        else self.mov_images['walk_1_right']

            if not self.jumping:
                self.dy -= 6 * params.scale

            if self.jumping:
                if not keys.get(Keyboard.keycodes['spacebar']):
                    self.jumping = False
                    self.movyval = 0

            if keys.get(Keyboard.keycodes['x']):
                Clock.schedule_once(self.atk)

            if keys.get(Keyboard.keycodes['spacebar']) and self.resting:
                self.jumping = True
                self.resting = False
                self.dy = 5 * params.scale
            elif keys.get(Keyboard.keycodes['spacebar']) and self.jumping:
                if self.movyval > 20:
                    self.jumping = False
                    self.movyval = 0
                else:
                    self.dy = 5 * params.scale
                    self.movyval += .5

            self.x += self.dx
            self.y += self.dy
            self.move_or_collide()

    def move_or_collide(self, Rect1=None, Rect2=None):
        """
        creates Rect around sprite image at center of transparent image.  Checks for collision, acts appropriately.
        :return: True if collision has occurred, False if not.  Takes optional arguments of rects to compare
        """
        blocked = False
        if Rect1 is not None:
            self.new = Rect1
        else:
            self.new = Rect(self.pos[0]+(self.width*.42),self.pos[1]+(self.height*.35), (self.size[0]*.16),
                            self.size[1]*.29)
        if Rect2 is not None:
            self.last = Rect2
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
            self.pos = self.new.bottomleft[0]-self.width*.42, self.new.bottomleft[1]-self.height*.35
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

