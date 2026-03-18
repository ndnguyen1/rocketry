#include <AirbrakeController.hpp>
#include <Constants.h>

void AirbrakeController::update(float altitude, float verticalVelocity) {
  const float airDensity = Atmosphere::airDensityAtAltitude(altitude);
  const float dragCoefficient = calculateCoeffientOfDrag(verticalVelocity, airDensity, calculateRocketCrossArea());

  this->computeEstimatedApogee(altitude, verticalVelocity, airDensity, dragCoefficient);
  this->computeOptimumVelocityTrajectory(altitude, airDensity, dragCoefficient);
  this->computeControlEffort(verticalVelocity);
}

/////////////calculates the drag coefficient 
//Input Velocity, rho and area 
//Output: Drag Coefficient (Cd)
float AirbrakeController::calculateCoeffientOfDrag(float vertVelocity, float airDensity, float rocketCrossArea) const {
  // Gains calculated using CFD analysis in combination with multivariate regression
  return (1.18)*((rocketCrossArea * config.dragCoeffAreaGain) +
    (vertVelocity * config.dragCoeffVelocityGain) +
    (airDensity * config.dragCoeffAirDensityGain) +
    config.dragCoeffIntercept);
}


///Need to calculate terminal velocity for the trajectory planner 
float AirbrakeController::calculateTerminalVelocity(float coefficientOfDrag, float airDensity) const {
  const float rocketCrossSectionalArea = this->calculateRocketCrossArea();
  return sqrt( (2.0 * config.rocketMass * CONST_GRAVITY) / (coefficientOfDrag * airDensity * rocketCrossSectionalArea));
}

//This then gets put into the trajectory planner
void AirbrakeController::computeOptimumVelocityTrajectory(
  float currentAltitude,
  float airDensity,
  float dragCoefficient) {
  // Vunerability fix.
  if (currentAltitude > config.targetApogee) {
    this->currentTargetVelocity = 0.0;
    return;
  }

  // Trajectory Planner
  const float terminalVelocity = this->calculateTerminalVelocity(dragCoefficient, airDensity);
  const float Vt2 = terminalVelocity * terminalVelocity;
  const float altitudeError = config.targetApogee - currentAltitude;
  const float w = altitudeError / (Vt2 / (2.0 * CONST_GRAVITY));

  // Optimal Velocity trajectory
  this->currentTargetVelocity = sqrtf((Vt2 * expf(w)) - Vt2);
  return;
}

///After the trajecotry planner it spits ou the target velocity to the controller 
//The controller will spit out a gain which would be then sent to the actuator in simulation
void AirbrakeController::computeControlEffort(float currentVertVelocity) {
  // Determine error between current and target vertical velocity
  const float velocityTrackingError = this->currentTargetVelocity - currentVertVelocity;

  // Calculate optimal cross sectional area of the rocket
  this->currentOptimalCrossArea = config.controllerGain * velocityTrackingError;  // m^2

  // // Limit optimal cross sectional area (max case)
  // if (this->currentOptimalCrossArea > this->config.maxRocketCrossSectArea) {
  //   this->currentOptimalCrossArea = this->config.maxRocketCrossSectArea;
  // }

  // // Limit optimal cross sectional area (min case)
  // if (this->currentOptimalCrossArea < this->config.minRocketCrossSectArea) {
  //   this->currentOptimalCrossArea = this->config.minRocketCrossSectArea;
  // }

  return;
}

void AirbrakeController::computeEstimatedApogee(
  float altitude,
  float verticalVelocity,
  float airDensity,
  float dragCoefficient) {
  const float terminalVelocity = calculateTerminalVelocity(dragCoefficient, airDensity);

  // Set estimated apogee
  this->currentEstimatedApogee = calculateEstimatedApogee(altitude, verticalVelocity, terminalVelocity);

  return;
}

float AirbrakeController::calculateEstimatedApogee(
  float currentAltitude,
  float currentVertVelocity,
  float terminalVertVelocity) {
  // Source: NASA Flight Equations with Drag (https://www.grc.nasa.gov/www/k-12/rocket/flteqs.html)
  const float currentVertVelocitySquared = powf(currentVertVelocity, 2.0);
  const float terminalVertVelocitySquared = powf(terminalVertVelocity, 2.0);
  const float lhs = terminalVertVelocitySquared / (2.0 * CONST_GRAVITY);
  const float rhs = log((currentVertVelocitySquared + terminalVertVelocitySquared) / terminalVertVelocitySquared);

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


