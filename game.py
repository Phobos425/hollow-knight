import pygame, os, time
import pygame._sdl2 as sdl2
import random
import level

GAMETITLE = "Hollow Knight"


def loadImage(dir, filename, alpha=0):
    try:
        imgdir = os.path.join(dir, filename)
        print(imgdir)
        image = pygame.image.load(imgdir)
        if image == None:
            image = pygame.Surface(64,64)
            image.fill((255,0,0))
        if alpha == 1:
            image.set_colorkey(image.get_at((0,0)))
            image.convert_alpha()
        else:
            image.convert()
        return image
    except:
        print("couldn't load image" + filename)


def loadSound(dir, filename):
    try:
        sound = pygame.mixer.Sound(os.path.join(dir, filename))
        return sound
    except:
        print("couldn't load sound " + filename)


def changeVolumes(los, vol):
    try:
        for i in los:
            i.set_volume(vol)
    except:
        print("could not adjust volume")


def getImageAt(image, loc, size):
    try:
        a = pygame.Surface(size).convert_alpha()
        a.blit(image, (0, 0), pygame.Rect((loc), (size)))
        a.set_colorkey((0,0,0))
        return a
    except:
        print("couldnt retreive image at " + loc)


def loadSpriteSheet(image, tilesize):
    try:
        w = image.get_width() // tilesize[0]
        h = image.get_height() // tilesize[1]
        print(w)
        print(h)
        x, y = 0, 0
        im = []
        for i in range(h):
            im2 = []
            for n in range(w):
                im2.append(getImageAt(image, (x, y), tilesize))
                x += tilesize[0]
            im.append(im2)
            y += tilesize[1]
            x = 0
        return im

    except:
        print("error occured while trying to load sprite sheet")


def get_key(adict,val):
    for key, value in adict.items():
        if val == value:
            return key

    return None


def sub_pos(pos1, pos2):
    x = pos1[0] - pos2[0]
    y = pos1[1] - pos2[1]
    return x, y


def add_pos(pos1, pos2):
    x = pos1[0] + pos2[0]
    y = pos1[1] + pos2[1]
    return x, y


def setx(pos, num):
    x = num
    y = pos[1]
    return x, y


def sety(pos, num):
    x = pos[0]
    y = num
    return x, y


def randpos(pos1, pos2):
    x = random.randint(pos1[0], pos2[0])
    y = random.randint(pos1[1], pos2[1])
    return x, y


def flipimages(im):
    a = []
    for i in im:
        a.append(pygame.transform.flip(i, True, False).convert_alpha())
    return a

class State:
    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def render(self):
        pass

    def enter(self):
        self.game.curr_state = self

    def exit(self):
        self.game.prev_state = self


class SpashScreen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.countdown = 75
        self.spashtext1 = self.game.large_font.render("Hollow Knight", True, (255, 255, 255))
        self.spashtext1rect = self.spashtext1.get_rect(
            center=(self.game.screen_width / 2, self.game.screen_height / self.countdown + 100))
        self.sound = loadSound(os.path.join("data", "sounds"), "depressurize.wav")

    def update(self):
        if pygame.mixer.music.get_pos() > 0:
            pygame.mixer.music.unload()
        if self.countdown == 75:
            self.sound.play()
        self.countdown -= .4
        self.spashtext1rect = self.spashtext1.get_rect(
            center=(self.game.screen_width / 2, self.game.screen_height / self.countdown * self.game.delta_time + 100))
        if self.countdown < -10:
            self.exit()
            self.game.start.enter()

    def render(self):
        tempsurf = pygame.Surface((self.game.screen_width, self.game.screen_height))
        tempsurf.blit(self.spashtext1, self.spashtext1rect)
        tempsurf.set_colorkey((0, 0, 0))
        tempsurf.set_alpha(random.randint(1, 50))
        self.game.screen.blit(tempsurf, (0, 0))


class pause(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.pause_text = self.game.small_font.render("*pause*", False, (0, 0, 0))
        self.pause_text_rect = self.pause_text.get_rect(
            center=(self.game.screen_width / 2, self.game.screen_height / 2))

    def update(self):
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.game.prev_state.enter()
            self.exit()

    def render(self):
        self.game.prev_state.render()
        self.game.screen.blit(self.pause_text, self.pause_text_rect)


class Gameover(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.gameover_text = self.game.large_font.render("Game over", False, (255, 255, 255))
        self.gameover_text_rect = self.gameover_text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 3))

    def update(self):
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.exit()
            self.game.spash.enter()
            self.game.spash.countdown = 75
            self.game.platformer.lives = 3
            self.game.levelselection.levellock = [0,1,1,1,1,1,1,1,1,1,1,1]
            self.game.platformer.coins = 0
            self.game.levelselection.current_sel = 0
            self.game.platformer.health = 3
            self.exit()

    def render(self):
        self.game.prev_state.render()
        self.game.screen.blit(self.gameover_text, self.gameover_text_rect)


class StartScreen(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.background = loadImage(os.path.join("data","images"),"skygrad.png")
        self.grassimage = loadImage(os.path.join("data","images"),"grass.png",1)
        self.grassshadow = loadImage(os.path.join("data","images"),"grasshadow.png" ,1)
        self.starttext = self.game.small_font.render("press Start", True, (255,255,255))
        self.starttextrect = self.starttext.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 2 - 30))
        self.titletext = self.game.large_font.render("Hollow knight", True, (255, 255, 255))
        self.titletext2 = self.game.large_font.render("Hollow knight", True, (25, 25, 25))
        self.titletextrect = self.titletext.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 4))
        self.musicstart = False

    def update(self):
        if self.musicstart == False:
            pygame.mixer.music.load(os.path.join("data", "music", "moesstartscreen.ogg"))
            pygame.mixer.music.play(-1, 0, 10)
            self.musicstart = True
        if self.game.actions["start"]:
            self.exit()
            pygame.mixer.music.stop()
            self.musicstart = False
            self.game.levelselection.enter()

    def render(self):
        rcolor = random.randint(20, 60)
        tempsurf = pygame.Surface((self.game.screen_width,self.game.screen_height))
        tempsurf.blit(pygame.transform.scale(self.background, (800, 640)), (0, 0))
        tempsurf.blit(pygame.transform.scale(self.grassshadow, (800, 640)), (random.randint(0, 5), 50))
        tempsurf.blit(pygame.transform.scale(self.grassimage, (800, 640)), (0, 55))
        tempsurf.blit(pygame.transform.scale(pygame.transform.flip(self.grassshadow, True, False), (800, 640)), (random.randint(0, 5), 75))
        tempsurf.blit(pygame.transform.scale(pygame.transform.flip(self.grassimage, True, False), (800, 640)), (0, 80))
        tempsurf.blit(self.titletext2, add_pos(self.titletextrect.topleft, (random.randint(5, 10), (random.randint(5, 10)))))
        tempsurf.blit(self.titletext, self.titletextrect)
        self.starttext.set_alpha(random.randint(50, 150))
        tempsurf.blit(self.starttext, self.starttextrect)
        pygame.draw.rect(tempsurf, (rcolor, rcolor, rcolor), self.starttextrect.inflate(random.randint(3, 10),random.randint(3,10)),1)
        tempsurf.set_colorkey((0, 0, 0))
        self.game.screen.blit(tempsurf, (0, 0))


