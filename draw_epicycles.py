from os import environ,path
import sys
import time
environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame 
from pygame import gfxdraw
import config as cfg 
import numpy as np
import matplotlib.pyplot as plt
from import_png import import_points_from_png

BLACK, WHITE, RED, GREEN, BLUE = (0,0,0), (255,255,255), (255,0,0), (0,128,0), (0,0,255)
GRAY = (58,58,56)
TEAL = (25,153,141)
DARKTEAL = (8,139,129)
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
        #self.check_quit()
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
    def __init__(self,r,phi,w,speed,points,N):
        self.t = 0
        self.speed = speed
        self.r = r
        self.phi = phi
        self.w = w

        self.x = self.r * np.cos(self.w * self.t + self.phi)
        self.y = self.r * np.sin(self.w * self.t + self.phi)
        
        self.points = points
        self.end_positions = []
        self.contour_index = 0
        self.end_positions_shifted = []
        self.n = len(self.r)
        self.N = N

    def update(self,dt):

        self.t += dt * self.speed


        self.x = self.r * np.cos(self.w * self.t + self.phi)
        self.y = self.r * np.sin(self.w * self.t + self.phi) 

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    self.N = self.n
                    self.end_positions = []
                    self.end_positions_shifted = []
                elif event.key == pygame.K_1:
                    self.N = 1
                    self.end_positions = []
                    self.end_positions_shifted = []

                elif event.key == pygame.K_UP:
                    self.N += 1
                    self.end_positions = []
                    self.end_positions_shifted = []

                elif event.key == pygame.K_w:
                    self.N += 10
                    self.end_positions = []
                    self.end_positions_shifted = []
                elif event.key == pygame.K_DOWN:
                    self.N -= 1
                    self.end_positions = []
                    self.end_positions_shifted = []

                elif event.key == pygame.K_s:
                    self.N -= 10
                    self.end_positions = []
                    self.end_positions_shifted = []
                
                elif event.key == pygame.K_PLUS:
                    self.speed += 20


                elif event.key == pygame.K_MINUS:
                    self.speed -= 20
     

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def draw_circle(self, display, x, y, radius, color,filled):
        if filled:
            gfxdraw.aacircle(display, round(x), round(y), round(radius), color)
            gfxdraw.filled_circle(display, round(x), round(y), round(radius), color)
        else:
            gfxdraw.aacircle(display, round(x), round(y), round(radius), color)
    

    def draw(self,display,frame_count):

        # for p in self.points:
        #    self.draw_circle(display,p[0]+WIDTH/2,-p[1]+HEIGHT/2,1,WHITE,True)

        self.x_screen = WIDTH/2
        self.y_screen = HEIGHT/2
        self.draw_circle(display,self.x_screen,self.y_screen,3,WHITE,True)
        previous_x = WIDTH/2
        previous_y = HEIGHT/2

        
        if self.N <= self.n:
            M = self.N
        else:
            M = self.n
        for i in range(M):
            self.x_screen += self.x[i]
            self.y_screen -= self.y[i]
            if i < 20:
                
                self.draw_circle(display,self.x_screen,self.y_screen,self.r[i+1],(255,255,255,20),False)

            if i<20:
                self.draw_circle(display,self.x_screen,self.y_screen,1,WHITE,True)
            
            pygame.draw.aaline(display,RED,(self.x_screen,self.y_screen),(previous_x,previous_y))
            previous_x = self.x_screen
            previous_y = self.y_screen

        self.end_positions.append((self.x_screen,self.y_screen))
        self.end_positions_shifted.append((self.x_screen+1,self.y_screen))

        if len(self.end_positions) > 2:
            pygame.draw.aalines(display,TEAL,False,self.end_positions)
            pygame.draw.aalines(display,TEAL,False,self.end_positions_shifted)



            




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


def get_fourier_coeffs(name,points,recompute_fourier=False):

    filename = f"data/{name}.txt"

    if path.isfile(filename) == False or recompute_fourier == True:
        r,w,phi = transform_points(points)
        with open(filename, "w") as file:
            file.write("#r w phi\n")
            for (r_i, w_i, phi_i) in zip(r, w, phi):
                file.write(f"{r_i} {w_i} {phi_i}\n")

    else:       
        data = np.genfromtxt(filename,skip_header=1)
        r,w,phi = data[:,0],data[:,1],data[:,2]
        return r,w,phi
    

    return r,w,phi
    
    


def main():
    print("Computing DFT:")
    png_name = "algo"
    filename=f"pictures/{png_name}.png"
    recompute_fourier = False
    M = 0
    points = import_points_from_png(filename=filename,width=WIDTH,height=HEIGHT,M=M)
    r,w,phi = get_fourier_coeffs(png_name,points,recompute_fourier)


    print("Displaying...")
    pygame.init()
    screen = Screen()
    speed = 120
    N = len(points)
    
    epicycle = Epicycle(r=r, phi=phi, w=w, speed=speed, points=points,N=N)
    previous_time = time.time()

    while True:
        screen.dt = time.time() - previous_time
        previous_time = time.time()
        screen.display.fill(GRAY)
        epicycle.update(screen.dt)
        epicycle.draw(display=screen.display,frame_count=screen.frame_count)
        screen.update()


#settings: 
# algo.png - M=4000, speed=120
# panda.png - M=1000
main()