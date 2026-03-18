%% Simulink with Arduino board as PIL
%  Example: Cruise control
% 
% 48560 Control Studio A,
% The University of Technology Sydney (UTS)
% Sydney, NSW, Australia
%
% Tested with boards: 
% MKR1000/MKR1010/ESP32/Teensy3.x/Teensy/4.x
%
% Dr Ricardo P. Aguilera
% August 2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clc;
clear;
warning('off','all');

simu = 'Simulink_Simulink_PIL_Cruise_Crontrol_r2020b';

%% Check available COM ports
%serialportlist("available")'

%% Simulation Settings
simulate = 0;   % 1: To to start simulation in Simulink
                % 0: only create data in Matlab's Worspace.
                %        Simulation in Simulink needs to be run manually

               
Tsim=15;        % Total Simulation length in seconds. 
                % Set Tsim=Inf to run indefinitely    
                
fs=100;          % Sampling Frequency in Hz

yo=0;           % Initial Output Condition

noise=0;        % 1: Add noise to measurements
                % 0: noiseless measurements

Ts=1/fs;        % Sampling Period

PIL=1;          %0: Manually start the PIL controller 
                %   after simulation started
                %1: Automatically start PIL controller 
                %   from the beginning of the simulation
                
%% System Parameters
m = 1000;   %Car mass
b = 100;    %Coefficient of friction
Km = 1000;  %Actuator gain

%% Plant Model
disp('Plant transfer function:')
s = tf('s');

Ko = Km*1/b;
tau_o = m/b;

Gs = Ko/(tau_o*s+1)

% Controller
disp('*************************')
disp('Closep-loop target:')
disp(' ')
disp('desired overshoot')
os = 20 %desired
os = 12 %actual
disp('desired settling time')
ts = 5  %desired
ts = 4 %actual

disp('*************************')
disp('Controller Desing:')
disp(' ')
disp('Damping factor:')
zeta = -log(os/100)/sqrt(pi^2+log(os/100))


disp('Natural Frequency')
wn = 4/(zeta*ts)    %

disp('Closed-Loop Poles')
sigma = -zeta*wn;
wd = wn*sqrt(1-zeta^2);
p12 = [-sigma+j*wd, -sigma-j*wd]

disp('Proportional Gain')
Kp = (2*zeta*wn*tau_o-1)/Ko

disp('Integral Gain')
Ki = tau_o*wn^2/Ko



disp('Controller: Continuous-Time Transfer Function')
Cs = Kp+Ki/s

disp('Controller: Discrete-Time Transfer Function')
Cz = c2d(Cs,Ts)

[Cz_num, Cz_den] = tfdata(Cz,'v');
Ka = Cz_num(1)
Kb = Cz_num(2)

%% Start Simulation
if (simulate)
    open_system(simu);
    disp('Simulating...')
    sim(simu)
    disp('Plotting...')
    
    save('result_data.mat')
    plot_results;
    disp('Done!!!')
    
end
