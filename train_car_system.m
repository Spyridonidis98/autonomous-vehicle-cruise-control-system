data = csvread('car_system.csv');
data = data';
%data is 4 rows [throttle_n , steering_n, speed_n, speed_n+1]  

n = 2;
train_input = data(1:end-1 , 1:end-n);
for i=1:n
    train_input(end+1:end+3, :) = data(1:end-1 , 1+i:end-n+i);
end
%train_input is 9 rows [throttle_n-2, steering_n-2, speed_n-2, throttle_n-1, steering_n-1, speed_n-1, throttle_n, steering_n, speed_n]  
%due to the nature of the model you need data from more than one previous moments to be predict the next one, in this case we found 
% that using 3 gets good results 

train_target = data(end, 1+n:end);
car_system_net = feedforwardnet([25, 25], 'trainlm');
car_system_net = train(car_system_net , train_input, train_target);

save car_system_net;


