import random  # we use randomness for the position and speed of enemies
import time
from dataclasses import dataclass
from enum import Enum
import random
from pprint import pprint

import pygame
from pygame import MOUSEBUTTONUP
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
    LeftUp = 10
    LeftDown = 11


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
    [TileType.UpDownLeftRight, TileType.Horizontal, TileType.Horizontal, TileType.Horizontal, TileType.UpDownLeftRight],
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
class Tower(pygame.sprite.Sprite):
    def __init__(self, board, x, y, color):
        self.board: Board = board
        self.x = x
        self.y = y
        self.color = color
        self.timer = 0
        self.range: int = 1
        self.surf = pygame.Surface((self.board.w_diff, self.board.h_diff))
        self.surf.fill(self.color)
        self.rect = self.surf.get_rect().move(self.x*self.board.w_diff, self.y*self.board.h_diff)


    def kill_3_enemies(self):
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
            print("killing", enemy)
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
        self.towers = []
        self.matrix_enemies = [[[] for _ in range(BOARD_FIELDS)] for _ in range(BOARD_FIELDS)]
        self.screen = screen

    def update(self):
        self.screen.fill(BLACK)
        for t in self.towers:
            self.screen.blit(t.surf, t.rect)

        # pprint(self.matrix_enemies)
        temp_enemies = [[[] for _ in range(BOARD_FIELDS)] for _ in range(BOARD_FIELDS)]
        for h in range(self.h):
            for w in range(self.w):
                for enemy in self.matrix_enemies[h][w]:
                    enemy.the_movement(temp_enemies)
        self.matrix_enemies = temp_enemies

        for h in range(self.h):
            for w in range(self.w):
                # if self.matrix_field[h][w] == TileType.Tower:
                #     pygame.draw.rect(self.screen, GREEN, (w*self.w_diff, h*self.h_diff, self.w_diff, self.h_diff))
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

    def get_enemies_at(self, col, row):
        try:
            return self.matrix_enemies[row][col]
        except IndexError:
            return []


    def get_tile(self, col, row) -> TileType:
        return self.matrix_field[row][col]

    def get_tower(self, col, row):
        for tower in self.towers:
            if tower.x == col and tower.y == row:
                return tower
        return None


    def mouse_clicked(self):
        """ When mouse click, the tower is placed on the field """
        state = pygame.mouse.get_pressed()
        if state[0]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_field_column = mouse_pos[0] // (SCREEN_WIDTH // BOARD_FIELDS)
            mouse_field_row = mouse_pos[1] // (SCREEN_HEIGHT // BOARD_FIELDS)

            tile_type = self.get_tile(mouse_field_column, mouse_field_row)
            if tile_type not in [TileType.Nothing, TileType.Tower]:  
                return

            if tile_type == TileType.Tower:
                tower = self.get_tower(mouse_field_column, mouse_field_row)
                if tower is None:
                    return
                self.towers.remove(tower)
                print("Tower removed")
            else:
                new_tower = Tower(board=self, x=mouse_field_column, y=mouse_field_row, color=(0, 255, 0))
                self.matrix_field[mouse_field_row][mouse_field_column] = TileType.Tower
                self.towers.append(new_tower)
                print("Tower placed")
            time.sleep(0.1)



