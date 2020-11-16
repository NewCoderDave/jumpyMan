# Import the pygame module
import pygame
import random
import time

clock = pygame.time.Clock()
# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Initialize pygame
pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 200

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# Define a Player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(
                self.surf.get_width()*2,
                SCREEN_HEIGHT - self.surf.get_height()/2,
            )
        )
        self.jump = False
        self.jump_speed = -12
        self.score = 0

    def add_to_score(self):
        self.score += 1
        return self.score

    def update(self, pressed_keys):
        if pressed_keys == K_UP:
            self.jump = True
        if self.jump:
            self.rect.move_ip(0, self.jump_speed)
            self.jump_speed += 1
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.jump = False
                self.jump_speed = -12
                self.rect.move(0, SCREEN_HEIGHT)

    def get_leading_edge(self):
        return self.rect.right

# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH + 20,
                SCREEN_HEIGHT - self.surf.get_height()/2,
            )
        )
        self.speed = 5

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)

    def getedge(self):
        if self.rect.left > 49:
            return self.rect.left
        else:
            return SCREEN_WIDTH

class ScoreBlock(pygame.sprite.Sprite):
    def __init__(self):
        super(ScoreBlock, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(
                -self.surf.get_width(),
                SCREEN_HEIGHT - self.surf.get_height()/2,
            )
        )

# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 1000, 0)

# Instantiate player. Right now, this is just a rectangle.
player = Player()

#create groups to hold sprites
enemies = pygame.sprite.Group()
scoring_sprite = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

#Create the Scoring section
score_block = ScoreBlock()
scoring_sprite.add(score_block)
all_sprites.add(score_block)

# Variable to keep the main loop running
running = True
jump_self = False
new_enemy = []
# Main loop
while running and jump_self:

    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False
        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False
        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            #new_enemy = Enemy()
            new_enemy.append(Enemy())
            enemies.add(new_enemy[len(new_enemy)-1])
            all_sprites.add(new_enemy[len(new_enemy)-1])
            #enemies.add(new_enemy)
            #all_sprites.add(new_enemy)
            pygame.time.set_timer(ADDENEMY, random.randint(700,1200), 0)

    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()

    # Update the player sprite based on user keypresses
    player.update(pressed_keys)

    # Update enemy position
    enemies.update()
#     for enemies in new_enemy:
#         enemies.update()

    # Fill the screen
    screen.fill((0, 0, 0))

    # for enemies in new_enemy:
    #     screen.blit(enemies.surf, enemies.rect)
    #     hit = pygame.sprite.spritecollide(enemies, all_sprites, 0)
    #
    #     if hit != None:
    #          print(hit)

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Check if any enemies have collided with the player
    if pygame.sprite.spritecollideany(player, enemies):
        #If so, then remove the player and stop the loop
        # player.kill()
        # running = False
        pass

    # If enemy collided with the score block add to score and kill the enemy
    if pygame.sprite.spritecollide(score_block, enemies, True) != []:
        print("killed")
        print(player.add_to_score())

    #update screen
    pygame.display.flip()
    clock.tick(40)
