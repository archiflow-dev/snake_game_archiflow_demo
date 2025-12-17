"""Test configuration and fixtures."""

import pytest
import pygame
from src.core.config import Config
from src.entities.grid import SquareGrid
from src.entities.snake import Snake, Direction
from src.entities.food import Food


@pytest.fixture(scope="session")
def pygame_setup():
    """Initialize pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def config():
    """Provide a test configuration."""
    return Config()


@pytest.fixture
def grid():
    """Provide a test grid."""
    return SquareGrid(20, 15)


@pytest.fixture
def snake(grid):
    """Provide a test snake."""
    start_pos = SquareCoord(10, 7)
    return Snake(start_pos, Direction.RIGHT, 3)


@pytest.fixture
def food(grid):
    """Provide a test food item."""
    pos = SquareCoord(5, 5)
    return Food(pos, "apple", 10)