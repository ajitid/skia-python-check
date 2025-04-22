import sys
import ctypes
import sdl3
import skia

class SDL3SkiaApp:
    def __init__(self, title="SDL3 + Skia", width=800, height=600):
        # Initialize SDL3
        if sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO) < 0:
            print(f"SDL could not initialize! SDL Error: {sdl3.SDL_GetError()}")
            sys.exit(1)
            
        self.width = width
        self.height = height
        
        # Create window with SDL3
        self.window = sdl3.SDL_CreateWindow(
            title.encode("utf-8"),
            width,
            height,
            sdl3.SDL_WINDOW_MAXIMIZED
        )
        
        if not self.window:
            print(f"Window could not be created! SDL Error: {sdl3.SDL_GetError()}")
            sys.exit(1)
        
        # Get window surface
        self.surface = sdl3.SDL_GetWindowSurface(self.window)
        
        # Get surface info for Skia
        info = skia.ImageInfo.MakeN32Premul(width, height)
        
        # Create Skia surface
        self.skia_surface = skia.Surface.MakeRaster(info)
        
        # Running flag
        self.is_running = True
        
    def handle_events(self):
        event = sdl3.SDL_Event()
        while sdl3.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl3.SDL_EVENT_QUIT:
                self.is_running = False
            elif event.type == sdl3.SDL_EVENT_KEY_DOWN:
                if event.key.key == sdl3.SDLK_ESCAPE:
                    self.is_running = False
                    
    def update(self):
        # This method can be overridden by subclasses to update application state
        pass
    
    def render(self):
        # Get canvas from Skia surface
        canvas = self.skia_surface.getCanvas()
        
        # Clear background
        canvas.clear(skia.Color(240, 240, 240))
        
        # Override this method to draw with Skia
        self.draw(canvas)
        
        # Get pixel data from Skia surface
        image = self.skia_surface.makeImageSnapshot()
        pixels = image.tobytes()
        
        # Copy Skia pixels to SDL surface
        surface_pixels = ctypes.c_void_p(self.surface.contents.pixels)
        ctypes.memmove(surface_pixels, pixels, len(pixels))
        
        # Update window surface
        sdl3.SDL_UpdateWindowSurface(self.window)
    
    def draw(self, canvas):
        # Default implementation - draws a simple demo
        # This method should be overridden by subclasses
        
        # Draw a rectangle
        paint = skia.Paint(Color=skia.Color(66, 133, 244), AntiAlias=True)
        canvas.drawRect(skia.Rect(100, 100, 300, 300), paint)
        
        # Draw a circle
        paint.setColor(skia.Color(127, 127, 0))
        canvas.drawCircle(500, 200, 100, paint)
        
        # Draw some text
        paint.setColor(skia.Color(15, 157, 88))
        font = skia.Font(None, 40)  # Create a font with size 40
        canvas.drawString("SDL3 + Skia Integration", 200, 400, font, paint)
    
    def run(self):
        # Main application loop
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        
        # Clean up
        self.cleanup()
    
    def cleanup(self):
        sdl3.SDL_DestroyWindow(self.window)
        sdl3.SDL_Quit()

# Example usage
if __name__ == "__main__":
    app = SDL3SkiaApp()
    app.run()