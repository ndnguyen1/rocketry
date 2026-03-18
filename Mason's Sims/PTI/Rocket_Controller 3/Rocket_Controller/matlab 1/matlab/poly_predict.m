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
    X_poly = get_poly_features(X, 8);

    % Predict using the polynomial model
    y_scaled = sum(coefficients .* X_poly) + intercept;

    % Inverse standardization of the prediction
    y_pred = y_scaled * scaler_y_std + scaler_y_mean;
end