class LevelSelect(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.mapimage = loadImage(os.path.join("data", "images"), "mapselect.png")
        self.points = [(622, 622), (650, 506), (738, 379), (688, 234), (520, 365), (345, 365), (333, 250), (469, 232), (496, 102), (383, 134), (246, 109), (81, 135)]
        self.current_sel = 0
        self.pressedonce = False
        self.musicplaying = False
        self.movesound = loadSound(os.path.join("data", "sounds"), "selmove.wav")
        self.levellock = level.levellocks

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            pass
        if self.game.actions["up"] and self.current_sel < 11 and self.pressedonce == False:
            self.current_sel += 1
            self.pressedonce = True
            self.movesound.play()
        if self.game.actions["down"] and self.current_sel > 0 and self.pressedonce == False:
            self.current_sel -= 1
            self.pressedonce = True
            self.movesound.play()
        if not self.game.actions["up"] and not self.game.actions["down"] :
            self.pressedonce = False
        if not self.musicplaying:
            pygame.mixer.music.load(os.path.join("data", "music", "levelsel.ogg"))
            pygame.mixer.music.play(-1)
            self.musicplaying = True
        if self.game.actions["a"]:
            if self.levellock[self.current_sel] == 0 or self.levellock[self.current_sel] == 2:
                self.exit()
                self.musicplaying = False
                self.game.platformer.enter()
                if self.current_sel == 0:
                    self.game.platformer.levelparse(self.game.platformer.level1)
                if self.current_sel == 1:
                    self.game.platformer.levelparse(self.game.platformer.level2)
                if self.current_sel == 2:
                    self.game.platformer.levelparse(self.game.platformer.level3)
                if self.current_sel == 3:
                    self.game.platformer.levelparse(self.game.platformer.level4)
                if self.current_sel == 4:
                    self.game.platformer.levelparse(self.game.platformer.level5)
                if self.current_sel == 5:
                    self.game.platformer.levelparse(self.game.platformer.level6)
                if self.current_sel == 6:
                    self.game.platformer.levelparse(self.game.platformer.level7)
                if self.current_sel == 7:
                    self.game.platformer.levelparse(self.game.platformer.level8)
                if self.current_sel == 8:
                    self.game.platformer.levelparse(self.game.platformer.level9)
                if self.current_sel == 9:
                    self.game.platformer.levelparse(self.game.platformer.level10)
                if self.current_sel == 10:
                    self.game.platformer.levelparse(self.game.platformer.level11)
                if self.current_sel == 11:
                    self.game.platformer.levelparse(self.game.platformer.level12)

    def render(self):
        self.game.screen.blit(pygame.transform.scale(self.mapimage, (self.game.screen_width,self.game.screen_height)),(0,0))
        pygame.draw.lines(self.game.screen, (25, 25, 25), False, self.points, 6)
        pygame.draw.lines(self.game.screen, (255, 255, 255), False, self.points, 3)
        at = 0
        for i in self.points:
            pygame.draw.circle(self.game.screen, (25, 25, 25), i, 14)
            pygame.draw.circle(self.game.screen, (255, 255, 255), i, 10)
            if self.levellock[at] == 1:
                pygame.draw.circle(self.game.screen, (255, 25, 25), i, 8)
            if self.levellock[at] == 2:
                pygame.draw.circle(self.game.screen, (25, 255, 25), i, 8)
            at += 1
        pygame.draw.circle(self.game.screen, (2, 2, 255), self.points[self.current_sel], 9)


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data", "images"), "moe.png", 1), (8, 8))
        self.game = game
        self.frame = 0

        self.idle_right = [self.images[0][0], self.images[0][1]]
        self.walk_right = [self.images[0][2], self.images[0][3]]
        self.right_jump = self.images[1][0]
        self.falling_right = self.images[2][1]
        self.land_right = self.images[1][1]
        self.hit_right = self.images[2][2]

        self.idle_left = flipimages(self.idle_right)
        self.walk_left = flipimages(self.walk_right)
        self.left_jump = pygame.transform.flip(self.right_jump,True, False).convert_alpha()
        self.falling_left = pygame.transform.flip(self.falling_right,True, False).convert_alpha()
        self.land_left = pygame.transform.flip(self.land_right, True, False).convert_alpha()
        self.hit_left = pygame.transform.flip(self.hit_right, True, False).convert_alpha()

        self.image = self.idle_right[0]
        self.rect = self.image.get_rect().inflate(-2, 0)
        self.position = self.rect.topleft
        self.collision_group = pygame.sprite.Group()
        self.direction = 0
        self.actstate = {"walking": False, "idle": False, "jumping": False, "falling": False, "hit": False}
        self.currstate = "idle"
        self.jumptimer = 0
        self.groundcount = 3
        self.grounded = False
        self.hasjumped = False
        self.hitcooldown = 0

    def set_pos(self, pos):
        self.rect.topleft = pos
        self.jumptimer = 0
        self.actstate = {"walking": False, "idle": False, "jumping": False, "falling": False, "hit": False}
        self.grounded = False
        self.hasjumped = False
        self.hitcooldown = 0
        self.direction = 0

    def move(self,x,y, rfix = False):
        self.move_single_axis(round(x), 0, rfix)
        self.move_single_axis(0, round(y), rfix)

    def baddiehit(self):
        if self.hitcooldown <= 0:
            self.game.health -=1
            self.hitcooldown = 40
            self.game.hitsound.play()

    def move_single_axis(self,x,y,rfix = False):
        self.rect.move_ip(x, y)
        hit = pygame.sprite.spritecollide(self, self.collision_group, False)
        for block in hit:
            if rfix:
                block.onhit(self, -1)
            if x > 0:
                block.onhit(self, 0)
            if x < 0:
                block.onhit(self, 1)
            if y > 0:
                block.onhit(self, 2)
            if y < 0:
                block.onhit(self, 3)
    def update(self):
        if self.groundcount > -10:
            self.move(0, 1)
        if self.groundcount <= -10:
            self.move(0, 2)
        self.frame += 1
        if get_key(self.actstate, True) == None:
            self.actstate["idle"] = True
        if self.groundcount < 0:
            self.actstate["falling"] = True
            self.grounded = False
        if self.jumptimer > 20:
            self.move(0,-3)
            self.jumptimer -= 1
            self.actstate["jumping"] = True
        elif self.jumptimer > 5:
            self.move(0, -2)
            self.jumptimer -= 1
            self.actstate["jumping"] = True
        elif self.jumptimer > 0:
            self.move(0, -1)
            self.jumptimer -= 1
            self.actstate["jumping"] = True
        if not self.game.game.actions["a"] and self.jumptimer < 20:
            self.jumptimer = 0
        if self.direction == 0:
            if self.actstate["walking"]:
                self.image = self.walk_right[int(self.frame/8%2)]
            if self.actstate["idle"]:
                self.image = self.idle_right[int(self.frame / 8 % 2)]
            if self.actstate["falling"]:
                self.image = self.falling_right
            if self.groundcount == 3 and self.grounded == False:
                self.image = self.land_right
                self.grounded = True
            if self.actstate["jumping"]:
                self.image = self.right_jump
            if self.hitcooldown > 35:
                self.image = self.hit_right
                self.move(-1,-2)
                self.jumptimer = 0
        if self.direction == 1:
            if self.actstate["walking"]:
                self.image = self.walk_left[int(self.frame/8%2)]
            if self.actstate["idle"]:
                self.image = self.idle_left[int(self.frame / 8 % 2)]
            if self.actstate["falling"]:
                self.image = self.falling_left
            if self.groundcount == 3  and self.grounded == False:
                self.image = self.land_left
                self.grounded = True
            if self.actstate["jumping"]:
                self.image = self.left_jump
            if self.hitcooldown > 35:
                self.jumptimer = 0
                self.image = self.hit_left
                self.move(1,-2)
        self.groundcount -= 1
        if self.grounded and self.hasjumped and not self.game.game.actions["a"]:
            self.hasjumped = False
        self.hitcooldown -= 1


        for k in self.actstate.keys():
            self.actstate[k] = False


class hud():
    def __init__(self,game):
        self.hudbg = loadImage(os.path.join("data","images"),"hudbg.png",1)
        self.game = game
        self.cointext = self.game.game.tiny_font.render("Coins: " + str(self.game.coins), False, (190, 190, 190))
        self.livestext = self.game.game.tiny_font.render("lives: " + str(self.game.lives), False, (190, 190, 190))
        self.time = 0
        self.timetext = self.game.game.tiny_font.render("time: " + str(self.time), False, (190, 190, 190))
    def update(self):
        self.cointext = self.game.game.tiny_font.render("Coins: " + str(self.game.coins), False, (190, 190, 190))
        self.livestext = self.game.game.tiny_font.render("Lives: " + str(self.game.lives), False, (190, 190, 190))
        self.time += 1 * self.game.game.delta_time * .01
        self.timetext = self.game.game.tiny_font.render("time: " + str(int(self.time)), False, (190, 190, 190))
    def render(self,surf):

        surf.blit(self.hudbg,(0,0))
        surf.blit(self.cointext, (140, 15))
        surf.blit(self.livestext, (70, 15))
        surf.blit(self.timetext, (10, 15))
        hx = 20
        for i in range(self.game.health):
            pygame.draw.circle(surf,(250,0,0),(hx, 10), 3)
            hx += 11


class hud():
    def __init__(self, game):
        self.hudbg = loadImage(os.path.join("data","images"),"hudbg.png",1)
        self.game = game
        self.cointext = self.game.game.tiny_font.render("Coins: " + str(self.game.coins), False, (190, 190, 190))
        self.livestext = self.game.game.tiny_font.render("lives: " + str(self.game.lives), False, (190, 190, 190))
        self.time = 0
        self.timetext = self.game.game.tiny_font.render("time: " + str(self.time), False, (190, 190, 190))
    def update(self):
        self.cointext = self.game.game.tiny_font.render("Coins: " + str(self.game.coins), False, (190, 190, 190))
        self.livestext = self.game.game.tiny_font.render("Lives: " + str(self.game.lives), False, (190, 190, 190))
        self.time += 1 * self.game.game.delta_time * .01
        self.timetext = self.game.game.tiny_font.render("time: " + str(int(self.time)), False, (190, 190, 190))
    def render(self,surf):

        surf.blit(self.hudbg,(0,0))
        surf.blit(self.cointext, (140, 15))
        surf.blit(self.livestext, (70, 15))
        surf.blit(self.timetext, (10, 15))
        hx = 20
        for i in range(self.game.health):
            pygame.draw.circle(surf,(250,0,0),(hx, 10), 3)
            hx += 11


class Camera():
    def __init__(self, target, screensize, levelsize, speed=1):
        self.offset = (0, 0)
        self.realoffest = target.rect.center
        self.target = target
        self. speed = speed
        self.screensize = screensize
        self.levelsize = levelsize

    def update(self):
        self.realoffset = sub_pos((self.screensize[0] / 2, self.screensize[1] / 2), self.target.rect.center)
        if self.offset[0] < self.realoffset[0]:
            self.offset = add_pos(self.offset, (self.speed, 0))
        if self.offset[0] > self.realoffset[0]:
            self.offset = add_pos(self.offset, (-self.speed, 0))
        if self.offset[1] < self.realoffset[1]:
            self.offset = add_pos(self.offset, (0, self.speed))
        if self.offset[1] > self.realoffset[1]:
            self.offset = add_pos(self.offset, (0, -self.speed))
        if self.offset[0] > 0:
            self.offset = setx(self.offset, 0)
        if self.offset[0] < -self.levelsize[0] + self.screensize[0] + 8:
            self.offset = setx(self.offset, -self.levelsize[0] + self.screensize[0] + 8)
        if self.offset[1] > 28:
            self.offset = sety(self.offset, 28)
        if self.offset[1] < self.screensize[1] - self.levelsize[1]:
            self.offset = sety(self.offset, self.screensize[1] - self.levelsize[1])

        print("offset" + str(self.offset))
        print(self.screensize[1] - self.levelsize[1])

    def get_offset(self):
        return self.offset
    def draw_sprite(self,screen,sprite):
        if sprite.rect.colliderect(pygame.rect.Rect(sub_pos(screen.get_rect().topleft, self.offset),(screen.get_width(),screen.get_height()))):
            screen.blit(sprite.image, add_pos(sprite.rect.topleft,self.offset))


class block(pygame.sprite.Sprite):
    def __init__(self,image = None, game = None):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.game = game
        self.rect = None
    def update(self):
        pass
    def onhit(self,object,direction = 0):
        pass
    def render(self,screen = None):
        pass

class wall(block):
    def __init__(self, image, pos, game):
        block.__init__(self,image, game)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def onhit(self,object,direction = 0):
        if True:
            if direction == 0:
                object.rect.right = self.rect.left
            if direction == 1:
                object.rect.left = self.rect.right
            if direction == 2:
                object.rect.bottom = self.rect.top
                if isinstance(object, Player):
                    object.groundcount = 3
                    object.actstate["jumping"] = False
            if direction == 3:
                object.rect.top = self.rect.bottom
                object.jumptimer = 0

    def render(self,screen):
        screen.blit(self.image,self.rect)

class PushBlock(block):
    def __init__(self, image, pos, collisiongroup, game):
        block.__init__(self,image, game)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.collision_group = collisiongroup
    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))


    def move_single_axis(self,x,y):
        self.rect.move_ip(x, y)
        hit = pygame.sprite.spritecollide(self, self.collision_group, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self, 0)
                if x < 0:
                    block.onhit(self, 1)
                if y > 0:
                    block.onhit(self, 2)
                if y < 0:
                    block.onhit(self, 3)

    def onhit(self, object, direction=0):
        if isinstance(object, Player):
            if direction == -1:
                self.move(1, 0)
            if direction == 0:
                self.move(1,0)
                object.rect.right = self.rect.left
            if direction == 1:
                self.move(-1,0)
                object.rect.left = self.rect.right
            if direction == 2:
                self.move(0,1)
                object.rect.bottom = self.rect.top
                object.groundcount = 3
            if direction == 3:
                self.move(0,-1)
                object.rect.top = self.rect.bottom
        else:
             if direction == 0:
                 object.rect.right = self.rect.left
             if direction == 1:
                 object.rect.left = self.rect.right
             if direction == 2:
                 object.rect.bottom = self.rect.top
             if direction == 3:
                 object.rect.top = self.rect.bottom
    def update(self):
        self.move(0,1)
    def render(self,screen):
        screen.blit(self.image,self.rect)

