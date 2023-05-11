import pygame
import os
import signal
import RPi.GPIO as GPIO
import time
import random
import wave
import sys
from pygame.locals import *
import multiprocessing as mp

ctx = mp.get_context('spawn')
q = ctx.Queue()
p = ctx.Queue()

def main(q,p):
    # ~ q.put('sent')
    quit_flag = False

    def GPIO_callback(channel):
        global quit_flag
        GPIO.cleanup()
        quit_flag = True

    pins = [4,26,17,22,23,27]
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in pins:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=GPIO_callback)

    os.putenv('SDL_VIDEODRIVER','fbcon')
    os.putenv('SDL_FBDEV','/dev/fb1')
    os.putenv('SDL_MOUSEDRV','TSLIB')
    os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

    pygame.init()

    fps = 48
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)

    size = width, height = 320, 240
    speed = [2,2]
    speed2 = [1, 1]
    white = 255, 255, 255
    black = 0, 0, 0
    screen = pygame.display.set_mode(size)

    font_default = pygame.font.Font(None, 20)
    font_small = pygame.font.Font(None, 15)
    font_mid = pygame.font.Font(None, 35)
    font_big = pygame.font.Font(None, 50)
    screen.fill(black)
    
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(20, 65, 80, 30)) # closer rectangle
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(195, 65, 80, 30)) # A440 rectangle
    pygame.draw.rect(screen, (0,0,255), pygame.Rect(20, 100, 80, 30)) # Song 3 rectangle
    pygame.draw.rect(screen,(255,100,0), pygame.Rect(195, 100, 80, 30)) # Song 4 rectangle
    pygame.draw.rect(screen,(230,240,10), pygame.Rect(20, 135, 80, 30)) # Song 5 rectangle
    pygame.draw.rect(screen,(200,80,200), pygame.Rect(195, 135, 80, 30)) # Song 6 rectangle
    pygame.draw.rect(screen,(130,10,245), pygame.Rect(20, 170, 80, 30)) # Song 7 rectangle
    pygame.draw.rect(screen,(10,240,240), pygame.Rect(195, 170, 80, 30)) # Song 8 rectangle

    # initializing text boxes and ball images
    quit_surface = font_default.render('QUIT', True, white)
    quit_rect = quit_surface.get_rect(center=(20, 230))
    screen.blit(quit_surface, quit_rect)

    back_surface = font_default.render('BACK', True, white)
    back_rect = back_surface.get_rect(center=(300, 230))

    song1_surface = font_default.render('CLOSER', True, white)
    song1_rect = song1_surface.get_rect(center=(60, 80))
    screen.blit(song1_surface, song1_rect)

    song2_surface = font_default.render('Disturbia', True, white)
    song2_rect = song2_surface.get_rect(center=(235, 80))
    screen.blit(song2_surface, song2_rect)

    song3_surface = font_small.render('Boom Boom Pow', True, white)
    song3_rect = song3_surface.get_rect(center=(60, 115))
    screen.blit(song3_surface, song3_rect)

    song4_surface = font_small.render('Thunderstruck', True, white)
    song4_rect = song4_surface.get_rect(center=(235, 115))
    screen.blit(song4_surface, song4_rect)

    song5_surface = font_default.render('Thriller', True, white)
    song5_rect = song5_surface.get_rect(center=(60, 150))
    screen.blit(song5_surface, song5_rect)

    song6_surface = font_default.render('Poker Face', True, white)
    song6_rect = song6_surface.get_rect(center=(235, 150))
    screen.blit(song6_surface, song6_rect)

    song7_surface = font_default.render('Let It Be', True, white)
    song7_rect = song7_surface.get_rect(center=(60, 185))
    screen.blit(song7_surface, song7_rect)

    song8_surface = font_default.render('Love Story', True, white)
    song8_rect = song8_surface.get_rect(center=(235, 185))
    screen.blit(song8_surface, song8_rect)

    song1playing_surface = font_default.render('Now Playing: Closer', True, white)
    song1playing_rect = song1playing_surface.get_rect(center=(160, 20))

    song2playing_surface = font_default.render('Now Playing: Disturbia', True, white)
    song2playing_rect = song2playing_surface.get_rect(center=(160, 20))

    song3playing_surface = font_default.render('Now Playing: Boom Boom Pow', True, white)
    song3playing_rect = song3playing_surface.get_rect(center=(160,20))

    song4playing_surface = font_default.render('Now Playing: Thunderstruck', True, white)
    song4playing_rect = song4playing_surface.get_rect(center=(160,20))

    song5playing_surface = font_default.render('Now Playing: Thriller', True, white)
    song5playing_rect = song5playing_surface.get_rect(center=(160,20))

    song6playing_surface = font_default.render('Now Playing: Poker Face', True, white)
    song6playing_rect = song6playing_surface.get_rect(center=(160,20))

    song7playing_surface = font_default.render('Now Playing: Let It Be', True, white)
    song7playing_rect = song7playing_surface.get_rect(center=(160,20))

    song8playing_surface = font_default.render('Now Playing: Love Story', True, white)
    song8playing_rect = song8playing_surface.get_rect(center=(160,20))

    songstart_surface = font_default.render('Select Song to Start', True, white)
    songstart_rect = songstart_surface.get_rect(center=(160, 45))
    screen.blit(songstart_surface, songstart_rect)

    volumemin_surface = font_big.render('-', True, white)
    volumemin_rect = volumemin_surface.get_rect(center=(25,66))

    volumemax_surface = font_big.render('+', True, white)
    volumemax_rect = volumemax_surface.get_rect(center =(275, 64))

    volume_surface = font_default.render('VOLUME', True, white)
    volume_rect = volume_surface.get_rect(center=(150, 80))

    bassmin_surface = font_big.render('-', True, white)
    bassmin_rect = bassmin_surface.get_rect(center=(25,106))

    bassmax_surface = font_big.render('+', True, white)
    bassmax_rect = bassmax_surface.get_rect(center =(275, 104))

    bass_surface = font_default.render('BASS', True, white)
    bass_rect = bass_surface.get_rect(center=(150, 120))

    midmin_surface = font_big.render('-', True, white)
    midmin_rect = midmin_surface.get_rect(center=(25,146))

    midmax_surface = font_big.render('+', True, white)
    midmax_rect = midmax_surface.get_rect(center=(275, 144))

    mid_surface = font_default.render('MID', True, white)
    mid_rect = mid_surface.get_rect(center=(150, 160))

    treblemin_surface = font_big.render('-', True, white)
    treblemin_rect = treblemin_surface.get_rect(center=(25, 186))

    treblemax_surface = font_big.render('+', True, white)
    treblemax_rect = treblemax_surface.get_rect(center =(275,184))

    treble_surface = font_default.render('TREBLE', True, white)
    treble_rect = treble_surface.get_rect(center=(150,200))
    
    rpidj_surface = font_big.render('STARTING RPI DJ', True, white)
    rpidj_rect = rpidj_surface.get_rect(center=(160, 50))
    
    loading_surface = font_big.render('LOADING...', True, white)
    loading_rect = loading_surface.get_rect(center=(160, 150))
    
    welcome_surface = font_mid.render('Welcome to RPi DJ', True, white)
    welcome_rect = welcome_surface.get_rect(center=(160, 20))
    screen.blit(welcome_surface, welcome_rect)

    song1_flag = False
    song2_flag = False
    song3_flag = False
    song4_flag = False
    song5_flag = False
    song6_flag = False
    song7_flag = False
    song8_flag = False
    paused_flag = False
    ready_flag = False

    start_flag = True

    volume_counter = 50
    bass_counter = 50
    treble_counter = 50
    mid_counter = 50
    
    pygame.display.flip()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(MOUSEBUTTONUP)

    start_time = time.clock_gettime(time.CLOCK_MONOTONIC)
    while (True):
        # ~ time.sleep(0.005)
        clock.tick(fps)
        pygame.event.wait()
        pos = pygame.mouse.get_pos()
        coordinates = pos
        x,y = pos
        # compatibilty for all button squares
        if start_flag:
            if x > 50 and x < 70 and y > 70 and y < 90: # Closer Selected
                q.put('Closer')
                song1_flag = True
                start_flag = False
            elif x > 225 and x < 245 and y > 70 and y < 90: # A440 Selected
                q.put('Disturbia')
                song2_flag = True
                start_flag = False
            elif x > 50 and x < 70 and y > 105 and y < 125: # Boom Boom Pow selected
                q.put('Boom')
                song3_flag = True
                start_flag = False
            elif x > 225 and x < 245 and y > 105 and y < 125: # Thunderstruck selected
                q.put('Thunderstruck')
                song4_flag = True
                start_flag = False
            elif x > 50 and x < 70 and y > 140 and y < 160: # Thriller selected
                q.put('Thriller')
                song5_flag = True
                start_flag = False
            elif x > 225 and x < 245 and y > 140 and y < 160: # Poker Face selected
                q.put('Poker')
                song6_flag = True
                start_flag = False
            elif x > 50 and x < 70 and y > 175 and y < 195: # Let It Be selected
                q.put('Let')
                song7_flag = True
                start_flag = False
            elif x > 225 and x < 245 and y > 175 and y < 195: # Love Story selected
                q.put('Love')
                song8_flag = True
                start_flag = False
        else:
            if ready_flag:
                if x > 285 and y > 210: # Back to start screen
                    q.put('back')
                    start_flag = True
                    song1_flag = False
                    song2_flag = False
                    song3_flag = False
                    song4_flag = False
                    song5_flag = False
                    song6_flag = False
                    song7_flag = False
                    song8_flag = False
                    ready_flag = False
                elif x > 10 and x < 40 and y > 50 and y < 80 and volume_counter > 0: # lower volume
                    volume_counter = volume_counter - 10
                    q.put('v'+ str(volume_counter))
                    # run volume code
                elif x > 260 and x < 290 and y > 50 and y < 80 and volume_counter < 100: # raise volume
                    volume_counter = volume_counter + 10
                    q.put('v'+ str(volume_counter))
                    # run volume code
                elif x > 10 and x < 40 and y > 90 and y < 120 and bass_counter > 0: # lower bass
                    bass_counter = bass_counter - 10
                    q.put('b'+ str(bass_counter))
                    # run bass code
                elif x > 260 and x < 290 and y > 90 and y < 120 and bass_counter < 100: # raise bass
                    bass_counter = bass_counter + 10
                    q.put('b'+ str(bass_counter))
                    # run bass code
                elif x > 10 and x < 40 and y > 130 and y < 160 and mid_counter > 0: # lower mid
                    mid_counter = mid_counter - 10
                    q.put('m'+ str(mid_counter))
                    # run mid code
                elif x > 260 and x < 290 and y > 130 and y < 160 and mid_counter < 100: # rasie mid
                    mid_counter = mid_counter + 10
                    q.put('m'+ str(mid_counter))
                    # run mid code
                elif x > 10 and x < 40 and y > 170 and y < 200 and treble_counter > 0: # lower treble
                    treble_counter = treble_counter - 10
                    q.put('t'+ str(treble_counter))
                    # run treble code
                elif x > 260 and x < 290 and y > 170 and y < 200 and treble_counter < 100: #raise treble
                    treble_counter = treble_counter + 10
                    q.put('t'+ str(treble_counter))
                    # run treble code
        if x < 40 and y > 210: # Quit Button Pressed
            q.put('Quit')
            pygame.quit()
            GPIO.cleanup()
            sys.exit()
            quit()
                    
        screen.fill(black)
        
        # flags for different conditions
        if not start_flag:
            if ready_flag: # allow for animations
                screen.blit(back_surface, back_rect)
                screen.blit(quit_surface, quit_rect)
                # Volume Display
                pygame.draw.rect(screen, (150,150,150), pygame.Rect(50, 65, 200, 3)) # volume bar
                pygame.draw.rect(screen, (0,0,255), pygame.Rect(10, 52, 30, 30)) # volume minus
                screen.blit(volumemin_surface, volumemin_rect)
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(260, 52, 30, 30)) # volume plus
                screen.blit(volumemax_surface, volumemax_rect)
                screen.blit(volume_surface, volume_rect)
                # Bass Display
                pygame.draw.rect(screen, (150,150,150), pygame.Rect(50, 105, 200, 3)) # bass bar
                pygame.draw.rect(screen, (0,0,255), pygame.Rect(10, 92, 30, 30)) # bass minus
                screen.blit(bassmin_surface, bassmin_rect)
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(260, 92, 30, 30)) # bass plus
                screen.blit(bassmax_surface, bassmax_rect)
                screen.blit(bass_surface, bass_rect)
                # Mid Display
                pygame.draw.rect(screen, (150,150,150), pygame.Rect(50, 145, 200, 3)) # mid bar
                pygame.draw.rect(screen, (0,0,255), pygame.Rect(10, 132, 30, 30)) # mid minus
                screen.blit(midmin_surface, midmin_rect)
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(260, 132, 30, 30)) # mid plus
                screen.blit(midmax_surface, midmax_rect)
                screen.blit(mid_surface, mid_rect)
                # Treble Display
                pygame.draw.rect(screen, (150,150,150), pygame.Rect(50, 185, 200, 3)) # treble bar
                pygame.draw.rect(screen, (0,0,255), pygame.Rect(10, 172, 30, 30)) # treble minus
                screen.blit(treblemin_surface, treblemin_rect)
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(260, 172, 30, 30)) # treble plus
                screen.blit(treblemax_surface, treblemax_rect)
                screen.blit(treble_surface, treble_rect)
                # Level Displays
                pygame.draw.circle(screen, (255,255,255), (50 + volume_counter*2, 66), 6) # volume tracker
                pygame.draw.circle(screen, (255,255,255), (50 + bass_counter*2, 106), 6) # bass tracker
                pygame.draw.circle(screen, (255,255,255), (50 + mid_counter*2, 146), 6) # mid tracker
                pygame.draw.circle(screen, (255,255,255), (50 + treble_counter*2, 186), 6) #treble tracker
            elif not ready_flag: # Loading Screen
                screen.blit(rpidj_surface, rpidj_rect)
                screen.blit(loading_surface, loading_rect)
        else: # startup screen
            screen.blit(quit_surface, quit_rect)
            pygame.draw.rect(screen, (0,255,0), pygame.Rect(20, 65, 80, 30)) # closer rectangle
            pygame.draw.rect(screen, (255,0,0), pygame.Rect(195, 65, 80, 30)) # A440 rectangle
            pygame.draw.rect(screen, (0,0,255), pygame.Rect(20, 100, 80, 30)) # Song 3 rectangle
            pygame.draw.rect(screen,(255,100,0), pygame.Rect(195, 100, 80, 30)) # Song 4 rectangle
            pygame.draw.rect(screen,(230,240,10), pygame.Rect(20, 135, 80, 30)) # Song 5 rectangle
            pygame.draw.rect(screen,(200,80,200), pygame.Rect(195, 135, 80, 30)) # Song 6 rectangle
            pygame.draw.rect(screen,(130,10,245), pygame.Rect(20, 170, 80, 30)) # Song 7 rectangle
            pygame.draw.rect(screen,(10,240,240), pygame.Rect(195, 170, 80, 30)) # Song 8 rectangle
            screen.blit(song1_surface, song1_rect)
            screen.blit(song2_surface, song2_rect)
            screen.blit(song3_surface, song3_rect)
            screen.blit(song4_surface, song4_rect)
            screen.blit(song5_surface, song5_rect)
            screen.blit(song6_surface, song6_rect)
            screen.blit(song7_surface, song7_rect)
            screen.blit(song8_surface, song8_rect)
            screen.blit(songstart_surface, songstart_rect)
            screen.blit(welcome_surface, welcome_rect)
        if ready_flag:
            if song1_flag:
                screen.blit(song1playing_surface, song1playing_rect)
            if song2_flag:
                screen.blit(song2playing_surface, song2playing_rect)
            if song3_flag:
                screen.blit(song3playing_surface, song3playing_rect)
            if song4_flag:
                screen.blit(song4playing_surface, song4playing_rect)
            if song5_flag:
                screen.blit(song5playing_surface, song5playing_rect)
            if song6_flag:
                screen.blit(song6playing_surface, song6playing_rect)
            if song7_flag:
                screen.blit(song7playing_surface, song7playing_rect)
            if song8_flag:
                screen.blit(song8playing_surface, song8playing_rect)
        pygame.display.flip()
        if not start_flag and not ready_flag:
            read = ''
            read = p.get()
            pygame.event.post(pygame.event.Event(MOUSEBUTTONUP))
            if read == 'Ready':
                ready_flag = True
                read = ''
        if quit_flag:
            # ~ time.sleep(1)
            pygame.quit()
            sys.exit()
    
if __name__ == '__main__':
    main(q,p)
