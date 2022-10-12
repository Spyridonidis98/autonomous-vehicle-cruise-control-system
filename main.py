import matlab
import matlab.engine
import glob
import sys

from carla_lib import World, KeyboardControl, ClientSideBoundingBoxes
import carla
import cv2
import numpy as np
from time import sleep
import copy
import random
import matlab
import matlab.engine
import csv


# #open/create file
# f1 = open('car_target_speed.csv', 'w')
# f2 = open('car_speed.csv', 'w')
# f3 = open('car_throttle.csv', 'w')
# # create the csv writer
# csv_target_speed = csv.writer(f1)
# csv_car_speed = csv.writer(f2)
# csv_car_throttle = csv.writer(f3)


# ==============================================================================
# -- ClientSideWaypoints ---------------------------------------------------
# ==============================================================================
class ClientSideWaypoints(object):  
    """This is a module responsible for drawing waypoints from a camera perspective on pygame surface.
    """
    BB_COLOR = (27, 64, 94)
    VIEW_WIDTH = None
    VIEW_HEIGHT = None

    @classmethod 
    def get_waypoints(cls, waypoints, camera):
        """
        get waypoints uv cordinates from world cordinates
        """
        cls.VIEW_WIDTH = int(camera.attributes["image_size_x"])
        cls.VIEW_HEIGHT = int(camera.attributes["image_size_y"])
        waypoints_uv = [ClientSideWaypoints.get_waypoint(waypoint, camera) for waypoint in waypoints]

        return waypoints_uv
    
    @staticmethod
    def get_waypoint(waypoint, camera):
        loc = waypoint.transform.location
        cords = np.transpose(np.matrix([loc.x, loc.y, loc.z, 1]))

        cords_x_y_z = ClientSideBoundingBoxes._world_to_sensor(cords, camera)
        #cordinates relative to the camera 
        cords_y_minus_z_x = np.concatenate([cords_x_y_z[1, :], -cords_x_y_z[2, :], cords_x_y_z[0, :]])
        bbox = np.transpose(np.dot(camera.calibration, cords_y_minus_z_x))
        camera_bbox = np.concatenate([bbox[:, 0] / bbox[:, 2], bbox[:, 1] / bbox[:, 2], bbox[:, 2]], axis=1)
        return camera_bbox

    @classmethod
    def draw_waypoints(cls, display, waypoints_uv, render_pos):
        wp_surface = pygame.Surface((cls.VIEW_WIDTH, cls.VIEW_HEIGHT))
        wp_surface.set_colorkey((0, 0, 0))

        target_waypoint_color = (255, 0, 0)
        wp = waypoints_uv[0]
        c  = (wp[0, 0], wp[0, 1])
        pygame.draw.circle(wp_surface, target_waypoint_color, c, 5)

        for wp in waypoints_uv[1:]:
            c  = (wp[0, 0], wp[0, 1])
            pygame.draw.circle(wp_surface, cls.BB_COLOR, c, 5)
        

        display.blit(wp_surface, render_pos)