class Ramp(block):
    def __init__(self,image,game,pos,dir = True):
        block.__init__(self,image,game)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.dir = dir

    def onhit(self, object, direction=0):
        if True:
            y = object.rect.left - self.rect.left
            if self.dir:
                if object.rect.bottom > self.rect.top - y:
                    if y > 0:
                        y = 0
                    object.rect.bottom = self.rect.top - y
                    object.move(0, 0, True)
                    object.groundcount = 3
            if not self.dir:
                if object.rect.bottom > self.rect.top + y and y > -1:
                    object.rect.bottom = self.rect.top + y
                    object.groundcount = 3


class decor(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.bottomleft = add_pos(pos, (-4, 8))

class bridge(block):
    def __init__(self, image, game, pos):
        block.__init__(self, image, game)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def onhit(self,object,direction = 0):
        if isinstance(object, Player):
            if direction == 2 and not self.game.game.actions["down"]:
               if object.rect.bottom < self.rect.top + 3:
                    object.rect.bottom = self.rect.top
                    object.groundcount = 3
        else:
             if direction == 2:
                 if object.rect.bottom < self.rect.top + 3:
                     object.rect.bottom = self.rect.top

class collectable(block):
    def __init__(self, image, game, type, pos):
        block.__init__(self, image, game)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.coin_sound = loadSound(os.path.join("data", "sounds"), "coin.wav")
        self.wobble = random.randint(0, 10) * .1
        self.wdir = True
        self.type = type

    def onhit(self,object,direction = 0):
        if isinstance(object, Player):
            if self.type == "coin":
                self.coin_sound.play()
                object.game.coins += 1
                self.kill()
            if self.type == "heart":
                self.game.healthsound.play()
                self.game.health += 1
                self.kill()
    def update(self):
        if self.wdir == True:
            self.wobble += .1
            self.rect.move_ip(0,-self.wobble)
            if self.wobble > 1:
                self.wobble = 0
                self.wdir = False
        else:
            self.wobble += .1
            self.rect.move_ip(0, self.wobble)
            if self.wobble > 1:
                self.wobble = 0
                self.wdir = True


class finish(block):
    def __init__(self, pos):
        block.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data", "images"), "finish.png", 1), (8, 8))
        self.image = self.images[0][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def onhit(self,object,direction = 0):
        if True:
            if direction == 0:
                object.rect.right = self.rect.left
            if direction == 1:
                object.rect.left = self.rect.right
            if direction == 2:
                object.rect.bottom = self.rect.top
                if isinstance(object, Player):
                    object.groundcount = 3
                    object.actstate["jumping"] = False
            if direction == 3:
                object.rect.top = self.rect.bottom
                if isinstance(object, Player):
                    self.image = self.images[0][1]
                    object.jumptimer = 0
                    object.game.win()


class Finalfinish(block):
    def __init__(self, pos):
        block.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data", "images"), "finish.png", 1), (8, 8))
        self.image = pygame.transform.scale(self.images[0][0],(32,32)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def onhit(self, object, direction=0):
        if True:
            if direction == 0:
                object.rect.right = self.rect.left
            if direction == 1:
                object.rect.left = self.rect.right
            if direction == 2:
                object.rect.bottom = self.rect.top
                if isinstance(object, Player):
                    object.groundcount = 3
                    object.actstate["jumping"] = False
            if direction == 3:
                object.rect.top = self.rect.bottom
                if isinstance(object, Player):
                    self.image = pygame.transform.scale(self.images[0][1], (32, 32)).convert_alpha()
                    object.jumptimer = 0
                    object.game.vic()


class Crab(pygame.sprite.Sprite):
    def __init__(self,pos,collisiongroup):
        pygame.sprite.Sprite.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data","images"),"crab.png",1),(8,8))[0]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy().inflate(-2, -2)
        self.collisiongroup = collisiongroup

        self.dir = True
        self.frame = 0

    def move(self, x, y, rfix=False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0, round(y))

    def move_single_axis(self, x, y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self and not isinstance(block, collectable):
                if x > 0:
                    block.onhit(self,0)
                    self.dir = False
                if x < 0:
                    block.onhit(self,1)
                    self.dir = True
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)

    def onhit(self,object,direction = 0):
        if isinstance(object,Player):
            if self.hitbox.colliderect(object.rect):
                object.baddiehit()
                self.dir = not self.dir


    def update(self):
        if self.dir:
            self.move(1,0)
        if not self.dir:
            self.move(-1,0)
        self.move(0,1)
        self.frame += 1
        self.image = self.images[int(self.frame / 8 % 2)]
        self.hitbox.center = self.rect.center
    def render(self,screen):
        screen.blit(self.image,self.rect)

class Dog(pygame.sprite.Sprite):
    def __init__(self,pos,collisiongroup):
        pygame.sprite.Sprite.__init__(self)
        self.rimages = loadSpriteSheet(loadImage(os.path.join("data","images"),"dog.png",1),(8,8))[0]
        self.limages = flipimages(self.rimages)
        self.image = self.rimages[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.collisiongroup = collisiongroup
        self.hitbox = self.rect.copy().inflate(-2, -2)

        self.dir = True
        self.frame = 0

    def move(self, x, y, rfix=False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0, round(y))

    def move_single_axis(self, x, y):
        self.rect.move_ip(x, y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                    self.dir = False
                if x < 0:
                    block.onhit(self,1)
                    self.dir = True
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self, 3)

    def onhit(self, object, direction=0):
        if isinstance(object, Player):
            if self.hitbox.colliderect(object.rect):
                object.baddiehit()
                self.dir = not self.dir

    def update(self):
        if self.dir:
            self.move(1,0)
        if not self.dir:
            self.move(-1,0)
        self.move(0,1)
        self.frame += 1
        if self.dir:
            self.image = self.rimages[int(self.frame / 8 % 3)]
        if not self.dir:
            self.image = self.limages[int(self.frame / 8 % 3)]
        self.hitbox.center = self.rect.center

    def render(self, screen):
        screen.blit(self.image, self.rect)


class Bee(pygame.sprite.Sprite):
    def __init__(self,pos,collisiongroup):
        pygame.sprite.Sprite.__init__(self)
        self.rimages = loadSpriteSheet(loadImage(os.path.join("data","images"),"Bee.png",1),(8,8))[0]
        self.limages = flipimages(self.rimages)
        self.image = self.rimages[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.collisiongroup = collisiongroup
        self.hitbox = self.rect.copy().inflate(-2, -2)

        self.dir = True
        self.frame = 0
        self.distance = 0
        self.wobble = random.randint(0, 10) * .1
        self.wdir = True

    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))


    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                    self.dir = False
                    self.distance = 40 - self.distance
                if x < 0:
                    block.onhit(self,1)
                    self.dir = True
                    self.distance = 40 - self.distance
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)

    def onhit(self,object, direction=0):
        if isinstance(object, Player):
            if self.hitbox.colliderect(object.rect):
                object.baddiehit()
                self.dir = not self.dir
                self.distance = 40 - self.distance


    def update(self):
        if self.dir:
            self.move(1,0)
        if not self.dir:
            self.move(-1, 0)
        self.frame += 1
        if self.dir:
            self.image = self.rimages[int(self.frame / 8 % 2)]
        if not self.dir:
            self.image = self.limages[int(self.frame / 8 % 2)]
        self.distance += 1
        if self.distance > 40:
            self.distance = 0
            self.dir = not self.dir
        if self.wdir:
            self.wobble += .1
            self.rect.move_ip(0,-self.wobble)
            if self.wobble > 1:
                self.wobble = 0
                self.wdir = False
        else:
            self.wobble += .1
            self.rect.move_ip(0, self.wobble)
            if self.wobble > 1:
                self.wobble = 0
                self.wdir = True
        self.hitbox.center = self.rect.center

    def render(self,screen):
        screen.blit(self.image,self.rect)

class Penguin(pygame.sprite.Sprite):
    def __init__(self,pos,collisiongroup):
        pygame.sprite.Sprite.__init__(self)
        self.rimages = loadSpriteSheet(loadImage(os.path.join("data","images"),"penguin.png",1),(8,8))[0]
        self.limages = flipimages(self.rimages)
        self.image = self.rimages[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.collisiongroup = collisiongroup
        self.hitbox = self.rect.copy().inflate(-2, -2)

        self.dir = True
        self.frame = 0

    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))


    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                    self.dir = False
                if x < 0:
                    block.onhit(self,1)
                    self.dir = True
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)
    def onhit(self,object,direction = 0):
        if isinstance(object, Player):
            if self.hitbox.colliderect(object.rect):
                object.baddiehit()
                self.dir = not self.dir


    def update(self):
        if self.dir:
            self.move(1,0)
        if not self.dir:
            self.move(-1,0)
        self.move(0,1)
        self.frame += 1
        if self.dir == True:
            self.image = self.rimages[int(self.frame / 8 % 3)]
        if self.dir == False:
            self.image = self.limages[int(self.frame / 8 % 3)]
        self.hitbox.center = self.rect.center
    def render(self,screen):
        screen.blit(self.image,self.rect)
