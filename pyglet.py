import skia
import pyglet
from pyglet.gl import *
# import numpy as np
# import ctypes

# Set up Pyglet window
window = pyglet.window.Window(width=800, height=600, caption="Skia + Pyglet (GPU)")

# Create Skia GPU context
context = None
surface = None

def init_skia():
    global context, surface
    # Create a GPU context using the current OpenGL context
    context = skia.GrDirectContext.MakeGL()
    
    # Set up the render target
    info = skia.ImageInfo.MakeN32Premul(window.width, window.height)
    
    # Create framebuffer info for the current GL context
    fbInfo = skia.GrGLFramebufferInfo()
    fbInfo.fFBOID = 0  # Default framebuffer
    fbInfo.fFormat = GL_RGBA8
    
    # Create backend render target
    backendRT = skia.GrBackendRenderTarget(
        window.width, window.height, 
        1,  # sample count (0 or 1 for no multisampling)
        8,  # stencil bits (typically 8)
        fbInfo
    )
    
    # Create Skia surface that renders directly to the GL framebuffer
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, 
        backendRT,
        skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType,
        skia.ColorSpace.MakeSRGB()
    )
    
    if not surface:
        print("Failed to create Skia surface")

def cleanup_skia():
    global context, surface
    if surface:
        surface.delete()
        surface = None
    if context:
        context.abandonContext()
        context = None

@window.event
def on_draw():
    window.clear()
    
    global context, surface
    
    # Initialize Skia on first draw or if context is lost
    if surface is None:
        init_skia()
    
    if surface:
        # Get canvas for drawing
        canvas = surface.getCanvas()
        
        # Clear with background color
        canvas.clear(skia.Color4f(0.9, 0.9, 0.9, 1.0))
        
        # Create paint objects
        paint = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(255, 0, 0),
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
        font = skia.Font(skia.Typeface(None), 24)
        text_paint = skia.Paint(Color=skia.Color(0, 0, 255))
        canvas.drawString("Skia + Pyglet with GPU Acceleration", 200, 150, font, text_paint)
        
        # Flush drawing commands directly to the GL context
        surface.flushAndSubmit()  # Preferred over manual canvas.flush() + context.flush()

@window.event
def on_resize(width, height):
    global surface
    # Release previous surface when window is resized
    if surface:
        surface.delete()
        surface = None
    return pyglet.event.EVENT_HANDLED

@window.event
def on_context_lost():
    global surface, context
    # Clean up resources when context is lost
    cleanup_skia()
    return pyglet.event.EVENT_HANDLED

@window.event
def on_context_state_lost():
    global surface, context
    # Clean up resources when context state is lost
    cleanup_skia()
    return pyglet.event.EVENT_HANDLED

@window.event
def on_close():
    # Clean up resources when window is closed
    cleanup_skia()

# Start the application
if __name__ == "__main__":
    pyglet.app.run()