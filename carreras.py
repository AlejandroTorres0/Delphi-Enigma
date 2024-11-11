import pygame
import sys
import math
import random 
import styles as s

width = 640
height = 640

lane_marker_move_y = 0
road_width = 400
marker_width = 10
marker_height = 50

# road and edge markers
road = (120, 0, road_width, height)
borde_izquierdo = (115, 0, marker_width, height) 
borde_derecho = (road_width + 120, 0, marker_width, height)

rect_borde_izq = pygame.Rect(borde_izquierdo) #Hago que los bordes de la calle sean rectángulos para poder usar colliderect() y detectar si se choca contra ellos
rect_borde_der = pygame.Rect(borde_derecho)

score = 0

class Vehiculo(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect() #Obtiene las coordenadas del rectángulo del vehiculo
        self.rect.center = [x, y]

class Vehiculo_Jugador(Vehiculo):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png') #Se carga el sprite del jugador
        image = pygame.transform.scale(image, (45, 90))
        self.ángulo = 0    #Solamente el PlayerVehicle tiene ángulo
        super().__init__(image, x, y) #Intancia PlayerVehicle con el constructor de Vehicle (su clase padre)

def dibujar_fondo(screen):
            # for animating movement of the lane markers
            global lane_marker_move_y 
            global marker_height, marker_height
            global borde_derecho, borde_izquierdo
            #global marker_width

            # Draw the grass
            screen.fill(s.VERDE)

            # draw the road
            pygame.draw.rect(screen, s.GRIS, road)
        
            # draw the edge markers
            pygame.draw.rect(screen, s.AMARILLO, borde_izquierdo)
            pygame.draw.rect(screen, s.AMARILLO, borde_derecho)


            # draw the lane markers
            lane_marker_move_y += 5 * 2 #* 2
            if lane_marker_move_y >= marker_height * 2:
                lane_marker_move_y = 0
            for y in range(marker_height * -2, height, marker_height * 2):
                pygame.draw.rect(screen, s.BLANCO, (180 + 45, y + lane_marker_move_y, marker_width, marker_height))
                pygame.draw.rect(screen, s.BLANCO, (340 + 45, y + lane_marker_move_y, marker_width, marker_height))

def crear_vehiculos(vehicle_group):
    # load the vehicle images
    image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
    vehicle_images = []
    for image_filename in image_filenames:
        image = pygame.image.load('images/' + image_filename)
        vehicle_images.append(image)

    # add a vehicle
    if len(vehicle_group) < 2:
        # ensure there's enough gap between vehicles
        add_vehicle = True
        for vehiculo in vehicle_group:
            if vehiculo.rect.top < vehiculo.rect.height * 1.5:
                add_vehicle = False
                    
        if add_vehicle:
            # select a random lane
            lane = random.choice(range(165, 470))
                
            # select a random vehicle image
            image = random.choice(vehicle_images)
            vehiculo = Vehiculo(image, lane, height / -2) #Instancia un vehiculo cualquiera
            vehicle_group.add(vehiculo)

def mover_vehiculos(vehicle_group):
    global score
    speed = 5 
    #Hace que los vehiculos se muevan
    for vehiculo in vehicle_group:
        vehiculo.rect.y += speed
            
        #Remueve un vehiculo cada vez que sale de la pantalla
        if vehiculo.rect.top >= height:
            vehiculo.kill()
                
            # add to score
            score += 1
                
            #Aumenta la velocidad despues de cada vehiculo
        if score > 0:
            speed += 3

def game_loop(screen):
    player_x = 320
    player_y = 500
    player = Vehiculo_Jugador(player_x, player_y) #Se instancia el auto del jugador
    
    vehicle_group = pygame.sprite.Group()

    crash = pygame.image.load('images/crash.png')
    crash_rect = crash.get_rect()
    
    clock = pygame.time.Clock()
    
    global rect_borde_izq
    global rect_borde_der
    global score
    
    # Frame settings
    fps = 60
    
    #Game settings
    speed = 5  
    gameover = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            player.ángulo += 3  # Rota hacia la izquierda
        if teclas[pygame.K_RIGHT]:
            player.ángulo -= 3  #Rota hacia la derecha
        if teclas[pygame.K_UP]: #Mueve al jugador en la dirección en la que está mirando
            player.rect.x -= int(speed * math.sin(math.radians(player.ángulo)))
        if teclas[pygame.K_DOWN]: 
            player.rect.x -= int(speed * math.sin(math.radians(player.ángulo)))

        #Se bloquea el ángulo del auto en 70 o -70
        if player.ángulo > 70: 
            player.ángulo = 70
        elif player.ángulo < -70:
            player.ángulo = -70
        
        crear_vehiculos(vehicle_group)

        #Detecta si hay una colisión al costado del auto
        for vehiculo in vehicle_group:
            if pygame.sprite.collide_rect(player, vehiculo):  
                gameover = True
                    # place the player's car next to other vehicle
                    # and determine where to position the crash image
                if event.key == teclas[pygame.K_LEFT]:
                    player.rect.left = vehiculo.rect.right
                    crash_rect.center = [player.rect.left, (player.rect.center[1] + vehiculo.rect.center[1]) / 2]
                elif event.key == teclas[pygame.K_RIGHT]:
                    player.rect.right = vehiculo.rect.left
                    crash_rect.center = [player.rect.right, (player.rect.center[1] + vehiculo.rect.center[1]) / 2]
        
        #Rota la imagen del auto del jugador
        rotated_image = pygame.transform.rotate(player.image, player.ángulo)
        rotated_rect = rotated_image.get_rect(center=player.rect.center)

        #Detecta si el auto chocó con los bordes de la calle
        if rotated_rect.colliderect(rect_borde_izq): 
            gameover = True
            crash_rect.center = [player.rect.left, player.rect.center[1]]
        if rotated_rect.colliderect(rect_borde_der):
            gameover = True
            crash_rect.center = [player.rect.right, player.rect.center[1]]
        
        #Mueve los vehiculos 
        mover_vehiculos(vehicle_group)

        #Dibuja la calle, los marcadores de calle (los rectangulos blancos), y los bordes
        dibujar_fondo(screen) 
        
        #Dibuja los vehiculos
        vehicle_group.draw(screen)
        
        #Dibuja la imagen del auto del jugador rotada 
        screen.blit(rotated_image, rotated_rect.topleft)

        #Checkea colisiones de frente
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]

        #Muestra el score, no importa mucho su ubicación en el código, podría ser una función también
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Score: ' + str(score) + '/20', True, s.BLANCO)
        text_rect = text.get_rect()
        text_rect.center = (50, 400)
        screen.blit(text, text_rect)

        #Muestra el mensaje de gameover 
        if gameover:
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, s.ROJO, (0, 50, width, 100))
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render('Game over. (Escribe ENTER para continuar)', True, s.BLANCO)
            text_rect = text.get_rect()
            text_rect.center = (width / 2, 100)
            screen.blit(text, text_rect)
            score = 0  #Reinicia el score
            speed = 0 #Reinicia la velocidad
        pygame.display.update()


        #Espera hasta que el usuario presione ENTER
        while gameover:
            clock.tick(fps)      
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameover = False
                    running = False
                    
                #Obtiene la input del usuario cuando pierde (s o n)
                if event.type == pygame.KEYDOWN: #Detecta que el usuario presiono algo
                    if event.key == pygame.K_RETURN: 
                        # exit the loops
                        gameover = False
                        running = False

              
        pygame.display.flip()  #Update the display
        clock.tick(fps)  #Limit to 60 FPS
    #pygame.quit() 

    return score

def main(): 
    global gameover
    ANCHO = 640
    ALTO = 640
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption('Minijuego de Carreras')
        
    while True:
        score = game_loop(screen)

        if score >= 20: 
            resultado = "WIN"
            break
        else: 
            resultado = "LOSE"
            break
    
    return resultado
        # Here you can handle the score, show it in the menu, etc.
if __name__ == "__main__": 
    main()