class Spike(pygame.sprite.Sprite):
    def __init__(self,pos,collisiongroup,dir):
        pygame.sprite.Sprite.__init__(self)
        self.image = loadImage(os.path.join("data","images"),"spike.png",1)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.collisiongroup = collisiongroup
        self.hitbox = self.rect.copy().inflate(-3, -3)

        self.dir = dir

        if self.dir == 1:
            self.image = pygame.transform.flip(self.image,True,True).convert_alpha()
        if self.dir == 2:
            self.image = pygame.transform.rotate(self.image,90).convert_alpha()
        if self.dir == 3:
            self.image = pygame.transform.rotate(self.image, -90).convert_alpha()


    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))


    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                    self.dir = False
                if x < 0:
                    block.onhit(self,1)
                    self.dir = True
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)
    def onhit(self,object,direction = 0):
        if isinstance(object, Player):
            if self.hitbox.colliderect(object.rect):
                object.baddiehit()


    def update(self):
        pass

    def render(self,screen):
        screen.blit(self.image,self.rect)

class Snowman(pygame.sprite.Sprite):
    def __init__(self,pos,collison_group):
        pygame.sprite.Sprite.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data","images"),"snowman.png", 1),(8,8))
        self.left_walking = self.images[0]
        self.left_throwing = self.images[1]
        self.right_walking = flipimages(self.left_walking)
        self.right_throwing = flipimages(self.left_throwing)
        self.image = self.left_walking[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.dir = False
        self.throwing = False
        self.distance = 0
        self.frame = 0
        self.collisiongroup = collison_group
        self.halfmove = True

    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))

    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                    self.dir = False
                if x < 0:
                    block.onhit(self,1)
                    self.dir = True
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)
    def onhit(self,object,direction = 0):
        if isinstance(object,Player):
            if self.hitbox.colliderect(object.rect):
                object.baddiehit()
    def update(self):
        if self.throwing == False:
            if self.halfmove == True:
                if self.dir == True:
                    self.move(1,0)
                    self.image = self.right_walking[int(self.frame / 8 % 3)]
                if self.dir == False:
                    self.move(-1,0)
                    self.image = self.left_walking[int(self.frame / 8 % 3)]
            self.distance += 1
            if self.distance > 30:
                self.throwing = True
                self.distance = 0
            self.halfmove = not self.halfmove
        self.frame += 1
        self.hitbox.center = self.rect.center
        if self.throwing == True:
            a = int(self.frame / 20 % 4) - 1
            if self.dir == True:
                self.image = self.right_throwing[a]
            if self.dir == False:
                self.image = self.left_throwing[a]
            if a >= 2:
                self.collisiongroup.add(Snowball(self.dir,self.rect.center,self.collisiongroup))
                self.dir = not self.dir
                self.throwing = False
                self.halfmove = True
