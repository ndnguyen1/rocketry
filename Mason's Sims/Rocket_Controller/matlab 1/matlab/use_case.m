% Load the model parameters from the .mat file
params = load('model_params.mat');

% Example Usage
area = 0.023990468; % area
rho = 1.2; % density
velocity = 120; % velocity (m/s)

% Generate predictions for a grid of angles, densities, and velocities
Cd_preds = arrayfun(@(v) poly_predict(area, rho, v, params), velocity); % prediction is force (N)
disp("Cd: " + Cd_preds)
