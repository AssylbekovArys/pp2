import pygame
pygame.init()
W, H = 1200, 800
x = W//2
y = H//2
WHITE = (255, 255, 255)
sc = pygame.display.set_mode((W, H))
mickey = pygame.image.load("images/mickeyclock.jpeg")
def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect)
    
angle = 0    
    
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
            
    sc.fill(WHITE)
    
    angle -= 1
    blitRotateCenter(sc, mickey, (0,0), angle) 
    
    pygame.display.update()