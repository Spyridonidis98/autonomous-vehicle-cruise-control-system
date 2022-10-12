clc
%close all
warning('off','all')
pctRunOnAll warning('off', 'all');

load car_system_net;
fis_speed = readfis("fis_speed.fis");
target_speed = 50;
cost_fun = @(fis)cost_function(fis, car_system_net, target_speed);
plot_responce(fis_speed, car_system_net, 50, "fis_speed")

% %optimization
% %Good cost for this optimization is around 3.7e+04 
% %optimization time on AMD ryzen 2600 for 10 generations is 20 minutes 
disp("wait a little bit for the first result to show")
[in, out, rules] = getTunableSettings(fis_speed);
options = tunefisOptions('Method','ga');
options.MethodOptions.PopulationSize = 200;
options.MethodOptions.MaxGenerations = 30;
options.UseParallel = true;
fisout = tunefis(fis_speed, [in; out;], cost_fun, options);
plot_responce(fisout, car_system_net, 50, "fis_speed_optimized")

%add integrator to reduce the steady state error
%the reason why the integrator is added after optimization is because that way the optimization takes much less time
%manualy tune the integrators membership functions
fisout.Inputs(3) = fisvar([-200 200], "Name", "Speed_Error_integral");
fisout.Inputs(3).MembershipFunctions(1) = fismf("zmf", [-25 25], "Name", "N");
fisout.Inputs(3).MembershipFunctions(2) = fismf("smf", [-25 25], "Name", "P");

fisout.Outputs(1).MembershipFunctions(5) = fismf("gbellmf", [0.2 2 -0.5], "Name", "NI");
fisout.Outputs(1).MembershipFunctions(6) = fismf("gbellmf", [0.2 2 0.5], "Name", "PI");

rules = [0 0 1 5 1 1;
         0 0 2 6 1 1;];

fisout = addRule(fisout, rules);
plot_responce(fisout, car_system_net, 50, "fis_speed_optimized_with_integral")
%save
writeFIS(fisout, "fis_speed_optimized")

function plot_responce(fis, net, target_speed, name)
    figure("Name", name)
    hold on

    n=2;
    time = 50;
    plot([0 time/2], [target_speed target_speed], "b")
    plot([time/2 time], [20 20], "b")
    vehicle_speed_history = [];
    
    input = zeros(1, 3*(n+1)); %initial conditions
    dt = 0.1;
    throttle = 0;
    throttle_dot = 0;
    vehilcle_speed = 0;
    speed_error_prev = target_speed;
    speed_error = target_speed-vehilcle_speed;
    speed_error_dot = (speed_error- speed_error_prev)/dt;
    speed_error_integral = speed_error * dt ;
    for i = 1:time/dt
        if i>time*0.5/dt
            target_speed = 20;
        end
        if length(fis.Inputs) == 2
            throttle_dot = evalfis(fis, [speed_error, speed_error_dot]);
        else
            throttle_dot = evalfis(fis, [speed_error, speed_error_dot, speed_error_integral]);
        end 
        throttle = throttle + throttle_dot * 0.1;
        throttle = max(min(throttle, 1), 0);
        
        input(1:end) = [input(4:end) throttle 0 vehilcle_speed];
        
        vehilcle_speed = net(input');
        speed_error = target_speed-vehilcle_speed;
        speed_error_dot = (speed_error- speed_error_prev)/dt;
        speed_error_prev = speed_error;
        speed_error_integral = speed_error_integral + speed_error * dt ;
        vehicle_speed_history = [vehicle_speed_history vehilcle_speed];
        
    end
    plot((0:length(vehicle_speed_history)-1)*dt, vehicle_speed_history, "r");

end

function cost = cost_function(fis, net, target_speed)
    n = 2;
    cost = 0;
    time = 50;
    input = zeros(1, 3*(n+1)); %initial conditions
    dt = 0.1;
    throttle = 0;
    vehilcle_speed = 0;
    vehilcle_speed_prev = 0;
    speed_error_prev = target_speed;
    speed_error = target_speed-vehilcle_speed;
    speed_error_dot = (speed_error- speed_error_prev)/dt;
    speed_error_integral = speed_error * dt ;
    for i = 1:time/dt
        if i>time*0.5/dt
            target_speed = 20;
        end
        if length(fis.Inputs) == 2
            throttle_dot = evalfis(fis, [speed_error, speed_error_dot]);
        else
            throttle_dot = evalfis(fis, [speed_error, speed_error_dot, speed_error_integral]);
        end 
        throttle = throttle + throttle_dot * 0.1;
        throttle = max(min(throttle, 1), 0);
        
        input(1:end) = [input(4:end) throttle 0 vehilcle_speed];
        
        vehilcle_speed =net(input');
        vehilcle_speed_prev = vehilcle_speed;
        speed_error = target_speed-vehilcle_speed;
        speed_error_dot = (speed_error- speed_error_prev)/dt;
        speed_error_integral = speed_error_integral + speed_error * dt ;
        speed_error_prev = speed_error;
        cost = cost + speed_error * speed_error + 100 * throttle_dot * throttle_dot;
    end
    
end