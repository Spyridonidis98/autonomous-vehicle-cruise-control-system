import glob
import sys

#sys.path.append('../carla_simulator/')

from carla_lib import World, KeyboardControl, ClientSideBoundingBoxes
import carla
import cv2
import numpy as np
from time import sleep
import csv
# ==============================================================================
# -- VehicleController ---------------------------------------------------
# ==============================================================================
class VehicleController(object):
    def __init__(self, world):
        self.world = world
        self.control = carla.VehicleControl()
        self.control.manual_gear_shift = True
        self.control.gear = 3 #max speed 70 km/h


    def apply_controll(self, controlls):
        self.control.throttle = controlls["R2"]
        self.control.steer = controlls["Joystick"]*0.5
        self.control.brake = controlls["L2"]
        self.world.vehicle.apply_control(self.control)
        

#params
width = 1280
height = 720

# pygame 
import pygame
world = None
#open/create file
f = open('car_system.csv', 'w')
# create the csv writer
csv_writer = csv.writer(f)
try:
    #pygame setup 
    pygame.init()
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((width,height))
    pygame.display.set_caption("game")

    #connect to server 
    client = carla.Client("localhost", 2000)
    client.set_timeout(4.0)
    
    #get world
    world = World(client.get_world())
    
    #spawn car
    world.spawn_ego_car(1)
    #world.vehicle.set_autopilot(True)
    
    #spawn camera
    box = world.vehicle.bounding_box
    camera_spawn_point = carla.Transform(carla.Location(x= box.location.x , y= box.location.y , z=box.location.z + 30), carla.Rotation(-90, 0, 0))
    camera_spawn_point2 = carla.Transform(carla.Location(x= box.location.x , y= box.location.y + 10 , z=box.location.z + 10), carla.Rotation(-45, -90, 0))
    world.spawn_camera(camera_spawn_point, (0, 0), (640*2, 360*2), attach_to=world.vehicle, type=0)
    #world.spawn_camera(camera_spawn_point2, (640, 0), (640, 360), attach_to=world.vehicle, type=0)
    car_start_transform  = world.world.get_map().get_spawn_points()[2]
    car_start_transform.location.x += 130
    car_start_transform.location.y += 2.5
    world.vehicle.set_transform(car_start_transform)
    #get vehicle controler
    controller = VehicleController(world)
   #Initialize controller
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i))
    for joystick in joysticks:
        joystick.init()
    controller_input = {"L2":0,"R2":0, "Joystick": 0}
    axis_data = {}

    while True:
        #check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.JOYAXISMOTION:
                axis_data[event.axis] = round(event.value,2)
                if 5 in axis_data:
                    controller_input["R2"] = round((axis_data[5]+1)/2.0, 2)

                if 4 in axis_data:
                    controller_input["L2"] = round((axis_data[4]+1)/2.0, 2)
                
                if 2 in axis_data:
                    controller_input["Joystick"] =  axis_data[2]
        #input data throttle, brake, vehicle_speed
        vehicle_speed_in = world.vehicle.get_velocity()
        vehicle_speed_in = np.linalg.norm([vehicle_speed_in.x, vehicle_speed_in.y])*3.6 # km/h
        controller.apply_controll(controller_input)
        
        world.world.tick()
        clock.tick(60)

        #output data vehicle_speed
        control = world.vehicle.get_control()
        vehicle_speed_out = world.vehicle.get_velocity()
        vehicle_speed_out = np.linalg.norm([vehicle_speed_out.x, vehicle_speed_out.y])*3.6 # km/h
        

        #save data
        row = np.array([control.throttle, control.steer, vehicle_speed_in, vehicle_speed_out])
        csv_writer.writerow(row)
        print(vehicle_speed_in)
        display.fill((0, 0, 0))
        world.render(display)
        
        
        pygame.display.update()
                
        
finally:
    if world is not None:
        world.destory_actors()
    # close the file
    f.close()
    print("done")