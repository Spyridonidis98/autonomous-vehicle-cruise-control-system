# Autonomous Vehicle Cruise Control System 
https://user-images.githubusercontent.com/79518257/195386371-1e43b4f6-a1fb-4b35-9d98-3302cca43a3a.mp4

To be able to run the code you must have matlab engine for python installed with some matlab labraries like fuzzy logic toolbox, global optimization toolbox. Is justed to use python 3.8 which is compatible both with carla and matlab engine 

We build the controller using fuzzy systems, we train a neural network to aproximate the behavior of the car which is a discrete dynamical system, using this network which now represents our car. We optimize our controller using genetic algorithm optimization in matlab. The time step between each frame is set to 0.1, and the system uses only the first gear of the car.


# Steering controller 
![Untitled](https://user-images.githubusercontent.com/79518257/195391776-f883b568-5f24-487b-96ee-56d10bbecbfb.png)

# Speed controller 
![Untitled2](https://user-images.githubusercontent.com/79518257/195391789-6e1fb61a-c163-47e8-8666-3c4b2a164247.png)

# Neural Network Response

Not Optimized &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;  Optimized
![Untitled3](https://user-images.githubusercontent.com/79518257/195392981-e68b6c92-35a7-46db-8c1f-c70b436140ed.png)

# Real System Responce 
Not Optimized &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;  Optimized
![Untitled](https://user-images.githubusercontent.com/79518257/195410670-8abf6094-1c6b-4a73-a849-e95b55abee65.png)
In Blue is the target Speed and Red the Speed of the Car and Green the Throttle 

