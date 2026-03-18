#include <Atmosphere.hpp>
#include <cmath>

float Atmosphere::airDensityAtAltitude(float altitude) {
  const float T = T_ZERO + (LAMBDA * altitude);   // K
  const float tRatio = T / T_ZERO;

  // Calculate the air density (kg/m^3) using the current altitude
  const float exp = (-CONST_GRAVITY * M) / (R * LAMBDA);
  return RHO_ZERO * pow(tRatio, exp - 1);
}
