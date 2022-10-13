# Autonomous Vehicle Cruise Control System 
https://user-images.githubusercontent.com/79518257/195386371-1e43b4f6-a1fb-4b35-9d98-3302cca43a3a.mp4

To be able to run the code you must have matlab engine for python installed with some matlab labraries like fuzzy logic toolbox, global optimization toolbox. It is recommened to use python 3.8 which is compatible with both carla and matlab engine.

We build the controller using fuzzy systems, we train a neural network to aproximate the behavior of the car which is a discrete dynamical system, the data for the neural network was collected by driving the car in carla using a ps4 controller.Using this network which now represents our car we optimize our controller using genetic algorithm optimization in matlab. The time step of the world between each frame is set to 0.1 sec, and the system uses only the first gear of the car. The model that is used is tesla model 3, if you want to create a controller that is optimized for another car you can collect data by connecting a ps4 controller and running the collect_data.py file.

# Steering controller 
![Untitled](https://user-images.githubusercontent.com/79518257/195391776-f883b568-5f24-487b-96ee-56d10bbecbfb.png)

# Speed controller 
![Untitled2](https://user-images.githubusercontent.com/79518257/195391789-6e1fb61a-c163-47e8-8666-3c4b2a164247.png)

# Neural Network 

![Untitled Diagram](https://user-images.githubusercontent.com/79518257/195580752-23a492f8-cefe-4e49-9899-502a4169b6d1.png)

# Neural Network Response
How our controler performs with the neural network that suppose to aproximate our car before and after optimization.

Not Optimized &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;  Optimized on neural network
![Untitled3](https://user-images.githubusercontent.com/79518257/195392981-e68b6c92-35a7-46db-8c1f-c70b436140ed.png)

# Real System Responce 
How our controler performs with the actual car in carla 

Not Optimized &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;  Optimized on neural network
![Untitled](https://user-images.githubusercontent.com/79518257/195410670-8abf6094-1c6b-4a73-a849-e95b55abee65.png)
In Blue is the target Speed and Red the Speed of the Car and Green the Throttle.

# Conclusion 
The neural network was a very good aproximation of our physical system, as we can see in the graph, the system that was optimized using the neural network was able to achive simiral results in the actual phusical system.

