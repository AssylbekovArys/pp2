import pygame

pygame.init()
work = True
cl = pygame.time.Clock()
color = (255, 0, 0)
screen = pygame.display.set_mode((700, 700))
x = 50
y = 50
circle = pygame.draw.circle(screen, color, (x, y), 25)
bounds = pygame.Rect(0, 0, 700, 700)

while work:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            work = False
    
    press = pygame.key.get_pressed()
    if press[pygame.K_UP]:
        y -= 20
    if press[pygame.K_DOWN]:
        y += 20
    if press[pygame.K_LEFT]:
        x -= 20
    if press[pygame.K_RIGHT]:
        x += 20
    
    circle_rect = pygame.Rect(x - 25, y - 25, 25 * 2, 25 * 2)
    circle_rect.clamp_ip(bounds)
    x, y = circle_rect.center
    
    screen.fill((0,0,0))
    pygame.draw.circle(screen, color, (x, y), 25)

    pygame.display.flip()
    cl.tick(60)