class Snowball(pygame.sprite.Sprite):
    def __init__(self,direction,startpos, colgro):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2,2))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.center = startpos
        self.dir = direction
        self.collisiongroup = colgro
        self.distance = 0
        self.slowmove = 0

    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))

    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self and self.distance > 5:
                if x > 0:
                    block.onhit(self,0)
                    self.kill()
                if x < 0:
                    block.onhit(self,1)
                    self.kill()
                if y > 0:
                    block.onhit(self,2)
                    self.kill()
                if y < 0:
                    block.onhit(self,3)
                    self.kill()
    def onhit(self,object,direction = 0):
        if isinstance(object,Player):
            object.baddiehit()
            self.kill()
    def update(self):
        if self.dir:
            self.move(1,0)
        if not self.dir:
            self.move(-1,0)
        self.distance += 1
        self.slowmove += .33
        if self.distance < 20:
            self.move(0,-self.slowmove)
        if self.distance > 30:
            self.move(0,self.slowmove)
        if self.slowmove > 1:
            self.slowmove = 0

class Bat(pygame.sprite.Sprite):
    def __init__(self,pos,collison_group):
        pygame.sprite.Sprite.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data","images"),"bat.png",1),(8,8))[0]
        self.rest_image = self.images[0]
        self.flying_image = [self.images[1],self.images[2]]
        self.image = self.rest_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy().inflate(-2,-2)
        self.state = "resting"
        self.rest_time = random.randint(1,100)
        self.fly_time = 0
        self.dir = True
        self.collisiongroup = collison_group
        self.frame = 0
    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))

    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self and (isinstance(block, wall) or isinstance(block, bridge)):
                if x > 0:
                    block.onhit(self,0)
                if x < 0:
                    block.onhit(self,1)
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)
                    self.state = "resting"
                    self.rest_time = random.randint(50,100)

    def onhit(self,object,direction = 0):
        if isinstance(object,Player):
            object.baddiehit()

    def update(self):
        self.frame += 1
        print(self.state)
        if self.state == "resting":
            self.image = self.rest_image
            self.rest_time -= 1
            if self.rest_time <= 0 :
                self.state = "flying"
                self.fly_time = 50
                self.dir = not self.dir
        if self.state == "flying":
            if self.dir == True:
                self.image = self.flying_image[int(self.frame / 8 % 2)]
                if self.fly_time > 25:
                    self.move(1,1)
                elif self.fly_time < 0:
                    self.move(1,-1)
                else:
                    self.move(1,0)
            if self.dir == False:
                self.image = self.flying_image[int(self.frame / 8 % 2)]
                if self.fly_time > 25:
                    self.move(-1,1)
                elif self.fly_time < 0:
                    self.move(-1,-1)
                else:
                    self.move(-1,0)
            self.fly_time -= 1

