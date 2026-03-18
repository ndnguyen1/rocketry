% Load the model parameters from the .mat file
params = load('model_params.mat');

% Define constants
area = 0.020900944; % area in square meters
rho = 0.7; % density in kg/m^3

% Define the velocity array from 0 to 300 m/s
velocity_array = linspace(30, 300, 40);

% Initialize an array to store force predictions
Cd_pred = zeros(size(velocity_array));

% Generate predictions for the velocity array
for i = 1:length(velocity_array)
    Cd_pred(i) = poly_predict(area, rho, velocity_array(i), params);
end

% Load CSV data
data = readtable('CFD_final.csv');  % Replace 'data.csv' with the actual file name if different

% Filter data with the same area and rho
filtered_data = data(data.Area == area & data.Density == rho, :);

% Extract variables from filtered data
velocities = filtered_data.Velocity;
cd_values = filtered_data.Cd;

% Plot the predictions of Cd and force
figure;
yyaxis left;
plot(velocity_array, Cd_pred, 'LineWidth', 2, 'Color', 'b');
hold on;
scatter(velocities, cd_values, 'filled', 'MarkerFaceColor', 'b');
xlabel('Velocity (m/s)');
ylabel('Drag Coefficient (Cd)', 'Color', 'b');
title('Drag Coefficient (Cd) and Force vs. Velocity');
grid on;