# ==============================================================================
# -- VehicleController ---------------------------------------------------
# ==============================================================================
class VehicleController(object):
    def __init__(self, world, waypoints):
        self.world = world
        self.control = carla.VehicleControl()
        self.waypoints = waypoints
        self.target = waypoints[0].transform.location
        self.reverse = False
        self.simulation_time_step = self.world.world.get_settings().fixed_delta_seconds
        self.control.manual_gear_shift = True
        self.control.gear = 3 #max speed 70 km/h
        self.control.brake = 0.0
        self.control.throttle = 0.2
        self.world.vehicle.apply_control(self.control)
        self.controller = KeyboardControl(world)
        self.eng = matlab.engine.start_matlab()
        self.fis_theta_tuner = self.eng.readfis("fis_theta_tuner")
        self.fis_steering = self.eng.readfis("fis_steering")
        self.fis_speed = self.eng.readfis("fis_speed_optimized")
        self.fis_max_turn_speed = self.eng.readfis("fis_max_turn_speed")
        self.target_speed = 50 #km/h
        self.speed_error = 50
        self.speed_error_prev = self.target_speed
        self.speed_error_integral = self.speed_error * self.simulation_time_step


    @staticmethod
    def distance_from_waypoints_line(waypoint, location):
        #returns positive distance if the point is left of the line
        x0 = waypoint.transform.location.x
        y0 = waypoint.transform.location.y
        f = waypoint.transform.rotation.yaw
        if f>180 :
            f-=360
        if f<-180:
            f+=360
        cos = np.cos(f*np.pi/180)
        sin = np.sin(f*np.pi/180)
        if f >= 0:
            c =1
        else:
            c = -1
        if cos==0:
            b = 0
            xb = x0
            if xb < 0:
                c *= 1
            if xb > 0:
                c *= -1
            a = -c/xb
        elif sin==0:
            a = 0
            yc = y0
            if yc < 0 :
                c *= -1
            if yc > 0 :
                c *= 1
            b = -c/yc
        else:
            xb = x0 - y0 * (cos/sin)
            if xb<0:
                c *= 1
            if xb>0:
                c *=-1
            a = -c/xb
            yc = y0 - x0 * (sin/cos)
            b = -c/yc

        dist = (a*location.x+b*location.y+c)/np.sqrt(a*a+b*b)
        return dist
    
    def curvature_of_trajectory(self, waypoints):
        """calculates the rate of change if in the direction of the car respect to distance from on waypoint to other"""
        point_to_look_ahead = 15
        if len(waypoints)<point_to_look_ahead:
            return 0

        max_k = 0 
        for i in range(point_to_look_ahead-1):
            yaw = waypoints[i].transform.rotation.yaw 
            if yaw > 180:
                yaw-=360
            if yaw < -180:
                yaw+=360
            yaw_next = waypoints[i+1].transform.rotation.yaw
            if yaw_next > 180:
                yaw_next-=360
            if yaw_next < - 180:
                yaw_next+=360

            res = yaw_next-yaw
            if res < -180:
                res+=360
            if res >180:
                res-=360

            k = abs(res)/( waypoints[i].transform.location.distance( waypoints[i+1].transform.location ) )
            if k > max_k:
                max_k = k

        return max_k


    def apply_controll(self):
        if len(self.waypoints)==0:
            self.control.throttle = 0       
            self.control.steer = 0
            self.control.brake = 1
            self.world.vehicle.apply_control(self.control)
        else:
            #get simulation data
            vehicle_position = self.world.vehicle.get_transform().location
            vehicle_rotation = self.world.vehicle.get_transform().rotation.yaw
            vehicle_speed = self.world.vehicle.get_velocity()
            vehicle_speed = np.linalg.norm([vehicle_speed.x, vehicle_speed.y])*3.6 # km/h
            vehicle_acceleration = self.world.vehicle.get_acceleration()
            
            #check if target reached
            dist_from_target = vehicle_position.distance(self.target)
            if dist_from_target < 1:
                self.waypoints.pop(0)
                if len(self.waypoints) !=0:
                    self.target = self.waypoints[0].transform.location
            if len(self.waypoints)==0:
                return

            #apply controller
            v = np.array([self.target.x - vehicle_position.x   , self.target.y - vehicle_position.y ])#normal from car to target
            v = v / np.linalg.norm(v)
            vf = np.arctan2(v[1], v[0])*180/np.pi
            f = vf - vehicle_rotation
            th = self.waypoints[0].transform.rotation.yaw - vehicle_rotation
            if th > 180:
                th-=360
            if th < -180:
                th+=360
            

            dist = self.distance_from_waypoints_line(self.waypoints[0], vehicle_position)
            max_k = self.curvature_of_trajectory(self.waypoints)
            max_speed = self.eng.evalfis(self.fis_max_turn_speed, matlab.double([max_k]))
            if self.target_speed > max_speed :
                allowed_target_speed = max_speed
            else:
                allowed_target_speed = self.target_speed

            self.speed_error = (allowed_target_speed - vehicle_speed)
            self.speed_error_dot = (self.speed_error - self.speed_error_prev)/self.simulation_time_step
            self.speed_error_prev = self.speed_error
            self.speed_error_integral += self.speed_error * self.simulation_time_step

            theta_minus = self.eng.evalfis(self.fis_theta_tuner, matlab.double([dist]))
            th += theta_minus
            self.control.steer = self.eng.evalfis(self.fis_steering, matlab.double([th]))
            throttle_dot = self.eng.evalfis(self.fis_speed, matlab.double([self.speed_error, self.speed_error_dot, self.speed_error_integral]))
            self.control.throttle += throttle_dot * self.simulation_time_step
            self.control.throttle = max(min(1, self.control.throttle),0)
            self.world.vehicle.apply_control(self.control)
            #save speed data 
            # row = np.array([vehicle_speed])
            # csv_car_speed.writerow(row)
            # row = np.array([allowed_target_speed])
            # csv_target_speed.writerow(row)
            # row = np.array([self.control.throttle])
            # csv_car_throttle.writerow(row)
            
            print("car_speed = " + str(round(vehicle_speed, 3)) + " km/h " + "target_speed = " + str(round(allowed_target_speed, 2)))
            
            
