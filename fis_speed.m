%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%FIS max_turn_speed
fis = mamfis("Name", "fis_max_turn_speed");

%inputs 
fis.Inputs(1) = fisvar([0 50], "Name", "max_k");
fis.Inputs(1).MembershipFunctions(1) = fismf("zmf", [0 20], "Name", "Small");
fis.Inputs(1).MembershipFunctions(2) = fismf("smf", [0 20], "Name", "Big");

%output
fis.Outputs(1) = fisvar([0 70], "Name", "max_turn_speed");
fis.Outputs(1).MembershipFunctions(1) = fismf("gbellmf", [5 2 10], "Name", "Small");
fis.Outputs(1).MembershipFunctions(2) = fismf("gbellmf", [5 2 60], "Name", "Big");

rules = [1 2 1 1;
         2 1 1 1;];
     
fis = addRule(fis, rules);
%plot 
figure("Name","Max Turn Speed")
subplot(2,2,1)
plotmf(fis, "input", 1)
subplot(2,2,2)
plotmf(fis, "output", 1)
subplot(2,2,3)
opt = gensurfOptions;
opt.NumGridPoints = 50;
gensurf(fis, opt)
evalfis(fis, 14.9)
%save
writeFIS(fis, "fis_max_turn_speed")

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%FIS Speed
fis = mamfis("Name", "fis_speed");

%inputs 
fis.Inputs(1) = fisvar([-80 80], "Name", "Speed_Error");
fis.Inputs(1).MembershipFunctions(1) = fismf("zmf", [-20 20], "Name", "N");
fis.Inputs(1).MembershipFunctions(2) = fismf("smf", [-20 20], "Name", "P");

fis.Inputs(2) = fisvar([-80 80], "Name", "Speed_Error_dot");
fis.Inputs(2).MembershipFunctions(1) = fismf("zmf", [-15 15], "Name", "N");
fis.Inputs(2).MembershipFunctions(2) = fismf("smf", [-15 15], "Name", "P");

%output
fis.Outputs(1) = fisvar([-3.5 3.5], "Name", "Trottle_dot");
fis.Outputs(1).MembershipFunctions(1) = fismf("gbellmf", [0.2 2 -1.3], "Name", "NP");
fis.Outputs(1).MembershipFunctions(2) = fismf("gbellmf", [0.2 2 1.3], "Name", "PP");
fis.Outputs(1).MembershipFunctions(3) = fismf("gbellmf", [0.2 2  -0.3], "Name", "ND");
fis.Outputs(1).MembershipFunctions(4) = fismf("gbellmf", [0.2 2 0.3], "Name", "PD");

rules = [1 0 1 1 1;
         2 0 2 1 1;
         0 1 3 1 1;
         0 2 4 1 1;
         ];
      
fis = addRule(fis, rules);

%plot 
figure("Name", "Speed")
subplot(2,2,1)
plotmf(fis, "input", 1)
subplot(2,2,2)
plotmf(fis, "input", 2)
subplot(2,2,3)
plotmf(fis, "output", 1)

%save
writeFIS(fis, "fis_speed")
