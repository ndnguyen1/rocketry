#ifndef ATMOSPHERE_HPP
#define ATMOSPHERE_HPP

class Atmosphere final {
 public:
  /**
   * Calculate air density at a given altitude
   *
   * @param float Altitude (m)
   * @return Air density (kg/m^3)
  */
  static float airDensityAtAltitude(float altitude);

 private:
  static constexpr double CONST_GRAVITY = 9.80665F; // m/s^2
  static constexpr float R = 8.314472;              // J/mol·K
  static constexpr float M = 28.97E-3;              // kg/mol
  static constexpr float LAMBDA = -6.5e-3;          // K/m
  static constexpr float T_ZERO = 288.15;           // K
  static constexpr float RHO_ZERO = 1.225;          // kg/m^3
};

#endif
