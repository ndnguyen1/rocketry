function [BoostPhase,CoastingPhase,BoostandCoastingPhase,Apogee] = splitFlightIntoStages(flightData)
% This function will divide flight data into its three stages.
% Phase 1: Boost Phase
% Phase 2: Coasting Phase 
% Phase 3: Descent Phase

        % Boost phase
        [~,I1] = min(flightData.ThrustN);
        BoostPhase = flightData(1:I1,:); 


        % Boost and coasting
        [M2,I2] = max(flightData.Altitudem);
        BoostandCoastingPhase = flightData(1:I2,:); % BOOST to apogee.
        Apogee = M2;

        % Coasting phase
        CoastingPhase = flightData(I1:I2,:);
        

end

