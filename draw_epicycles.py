from os import environ
import sys
import time
environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame 
from pygame import gfxdraw
import config as cfg 
import numpy as np
import matplotlib.pyplot as plt

BLACK, WHITE, RED, GREEN, BLUE = (0,0,0), (255,255,255), (255,0,0), (0,128,0), (0,0,255)
WIDTH, HEIGHT = 1280, 720
FPS = 60

class Screen:
    def __init__(self):
        self.display = pygame.display.set_mode((WIDTH,HEIGHT),0,5)
        self.frame_count = 0
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.fps = FPS

    def update(self):
        self.check_quit()
        self.frame_count += 1
        self.clock.tick(FPS)
        if self.dt != 0 and self.frame_count % 10 == 0:
            self.fps = 1/self.dt
        self.print_fps()
        pygame.display.update()


    def print_fps(self):
        self.font = pygame.font.SysFont("Verdana", 20)
        self.text = self.font.render(str(round(self.fps))+" FPS", True, WHITE)
        self.display.blit(self.text, (WIDTH/30, HEIGHT/25))

    def check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


class Epicycle:
    def __init__(self,r,phi,w,speed,points):
        self.t = 0
        self.speed = speed
        self.r = r
        self.phi = phi
        self.w = w


        self.points = points
        self.end_positions = []
        self.n = len(self.r)

    def update(self,dt):
        self.t += dt * self.speed
        self.x = self.r * np.cos(self.w * self.t + self.phi)
        self.y = self.r * np.sin(self.w * self.t + self.phi)

    def draw_circle(self, display, x, y, radius, color,filled):
        if filled:
            gfxdraw.aacircle(display, round(x), round(y), round(radius), color)
            gfxdraw.filled_circle(display, round(x), round(y), round(radius), color)
        else:
            gfxdraw.aacircle(display, round(x), round(y), round(radius), color)
    
        #gfxdraw.filled_circle(display, round(x), round(y), round(radius), color)

    def draw(self,display,frame_count,N):


        for p in self.points:
            self.draw_circle(display,p[0]+WIDTH/2,-p[1]+HEIGHT/2,5,WHITE,True)

        self.x_screen = WIDTH/2
        self.y_screen = HEIGHT/2
        self.draw_circle(display,self.x_screen,self.y_screen,3,WHITE,True)
        previous_x = WIDTH/2
        previous_y = HEIGHT/2
        for i in range(N):
            self.x_screen += self.x[i]
            self.y_screen -= self.y[i]
            if i < self.n - 1:
                self.draw_circle(display,self.x_screen,self.y_screen,self.r[i+1],(80,80,80),False)

            self.draw_circle(display,self.x_screen,self.y_screen,1,WHITE,True)
            
            pygame.draw.aaline(display,RED,(self.x_screen,self.y_screen),(previous_x,previous_y))
            previous_x = self.x_screen
            previous_y = self.y_screen

        self.end_positions.append((self.x_screen,self.y_screen))

        if frame_count > 2:
            pygame.draw.aalines(display,WHITE,False,self.end_positions)




def transform_points(points):
    N = len(points)
    z = np.zeros(N,complex)
    x = np.zeros(N,complex)
    r = np.zeros(N,float)
    w = np.zeros(N,float)
    phi = np.zeros(N,float)

    for i,p_i in enumerate(points):
        z[i]=complex(p_i[0],p_i[1])

    # x = np.fft.fft(z,norm="forward")
    
    # by hand:
    m = int(N/2)
    for k in range(N):
        x_k = 0
        for n in range(-m,m):
            w_kn = (k-m)*2*np.pi*n/N
            x_k += 1/N*z[n+m]*np.exp(-w_kn*1j)
        x[k] = x_k

    r = np.absolute(x)
    phi = np.angle(x)
    w = np.array([2*i*np.pi/N for i in range(-m,m)])


    
    phi_sorted = np.array([x for _, x in sorted(zip(r, phi),reverse=True)])
    w_sorted = np.array([x for _, x in sorted(zip(r, w),reverse=True)])
    r_sorted = sorted(r,reverse=True)
    
    return r_sorted,w_sorted,phi_sorted




def main():
    print("Computing DFT:")
    #points = [[50,100],[50,0],[25,25],[-25,10],[-50,55],[-50,125],[0,100]]
    points=150*np.array([(2, 2), (2, 3/2), (2, 1), (2, 1/2), (2, 0), (2, -1/2), (2, -1), (2, -3/2), (2, -2), (3/2, -2), (1, -2), (1/2, -2), (0, -2), (-1/2, -2), (-1, -2), (-3/2, -2), (-2, -2), (-2, -3/2), (-2, -1), (-2, -1/2), (-2, 0), (-2, 1/2), (-2, 1), (-2, 3/2), (-2, 2), (-3/2, 2), (-1, 2), (-1/2, 2), (0, 2), (1/2, 2), (1, 2), (3/2, 2)])
    #points = points[::-1]
    r,w,phi = transform_points(points)

    print("Displaying...")
    pygame.init()
    screen = Screen()
    speed = 0.5
    N = 4
    
    epicycle = Epicycle(r=r, phi=phi, w=w, speed=speed, points=points)
    previous_time = time.time()

    while True:
        screen.dt = time.time() - previous_time
        previous_time = time.time()
        screen.display.fill(BLACK)
        epicycle.update(screen.dt)
        epicycle.draw(display=screen.display,frame_count=screen.frame_count,N=N)
        screen.update()


main()