class Wolf(Dog):
    def __init__(self,pos,collisiongroup):
        Dog.__init__(self, pos, collisiongroup)
        self.rimages = loadSpriteSheet(loadImage(os.path.join("data","images"),"wolves.png",1),(8,8))[0]
        self.limages = flipimages(self.rimages)


class Jelly(pygame.sprite.Sprite):
    def __init__(self,pos,colgroup):
        pygame.sprite.Sprite.__init__(self)
        self.images = loadSpriteSheet(loadImage(os.path.join("data","images"),"jellyfish.png",1),(8,8))[0]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy().inflate(-2,-2)
        self.ydir = True
        self.xdir = True
        self.ytime = random.randint(1,40)
        self.xtime = random.randint(1,40)
        self.frame = 0
        self.collisiongroup = colgroup
        self.slowdown = 0
    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))

    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        hit = pygame.sprite.spritecollide(self, self.collisiongroup, False)
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                if x < 0:
                    block.onhit(self,1)
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)
            if isinstance(block, bridge):
                self.ydir = True
    def onhit(self,object,direction = 0):
        if isinstance(object,Player):
            object.baddiehit()
    def update(self):
        if self.slowdown == 3:
            self.xtime -= 1
            self.ytime -= 1
            self.frame += 1
            self.image = self.images[int(self.frame / 8 % 4)]
            if self.xdir == True:
                self.move(1,0)
            if self.xdir == False:
                self.move(-1,0)
            if self.ydir == True:
                self.move(0,1)
            if self.ydir == False:
                self.move(0,-1)
            if self.xtime < 0:
                self.xdir = random.choice([True,False])
                self.xtime = random.randint(1,40)
            if self.ytime < 0:
                self.ydir = random.choice([True,False])
                self.ytime = random.randint(1,40)
            self.slowdown = 0
        self.slowdown += 1


