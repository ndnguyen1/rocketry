#ifndef AIRBRAKE_CONTROLLER_HPP
#define AIRBRAKE_CONTROLLER_HPP

class AirbrakeController {
 public:
  explicit AirbrakeController(float targetApogee) {
    this->targetApogee = targetApogee;
  }

  void ProvideLatestReadings(
    V3F postition,
    V3F velocity,
    V3F attitude,
    V3F attitudeVelocity) {
    // Use position, velocity, attitude, attitudeVelocity to update the linear model
    this->updateLinearModel(postition, velocity, attitude, attitudeVelocity);

    // Solve optimal tragectory (internally updates the estimated apogee)
    this->solveOptimalTragectory();

    // Calculate control action based upon target apogee and current estimated apogee
    this->generateControllerGains();
    this->currentControlAction = this->computeControllerEffort();
  }

  float getControlAction() {
    return this->currentControlAction;
  }

  float getEstimatedApogee() {
    return this->currentEstimatedApogee;
  }

 private:
  void updateLinearModel(
    V3F postition,
    V3F velocity,
    V3F attitude,
    V3F attitudeVelocity) {
    // TODO: IMPLEMENT ME
    return;
  }

  void solveOptimalTragectory() {
    // TODO: IMPLEMENT ME
    return;
  }

  void generateControllerGains() {
    // TODO: IMPLEMENT ME
    return;
  }

  float computeControllerEffort() {
    // TODO: IMPLEMENT ME
    return;
  }

  float targetApogee;             // IN METRES
  float currentEstimatedApogee;   // IN METRES
  float currentControlAction;     // Between 0.0 and 1.0
}

#endif
