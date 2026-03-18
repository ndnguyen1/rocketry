

function X_poly = get_poly_features(X, degree)
    % Generate polynomial features up the desired degree
    n = length(X);
    X_poly = 1;  % constant bias term
    
    for d = 1:degree
        combos = nchoosek(repmat(1:n, 1, d), d);
        combos = unique(sort(combos, 2), 'rows');
        for i = 1:size(combos, 1)
            term = prod(X(combos(i, :)));
            X_poly = [X_poly, term];
        end
    end
end

function y_pred = poly_predict(area, rho, velocity, params)
    % Extract the parameters
    scaler_X_mean = params.scaler_X_mean;
    scaler_X_std = params.scaler_X_std;
    scaler_y_mean = params.scaler_y_mean;
    scaler_y_std = params.scaler_y_std;
    coefficients = params.coefficients;
    intercept = params.intercept;

    % Standardize input features (This is required because the GPR was
    % trained this way)
    X = [(area - scaler_X_mean(1)) / scaler_X_std(1), ...
         (rho - scaler_X_mean(2)) / scaler_X_std(2), ...
         (velocity - scaler_X_mean(3)) / scaler_X_std(3)];

    % Compute polynomial features up to the desired degree
    X_poly = get_poly_features(X, 3);

    % Predict using the polynomial model
    y_scaled = sum(coefficients .* X_poly) + intercept;

    % Inverse standardization of the prediction
    y_pred = y_scaled * scaler_y_std + scaler_y_mean;
end


% Load the model parameters from the .mat file
params = load('model_params.mat');

% Example Usage
area = 0.023990468; % area
rho = 1.2; % density
velocity = 120; % velocity (m/s)

% Generate predictions for a grid of angles, densities, and velocities
force_preds = arrayfun(@(v) poly_predict(area, rho, v, params), velocity); % prediction is force (N)
disp("Force: " + force_preds + " N")


Cd = (force_preds)/(0.5*rho*area*(velocity^2)); % convert to Cd 
disp("Cd: " + Cd)