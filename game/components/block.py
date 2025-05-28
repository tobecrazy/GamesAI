import pygame
import random

class Block:
    SHAPES = [
        [[1, 1, 1, 1]],  # I
        [[1, 1, 1], [0, 1, 0]],  # T
        [[1, 1, 1], [1, 0, 0]],  # J
        [[1, 1, 1], [0, 0, 1]],  # L
        [[1, 1], [1, 1]],  # O
        [[1, 1, 0], [0, 1, 1]],  # S
        [[0, 1, 1], [1, 1, 0]]  # Z
    ]

    COLORS = [
        (0, 255, 255),  # Cyan (I)
        (128, 0, 128),  # Purple (T)
        (0, 0, 255),    # Blue (J)
        (255, 127, 0),  # Orange (L)
        (255, 255, 0),  # Yellow (O)
        (0, 255, 0),    # Green (S)
        (255, 0, 0)     # Red (Z)
    ]

    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = 3
        self.y = 0

    def to_dict(self):
        """Return a dictionary representation of the block."""
        return {
            'shape': self.shape,
            'color': self.color,
            'x': self.x,
            'y': self.y
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Block instance from a dictionary."""
        # We assume shape and color are directly usable by __init__
        # If SHAPES and COLORS were just indices, we'd need to look them up.
        # For now, direct assignment is fine as per current __init__ structure.
        block = cls(data['shape'], data['color'])
        block.x = data['x']
        block.y = data['y']
        return block

    @classmethod
    def random(cls):
        shape_index = random.randint(0, len(cls.SHAPES) - 1)
        return cls(cls.SHAPES[shape_index], cls.COLORS[shape_index])

    def rotate(self, direction=1):
        self.shape = list(zip(*self.shape[::-direction]))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen, offset_x=0, offset_y=0):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        self.color,
                        (
                            (self.x + x) * 30 + offset_x,
                            (self.y + y) * 30 + offset_y,
                            30,
                            30
                        )
                    )
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        (
                            (self.x + x) * 30 + offset_x,
                            (self.y + y) * 30 + offset_y,
                            30,
                            30
                        ),
                        1
                    )