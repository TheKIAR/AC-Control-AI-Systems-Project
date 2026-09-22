import os

import pytest


@pytest.mark.skipif(os.name != "posix" or not os.environ.get("DISPLAY"),
                    reason="Tk GUI smoke test needs a display")
def test_gui_builds_and_theme_toggles():
    from src.main import DemoApp

    app = DemoApp()
    try:
        app.update_idletasks()
        assert app.title().startswith("AI Control System")
        assert app.temp_var.get() == 22
        assert app.rl_stats_var.get() != ""

        app.toggle_theme()
        app.update()
        app.update_idletasks()
        assert app.theme == "light"

        app.toggle_theme()
        app.update()
        app.update_idletasks()
        assert app.theme == "dark"
    finally:
        app.destroy()
