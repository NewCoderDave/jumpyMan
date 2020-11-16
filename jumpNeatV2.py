# Import the pygame module
import pygame
import random
import time
import jump
import sys
import os
import neat
import visualize
import pickle
import math

gen = 0
jump.jump_self = False
clock = pygame.time.Clock()
# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 200

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

#
# Instantiate player. Right now, this is just a rectangle.
# player = jump.Player()
#
#create groups to hold sprites
# enemies = pygame.sprite.Group()
# scoring_sprite = pygame.sprite.Group()
# all_sprites = pygame.sprite.Group()
# all_sprites.add(player)
#
# #Create the Scoring section
# score_block = jump.ScoreBlock()
# scoring_sprite.add(score_block)
# all_sprites.add(score_block)
#
# # create the list of enemies
# new_enemy = []
# # Variable to keep the main loop running

# Main loop
pygame.init()

# # Create the screen object
# # The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#
# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 1000, 0)

# Create a custom event for increaing speed
SPEEDUP = pygame.USEREVENT + 2
pygame.time.set_timer(SPEEDUP, 5000)

# create groups to hold sprites
enemies = pygame.sprite.Group()
scoring_sprite = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
player_sprites = pygame.sprite.Group()
#    all_sprites.add(player)

# Create the Scoring section
score_block = jump.ScoreBlock()
#scoring_sprite.add(score_block)
all_sprites.add(score_block)
def eval_genomes(genomes, config):
    # create the list of enemies
    new_enemy = []

    #set the gamespeed
    GAME_SPEED = 1.0

    global gen
    print_score = 0
    #Create List for genomes and players and nueral networks
    nets = []
    players = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(jump.Player())
        ge.append(genome)

    for x, player in enumerate(players):
        all_sprites.add(player)
        player_sprites.add(player)

    running = True
    while running:
        # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    running = False
                    pygame.quit()
                    quit()
                    break
            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                running = False
                pygame.quit()
                quit()
                break
            # Add a new enemy?
            elif event.type == ADDENEMY:
                # Create the new enemy and add it to sprite groups
                # new_enemy = Enemy()
                new_enemy.append(jump.Enemy())
                enemies.add(new_enemy[len(new_enemy) - 1])
                all_sprites.add(new_enemy[len(new_enemy) - 1])
                # enemies.add(new_enemy)
                # all_sprites.add(new_enemy)
                pygame.time.set_timer(ADDENEMY, random.randint(int(3000 / GAME_SPEED), int(4500 / GAME_SPEED)), 0)
            #increase speed
            elif event.type == SPEEDUP:
                GAME_SPEED += 0.5


        # Update enemy position
        enemies.update()

        for x, player in enumerate(players):
            #calculate the x distance to the closest enemy
            closeness = [SCREEN_WIDTH]
            min_closeness = []
            for y in range(len(new_enemy)):
                if new_enemy[y].alive():
                    closeness.append(new_enemy[y].getedge())
            min_closeness.append(min(closeness)/SCREEN_HEIGHT)
            # Get the set of keys pressed and check for user input
            output = nets[players.index(player)].activate( (min_closeness) )
            if output[0] > 0.75:
                pressed_keys = K_UP
            else:
                pressed_keys = None
            player.update(pressed_keys)
            #pressed_keys = pygame.key.get_pressed()

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
            #
            # Check if any enemies have collided with the player
        for x, player in enumerate(players):
            if pygame.sprite.spritecollideany(player, enemies):
                # If so, then remove the player and stop the loop
                player.kill()
            # running = False
            #
        # If enemy collided with the score block add to score and kill the enemy
        if pygame.sprite.spritecollide(score_block, enemies, True) != []:
            for x, player in enumerate(players):
                if player.alive():
                    print_score = player.add_to_score()

        #Exit the loop is there isnt at least 1 alive
        any_alive = False
        for x, player in enumerate(players):
            if player.alive():
                any_alive = True

        running = any_alive

        # update screen
        score_label = STAT_FONT.render("Score: " + str(print_score), 1, (255,255,255))
        print_speed = STAT_FONT.render("Speed: " + str(GAME_SPEED), 1, (255,255,255))
        screen.blit(score_label, (SCREEN_WIDTH - score_label.get_width()-15, 10))
        screen.blit(print_speed, (SCREEN_WIDTH - score_label.get_width()- 50, 40))
        pygame.display.flip()
        clock.tick(40)
    #clean Groups
    pygame.sprite.Group.empty(enemies)
    pygame.sprite.Group.empty(all_sprites)
   # all_sprites.add(score_block)

    for x, player in enumerate(players):
        ge[x].fitness = player.score
    print(GAME_SPEED)

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 100 generations.
    winner = p.run(eval_genomes)
################################################3


if __name__ == '__main__':
#    Determine path to configuration file. This path manipulation is
#    here so that the script will run successfully regardless of the
#    current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)