%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%FIS theta tuner 
fis = mamfis("Name", "fis_theta_tuner");

%inputs 
fis.Inputs(1) = fisvar([-15 15], "Name", "Distance");
fis.Inputs(1).MembershipFunctions(1) = fismf("zmf", [-5 5], "Name", "Negative");
fis.Inputs(1).MembershipFunctions(2) = fismf("smf", [-5 5], "Name", "Positive");

%output
fis.Outputs(1) = fisvar([-180 180], "Name", "Theta_minus");%Theta - 90 degrees
fis.Outputs(1).MembershipFunctions(1) = fismf("gbellmf", [10 2 -90], "Name", "Negative");
fis.Outputs(1).MembershipFunctions(2) = fismf("gbellmf", [10 2 90], "Name", "Positive");


rules = [1 1 1 1;
         2 2 1 1;
         ];
     
fis = addRule(fis, rules);

%plot 
figure("Name","Theta Tuner")
subplot(2,2,1)
plotmf(fis, "input", 1)
subplot(2,2,3)
plotmf(fis, "output", 1)

subplot(2,2,4)
gensurf(fis)

%save
writeFIS(fis, "fis_theta_tuner")
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%FIS STEERING
fis = mamfis("Name", "fis_steering");

%inputs 
fis.Inputs(1) = fisvar([-180 180], "Name", "Theta");
fis.Inputs(1).MembershipFunctions(1) = fismf("zmf", [-60 60], "Name", "Negative");
fis.Inputs(1).MembershipFunctions(2) = fismf("smf", [-60 60], "Name", "Positive");


%output
fis.Outputs(1) = fisvar([-1.3 1.3], "Name", "Steering");
fis.Outputs(1).MembershipFunctions(1) = fismf("gbellmf", [0.2 2 -1], "Name", "Negative");
fis.Outputs(1).MembershipFunctions(2) = fismf("gbellmf", [0.2 2 1], "Name", "Positive");

%Rules
%Rule length must be m+n+2, where m is the number of inputs and n is the
%number of outputs,weight and rule (1 and, 2 or)  


rules = [%Theta
         1 1 1 1;
         2 2 1 1];
              
fis = addRule(fis, rules);

%plot 
figure("Name", "Steering")
subplot(2,2,1)
plotmf(fis, "input", 1)
subplot(2,2,2)
plotmf(fis, "output", 1)

%steering 
% opt = gensurfOptions;
% opt.OutputIndex = 1;
% opt.InputIndex = 1;

subplot(2,2,3)
gensurf(fis)
%save
writeFIS(fis, "fis_steering")