ENEMY_SIZE = 20
ENEMY_TICK = 180
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y,decoy,buddy,direction,board:Board):
        super(Enemy, self).__init__()
        self.board = board
        self.surf = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))  # Enemies are smaller than our photonic ship
        self.surf.fill(RED)  # the color of enemies - would you like to try different colors here?
        self.x = x
        self.y = y
        self.w_padding = (self.board.w_diff - ENEMY_SIZE) / 2
        self.h_padding = (self.board.h_diff - ENEMY_SIZE) / 2
        self.rect = self.surf.get_rect().move(self.w_padding + self.x * self.board.w_diff, self.h_padding + self.y * self.board.h_diff)
        self.decoy = decoy
        self.tick = 0
        if not self.decoy :
            self.buddy = buddy
        else:
            self.buddy = None
        self.direction = direction # 0-no 1-up 2-down 3-right 4-left
        #self.rect = self.surf.get_rect()
        #board.matrix_enemies[0][2] = self
        # we assign a random speed - how many pixel to move to the left in each frame
        # self.speed = random.randint(5, 20)

    def get_rect(self):
        newx = self.w_padding + self.x * self.board.w_diff
        newy = self.h_padding + self.y * self.board.h_diff
        return self.surf.get_rect().move(newx, newy)

    def the_movement(self, temp_board):
        if self.tick == ENEMY_TICK:
            self.tick = 0
            # pprint(self.board.matrix_enemies)
            # print(self.x, self.y)
            self.board.get_enemies_at(self.x, self.y).remove(self)
            self.movement()
            # self.board.get_enemies_at(self.x, self.y).append(self)
        else:
            self.tick += 1
        temp_board[self.y][self.x].append(self)

    def moveDirection(self,direction):
        if direction == DirectionType.Up:
            self.y-=1
        if direction == DirectionType.Down:
            self.y+=1
        if direction == DirectionType.Right:
            self.x+=1

    def update(self):
        #tile = self.board.get_tile(self.x,self.y)
        # pygame.draw.rect(self.board.screen, RED, (w_padding + self.x * self.board.w_diff, h_padding + self.y * self.board.h_diff, ENEMY_SIZE, ENEMY_SIZE))

        # if self.tick == ENEMY_TICK:
        #     self.tick = 0
        #     self.board.get_enemies_at(self.x, self.y)
        #     self.movement()
        # else:
        #     self.tick += 1
        # print(self.tick)
        self.rect = self.get_rect()
        # print(self.rect)
        self.board.screen.blit(self.surf, self.rect)
        
    def movement(self):
        tile = self.board.get_tile(self.x,self.y)
        if tile == TileType.Vertical:
            if self.direction == DirectionType.Up:
                self.y -= 1
                self.direction = DirectionType.Up
            elif self.direction == DirectionType.Down:
                self.y += 1
                self.direction = DirectionType.Down
        if tile == TileType.Horizontal:
            self.direction = DirectionType.Right
            self.x += 1
        elif tile == TileType.RightDown:
            if self.direction == DirectionType.Up:
                self.x += 1 
                self.direction = DirectionType.Right
        elif tile == TileType.RightUp:
            if self.direction == DirectionType.Down:
                self.x += 1 
                self.direction = DirectionType.Right
        elif tile == TileType.UpDownLeftRight:
            if self.direction == DirectionType.Right:
                free_dir = [1, 2, 3]
                rand_direction = chooseDirection(free_dir)
                print(rand_direction)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                # self.x, self.y = moveDirection(self.x, self.y, rand_direction)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
                print(self.x,self.y)
            elif self.direction == DirectionType.Up:
                free_dir = [1, 3]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
            elif self.direction == DirectionType.Down:
                free_dir = [2, 3]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    # rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    # self.board.get_enemies_at(newx,newy).append(buddy)
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
        #UpDownLeft=4UpDownRight=5LeftRigthUp=6 LeftRightDown=7
        elif tile == TileType.UpDownLeft:
            if self.direction == DirectionType.Right:
                free_dir = [1, 2]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
            elif self.direction == DirectionType.Up:
                self.y -= 1
                self.direction = DirectionType.Up
            elif self.direction == DirectionType.Down:
                self.y += 1
                self.direction = DirectionType.Down
        elif tile == TileType.UpDownRight:
            if self.direction == DirectionType.Up:
                free_dir = [1, 3]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
            elif self.direction == DirectionType.Down:
                free_dir = [2, 3]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
        elif tile == TileType.LeftRigthUp:
            if self.direction == DirectionType.Right:
                free_dir = [1, 3]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
            elif self.direction == DirectionType.Down:
                self.x += 1 
                self.direction = DirectionType.Right
        elif tile == TileType.LeftRightDown:
            if self.direction == DirectionType.Right:
                free_dir = [2, 3]
                rand_direction = chooseDirection(free_dir)
                free_dir.remove(rand_direction)
                if not self.decoy:
                    rand_dummy_direction = chooseDirection(free_dir)
                    # newx,newy = moveDirection(self.x, self.y, rand_dummy_direction)
                    # buddy = Enemy(newx,newy, True, None, rand_dummy_direction,
                    #                 self.board)
                    buddy = Enemy(self.x, self.y, True, None, rand_dummy_direction, self.board)
                    buddy.moveDirection(rand_dummy_direction)
                    self.board.get_enemies_at(buddy.x,buddy.y).append(buddy)
                self.moveDirection(rand_direction)
                self.direction = rand_direction
                if self.buddy == None:
                    self.buddy = buddy
            elif self.direction == DirectionType.Up:
                self.x += 1 
                self.direction = DirectionType.Right

    def kill(self):
        super().kill()
    
        for rows in self.board.matrix_enemies:
            for enemies in rows:
                enemies.remove(self)

def chooseDirection(free_dir):
    chosen = random.randint(0,len(free_dir)-1)
    return free_dir[chosen]

def moveDirection(self,direction):
    if direction == DirectionType.Up:
        self.y-=1
    if direction == DirectionType.Down:
        self.y+=1
    if direction == DirectionType.Right:
        self.x+=1
    # return x,y

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
        enem = Enemy(0,2,False,None,DirectionType.Right,self.board)
        # self.board.matrix_enemies[2][0].append(enem)
        self.board.get_enemies_at(0, 2).append(enem)


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