function Cd = fcn(SA, V, rho)
    u1 = 43.32270126;  % Total rocket SA
    u2 = -0.000687709; % Velocity
    u3 = 0.531869262;  % Air density
    intercept = -0.447146101;
    Cd = (SA * u1) + (V * u2) + (rho * u3) + intercept;
end