class Platformer(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.tempsurf = pygame.Surface((200, 160))
        self.player = Player(self)
        self.collidables = pygame.sprite.Group()
        self.decor = pygame.sprite.Group()

        self.level1 = level.level1
        self.level2 = level.level2
        self.level3 = level.level3
        self.level4 = level.level4
        self.level5 = level.level5
        self.level6 = level.level6
        self.level7 = level.level7
        self.level8 = level.level8
        self.level9 = level.level9
        self.level10 = level.level10
        self.level11 = level.level11
        self.level12 = level.level12
        self.currentlvl = 0
        self.backgroundimage = None
        self.coinimage = loadImage(os.path.join("data", "images"), "coin.png", 1)
        self.heartimage = loadImage(os.path.join("data", "images"), "heart.png", 1)
        self.bridgeimages = loadSpriteSheet(
            loadImage(os.path.join("data", "images"), "bridge.png", 1), (8, 8))
        self.treeimage = loadImage(os.path.join("data", "images"), "palmtree1.png", 1)
        self.player.collision_group = self.collidables
        self.camera = Camera(self.player, (self.tempsurf.get_width(), self.tempsurf.get_height()),
                                    (len(self.level1["map"][0] * 8), len(self.level1["map"] * 8)))

        self.coins = 0
        self.lives = 3
        self.health = 3

        self.jumpsound = loadSound(os.path.join("data", "sounds"), "jump.wav")
        self.oneupsound = loadSound(os.path.join("data", "sounds"), "1up.wav")
        self.jumpsound.set_volume(.5)
        self.hitsound = loadSound(os.path.join("data", "sounds"), "hit.wav")
        self.healthsound = loadSound(os.path.join("data", "sounds"), "health.wav")
        self.hud = hud(self)

    def action_update(self):
        if self.game.actions["right"] and self.player.hitcooldown < 10:
            self.player.move(1 * self.game.delta_time, 0)
            self.player.direction = 0
            self.player.actstate["walking"] = True
        if self.game.actions["left"] and self.player.hitcooldown < 10:
            self.player.move(-(1 * self.game.delta_time), 0)
            self.player.direction = 1
            self.player.actstate["walking"] = True
        if self.game.actions["up"]:
            pass
        if self.game.actions["down"]:
            pass
        if self.game.actions["a"] and not self.player.hasjumped:
            if self.player.jumptimer <= 0 and self.player.groundcount > 0:
                self.player.jumptimer = 25
                self.jumpsound.play()
                self.player.actstate["jumping"] = True
                self.player.hasjumped = True

        if self.game.actions["b"]:
            pass
        if self.game.actions["select"]:
            pass
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.exit()
            self.game.pause.enter()

    def win(self):
        self.exit()
        self.game.winscreen.enter()

    def vic(self):
        self.exit()
        pygame.mixer.music.unload()
        self.game.victory.enter()

    def die(self):
        self.exit()
        self.lives -= 1
        if self.lives <= 0:
            self.game.curr_state.exit()
            self.game.gameover.enter()
        else:
            self.game.deathscreen.enter()

    def update(self):
        self.action_update()
        self.player.update()
        self.collidables.update()
        self.camera.update()
        self.hud.update()
        if self.health <= 0:
            self.die()
        if self.coins > 100:
            self.lives += 1
            self.oneupsound.play()
            self.coins -= 100

    def render(self):
        self.tempsurf.fill((0, 0, 0))
        self.tempsurf.blit(self.backgroundimage, (0, 0))
        for i in self.decor:
            self.camera.draw_sprite(self.tempsurf, i)
        for i in self.collidables.sprites():
            self.camera.draw_sprite(self.tempsurf, i)

        self.camera.draw_sprite(self.tempsurf, self.player)
        self.hud.render(self.tempsurf)
        self.game.screen.blit(pygame.transform.scale(self.tempsurf, (800, 640)), (0, 0))

    def getsurroundings(self, letter, map, x, y):
        loh = [0, 0, 0, 0]
        try:
            if map[y // 8 + 1][x // 8] == letter:
                loh[0] = 1
        except:
            loh[0] = 0
        try:
            if map[y // 8 - 1][x // 8] == letter:
                loh[1] = 1
        except:
            loh[1] = 0
        try:
            if map[y // 8][x // 8 + 1] == letter:
                loh[2] = 1
        except:
            loh[2] = 0
        try:
            if map[y // 8][x // 8 - 1] == letter:
                loh[3] = 1
        except:
            loh[3] = 0
        return loh

    def lvlclear(self):
        for i in self.collidables:
            i.kill()
        for i in self.decor:
            i.kill()

    def levelparse(self, level):

        self.lvlclear()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(os.path.join("data", "music", level["music"]))
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(.5)
        map = level["map"]
        self.currentlvl = level["num"]
        self.backgroundimage = loadImage(os.path.join("data", "images"), level["background image"])
        groundimages = loadSpriteSheet(
            loadImage(os.path.join("data", "images"), level["ground image"], 1), (8, 8))
        miscblocks = loadSpriteSheet(loadImage(os.path.join("data", "images"), "miscblocks.png", 1),
                                               (8, 8))
        dimages = []
        for i in level["decor"]:
            dimages.append(loadImage(os.path.join("data", "images"), i, 1))
        self.camera = Camera(self.player, (self.tempsurf.get_width(), self.tempsurf.get_height()),
                                    (len(level["map"][0] * 8), len(level["map"] * 8)))
        x = 0
        y = 0
        for i in map:
            for k in i:
                if k == "g":
                    loh = self.getsurroundings("g", map, x, y)
                    lor = self.getsurroundings("r", map, x, y)
                    lol = self.getsurroundings("l", map, x, y)
                    if loh == [1, 0, 1, 0]:
                        self.collidables.add(wall(groundimages[0][0], (x, y), self))
                    elif loh == [1, 0, 1, 1]:
                        self.collidables.add(wall(groundimages[0][1], (x, y), self))
                    elif loh == [1, 0, 0, 1] and not lor == [0, 1, 0, 1] and not lol == [0, 1, 1, 0]:
                        self.collidables.add(wall(groundimages[0][2], (x, y), self))
                    elif loh == [1, 1, 1, 0]:
                        self.collidables.add(wall(groundimages[1][0], (x, y), self))
                    elif loh == [1, 1, 1, 1]:
                        self.collidables.add(wall(groundimages[1][1], (x, y), self))
                    elif loh == [1, 1, 0, 1]:
                        self.collidables.add(wall(groundimages[1][2], (x, y), self))
                    elif loh == [0, 1, 1, 0]:
                        self.collidables.add(wall(groundimages[2][0], (x, y), self))
                    elif loh == [0, 1, 1, 1]:
                        self.collidables.add(wall(groundimages[2][1], (x, y), self))
                    elif loh == [0, 1, 0, 1]:
                        self.collidables.add(wall(groundimages[2][2], (x, y), self))
                    elif loh == [0, 0, 1, 0]:
                        self.collidables.add(wall(groundimages[3][0], (x, y), self))
                    elif loh == [0, 0, 1, 1]:
                        self.collidables.add(wall(groundimages[3][1], (x, y), self))
                    elif loh == [0, 0, 0, 1]:
                        self.collidables.add(wall(groundimages[3][2], (x, y), self))
                    elif loh == [0, 0, 0, 0]:
                        self.collidables.add(wall(groundimages[3][3], (x, y), self))
                    elif loh == [1, 0, 0, 0]:
                        self.collidables.add(wall(groundimages[3][4], (x, y), self))
                    elif loh == [1, 1, 0, 0]:
                        self.collidables.add(wall(groundimages[3][5], (x, y), self))
                    if lor == [0, 1, 0, 0]:
                        self.collidables.add(wall(groundimages[2][4], (x, y), self))
                    elif lol == [0, 1, 0, 0]:
                        self.collidables.add(wall(groundimages[2][3], (x, y), self))
                    elif lor == [0, 0, 0, 1] and loh[1] == 0:
                        self.collidables.add(wall(groundimages[0][1], (x, y), self))
                    elif lol == [0, 0, 1, 0] and loh[1] == 0:
                        self.collidables.add(wall(groundimages[0][1], (x, y), self))
                    elif lor == [0, 1, 0, 1]:
                        self.collidables.add(wall(groundimages[2][4], (x, y), self))
                    elif lol == [0, 1, 1, 0]:
                        self.collidables.add(wall(groundimages[2][3], (x, y), self))
                if k == "r":
                    self.collidables.add(Ramp(groundimages[0][3], self, (x, y), True))
                if k == "l":
                    self.collidables.add(Ramp(groundimages[0][4], self, (x, y), False))
                if k == "t":
                    self.decor.add(decor(dimages[0], (x, y)))
                if k == "T":
                    self.decor.add(decor(dimages[1], (x, y)))
                if k == "a":
                    self.decor.add(decor(dimages[2], (x, y)))
                if k == "b":
                    log = self.getsurroundings("g", map, x, y)
                    if log[2]:
                        self.collidables.add(bridge(self.bridgeimages[0][2], self, (x, y)))
                    elif log[3]:
                        self.collidables.add(bridge(self.bridgeimages[0][0], self, (x, y)))
                    else:
                        self.collidables.add(bridge(self.bridgeimages[0][1], self, (x, y)))
                if k == "c":
                    self.collidables.add(collectable(self.coinimage, self, "coin", (x, y)))
                if k == "h":
                    self.collidables.add(collectable(self.heartimage, self, "heart", (x, y)))
                if k == "p":
                    self.collidables.add(PushBlock(miscblocks[0][4], (x, y), self.collidables, self))
                if k == "P":
                    self.player.set_pos((x, y))
                if k == "C":
                    self.collidables.add(Crab((x, y), self.collidables))
                if k == "f":
                    self.collidables.add(finish((x, y)))
                if k == "E":
                    self.collidables.add(Finalfinish((x, y)))
                if k == "D":
                    self.collidables.add(Dog((x, y), self.collidables))
                if k == "B":
                    self.collidables.add(Bee((x, y), self.collidables))
                if k == "M":
                    self.collidables.add(Bat((x, y), self.collidables))
                if k == "W":
                    self.collidables.add(Wolf((x, y), self.collidables))
                if k == "Q":
                    self.collidables.add(Penguin((x, y), self.collidables))
                if k == "J":
                    self.collidables.add(Jelly((x, y), self.collidables))
                if k == "8":
                    self.collidables.add(Snowman((x, y), self.collidables))
                if k == "S":
                    log = self.getsurroundings("g", map, x, y)
                    try:
                        if log[0]:
                            self.collidables.add(Spike((x, y), self.collidables, 0))
                        elif log[1]:
                            self.collidables.add(Spike((x, y), self.collidables, 1))
                        elif log[2]:
                            self.collidables.add(Spike((x, y), self.collidables, 2))
                        elif log[3]:
                            self.collidables.add(Spike((x, y), self.collidables, 3))
                    except:
                        pass
                x += 8
            y += 8
            x = 0


class Victory(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.credits = ["programming ,art, and music by Artyom Sukhomlin, T",
                        "sound effect from Juhani Junkala 512 sound effect on opengameart.org",
                        "special thanks to the pygame community",
                        "thanks for playing"]
        self.background = loadImage(os.path.join("data", "images"), "skygrad.png")
        self.grassimage = loadImage(os.path.join("data", "images"), "grass.png", 1)
        self.grassshadow = loadImage(os.path.join("data", "images"), "grasshadow.png", 1)
        self.credittext = self.game.small_font.render(self.credits[0], True, (255, 255, 255))
        self.credittextrect = self.credittext.get_rect(
            center=(self.game.screen_width / 2, self.game.screen_height / 2 - 30))
        self.titletext = self.game.large_font.render("Victory", True, (255, 255, 255))
        self.titletext2 = self.game.large_font.render("Victory", True, (25, 25, 25))
        self.titletextrect = self.titletext.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 4))
        self.musicstart = False
        self.credit_count = 0
        self.credit_timer = 100

    def update(self):
        if self.musicstart == False:
            pygame.mixer.music.load(os.path.join("data", "music", "moesstartscreen.ogg"))
            pygame.mixer.music.play(-1, 0, 10)
            self.musicstart = True
        if self.credit_timer <= 0:
            self.credit_timer = 100
            self.credit_count += 1
            if self.credit_count < 4:
                self.credittext = self.game.small_font.render(self.credits[self.credit_count], True, (255, 255, 255))
                self.credittextrect = self.credittext.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 2 - 30))
            else:
                self.exit()
                pygame.mixer.music.unload()
                self.musicstart = False
                self.game.spash.enter()
                self.game.spash.countdown = 75

        self.credit_timer -= 1


        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.credit_timer = 100
            self.credit_count += 1
            if self.credit_count < 4:
                self.credittext = self.game.small_font.render(self.credits[self.credit_count], True, (255, 255, 255))
                self.credittextrect = self.credittext.get_rect(
                    center=(self.game.screen_width / 2, self.game.screen_height / 2 - 30))
            else:
                self.exit()
                pygame.mixer.music.unload()
                self.musicstart = False
                self.game.spash.enter()
                self.game.spash.countdown = 75

    def render(self):
        rcolor = random.randint(20, 60)
        tempsurf = pygame.Surface((self.game.screen_width, self.game.screen_height))
        tempsurf.blit(pygame.transform.scale(self.background, (800, 640)), (0, 0))
        tempsurf.blit(pygame.transform.scale(self.grassshadow, (800, 640)), (random.randint(0, 5), 50))
        tempsurf.blit(pygame.transform.scale(self.grassimage, (800, 640)), (0, 55))
        tempsurf.blit(pygame.transform.scale(pygame.transform.flip(self.grassshadow, True, False), (800, 640)),
                      (random.randint(0, 5), 75))
        tempsurf.blit(pygame.transform.scale(pygame.transform.flip(self.grassimage, True, False), (800, 640)), (0, 80))
        tempsurf.blit(self.titletext2,
                      add_pos(self.titletextrect.topleft, (random.randint(5, 10), (random.randint(5, 10)))))
        tempsurf.blit(self.titletext, self.titletextrect)
        self.credittext.set_alpha(random.randint(50, 150))
        tempsurf.blit(self.credittext, self.credittextrect)
        pygame.draw.rect(tempsurf, (rcolor, rcolor, rcolor),
                         self.credittextrect.inflate(random.randint(3, 10), random.randint(3, 10)), 1)
        tempsurf.set_colorkey((0, 0, 0))
        self.game.screen.blit(tempsurf, (0, 0))


class win(State):
    def __init__(self,game):
        State.__init__(self, game)
        self.win_text = self.game.large_font.render("*level beat*",False,(0,0,0))
        self.win_text_rect = self.win_text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 2))
    def update(self):
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.game.levelselection.enter()
            if self.game.levelselection.levellock[self.game.prev_state.currentlvl] == 1:
                self.game.levelselection.levellock[self.game.prev_state.currentlvl] = 0
            self.game.levelselection.levellock[self.game.prev_state.currentlvl - 1] = 2
            self.exit()
    def render(self):
        self.game.prev_state.render()
        self.game.screen.blit(self.win_text,self.win_text_rect)
