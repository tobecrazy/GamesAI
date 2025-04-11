import pygame
from .block import Block

class Board:
    WIDTH = 10
    HEIGHT = 20
    CELL_SIZE = 30

    def __init__(self):
        self.grid = [[None for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]

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
        lines_cleared = 0
        y = self.HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(self.WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        return lines_cleared

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