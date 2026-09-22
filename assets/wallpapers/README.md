# Live Weather Wallpapers

Looping 1920×1080 MP4 backgrounds rendered from the app's own sky engine
(same navy theme, border sweep included): `snow.mp4`, `rain.mp4`, `sun.mp4`
(7 seconds each, seamless loops).

Windows cannot use a Tkinter app as wallpaper directly, so to put these on
your desktop:

1. Install **Lively Wallpaper** (free, Microsoft Store).
2. In Lively, click **Add Wallpaper** → drag in a `.mp4` file.
3. Right-click the desktop → it plays live behind your icons.

Regenerate any time with the render script (needs `imageio` + `imageio-ffmpeg`
in the venv).
