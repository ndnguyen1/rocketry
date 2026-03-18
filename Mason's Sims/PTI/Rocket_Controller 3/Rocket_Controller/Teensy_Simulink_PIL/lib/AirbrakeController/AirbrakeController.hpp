#ifndef AIRBRAKE_CONTROLLER_HPP
#define AIRBRAKE_CONTROLLER_HPP

#include <Constants.h>
#include <Mat3x3F.h>
#include <V3F.h>

#include <Atmosphere.hpp>
#include <memory>

class AirbrakeController {
 public:
  struct Config {
    // Controller goal
    float targetApogee;  // m (height above ground)

    // Physical parameters
    float rocketMass;              // kg
    float minRocketCrossSectArea;  // m^2
    float maxRocketCrossSectArea;  // m^2

    // Gains
    float controllerGain;           // arbitrary unit
    float dragCoeffAreaGain;        // arbitrary unit
    float dragCoeffVelocityGain;    // arbitrary unit
    float dragCoeffAirDensityGain;  // arbitrary unit
    float dragCoeffIntercept;       // arbitrary unit
  };
  float calculateCoeffientOfDrag(float vertVelocity, float airDensity,
                                 float rocketCrossArea) const;

  explicit AirbrakeController(Config config) {
    this->config = config;

    // Set reasonable default values
    this->currentOptimalCrossArea = this->config.minRocketCrossSectArea;
  }

  // Declare empty copy and move constructors
  AirbrakeController(const AirbrakeController &) {}
  AirbrakeController(const AirbrakeController &&) {}

  /**
   * Provide the latest estimated position, velocity and attitude of the rocket
   *
   * @param altitude Altitude of the rocket (m)
   * @param verticalVelocity Vertical velocity of the rocket (m/s)
   */
  float update(float altitude, float verticalVelocity);

  float getOptimalCrossSectionalArea() const;
  float getEstimatedApogee() const;
  float getTargetVelocity() const;

  // private:
  /**
   * Computes the optimum velocity tragectory of the rocket
   */
  float computeOptimumVelocityTrajectory(float currentAltitude,
                                         float airDensity,
                                         float dragCoefficient);

  /**
   * Calculate the controller effort using the current and target velocity of
   * the rocket
   *
   * @param verticalVelocity Current vertical velocity of the rocket (m/s)
   *
   */
  float computeControlEffort(float currentTargetVelocity,
                             float verticalVelocity);

  /**
   * Compute the estimated apogee of the rocket using its current position and
   * velocity
   *
   * @param altitude Altitude of the rocket (m)
   * @param verticalVelocity Vertical velocity of the rocket (m/s)
   */
  void computeEstimatedApogee(float altitude, float verticalVelocity,
                              float airDensity, float dragCoefficient);

  float calculateRocketCrossArea() const;
  // float calculateCoeffientOfDrag(float vertVelocity, float airDensity, float
  // rocketCrossArea) const;

  // float calculateTerminalVelocity(float coefficientOfDrag, float airDensity)
  // const;

  // CHANGED TERMINAL VELOCITY FUNCTION FOR PIL TESTING BELOW
  float calculateTerminalVelocity(float coefficientOfDrag, float airDensity,
                                  float rocketCrossSectionalArea) const;

  float calculateEstimatedApogee(float currentAltitude,
                                 float currentVertVelocity,
                                 float terminalVertVelocity);

  // Configuration
  Config config;

  // State
  float currentEstimatedApogee = 0.0;   // m
  float currentOptimalCrossArea = 0.0;  // m^2
  float currentTargetVelocity = 0.0;    // m/s


};

extern std::unique_ptr<AirbrakeController> airbrakeController;

#endif