#params
width = 1280
height = 720

# pygame 
import pygame
world = None

# create the csv writer
try:
    #pygame setup 
    pygame.init()
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((width,height))
    pygame.display.set_caption("game")

    #connect to server 
    client = carla.Client("localhost", 2000)
    client.set_timeout(6.0)
    
    #get world
    world = World(client.load_world('Town03'))
    
    #spawn car
    world.spawn_ego_car(22)
    #world.vehicle.set_autopilot(True)
    
    #spawn camera
    box = world.vehicle.bounding_box
    camera_spawn_point = carla.Transform(carla.Location(x= box.location.x , y= box.location.y , z=box.location.z + 35), carla.Rotation(-90, 0, 0))
    camera_spawn_point2 = carla.Transform(carla.Location(x= box.location.x , y= box.location.y + 10 , z=box.location.z + 10), carla.Rotation(-45, -90, 0))
    world.spawn_camera(camera_spawn_point, (0, 0), (640*2, 360*2), attach_to=world.vehicle, type=0)
    #world.spawn_camera(camera_spawn_point2, (640, 0), (640, 360), attach_to=world.vehicle, type=0)
    car_start_transform  = world.world.get_map().get_spawn_points()[2]
    car_start_transform.location.x += 50
    car_start_transform.location.y += 2.5
    world.vehicle.set_transform(car_start_transform)

    #get waypoint
    waypoint = world.world.get_map().get_waypoint(car_start_transform.location)
    waypoints = []
    wp_dist = 5
    wp_number =98
    for i in range(wp_number):
        waypoint = waypoint.next(wp_dist)[0]
        waypoints.append(waypoint)

    #get vehicle controler
    controller = VehicleController(world, waypoints)
    target_reached = False
    while True:
        #check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Choose the next waypoint and update the car location.
        #waypoint = random.choice(waypoint.next(2.5))
        #world.vehicle.set_transform(waypoint.transform)
        
        controller.apply_controll()
        if len(waypoints) == 0 and not target_reached:
            target_reached = True
            print("destination reached !!!")

        world.world.tick()
        clock.tick(10)
        #print(clock.get_fps())

        display.fill((0, 0, 0))
        world.render(display)
        bounding_boxes = ClientSideBoundingBoxes.get_3d_bounding_boxes(world.actor_list, world.sensor_list[0].sensor)
        ClientSideBoundingBoxes.draw_3d_bounding_boxes(display, bounding_boxes, (0, 0))
        if len(waypoints) != 0:
            wp_uv = ClientSideWaypoints.get_waypoints(waypoints[:20] , world.sensor_list[0].sensor)
            ClientSideWaypoints.draw_waypoints(display, wp_uv, (0, 0))
            #wp_uv = ClientSideWaypoints.get_waypoints(waypoints , world.sensor_list[1].sensor)
            #ClientSideWaypoints.draw_waypoints(display, wp_uv, (640, 0))
        pygame.display.update()
                
        
finally:
    if world is not None:
        world.destory_actors()
    print("done")
    # close the file
    # f1.close()
    # f2.close()
    # f3.close()