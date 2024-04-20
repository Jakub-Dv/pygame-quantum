import random  # we use randomness for the position and speed of enemies
import time
from dataclasses import dataclass
from enum import Enum
import random

import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
FPS = 120


class TileType(Enum):
    Nothing=0
    Tower=-1
    Horizontal=1
    Vertical=2
    UpDownLeftRight=3
    UpDownLeft=4
    UpDownRight=5
    LeftRigthUp=6
    LeftRightDown=7
    RightUp = 8
    RightDown = 9
    LeftUp = 10,
    LeftDown = 11,
    Cross = 20

class DirectionType(Enum):
    No = 0
    Up = 1
    Down = 2
    Right = 3
    Left = 4

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
INIT_BOARD = [
    [TileType.RightDown, TileType.Horizontal, TileType.Horizontal, TileType.Horizontal, TileType.LeftDown],
    [TileType.Vertical, TileType.Nothing, TileType.Nothing, TileType.Nothing, TileType.Vertical],
    [TileType.Cross, TileType.Horizontal, TileType.Horizontal, TileType.Horizontal, TileType.Cross],
    [TileType.Vertical, TileType.Nothing, TileType.Nothing, TileType.Nothing, TileType.Vertical],
    [TileType.RightUp, TileType.Horizontal, TileType.Horizontal, TileType.Horizontal, TileType.LeftUp],
]

pygame.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()

CREATING_ENEMY_TIME_INTERVAL = 250  # later we can set it to different values if we wish
ADDENEMY = pygame.USEREVENT + 1  # each event is associated with an integer
pygame.time.set_timer(ADDENEMY, CREATING_ENEMY_TIME_INTERVAL)

class Player(pygame.sprite.Sprite):  # define this class before the infinite loop
    def __init__(self):
        super(Player, self).__init__()  # execute the __init__ method of the parent (Sprite object)
        self.surf = pygame.Surface((75, 25))  # create a surface <- our photonic ship
        self.surf.fill((255, 255, 255))  # color of our photonic ship
        self.rect = self.surf.get_rect()  # create a variable to access the surface as a rectangle

    def update(self, pressed_keys):  # we move the rectangular with (x,y)
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

TOWER_MAX_TICK = 20

@dataclass
class Tower:
    board: "Board"
    x: int
    y: int
    color: tuple[int, int, int]
    timer: int = 0
    range: int = 1

    tick: int = 0

    def kill_3_enemies(self) -> list["Enemy"]:
        enemies = []
        enemies += self.board.get_enemies_at(self.x + self.range, self.y + self.range)
        enemies += self.board.get_enemies_at(self.x - self.range, self.y + self.range)
        enemies += self.board.get_enemies_at(self.x + self.range, self.y - self.range)
        enemies += self.board.get_enemies_at(self.x - self.range, self.y - self.range)
        enemies += self.board.get_enemies_at(self.x, self.y + self.range)
        enemies += self.board.get_enemies_at(self.x, self.y - self.range)
        enemies += self.board.get_enemies_at(self.x + self.range, self.y)
        for _ in range(3):
            if len(enemies) == 0:
                break
            enemy = random.choice(enemies)
            enemy.kill()
            enemies.remove(enemy)

    def update(self):
        num_ticks = FPS * 2
        if self.tick % num_ticks == 0:
            self.tick += 1
            self.kill_3_enemies()
            self.tick = TOWER_MAX_TICK


BOARD_FIELDS = 5
class Board:
    def __init__(self, screen):
        self.w = BOARD_FIELDS
        self.h = BOARD_FIELDS
        self.w_diff = SCREEN_WIDTH / self.w
        self.h_diff = SCREEN_HEIGHT / self.h
        self.matrix_field = INIT_BOARD
        self.matrix_enemies = [[[] for _ in range(BOARD_FIELDS)] for _ in range(BOARD_FIELDS)]
        self.screen = screen

    def update(self):
        self.screen.fill(BLACK)

        for h in range(self.h):
            for w in range(self.w):
                if self.matrix_field[h][w] == TileType.Tower:
                    pygame.draw.rect(self.screen, GREEN, (w*self.w_diff, h*self.h_diff, self.w_diff, self.h_diff))
                if self.matrix_field[h][w] in [
                    TileType.Horizontal,
                    TileType.Vertical,
                    TileType.UpDownLeftRight,
                    TileType.UpDownLeft,
                    TileType.UpDownRight,
                    TileType.LeftRigthUp,
                    TileType.LeftRightDown,
                    TileType.RightUp,
                    TileType.RightDown,
                    TileType.LeftUp,
                    TileType.LeftDown,
                    TileType.Cross
                ]:
                    pygame.draw.rect(self.screen, BLUE, (w*self.w_diff, h*self.h_diff, self.w_diff, self.h_diff))
                for enemy in self.matrix_enemies[h][w]:
                    enemy.update()


        for h in range(self.h):
            pygame.draw.line(self.screen, WHITE, (0, (h+1)*self.h_diff), (SCREEN_WIDTH, (h+1)*self.h_diff))
        for w in range(self.w):
            pygame.draw.line(self.screen, WHITE, ((w+1)*self.w_diff, 0), ((w+1)*self.w_diff, SCREEN_HEIGHT))

    def add_enemy(self, enemy, x, y):
        self.matrix_enemies[x][y].append(enemy)

    def get_enemies_at(self, x, y):
        try:
            return self.matrix_enemies[x][y]
        except IndexError:
            return []


    def get_tile(self, x, y) -> TileType:
        return self.matrix_field[x][y]


    def mouse_clicked(self):
        """ When mouse click, the tower is placed on the field """
        state = pygame.mouse.get_pressed()
        if state[0]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_field_column = mouse_pos[0] // (SCREEN_WIDTH // BOARD_FIELDS)
            mouse_field_row = mouse_pos[1] // (SCREEN_HEIGHT // BOARD_FIELDS)
            print(mouse_field_row, mouse_field_column)
            if self.matrix_field[mouse_field_row][mouse_field_column] == TileType.Tower:
                self.matrix_field[mouse_field_row][mouse_field_column] = TileType.Nothing
            elif self.matrix_field[mouse_field_row][mouse_field_column] == TileType.Nothing:
                self.matrix_field[mouse_field_row][mouse_field_column] = TileType.Tower
            else:
                print("Cannot place tower here.")


