import pygame
pygame.init()

screen_x_max = 1000
screen_y_max = 1000

screen = pygame.display.set_mode([screen_x_max, screen_y_max])

screen_center_x = screen_x_max/2
screen_center_y = screen_y_max/2

game_start_x = screen_center_x
game_start_y = screen_y_max - 50

# simulation coordinates (require conversion to screen coordinates)
init_loc_x = 0
init_loc_y = 0

loc_x = init_loc_x
loc_y = init_loc_y

tick_move = 1

def screen_x(x):
    return game_start_x + x

def screen_y(y):
    return game_start_y - y


#------------------------------------------------------
import math
#------------------------------------------------------
# Rear (driving) wheel
# touch point
rx = 0
ry = 0

# Frame properties
frame_size = 80 # pixels

# Front wheel (this wheel is being pushed)
# touch point
fx = 0
fy = ry + frame_size

# velocity (pixel/time)
v = 1.6

steering_angle_limit = math.pi/2 - math.pi/10
#------------------------------------------------------
def frame_angle(rx, ry, fx, fy):
    # angle with regard to Y-axis of the plane
    nominator = (fy - ry)
    denominator = (fx - rx)
    if (denominator != 0):
        frame_angle = math.atan(nominator / denominator)
    else:
        frame_angle = math.pi / 2

    if (rx > fx):
        frame_angle -= math.pi

    return frame_angle
#------------------------------------------------------
rxt = []
ryt = []
rxt.append(rx)
ryt.append(ry)
fxt = []
fyt = []
fxt.append(fx)
fyt.append(fy)
steering_angle = 0

delta_t = 1
# angle increment when steering is applied
angle_delta = math.pi/500

def rad_to_deg(rads):
    return (rads/math.pi)*180

def relative_steering_angle(rad_steering):
    return rad_to_deg(rad_steering)

def distance(rx, ry, fx, fy):
    return math.sqrt(math.pow(fx - rx, 2) + math.pow(fy - ry, 2))

def draw_a_bicycle(rx, ry, fx, fy, frame_angle, steering_angle, color, screen):

    # rear wheel's touch point
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(screen_x(rx),screen_y(ry),5, 5), 2)
    # front wheel's touch point
    pygame.draw.rect(screen, (255,200,0), pygame.Rect(screen_x(fx),screen_y(fy),5, 5), 2)

    frame_size = distance(rx, ry, fx, fy)
    print(f"frame_size={frame_size}")
    wheel_size = 0.5*frame_size
    print(f"wheel_size={wheel_size}")

    # draw the front wheel
    fw_front_x = fx + wheel_size/2 * math.cos(frame_angle + steering_angle)
    fw_front_y = fy + wheel_size/2 * math.sin(frame_angle + steering_angle)
    print(f"fw_front=({fw_front_x}, {fw_front_y})")

    fw_rear_x = fx - wheel_size/2 * math.cos(frame_angle + steering_angle)
    fw_rear_y = fy - wheel_size/2 * math.sin(frame_angle + steering_angle)
    print(f"fw_rear=({fw_rear_x}, {fw_rear_y})")

    pygame.draw.line(screen, color, (screen_x(fw_rear_x), screen_y(fw_rear_y)),
                     (screen_x(fw_front_x), screen_y(fw_front_y)), 3)

    # draw the rear wheel
    rw_front_x = rx + wheel_size/2 * math.cos(frame_angle)
    rw_front_y = ry + wheel_size/2 * math.sin(frame_angle)

    rw_rear_x = rx - wheel_size/2 * math.cos(frame_angle)
    rw_rear_y = ry - wheel_size/2 * math.sin(frame_angle)

    pygame.draw.line(screen, color, (screen_x(rw_rear_x), screen_y(rw_rear_y)),
                     (screen_x(rw_front_x), screen_y(rw_front_y)), 3)

    # draw the frame
    pygame.draw.line(screen, (50,50,250), (screen_x(rx), screen_y(ry)),
                     (screen_x(fx), screen_y(fy)), 3)

running = True

while running:

    move_forward = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        move_forward = 1
    if keys[pygame.K_RIGHT]:
        if (steering_angle > -steering_angle_limit):
            steering_angle -= angle_delta
    if keys[pygame.K_LEFT]:
        if (steering_angle < steering_angle_limit):
            steering_angle += angle_delta

    fa = frame_angle(rx, ry, fx, fy)

    loc_x = loc_x
    if move_forward > 0:
        #print(f"frame_angle={fa}, cos={math.cos(fa)}, sin={math.sin(fa)}")

        # move the rear wheel forward in the direction of the frame
        rx = rx + (v * delta_t) * math.cos(fa)
        ry = ry + (v * delta_t) * math.sin(fa)


        # find the delta angle (alpha) b/w current and future frame positions
        sin_o = math.sin(math.pi - steering_angle) * (frame_size - v * delta_t) / frame_size
        o = math.asin(sin_o)
        alpha = steering_angle - o

        # rotate shifted front wheel touch point by this angle (alpha)
        fx_n = fx + (v * delta_t) * math.cos(fa)
        fy_n = fy + (v * delta_t) * math.sin(fa)

        fx_n = fx_n - rx
        fy_n = fy_n - ry
        fx_nt = fx_n * math.cos(alpha) - fy_n * math.sin(alpha)
        fy_nt = fx_n * math.sin(alpha) + fy_n * math.cos(alpha)
        fx = fx_nt + rx
        fy = fy_nt + ry

        # save both trails for re-draws
        rxt.append(rx)
        ryt.append(ry)
        fxt.append(fx)
        fyt.append(fy)

    screen.fill((255, 255, 255))

    # Analytics
    my_font = pygame.font.SysFont('Arial', 20)
    text_surface = my_font.render("Steering angle: {:.2f} (deg)".format(relative_steering_angle(steering_angle)),
                                  False, (0, 200, 0))
    screen.blit(text_surface, (10, screen_y_max - 100))
    text_surface = my_font.render("Frame angle: {:.2f} (deg)".format(relative_steering_angle(fa)), False, (0, 200, 0))
    screen.blit(text_surface, (10, screen_y_max - 50))

    # draw the tracks
    for i in range(len(rxt)):
        pygame.draw.rect(screen, (0,200,0), pygame.Rect(screen_x(rxt[i]),screen_y(ryt[i]),2, 2), 2)
        pygame.draw.rect(screen, (200,0,0),   pygame.Rect(screen_x(fxt[i]),screen_y(fyt[i]),2, 2), 2)

    bicycle_color = (10, 250, 10)
    draw_a_bicycle(rx, ry, fx, fy, fa, steering_angle, bicycle_color, screen)

    pygame.display.flip()
    pygame.time.wait(6)

pygame.quit()