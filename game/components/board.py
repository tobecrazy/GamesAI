import pygame
from .block import Block

class Board:
    WIDTH = 10
    HEIGHT = 20
    CELL_SIZE = 30
    ANIMATION_STEPS = 10  # Number of steps for the clearing animation

    def __init__(self):
        self.grid = [[None for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.clearing_lines = []  # List of y coordinates for lines being cleared
        self.animation_progress = 0  # Shared progress for all clearing animations
        self.lines_cleared = 0  # Track the number of lines cleared

    def is_valid_position(self, block):
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x, board_y = block.x + x, block.y + y
                    if (board_x < 0 or board_x >= self.WIDTH or
                        board_y >= self.HEIGHT or
                        (board_y >= 0 and self.grid[board_y][board_x] is not None)):
                        return False
        return True

    def place_block(self, block):
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[block.y + y][block.x + x] = block.color

    def clear_lines(self):
        self.lines_cleared = 0
        # Identify all full lines
        full_lines = []
        for y in range(self.HEIGHT - 1, -1, -1):
            if all(cell is not None for cell in self.grid[y]):
                full_lines.append(y)
                self.lines_cleared += 1
        
        if full_lines:
            self.clearing_lines = full_lines
            self.animation_progress = 0
            
        return self.lines_cleared

    def update_clearing_animation(self):
        if not self.clearing_lines:
            return
            
        self.animation_progress += 1
        
        if self.animation_progress >= self.ANIMATION_STEPS:
            # Remove all cleared lines and insert new rows at top
            # Sort lines in descending order first
            sorted_lines = sorted(self.clearing_lines, reverse=True)
            
            # Remove all marked lines
            for y in sorted_lines:
                del self.grid[y]
            
            # Add new empty rows at the top equal to the number of cleared lines
            for _ in range(len(sorted_lines)):
                self.grid.insert(0, [None for _ in range(self.WIDTH)])
            self.clearing_lines = []
            self.animation_progress = 0

    def is_animation_complete(self):
        return len(self.clearing_lines) == 0

    def draw(self, screen):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pygame.draw.rect(
                    screen,
                    (50, 50, 50),
                    (x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE),
                    1
                )
                if cell:
                    if y in self.clearing_lines:
                        # Draw clearing animation using shared progress
                        alpha = int(255 * (1 - self.animation_progress / self.ANIMATION_STEPS))
                        color = (*cell, alpha)
                        surface = pygame.Surface((self.CELL_SIZE - 2, self.CELL_SIZE - 2), pygame.SRCALPHA)
                        pygame.draw.rect(surface, color, (0, 0, self.CELL_SIZE - 2, self.CELL_SIZE - 2))
                        screen.blit(surface, (x * self.CELL_SIZE + 1, y * self.CELL_SIZE + 1))
                    else:
                        # Draw normal block
                        pygame.draw.rect(
                            screen,
                            cell,
                            (x * self.CELL_SIZE + 1, y * self.CELL_SIZE + 1, self.CELL_SIZE - 2, self.CELL_SIZE - 2)
                        )

    def get_ghost_position(self, block):
        ghost_block = Block(block.shape, block.color)
        ghost_block.x, ghost_block.y = block.x, block.y

        while self.is_valid_position(ghost_block):
            ghost_block.y += 1

        ghost_block.y -= 1
        return ghost_block

    def draw_ghost(self, screen, block):
        ghost_block = self.get_ghost_position(block)
        for y, row in enumerate(ghost_block.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        (100, 100, 100),
                        ((ghost_block.x + x) * self.CELL_SIZE, (ghost_block.y + y) * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE),
                        1
                    )