ENEMY_SIZE = 20
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y,decoy,buddy,direction,board:Board):
        super(Enemy, self).__init__()
        self.board = board
        self.surf = pygame.Surface((30, 30))  # Enemies are smaller than our photonic ship
        self.surf.fill((255, 0, 0))  # the color of enemies - would you like to try different colors here?
        self.x = x
        self.y = y
        self.decoy = decoy
        if not self.decoy :
            self.buddy = buddy
        else:
            self.buddy = None
        self.direction = direction # 0-no 1-up 2-down 3-right 4-left
        #self.rect = self.surf.get_rect()
        #board.matrix_enemies[0][2] = self
        # we assign a random speed - how many pixel to move to the left in each frame
        # self.speed = random.randint(5, 20)

    def update(self):
        tile = self.board.get_tile(self.x,self.y)
        pygame.draw.rect(self.board.screen, RED, ((self.x * (self.board.w_diff - ENEMY_SIZE) / 2), (self.y * (self.board.h_diff - ENEMY_SIZE) / 2), ENEMY_SIZE, ENEMY_SIZE))
        
        if tile == TileType.Horizontal:
            if self.direction == DirectionType.Up:
                self.x += 1
                self.direction = DirectionType.Up
            elif self.direction == DirectionType.Down:
                self.x -= 1
                self.direction = DirectionType.Down
        elif tile == TileType.RightDown:
            if self.direction == DirectionType.Up:
                self.y += 1 
                self.direction = DirectionType.Right
        elif tile == TileType.RightUp:
            if self.direction == DirectionType.Down:
                self.y += 1 
                self.direction = DirectionType.Right
        elif tile == TileType.UpDownLeftRight:
            if self.direction == DirectionType.Right:
                rand_direction = random.randint(1,3)
                if rand_direction == DirectionType.Up:
                    self.direction = DirectionType.Up

                    pass
                
        pass
        #self.rect.move_ip(-self.speed, 0)
        #if self.rect.right < 0:  # remove any enemy moveing out side of the screen
        #    self.kill()  # a nice method inherited from Sprite()

    def kill(self):
        super().kill()
    
        for rows in self.board.matrix_enemies:
            for enemies in rows:
                enemies.remove(self)

def chooseDirection():
    pass

def handle_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == ADDENEMY:  # we catch the new event here and then we will create a new enemy
            new_enemy = Enemy()
            # enemies.add(new_enemy)  # add the new enemy
            # all_sprites.add(new_enemy)  # add the new enemy

class TowerDefense:
    def __init__(self, screen):
        self.running = True
        self.board = Board(screen)

    def new_enemy(self):
        enem = Enemy(2,0,False,None,DirectionType.No,self.board)
        self.board.matrix_enemies[0][2].append(enem)


    def run(self):
        self.new_enemy()
        while self.running:
            # screen.fill(BLACK)
            for event in pygame.event.get(): # check all events one by one since the last frame
                if event.type == pygame.QUIT: # if the window is closed
                    self.running = False
            self.board.update()
            self.board.mouse_clicked()
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_ESCAPE]:
                self.running = False  # let's exit the game if the player press "ESC"
            pygame.display.flip()  # Show everything on the screen
            clock.tick(FPS)  # frame rate

if __name__ == "__main__":
    TowerDefense(screen).run()
    # TowerDefense.run(screen)



# player = Player()  # define an instance -> our photonic ship
# enemies = pygame.sprite.Group()  # keep all enemies - the enemies will be added in the game infinite loop
# all_sprites = pygame.sprite.Group()  # keep all enemies and player(s)
# all_sprites.add(player)  # add the player here

            # handle_event()
            # enemies.update()  # a nice property of sprite groups

            # for entity in all_sprites:
            #     screen.blit(entity.surf, entity.rect)

            # screen.blit(player.surf, player.rect)  # player is "transferred as a block" on the screen
            # pressed_keys = pygame.key.get_pressed()
            # player.update(pressed_keys)

            # if pygame.sprite.spritecollideany(player, enemies):  # check if "player" is hit by any entity in the "enemies" group
            #     # if so: then remove the player and stop the infinite loop
            #     player.kill()
            #     running = False
            #     my_font = pygame.font.SysFont(name='Comic Sans MS', size=28)  # create a font object
            #     # we create a text surface to blit on the screen
            #     # message / anti-aliasing effect / text color / background color
            #     text_surface = my_font.render(text="Game Over :( ", False, color=(255, 255, 0), background=BLACK)
            #     screen.blit(
            #         source=text_surface,
            #         dest=(SCREEN_WIDTH / 8, SCREEN_HEIGHT / 2 - text_surface.get_height() / 2)
            #     )  # blit the text on the screen with the specified position
            #     there_is_message = True


            # if there_is_message:
            #     time.sleep(2)  # sleep for 2 seconds