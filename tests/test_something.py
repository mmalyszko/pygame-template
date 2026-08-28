import pytest

from src.core.objects import GameObject
from src.core.raycasting import Raycaster
from src.game.level import Level

SIMPLE_MAP = [
    [1, 1, 1, 1],
    [1, 8, 0, 1],
    [1, 0, 0, 1],
    [1, 1, 1, 1],
]

# --- VERY BASIC TESTS ---


def test_new_game_object_gets_incrementing_uid():
    a = GameObject(0, 0)
    b = GameObject(0, 0)
    assert b.uid == a.uid + 1


def test_can_move_to_open_space():
    assert Level(SIMPLE_MAP).can_move_to(1.5, 1.5, radius=0.3) is True


def test_spawn_position_returns_the_spawn_tile_center():
    assert Level(SIMPLE_MAP).spawn_position() == (1.5, 1.5)


def test_spawn_position_raises_when_missing():
    grid_without_spawn = [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ]
    with pytest.raises(ValueError):
        Level(grid_without_spawn).spawn_position()


def test_cast_single_ray_hits_wall_to_the_east():
    grid = Level(SIMPLE_MAP)
    raycaster = Raycaster(grid)

    hit = raycaster.cast_single_ray(origin_x=1.5, origin_y=1.5, angle=0.0)

    assert hit.is_vertical is True
    assert hit.depth == pytest.approx(1.5)
    assert hit.x == pytest.approx(3.0)
