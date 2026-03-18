
%desiredAngle = 0:0.1:90;

%output = (60-192)/90 * (desiredAngle) + 192;

%plot(desiredAngle, output)

area = 0.018801:0.001:(0.005352 + 0.018801);

%angle = 0:0.1:90;

angle = (7e8 * power(area, 3)) - (4e7 * power(area, 2)) + (907136 * area) - 6253.3;

%angle = (-6e-07 * power(area, 2)) + 0.0001*area + 0.0189;

plot(area, angle)
