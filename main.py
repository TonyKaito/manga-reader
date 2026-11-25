from raylib import *
from dataclasses import dataclass
from enum import Enum
import math



@dataclass
class GameData:
    divider: object
    
    
class MenuState(Enum):
    MAIN = 0
    PALETTE = 1 

def main():
    screenWidth = 1200
    screenHeight = 720
    
    InitWindow(screenWidth, screenHeight, b"Manga Reader Thing IDK Good Name Yet")
    SetTargetFPS(60)
    SetExitKey(KEY_NULL)
    
    
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
    
    
    # TODO(kt): do a "render distance" type thing, render more pages at far enough zoom-out (i think max 6 per side?)
    image = LoadImage(b"00_cover.jpg") # hardcoded for now
    image2 = LoadImage(b"01_001.jpg") # hardcoded for now
    textureImg = LoadTextureFromImage(image)
    textureImg2 = LoadTextureFromImage(image2)
    UnloadImage(image)
    UnloadImage(image2)
    
    blurShader = LoadShader(ffi.NULL, b"shaders/blur.fs")
    
    kernelLoc = GetShaderLocation(blurShader, b"kernelSize")
    texelLoc = GetShaderLocation(blurShader, b"texelSize")

    # Keep these pointers alive while you use them.
    kernelSize = ffi.new("int *", 41)
    texelSize = ffi.new("float[2]", [1.0 / screenWidth, 1.0 / screenHeight])

    SetShaderValue(blurShader, kernelLoc, kernelSize, SHADER_UNIFORM_INT)
    SetShaderValue(blurShader, texelLoc, texelSize, SHADER_UNIFORM_VEC2)
    
    splitX = screenWidth / 2 # gameData variable
    dividerWidth = 8
    draggingDivider = False # gameData variable
    draggingLeft = False # gameData variable
    menuState = MenuState.MAIN # gameData variable...?
    
    paletteMenuWindowRec = ffi.new("struct Rectangle *", [int(1/10 * screenWidth), int(1/10 * screenHeight), int(8/10 * screenWidth), int(8/10 * screenHeight)])
    roundedRecVal = 0.05
    roundedRecSeg = 10
    
    
    cameras = [cameraPlayer1, cameraPlayer2]
    syncOptions = ffi.new("int *", 1) # gameData variable
    
    
    

    while not WindowShouldClose():
        # handle input
        mouse = GetMousePosition()
        
        divider = ffi.new("struct Rectangle *", [float(splitX - dividerWidth/2), 0.0, float(dividerWidth), float(screenHeight)])
        leftPanelTexture = ffi.new("struct Rectangle *", [0.0, 0.0, float(divider.x), -float(screenHeight)])
        rightPanelTexture = ffi.new("struct Rectangle *", [0.0, 0.0, float(screenWidth - (divider.x + divider.width)), -float(screenHeight)])
        
        # for seeing if cameras need to sync, dervied from syncOptions
        activeCameras = (1 << syncOptions[0]) - 1
        leftActiveCameraInd = (activeCameras >> 1) & 1
        rightActiveCameraInd = (activeCameras >> 0) & 1
        
        match menuState:
            case MenuState.PALETTE:
                if IsKeyPressed(KEY_ESCAPE):
                    menuState = MenuState.MAIN
            case MenuState.MAIN: 
                if IsKeyPressed(KEY_P):
                    menuState = MenuState.PALETTE
                
                leftPanelInteract = ffi.new("struct Rectangle *", [0.0, 0.0, float(divider.x), float(screenHeight)])
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
                        delta = Vector2Scale(delta, -1.0 / cameras[leftActiveCameraInd].zoom)
                        cameras[leftActiveCameraInd].target = Vector2Add(cameras[leftActiveCameraInd].target, delta)
                        
                    if draggingRight:
                        delta = GetMouseDelta()
                        delta = Vector2Scale(delta, -1.0 / cameras[rightActiveCameraInd].zoom)
                        cameras[rightActiveCameraInd].target = Vector2Add(cameras[rightActiveCameraInd].target, delta)
                
                if GetMouseWheelMove():
                    if CheckCollisionPointRec(mouse, leftPanelInteract[0]):
                        worldUnderMouse = GetScreenToWorld2D(mouse, cameras[leftActiveCameraInd][0])
                        
                        # handle edge case where if scrolling fast enough, the log becomes negative
                        mouseWheelMove = max(GetMouseWheelMove(), 1 - 10 * cameras[leftActiveCameraInd].zoom)
                        
                        cameras[leftActiveCameraInd].zoom = math.exp(math.log(cameras[leftActiveCameraInd].zoom + mouseWheelMove * 0.1))
                        cameras[leftActiveCameraInd].target = Vector2Add(worldUnderMouse, Vector2Scale(Vector2Subtract(cameras[leftActiveCameraInd].offset, mouse), 1.0 / cameras[leftActiveCameraInd].zoom))
                    
                    if CheckCollisionPointRec(mouse, rightPanelInteract[0]):
                        mouseOffset = Vector2Subtract(mouse, ffi.new("struct Vector2 *", [float(divider.x + divider.width), 0.0])[0])
                        worldUnderMouse = GetScreenToWorld2D(mouseOffset, cameras[rightActiveCameraInd][0])
                        
                        # handle edge case where if scrolling fast enough, the log becomes negative
                        mouseWheelMove = max(GetMouseWheelMove(), 1 - 10 * cameras[rightActiveCameraInd].zoom)
                        
                        cameras[rightActiveCameraInd].zoom = math.exp(math.log(cameras[rightActiveCameraInd].zoom + mouseWheelMove * 0.1))
                        cameras[rightActiveCameraInd].target = Vector2Add(worldUnderMouse, Vector2Scale(Vector2Subtract(cameras[rightActiveCameraInd].offset, mouseOffset), 1.0 / cameras[rightActiveCameraInd].zoom))
                
        if cameraPlayer1.zoom >= 5.0: cameraPlayer1.zoom = 5.0
        if cameraPlayer1.zoom <= 0.02: cameraPlayer1.zoom = 0.02
        
        if cameraPlayer2.zoom >= 5.0: cameraPlayer2.zoom = 5.0
        if cameraPlayer2.zoom <= 0.02: cameraPlayer2.zoom = 0.02
        
        # Draw Textures
        BeginTextureMode(rtScreenPlayer1)
        if True:
            ClearBackground(GetColor(0x181818FF))
            
            BeginMode2D(cameras[leftActiveCameraInd][0])
            if True:
                DrawTexture(textureImg2, 0, 0, WHITE)
            EndMode2D()
        
        EndTextureMode()
        
        BeginTextureMode(rtScreenPlayer2)
        if True:
            ClearBackground(GetColor(0x181818FF))
            
            BeginMode2D(cameras[rightActiveCameraInd][0])
            if True:
                DrawTexture(textureImg2, 0, 0, WHITE)
            EndMode2D()
        
        EndTextureMode()
        
        BeginDrawing()
        ClearBackground(BLACK)
        match menuState:
            case MenuState.PALETTE:
                BeginShaderMode(blurShader)
                if True:
                    originScreenPlayer1 = ffi.new("struct Vector2 *", [0.0, 0.0])
                    DrawTextureRec(rtScreenPlayer1.texture, leftPanelTexture[0], originScreenPlayer1[0], WHITE)
                    originScreenPlayer2 = ffi.new("struct Vector2 *", [divider.x + divider.width, 0.0])
                    DrawTextureRec(rtScreenPlayer2.texture, rightPanelTexture[0], originScreenPlayer2[0], WHITE)
                    
                    DrawRectanglePro(divider[0], originScreenPlayer1[0], 0.0, LIGHTGRAY)
                EndShaderMode()
                
                DrawRectangleRounded(paletteMenuWindowRec[0], roundedRecVal, roundedRecSeg, GetColor(0x181818FF))
                
                # TODO(kt): make this look nicer lol
                GuiComboBox(ffi.new("struct Rectangle *",[160, 170, 500, 72])[0], b"Sync To Left;Unsynced;Sync to Right", syncOptions);
            case MenuState.MAIN:
                originScreenPlayer1 = ffi.new("struct Vector2 *", [0.0, 0.0])
                DrawTextureRec(rtScreenPlayer1.texture, leftPanelTexture[0], originScreenPlayer1[0], WHITE)
                originScreenPlayer2 = ffi.new("struct Vector2 *", [divider.x + divider.width, 0.0])
                DrawTextureRec(rtScreenPlayer2.texture, rightPanelTexture[0], originScreenPlayer2[0], WHITE)
                
                DrawRectanglePro(divider[0], originScreenPlayer1[0], 0.0, LIGHTGRAY)
        
        # DrawText(b"Hello World", 190, 200, 20, RAYWHITE)
        EndDrawing()
    CloseWindow()

if __name__ == "__main__":
    main()