%FIS
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
figure 
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




