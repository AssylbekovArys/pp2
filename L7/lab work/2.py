import pygame
pygame.init()
songs = ['C:/Users/acer/Desktop/git lessin/L7/lab work/Alec Benjamin feat. Alessia Cara - Let Me Down Slowly (feat.mp3','C:/Users/acer/Desktop/git lessin/L7/lab work/week7_Fly High x Peaches .mp3','C:/Users/acer/Desktop/git lessin/L7/lab work/week7_Fly High x Peaches .mp3']
l = 0
pygame.mixer.music.load(songs[l])
pygame.mixer.music.play()
screen = pygame.display.set_mode((400, 300))
running = True
while running: 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                pygame.mixer.music.load(songs[l+1])
                pygame.mixer.music.play()
                l +=1
            elif event.key == pygame.K_5:
                pygame.mixer.music.load(songs[l-1])
                pygame.mixer.music.play()
                l-=1
            elif event.key == pygame.K_1:
                pygame.mixer.music.stop()
            elif event.key == pygame.K_2:
                pygame.mixer.music.pause()
            elif event.key == pygame.K_3:
                pygame.mixer.music.unpause()
            elif event.key == pygame.K_4:
                pygame.mixer.music.rewind()
    pygame.display.flip()