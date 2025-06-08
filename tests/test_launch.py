import pytest

kivy = pytest.importorskip('kivy')

from main import ZippyApp, ZippyGame


def test_app_build_returns_game():
    app = ZippyApp()
    game = app.build()
    assert isinstance(game, ZippyGame)


def test_game_has_map():
    app = ZippyApp()
    game = app.build()
    assert hasattr(game, 'map')
