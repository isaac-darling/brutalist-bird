#May 2021
#Flappy Bird game with lazy artwork, intended as a test bed for neat ai

import neat, sys
import pygame as pg
from random import randint

class Bird(pg.sprite.Sprite):
    def __init__(self, w, h, size):
        super().__init__()
        self.size = size
        self.score = 0
        self.vel = 0
        self.image = pg.Surface((self.size, self.size))
        self.image.fill((255, 255, 255))
        self.rect = pg.Rect(int(w/2*0.9), h//2-self.size//2, self.size, self.size)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def jump(self):
        self.rect.y-=60
        self.vel = 0

class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, pipes):
        super().__init__()
        self.width = w
        self.height = h
        self.image = pg.Surface((self.width, self.height))
        self.image.fill((0, 0, 0))
        self.rect = pg.Rect(x, y, self.width, self.height)
        pipes.add(self)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

def draw_screen(screen, bg, bgx, bgx2, pipes, birds, score):
    screen.blit(bg, (bgx, 0))
    screen.blit(bg, (bgx2, 0))

    for pipe in pipes.sprites():
        pipe.draw(screen)
    for bird in birds.sprites():
        bird.draw(screen)

    score_surface = pg.font.SysFont("Consolas", 30).render(str(int(score)), True, (255, 255, 255))

    screen.blit(score_surface, (10, 10))
    pg.display.flip()

def new_pipe(w, fh, difficulty, birds, pipes):
    Pipe(w+100, 0, 60, h:=randint(20, int(fh-20-difficulty*birds.sprites()[0].size)), pipes)
    Pipe(w+100, y:=int(h+difficulty*birds.sprites()[0].size), 60, fh-y, pipes)

def manual_loop():
    pg.init()
    pg.display.set_caption("Bird Game Screen")

    WIDTH, HEIGHT = 500, 650
    FLOOR_HEIGHT = HEIGHT-HEIGHT//10
    SCREEN = pg.display.set_mode((WIDTH, HEIGHT))

    BG = pg.Surface((WIDTH, HEIGHT))
    BG.fill((100, 100, 100))
    bgx = 0
    bgx2 = WIDTH

    pipes = pg.sprite.Group()
    Pipe(0, FLOOR_HEIGHT, WIDTH, int(HEIGHT/10), pipes)

    birds = pg.sprite.Group()
    birds.add(Bird(WIDTH, HEIGHT, 40))

    highscore = 0
    END_LOOP = False
    SPEED = 1
    ACCEL = 0.1
    clock = pg.time.Clock()

    new_pipe(WIDTH, FLOOR_HEIGHT, 3.45, birds, pipes)
    pg.time.set_timer(pg.USEREVENT, 3750)

    while not END_LOOP:
        draw_screen(SCREEN, BG, bgx, bgx2, pipes, birds, highscore)

        if len(birds.sprites()) == 0:
            END_LOOP = True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                END_LOOP = True

            if event.type == pg.USEREVENT:
                new_pipe(WIDTH, FLOOR_HEIGHT, 3.45, birds, pipes)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                    for bird in birds.sprites():
                        bird.jump()
                    break

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for bird in birds.sprites():
                    bird.jump()
                break

        bgx-=SPEED
        bgx2-=SPEED

        if bgx + WIDTH < 0:
            bgx = WIDTH
        if bgx2 + WIDTH < 0:
            bgx2 = WIDTH

        for bird in birds.sprites():
            bird.vel+=ACCEL
            bird.rect.y+=int(bird.vel)

        for pipe in pipes.sprites()[1:]:
            if pipe.rect.x + pipe.width < 0:
                pipe.kill()

            for bird in birds.sprites():
                if bird.rect.x + bird.size == pipe.rect.x and bird.rect.y < 0:
                        bird.kill()

                elif pipe.rect.x == bird.rect.x:
                    bird.score+=0.5
                    if bird.score > highscore:
                        highscore = bird.score

            pipe.rect.x-=SPEED

        for bird in (collisions:=pg.sprite.groupcollide(birds, pipes, False, False)):
            if collisions[bird]:
                bird.kill()

        clock.tick(60)
    pg.quit()

def mainloop(genomes, config):
    pg.init()
    pg.display.set_caption("Bird Game Screen")

    WIDTH, HEIGHT = 500, 650
    FLOOR_HEIGHT = HEIGHT-HEIGHT//10
    SCREEN = pg.display.set_mode((WIDTH, HEIGHT))

    BG = pg.Surface((WIDTH, HEIGHT))
    BG.fill((100, 100, 100))
    bgx = 0
    bgx2 = WIDTH

    pipes = pg.sprite.Group()
    Pipe(0, FLOOR_HEIGHT, WIDTH, int(HEIGHT/10), pipes)

    birds = pg.sprite.Group()

    highscore = 0
    END_LOOP = False
    SPEED = 1
    ACCEL = 0.1
    clock = pg.time.Clock()

    nn_dict = {}

    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        bird = Bird(WIDTH, HEIGHT, 40)
        nn_dict[bird] = (net, genome)
        birds.add(bird)

    new_pipe(WIDTH, FLOOR_HEIGHT, 3.45, birds, pipes)
    pg.time.set_timer(pg.USEREVENT, 3750)

    while not END_LOOP:
        draw_screen(SCREEN, BG, bgx, bgx2, pipes, birds, highscore)

        if len(birds.sprites()) == 0:
            END_LOOP = True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.USEREVENT:
                new_pipe(WIDTH, FLOOR_HEIGHT, 3.45, birds, pipes)

        bgx-=SPEED
        bgx2-=SPEED

        if bgx + WIDTH < 0:
            bgx = WIDTH
        if bgx2 + WIDTH < 0:
            bgx2 = WIDTH

        for bird in birds.sprites():
            nn_dict[bird][1].fitness+=0.1
            bird.vel+=ACCEL
            bird.rect.y+=int(bird.vel)

            pipe_index = pipes.sprites().index([pipe for pipe in pipes.sprites()[1:] if (pipe.rect.x+pipe.width) >= bird.rect.x][0])
            top_pipe, bot_pipe = pipes.sprites()[pipe_index], pipes.sprites()[pipe_index+1]
            top_y, bot_y = top_pipe.height, bot_pipe.rect.y

            if nn_dict[bird][0].activate((bird.vel, abs(bird.rect.x-top_pipe.rect.x), bird.rect.y, abs(bird.rect.y-top_y), abs(bird.rect.y-bot_y)))[0] > 0.5:
                bird.jump()

        for pipe in pipes.sprites()[1:]:
            if pipe.rect.x + pipe.width < 0:
                pipe.kill()

            for bird in birds.sprites():
                if bird.rect.x + bird.size == pipe.rect.x and bird.rect.y < 0:
                    nn_dict.pop(bird)
                    bird.kill()

                elif pipe.rect.x == bird.rect.x:
                    nn_dict[bird][1].fitness+=0.5

                    bird.score+=0.5
                    if bird.score > highscore:
                        highscore = bird.score

            pipe.rect.x-=SPEED

        for bird in (collisions:=pg.sprite.groupcollide(birds, pipes, False, False)):
            if collisions[bird]:
                nn_dict.pop(bird)
                bird.kill()

        clock.tick(60)

if __name__=="__main__":
    manual_loop()
