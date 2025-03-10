import pygame
import numpy as np
import random

# Constants
GRID_SIZE = 1000
VISIBLE_GRID = 100
CELL_SIZE = 8
SCREEN_SIZE = VISIBLE_GRID * CELL_SIZE
FPS = 10

PHEROMONE_DECAY_STEPS = 5  # Pheromone influence lasts ~5 moves
DECAY_RATE = 1 / PHEROMONE_DECAY_STEPS  # Linear decay step

DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
"""
Ant Class
---------
Represents an individual ant in the Langton's Ant simulation.
Each ant has a position (x, y), a direction, and a unique pheromone identifier.
The ant moves according to the rules of Langton's Ant, modified by pheromone influences.
"""

class Ant:
    def __init__(self, x, y, direction, pheromone):
        self.x = x
        self.y = y
        self.direction = direction
        self.pheromone = pheromone

    def move(self, grid, pheromones, pheromone_strengths):
        current_color = grid[self.y, self.x]
        current_pheromone = pheromones[self.y, self.x]
        pheromone_strength = pheromone_strengths[self.y, self.x]

        # Default probability of moving straight
        move_straight_prob = 0.5  

        if current_pheromone == self.pheromone:  # Own pheromone
            move_straight_prob = 0.8 * pheromone_strength  # Influence scales with strength
        elif current_pheromone != 0:  # Other ant's pheromone
            move_straight_prob = 0.2 * pheromone_strength  

        if random.random() < move_straight_prob:
            new_direction = self.direction  # Move straight
        else:
            new_direction = (self.direction + (1 if current_color == 0 else -1)) % 4  # Langton's Ant rule

        # Flip cell color and deposit pheromone
        grid[self.y, self.x] ^= 1
        pheromones[self.y, self.x] = self.pheromone
        pheromone_strengths[self.y, self.x] = 1  # Reset to full strength

        # Move in the new direction
        self.direction = new_direction
        dx, dy = DIRECTIONS[self.direction]
        self.x = (self.x + dx) % GRID_SIZE
        self.y = (self.y + dy) % GRID_SIZE


class LangtonsAntSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Langton's Ant Simulation")
        self.clock = pygame.time.Clock()

        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.pheromones = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.pheromone_strengths = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)

        self.ants = [
            Ant(GRID_SIZE // 2, GRID_SIZE // 2, random.randint(0, 3), 1),
            Ant(GRID_SIZE // 2 + 10, GRID_SIZE // 2 + 10, random.randint(0, 3), 2)
        ]

        self.steps = 0
        self.font = pygame.font.Font(None, 36)
        self.offset_x = GRID_SIZE // 2 - VISIBLE_GRID // 2
        self.offset_y = GRID_SIZE // 2 - VISIBLE_GRID // 2

    def draw_cells(self):
        for y in range(VISIBLE_GRID):
            for x in range(VISIBLE_GRID):
                color = (255, 255, 255) if self.grid[y + self.offset_y, x + self.offset_x] == 0 else (0, 0, 0)
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def draw_step_counter(self):
        text = self.font.render(f"Steps: {self.steps}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

    def decay_pheromones(self):
        """Gradually reduces pheromone strength over 5 steps."""
        self.pheromone_strengths[self.pheromone_strengths > 0] -= DECAY_RATE
        self.pheromone_strengths = np.clip(self.pheromone_strengths, 0, 1)

        # Remove pheromones that have fully decayed
        self.pheromones[self.pheromone_strengths == 0] = 0  

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update ants' positions
            for ant in self.ants:
                ant.move(self.grid, self.pheromones, self.pheromone_strengths)

            # Apply pheromone decay
            self.decay_pheromones()

            self.steps += 1

            # Adjust the viewing window
            self.offset_x = min(ant.x for ant in self.ants) - VISIBLE_GRID // 2
            self.offset_y = min(ant.y for ant in self.ants) - VISIBLE_GRID // 2
            self.offset_x = max(0, min(self.offset_x, GRID_SIZE - VISIBLE_GRID))
            self.offset_y = max(0, min(self.offset_y, GRID_SIZE - VISIBLE_GRID))

            # Draw the updated simulation
            self.screen.fill((255, 255, 255))
            self.draw_cells()
            for ant in self.ants:
                screen_x = (ant.x - self.offset_x) * CELL_SIZE + CELL_SIZE // 4
                screen_y = (ant.y - self.offset_y) * CELL_SIZE + CELL_SIZE // 4
                if 0 <= screen_x < SCREEN_SIZE and 0 <= screen_y < SCREEN_SIZE:
                    rect = pygame.Rect(screen_x, screen_y, CELL_SIZE // 2, CELL_SIZE // 2)
                    color = (255, 0, 0) if ant.pheromone == 1 else (0, 0, 255)
                    pygame.draw.rect(self.screen, color, rect)

            self.draw_step_counter()
            pygame.display.flip()
            self.clock.tick(FPS)

# Run the simulation
if __name__ == "__main__":
    simulation = LangtonsAntSimulation()
    simulation.run()
    pygame.quit()
