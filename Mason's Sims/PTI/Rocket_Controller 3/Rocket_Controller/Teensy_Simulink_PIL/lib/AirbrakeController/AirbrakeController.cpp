#include <Constants.h>

#include <AirbrakeController.hpp>

float AirbrakeController::update(float altitude, float verticalVelocity) {
  static float rocketCrossArea = config.minRocketCrossSectArea;
  const float airDensity = Atmosphere::airDensityAtAltitude(altitude);
  const float dragCoefficient = calculateCoeffientOfDrag(verticalVelocity, airDensity, rocketCrossArea);
  this->calculateTerminalVelocity(dragCoefficient, airDensity, rocketCrossArea);

  this->computeEstimatedApogee(altitude, verticalVelocity, airDensity, dragCoefficient);
  // this->computeOptimumVelocityTrajectory(altitude, airDensity,
  // dragCoefficient);
  float currentTargetVel = this->computeOptimumVelocityTrajectory(
      altitude, airDensity, dragCoefficient);
  float optimalArea =
      this->computeControlEffort(currentTargetVel, verticalVelocity);
  return optimalArea;
}

/////////////calculates the drag coefficient
// Input Velocity, rho and area
// Output: Drag Coefficient (Cd)
float AirbrakeController::calculateCoeffientOfDrag(
    float vertVelocity, float airDensity, float rocketCrossArea) const {
  // Gains calculated using CFD analysis in combination with multivariate
  // regression
  return (rocketCrossArea * config.dragCoeffAreaGain) +
         (vertVelocity * config.dragCoeffVelocityGain) +
         (airDensity * config.dragCoeffAirDensityGain) +
         config.dragCoeffIntercept;
}

// ///Need to calculate terminal velocity for the trajectory planner
// float AirbrakeController::calculateTerminalVelocity(float coefficientOfDrag,
// float airDensity) const {
//   const float rocketCrossSectionalArea = this->calculateRocketCrossArea();
//   return sqrt( (2 * config.rocketMass * CONST_GRAVITY) / (coefficientOfDrag *
//   airDensity * rocketCrossSectionalArea));
// }

/// MODIFIED TERMINAL VELOCITY CALCUALTOR FOR PIL
float AirbrakeController::calculateTerminalVelocity(
    float coefficientOfDrag, float airDensity,
    float rocketCrossSectionalArea) const {
  return sqrt((2 * config.rocketMass * CONST_GRAVITY) /
              (coefficientOfDrag * airDensity * rocketCrossSectionalArea));
}

// This then gets put into the trajectory planner
float AirbrakeController::computeOptimumVelocityTrajectory(
    float currentAltitude, float airDensity, float dragCoefficient) {
  // Vunerability fix.
  if (currentAltitude > config.targetApogee) {
    this->currentTargetVelocity = 0.0;
    return currentTargetVelocity;
  }
  float rocketCrossSectionalArea = config.minRocketCrossSectArea;
  // // Trajectory Planner
  const float terminalVelocity = this->calculateTerminalVelocity(
      dragCoefficient, airDensity, rocketCrossSectionalArea);
  const float Vt2 = terminalVelocity * terminalVelocity;
  const float altitudeError = config.targetApogee - currentAltitude;
  const float w = altitudeError / (Vt2 / (2.0 * CONST_GRAVITY));

  // Optimal Velocity trajectory
  this->currentTargetVelocity = sqrtf((Vt2 * expf(w)) - Vt2);
  return currentTargetVelocity;  // ADDED 26th July For PIL
}

/// After the trajecotry planner it spits ou the target velocity to the
/// controller
// The controller will spit out a gain which would be then sent to the actuator
// in simulation
float AirbrakeController::computeControlEffort(float currentTargetVelocity,
                                               float currentVertVelocity) {
  // Determine error between current and target vertical velocity
  float velocityTrackingError =
      this->currentTargetVelocity - currentVertVelocity;

  // Calculate optimal cross sectional area of the rocket
  this->currentOptimalCrossArea =
      config.controllerGain * velocityTrackingError;  // m^2

  // // Limit optimal cross sectional area (max case)
  // if (this->currentOptimalCrossArea > this->config.maxRocketCrossSectArea) {
  //   this->currentOptimalCrossArea = this->config.maxRocketCrossSectArea;
  // }

  // // Limit optimal cross sectional area (min case)
  // if (this->currentOptimalCrossArea < this->config.minRocketCrossSectArea) {
  //   this->currentOptimalCrossArea = this->config.minRocketCrossSectArea;
  // }
  return this->currentOptimalCrossArea;
}

void AirbrakeController::computeEstimatedApogee(float altitude,
                                                float verticalVelocity,
                                                float airDensity,
                                                float dragCoefficient) {
  // const float terminalVelocity = calculateTerminalVelocity(dragCoefficient,
  // airDensity);

  // // Set estimated apogee
  // this->currentEstimatedApogee = calculateEstimatedApogee(altitude,
  // verticalVelocity, terminalVelocity);

  return;
}

float AirbrakeController::calculateEstimatedApogee(float currentAltitude,
                                                   float currentVertVelocity,
                                                   float terminalVertVelocity) {
  // Source: NASA Flight Equations with Drag
  // (https://www.grc.nasa.gov/www/k-12/rocket/flteqs.html)
  const float currentVertVelocitySquared = powf(currentVertVelocity, 2.0);
  const float terminalVertVelocitySquared = powf(terminalVertVelocity, 2.0);
  const float lhs = terminalVertVelocitySquared / (2.0 * CONST_GRAVITY);
  const float rhs =
      log((currentVertVelocitySquared + terminalVertVelocitySquared) /
          terminalVertVelocitySquared);

  // Calculate yMax (distance to estimated apogee from current height)
  const float yMax = lhs * rhs;
  return currentAltitude + yMax;
}

float AirbrakeController::getOptimalCrossSectionalArea() const {
  return this->currentOptimalCrossArea;
}

float AirbrakeController::getTargetVelocity() const {
  return this->currentTargetVelocity;
}

float AirbrakeController::getEstimatedApogee() const {
  return this->currentEstimatedApogee;
}

float AirbrakeController::calculateRocketCrossArea() const {
  return config.minRocketCrossSectArea + this->currentOptimalCrossArea;
}

std::unique_ptr<AirbrakeController> airbrakeController;