import random

import pygame
import sys

# Inicialização
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Pong')


# Classes
class Entity:
    def update(self, dt):
        pass
    
    def draw(self, screen):
        pass


class Physics:
    def update(self, world, dt):
        pass


class Observer:
    def update(self, subject):
        pass


# 0: nenhum; 1: defesa do jogador; 2: defesa do oponente; 3: gol jogador; 4: gol oponente; 5: parede
class AudioSystem(Observer):
    _instance = None

    def __init__(self):
        self.some_attribute = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def update(self, subject):
        if subject.state == 1 or subject.state == 2:
            pygame.mixer.music.load('Metal.mp3')
            pygame.mixer_music.play()
        if subject.state == 3 or subject.state == 4:
            pygame.mixer.music.load('Crash.mp3')
            pygame.mixer_music.play()
        if subject.state == 5:
            pygame.mixer.music.load('Wooden.mp3')
            pygame.mixer_music.play()


class AchievementSystem(Observer):
    p_score = 0
    o_score = 0
    pht_score = 0
    oht_score = 0

    _instance = None

    def __init__(self):
        self.some_attribute = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def update(self, subject):
        if subject.state == 3:
            print("gol do oponente")
            self.p_score += 1
            self.pht_score += 1
            self.oht_score = 0
        elif subject.state == 4:
            print("gol do jogador")
            self.o_score += 1
            self.pht_score = 0
            self.oht_score += 1
        if self.pht_score == 3:
            print("Hat Trick do Opponent")
            self.pht_score = 0
        if self.oht_score == 3:
            print("Hat Trick do Player")
            self.oht_score = 0


class BallPhysics(Physics):
    def update(self, world, dt):
        world.ball.body.x = world.ball.body.x + world.ball.speedX * dt
        world.ball.body.y = world.ball.body.y + world.ball.speedY * dt
        if world.ball.body.top <= 0:
            world.ball.speedY = abs(world.ball.speedY)
            world.ball.state = 5
            world.ball.notify()
        if world.ball.body.bottom >= world.screenHeight:
            world.ball.speedY = -abs(world.ball.speedY)
            world.ball.state = 5
            world.ball.notify()
        if world.ball.body.left > world.screenWidth:
            world.ball.body.center = (world.screenWidth / 2, world.screenHeight / 2)
            world.ball.speedX = random.choice((-0.5, 0.5))
            world.ball.state = 3
            world.ball.notify()
        if world.ball.body.right < 0:
            world.ball.body.center = (world.screenWidth / 2, world.screenHeight / 2)
            world.ball.speedX = random.choice((-0.5, 0.5))
            world.ball.state = 4
            world.ball.notify()



class Ball(Entity):
    state = 0
    observers = []

    def __init__(self, physics, screenWidth, screenHeight):
        self.physics = physics
        self.body = pygame.Rect(screenWidth / 2 - 15, screenHeight / 2 - 15, 30, 30)
        self.speedX = 0.4
        self.speedY = 0.4
        audio = AudioSystem.instance()
        self.attach(audio)
        achievement = AchievementSystem.instance()
        self.attach(achievement)
        

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, (200, 200, 200), self.body)
    

# 1: defesa do jogador;
class PlayerPhysics(Physics):
    def update(self, world, dt):
        if world.ball.body.bottom >= world.player.body.top and world.ball.body.top <= world.player.body.bottom and \
                world.ball.body.right >= world.player.body.left:
            delta = world.ball.body.centery - world.player.body.centery
            world.ball.speedY = delta * 0.01
            world.ball.speedX *= -1
            world.ball.state = 1
            world.ball.notify()

        (x, y) = pygame.mouse.get_pos()
        world.player.body.y = y - 70
    

class Player(Entity):
    state = 0
    observers = []

    def __init__(self, physics, screenWidth, screenHeight):
        self.physics = physics
        self.body = pygame.Rect(screenWidth - 20, screenHeight / 2 - 70, 10, 140)
        audio = AudioSystem.instance()
        self.attach(audio)
        achievement = AchievementSystem.instance()
        self.attach(achievement)

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.body)
    

class OpponentPhysics(Physics):
    def update(self, world, dt):
        if world.opponent.body.bottom < world.ball.body.y:
            world.opponent.body.bottom += world.opponent.speed
        if world.opponent.body.top > world.ball.body.y:
            world.opponent.body.top -= world.opponent.speed
        if world.ball.body.bottom >= world.opponent.body.top and world.ball.body.top <= world.opponent.body.bottom \
                and world.ball.body.left <= world.opponent.body.right:
            delta = world.ball.body.centery - world.opponent.body.centery
            world.ball.speedY = delta * 0.01
            world.ball.speedX *= -1
            world.ball.state = 2
            world.ball.notify()
    
    


class Opponent(Entity):
    state = 0
    observers = []

    def __init__(self, physics, screenWidth, screenHeight):
        self.physics = physics
        self.body = pygame.Rect(10, screenHeight / 2 - 70, 10, 140)
        self.speed = 8
        audio = AudioSystem.instance()
        self.attach(audio)
        achievement = AchievementSystem.instance()
        self.attach(achievement)

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.body)


class World:
    def __init__(self):
        self.screenWidth = 1280
        self.screenHeight = 960
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        ballPhysics = BallPhysics()
        self.ball = Ball(ballPhysics, self.screenWidth, self.screenHeight)
        playerPhysics = PlayerPhysics()
        self.player = Player(playerPhysics, self.screenWidth, self.screenHeight)
        opponentPhysics = OpponentPhysics()
        self.opponent = Opponent(opponentPhysics, self.screenWidth, self.screenHeight)
        self.entities = []
        self.entities.append(self.ball)
        self.entities.append(self.player)
        self.entities.append(self.opponent)
    
    def gameloop(self):
        previous = pygame.time.get_ticks()
        lag = 0
        FPS = 60
        MS_PER_UPDATE = 1000 / FPS
        while True:
            current = pygame.time.get_ticks()
            elapsed = current - previous
            previous = current
            lag += elapsed
            # Entradas
            self.inputs()
            # Atualização
            while lag >= MS_PER_UPDATE:
                # Atualização
                for e in self.entities:
                    e.physics.update(self, MS_PER_UPDATE)
                lag -= MS_PER_UPDATE
            
            # Desenho
            pygame.display.flip()
            self.screen.fill((0, 0, 0))

            for e in self.entities:
                e.draw(self.screen)

    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


# Objetos
world = World()
world.gameloop()
