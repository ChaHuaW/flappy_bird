import pygame
import random
import sys
from pygame.locals import *

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()

SCREEN_WIDTH = 432
SCREEN_HEIGHT = 468

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

clock = pygame.time.Clock()

assets = {
    'bg': pygame.image.load('images/bg.png'),
    'ground': pygame.image.load('images/ground.png'),
    'button': pygame.image.load('images/restart.png'),
}

sfx = {
    'flap': pygame.mixer.Sound('soundfx/Flap.wav'),
    'point': pygame.mixer.Sound('soundfx/point.wav'),
    'die': pygame.mixer.Sound('soundfx/die.wav')
}

sfx['flap'].set_volume(0.6)
sfx['point'].set_volume(0.4)
sfx['die'].set_volume(0.5)

bg = pygame.transform.scale(assets['bg'], (432, 384))
ground = pygame.transform.scale(assets['ground'], (450, 84))
button = pygame.transform.scale(assets['button'], (120, 42))

font = pygame.font.SysFont('Bauhaus 93', 30)
white = (255, 255, 255)

ground_scroll = 0
scroll_speed = 2
flying = False
game_over = False
pipe_gap = 75
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
previous_score = 0
high_score = 0
pass_pipe = False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 50
    flappy.rect.y = int(SCREEN_HEIGHT / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            self.bird = pygame.image.load(f"images/bird{num}.png")
            self.img = pygame.transform.scale(self.bird, (25.5, 18))
            self.images.append(self.img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.clicked = False
        self.vel = 0

    def update(self):
        if flying == True:
            self.vel += 0.3
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 380:
                self.rect.y += int(self.vel)

        if game_over == False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -6
                sfx['flap'].play()

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -3)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        pipe = pygame.image.load('images/pipe.png')
        self.image = pygame.transform.scale(pipe, (39, 280))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

    def draw(self):
        action = False
        mpos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mpos):
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(255)
        if self.rect.collidepoint(mpos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

bird_group = pygame.sprite.Group()
flappy = Bird(50, int(SCREEN_HEIGHT / 2))
bird_group.add(flappy)

showbutton = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100, button)

pipe_group = pygame.sprite.Group()

pygame.mixer.music.load('music/bgmusic.wav')
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)

run = True
while run:

    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    screen.blit(ground, (ground_scroll, 384))

    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                sfx['point'].play()
                pass_pipe = False

    draw_text(str(score), font, white, int(SCREEN_WIDTH / 2), 10)

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        if not game_over:
            game_over = True
            sfx['die'].play()

    if flappy.rect.bottom >= 380:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        time_now = pygame.time.get_ticks()
        pipe_height = random.randint(-50, 50)
        if time_now - last_pipe > pipe_frequency:
            btm_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    if game_over == True:
        if showbutton.draw() == True:
            game_over = False
            previous_score = score
            if score > high_score:
                high_score = score
            score = reset_game()
            reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    if flying == False and game_over == False:
        draw_text('*Click to Start*', pygame.font.SysFont('Bauhaus 93', 30), white, 110, 90 )

    draw_text('High Score:' + str(high_score), pygame.font.SysFont('Bauhaus 93', 20), white, 20, 20)
    pygame.display.update()
    clock.tick(60)

pygame.quit()

