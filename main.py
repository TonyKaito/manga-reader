from raylib import *
from dataclasses import dataclass
import math

@dataclass
class GameData:
    
    mouseClickingOn: bool
    divider: object
    
    

def main():
    screenWidth = 1200
    screenHeight = 720
    
    InitWindow(screenWidth, screenHeight, b"Manga Reader Thing IDK Good Name Yet")
    SetTargetFPS(60)
    
    
    cameraPlayer1 = ffi.new("struct Camera2D *", {
        "offset": [0.0, 0.0],
        "target": [0.0, 0.0],
        "rotation": 0.0,
        "zoom": 1.0,
    })
    rtScreenPlayer1 = LoadRenderTexture(screenWidth, screenHeight)
    
    cameraPlayer2 = ffi.new("struct Camera2D *", {
        "offset": [0.0, 0.0],
        "target": [0.0, 0.0],
        "rotation": 0.0,
        "zoom": 1.0,
    })
    rtScreenPlayer2 = LoadRenderTexture(screenWidth, screenHeight)
    
    
    
    image = LoadImage(b"01_001.jpg") # hardcoded for now
    textureImg = LoadTextureFromImage(image)
    UnloadImage(image)
    
    
    
    splitX = screenWidth / 2 # gameData variable
    dividerWidth = 8
    draggingDivider = False # gameData variable
    draggingLeft = False # gameData variable
    

    while not WindowShouldClose():
        # handle input
        mouse = GetMousePosition()
        
        divider = ffi.new("struct Rectangle *", [float(splitX - dividerWidth/2), 0.0, float(dividerWidth), float(screenHeight)])
        leftPanelTexture = ffi.new("struct Rectangle *", [0.0, 0.0, float(divider.x), -float(screenHeight)])
        leftPanelInteract = ffi.new("struct Rectangle *", [0.0, 0.0, float(divider.x), float(screenHeight)])
        rightPanelTexture = ffi.new("struct Rectangle *", [0.0, 0.0, float(screenWidth - (divider.x + divider.width)), -float(screenHeight)])
        rightPanelInteract = ffi.new("struct Rectangle *", [float(divider.x + divider.width), 0.0, float(screenWidth - (divider.x + divider.width)), float(screenHeight)])
        
        if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            draggingDivider = CheckCollisionPointRec(mouse, divider[0])
            draggingLeft = CheckCollisionPointRec(mouse, leftPanelInteract[0])
            draggingRight = CheckCollisionPointRec(mouse, rightPanelInteract[0])
            
        if IsMouseButtonReleased(MOUSE_BUTTON_LEFT):
            draggingDivider = False
            draggingLeft = False
            draggingRight = False
        
        if IsMouseButtonDown(MOUSE_BUTTON_LEFT):
            if draggingDivider:
                splitX = max(1/6 * screenWidth, min(5/6 * screenWidth, mouse.x))
            
            if draggingLeft:
                delta = GetMouseDelta()
                delta = Vector2Scale(delta, -1.0 / cameraPlayer1.zoom)
                cameraPlayer1.target = Vector2Add(cameraPlayer1.target, delta)
                
            if draggingRight:
                delta = GetMouseDelta()
                delta = Vector2Scale(delta, -1.0 / cameraPlayer1.zoom)
                cameraPlayer1.target = Vector2Add(cameraPlayer1.target, delta)
        
        if GetMouseWheelMove():
            if CheckCollisionPointRec(mouse, leftPanelInteract[0]):
                # handle edge case where if scrolling fast enough, the log becomes negative
                mouseWheelMove = max(GetMouseWheelMove(), 1 - 10 * cameraPlayer1.zoom)
                cameraPlayer1.zoom = math.exp(math.log(cameraPlayer1.zoom + mouseWheelMove * 0.1))
            
            if CheckCollisionPointRec(mouse, rightPanelInteract[0]):
                # handle edge case where if scrolling fast enough, the log becomes negative
                mouseWheelMove = max(GetMouseWheelMove(), 1 - 10 * cameraPlayer1.zoom)
                cameraPlayer1.zoom = math.exp(math.log(cameraPlayer1.zoom + mouseWheelMove * 0.1))
        
        if cameraPlayer1.zoom >= 5.0: cameraPlayer1.zoom = 5.0
        if cameraPlayer1.zoom <= 0.02: cameraPlayer1.zoom = 0.02
        
        
        if cameraPlayer2.zoom >= 5.0: cameraPlayer2.zoom = 5.0
        if cameraPlayer2.zoom <= 0.02: cameraPlayer2.zoom = 0.02
        
        # Draw Textures
        BeginTextureMode(rtScreenPlayer1)
        if True:
            ClearBackground(GetColor(0xFF181818))
            BeginMode2D(cameraPlayer1[0])
            if True:
                DrawTexture(textureImg, 0, 0, WHITE)
            EndMode2D()
        
        EndTextureMode()
        
        BeginTextureMode(rtScreenPlayer2)
        if True:
            ClearBackground(BLUE)
        
        EndTextureMode()
        
        BeginDrawing()
        ClearBackground(BLACK)
        
        originScreenPlayer1 = ffi.new("struct Vector2 *", [0.0, 0.0])
        DrawTextureRec(rtScreenPlayer1.texture, leftPanelTexture[0], originScreenPlayer1[0], WHITE)
        originScreenPlayer2 = ffi.new("struct Vector2 *", [divider.x + divider.width, 0.0])
        DrawTextureRec(rtScreenPlayer1.texture, rightPanelTexture[0], originScreenPlayer2[0], WHITE)
        
        DrawRectanglePro(divider[0], originScreenPlayer1[0], 0.0, LIGHTGRAY)
        
        # DrawText(b"Hello World", 190, 200, 20, RAYWHITE)
        EndDrawing()
    CloseWindow()

if __name__ == "__main__":
    main()