class death(State):
    def __init__(self,game):
        State.__init__(self, game)
        self.death_text = self.game.large_font.render("*you died*",False,(0,0,0))
        self.death_text_rect = self.death_text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 2))
    def update(self):
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.game.levelselection.enter()
            self.exit()
            self.game.platformer.health = 3
    def render(self):
        self.game.prev_state.render()
        self.game.screen.blit(self.death_text,self.death_text_rect)


class game():
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()

        pygame.display.set_caption(GAMETITLE)
        self.screen_width, self.screen_height = 800, 640
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height),pygame.RESIZABLE|pygame.SCALED)
        pygame.display.set_icon(loadImage(os.path.join("data", "images"), "icon.png"))

        self.font_path = os.path.join("data", "fonts", "Cave-Story.ttf")
        self.large_font = pygame.font.Font(self.font_path, 75)
        self.small_font = pygame.font.Font(self.font_path, 30)
        self.tiny_font = pygame.font.Font(self.font_path, 15)

        self.curr_state = "game"
        self.prev_state = "game"

        pygame.joystick.init()
        self.joystick = None
        try:
            self.joystick = pygame.joystick.Joystick(0)
        except:
            print("none")
        self.actions = {"a":False,"b":False,"up": False,"down":False,"left":False,"right":False,"start":False, "select":False}
        self.action_mapping = { "a":pygame.K_a,"b":pygame.K_s,"up":pygame.K_UP, "down":pygame.K_DOWN, "left":pygame.K_LEFT,"right":pygame.K_RIGHT,"start":pygame.K_RETURN,"select":pygame.K_RIGHTBRACKET}

        self.clock = pygame.time.Clock()
        self.delta_time = 0
        self.target_fps = 60

        self.running = False

        # game states
        self.gameover = Gameover(self)
        self.deathscreen = death(self)
        self.winscreen = win(self)
        self.pause = pause(self)
        self.spash = SpashScreen(self)
        self.start = StartScreen(self)
        self.levelselection = LevelSelect(self)
        self.platformer = Platformer(self)
        self.pausecooldown = 20
        self.victory = Victory(self)

    def update_actions(self):
        keys = pygame.key.get_pressed()
        for k in self.actions:
            self.actions[k] = False
        for k in self.action_mapping.values():
            if keys[k]:
                self.actions[get_key(self.action_mapping,k)] = True
        self.pausecooldown -= 1
        if keys[pygame.K_ESCAPE]:
            self.running = False
            pygame.quit()


    def update(self):
        self.delta_time = (self.clock.tick(self.target_fps) * .001 * self.target_fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            if event.type == pygame.JOYBUTTONDOWN:
                print(event)

        self.update_actions()
        try:
            if self.joystick.get_button(1):
                self.actions["a"] = True
            if self.joystick.get_button(9):
                self.actions["start"] = True
            if self.joystick.get_axis(1) > .5:
                self.actions["right"] = True
            if self.joystick.get_axis(1) < -.5:
                self.actions["left"] = True
            if self.joystick.get_axis(4) > .5:
                self.actions["down"] = True
            if self.joystick.get_axis(4) < -.5:
                self.actions["up"] = True

        except:
            pass
        self.curr_state.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.curr_state.render()
        pygame.display.update()

    def gameloop(self):
        self.running = True
        self.spash.enter()
        while self.running:
            self.update()
            self.render()
