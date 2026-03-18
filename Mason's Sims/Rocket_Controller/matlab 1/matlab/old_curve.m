% Define constants
area = 0.023990468; % area in square meters
rho = 1.2; % density in kg/m^3

% Define the velocity array from 0 to 300 m/s
velocity_array = linspace(0, 300, 100);

% Calculate Cd using the provided formula
Cd_formula = fcn(area, velocity_array, rho);

% Calculate the force based on the Cd values
force_formula = Cd_formula .* (0.5 * rho * area * (velocity_array.^2));

% Plot the predictions of Cd and force
figure;
yyaxis left;
plot(velocity_array, Cd_formula, 'LineWidth', 2, 'Color', 'b');
xlabel('Velocity (m/s)');
ylabel('Drag Coefficient (Cd)', 'Color', 'b');
title('Drag Coefficient (Cd) and Force vs. Velocity');
grid on;

yyaxis right;
plot(velocity_array, force_formula, 'LineWidth', 2, 'Color', 'r');
ylabel('Force (N)', 'Color', 'r');
legend('Calculated Cd', 'Calculated Force');
