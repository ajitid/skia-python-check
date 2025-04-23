import skia
import pyglet
from pyglet import gl

# taken from @/.venv/Lib/site-packages/pyglet/window/__init__.py
# and from https://pyglet.readthedocs.io/en/latest/programming_guide/opengles.html
display = pyglet.display.get_display()
screen = display.get_default_screen()
config = screen.get_best_config()
# pyglet automatically sets 
# - both major_version and minor_version to 3,
# - double_buffer on, and
# - keeps multisampling (MSAA) off
# so we won't set them manually
config.depth_size = 0 # would need a value for 3D (if you remove it to altogether, pyglet will default to 24)
config.stencil_size = 8

# Set up Pyglet window
window = pyglet.window.Window(width=800, height=600, caption="Skia + Pyglet (GPU)", config=config, resizable=True)
assert window.config.stencil_size == 8

# Create Skia GPU context
context = None
surface = None

def init_skia():
    global context, surface
    # Create a GPU context using the current OpenGL context
    context = skia.GrDirectContext.MakeGL()
    if not context:
        # Alternatively I could've used `assert` or `raise RuntimeError`. See https://kyamagu.github.io/skia-python/tutorial/canvas.html#opengl-window
        print("Failed to create Skia GrDirectContext")
        return

    # Create framebuffer info for the current GL context
    fbInfo = skia.GrGLFramebufferInfo(0, gl.GL_RGBA8)

    # Create backend render target wrapping the Pyglet window's framebuffer
    backendRT = skia.GrBackendRenderTarget(
        window.width, window.height,
        1,  # sample count (1 for no multisampling if using Skia >= m116, 0 otherwise)
            # Pyglet's default window usually doesn't have MSAA unless requested.
            # If you configure Pyglet for MSAA, match the sample count here.
        8,  # stencil bits
        fbInfo
    )

    # Create Skia surface that renders directly to the GL framebuffer
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context,
        backendRT,
        skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType,        # Match GL_RGBA8
        skia.ColorSpace.MakeSRGB(),       # Common color space
        # Optional: Surface properties
        # skia.SurfaceProps(flags=skia.kDefault_SurfacePropsFlags)
    )

    if not surface:
        print("Failed to create Skia surface")
        # Clean up context if surface creation failed
        context.abandonContext()
        context = None
        backendRT = None 
        fbInfo = None
    else:
        print(f"Skia surface created ({window.width}x{window.height})")


def cleanup_skia():
    global context, surface
    surface = None
    if context:
        context.abandonContext()
        context = None

@window.event
def on_draw():
    # Docs say to use `switch_to()`` if you have multiple windows. I don't have multiple windows,
    # but still using if I introduce multiple windows later. See links in [this ticket](https://github.com/pyglet/pyglet/issues/726) 
    # and see [this ticket](https://github.com/pyglet/pyglet/issues/1249) for more details. 
    # The latter ticket mentions at several places, which [this Gemini response](https://gemini.google.com/share/0ac5b7150d96) does.
    # Confirm if you'd also have to put `switch_to()` at several places as well.
    window.switch_to() 
    
    gl.glClearColor(0.0, 0.0, 0.0, 1.0) # Only sets the color (to black). Doesn't clears by itself. Actual clearing happens when you use `gl.glClear()`
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_STENCIL_BUFFER_BIT) # `| gl.GL_DEPTH_BUFFER_BIT` would be needed if you're doing 3D
    # ^ Not using window.clear() because we're using gl.glClear() instead. But windows.clear() docs mention to use window.switch_to() before, which we're doing.

    global context, surface

    # Initialize Skia on first draw or if context is lost
    if surface is None:
        init_skia()

    if surface:
        # Get canvas for drawing
        canvas = surface.getCanvas()

        # Clear Skia surface with a background color
        canvas.clear(skia.Color4f(0.9, 0.9, 0.9, 1.0))

        # --- Drawing commands ---
        paint = skia.Paint(
            AntiAlias=True,
            Color=skia.ColorRED, # or skia.Color(255, 0, 0)
            StrokeWidth=4,
            Style=skia.Paint.kStroke_Style
        )

        fill_paint = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(0, 150, 255, 128),
            Style=skia.Paint.kFill_Style
        )

        # Draw shapes
        canvas.drawCircle(400, 300, 100, paint)
        canvas.drawRect(skia.Rect(250, 200, 550, 400), fill_paint)

        # Draw text
        font = skia.Font(skia.Typeface(None), 24) # If you want to pass a typeface you'd use `skia.Typeface('Arial')` instead
        text_paint = skia.Paint(Color=skia.Color(0, 0, 255)) # Skia by default enables anti-aliasing for text so we don't have to explicitly specify it
        canvas.drawString("Skia + Pyglet with GPU Acceleration", 200, 150, font, text_paint)
        # --- End Drawing ---

        # Flush drawing commands directly to the GL context
        surface.flushAndSubmit()  # Preferred over manual canvas.flush() + context.flush()

    else:
        # Handle case where Skia initialization failed
        # (Could draw fallback text using Pyglet's labels if needed)
        pass

@window.event
def on_resize(width, height):
    global surface
    # Release previous surface when window is resized
    surface = None
    return pyglet.event.EVENT_HANDLED

@window.event
def on_context_lost():
    print("OpenGL context lost!")
    cleanup_skia()
    return pyglet.event.EVENT_HANDLED

@window.event
def on_context_state_lost():
    print("OpenGL context state lost!")
    cleanup_skia()
    return pyglet.event.EVENT_HANDLED

@window.event
def on_close():
    cleanup_skia()

# Start the application
if __name__ == "__main__":
    pyglet.app.run()