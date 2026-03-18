#ifndef AIRBRAKE_CONTROLLER_PROFILES_HPP
#define AIRBRAKE_CONTROLLER_PROFILES_HPP

#include <AirbrakeController.hpp>
namespace AIRBRAKE_CONTROLLER_PROFILES {
// GECKO CONFIG
// Get Gecko-J270 CONFIG
// 2.5kg Rocketmass after motorburnout
//(DONE) --> Show Myung
AirbrakeController::Config GECKO_J20 = {
    .targetApogee = 33.0,  // 1530m without aibrake actuation
    .rocketMass = 2.711,   // RocketMass after motor burnout
    .minRocketCrossSectArea =
        0.004,  // Gecko -> 0.0036 m^2 ; //Bluetongue -> 0.0082 m^2
    .maxRocketCrossSectArea =
        0.004 + 0.0015,        // Gecko -> 0.000484167 m^2  BT 0.004 m^2
    .controllerGain = -0.001,  //
    .dragCoeffAreaGain = 0.0,
    .dragCoeffVelocityGain = 0.0,
    .dragCoeffAirDensityGain = 0.0,
    .dragCoeffIntercept = 0.6,
};
// BETA CONFIG
// K850-BETA
// Bigger fins (No payload)
// 5.5kg Rocketmass after burnout
//-0.003 (K850)
//(DONE) --> Show Myung
AirbrakeController::Config BETA_K455 = {
    .targetApogee = 2200.0,  //
    .rocketMass = 7.44,      //
    .minRocketCrossSectArea =
        0.0082,  // Gecko -> 0.0036 m^2 ; //Bluetongue -> 0.0082 m^2
    .maxRocketCrossSectArea =
        0.0082 + 0.004,         // Gecko -> 0.000484167 m^2  BT 0.004 m^2
    .controllerGain = -0.0068,  //
    .dragCoeffAreaGain = 43.32270126,
    .dragCoeffVelocityGain = -0.000687709,
    .dragCoeffAirDensityGain = 0.531869262,
    .dragCoeffIntercept = -0.447146101 + 0.1,
};
// GAMMA CONFIG
// L2200-GAMMA
// 8.5kg Rocketmass after burnout
AirbrakeController::Config BT = {
    .targetApogee = 3048,  //
    .rocketMass = 10.8250,   //
    .minRocketCrossSectArea =
        0.0082,  // Gecko -> 0.0036 m^2 ; //Bluetongue -> 0.0082 m^2
    .maxRocketCrossSectArea =
        0.0082 + 0.0036,         // Gecko -> 0.000484167 m^2  BT 0.004 m^2
    .controllerGain = -1.0,  //
    .dragCoeffAreaGain = 43.32270126,
    .dragCoeffVelocityGain = -0.000687709,
    .dragCoeffAirDensityGain = 0.531869262,
    .dragCoeffIntercept = -0.447146101,

};
// DELTA CONFIG
// Delta L1365
// 8.5kg Rocketmass after motor burnout
//  For testing
AirbrakeController::Config GOANNA_PIL = {
    .targetApogee = 2500.0,  //
    .rocketMass = 13.00,     //
    .minRocketCrossSectArea =
        0.0188,  // Gecko -> 0.0036 m^2 ; //Bluetongue -> 0.0082 m^2
    .maxRocketCrossSectArea =
        0.0188 + 0.0268,       // Gecko -> 0.000484167 m^2  BT 0.004 m^2
    .controllerGain = -0.035,  //
    .dragCoeffAreaGain = 21.038140859140483,           //
    .dragCoeffVelocityGain = -0.00013081819610389527,  //
    .dragCoeffAirDensityGain = -0.01571134830357142,   //
    .dragCoeffIntercept = -0.008812382900499849,       //
};
// //BETA CONFIG
// //BETA-K850
// //5.5kg Rocketmass after motor burnout
// AirbrakeController::Config PiL = {
//   .targetApogee = 2500.0,   // H195 ( G1,2 )-> 250m, K650 (BT1)-> 824m  ,
//   H550 (G3)->446m, J270 (G4) -> 1472m, K455 (G5)->3300m , L1365( BT2 ) ->
//   3361m .rocketMass = 9.7,     // H195 ( G1,2 )-> _kg, K650 (BT1)-> _kg  ,
//   H550 (G3)->_kg, J270 (G4) -> _kg, K455 (G5)-> _kg , L1365( BT2 ) -> _kg
//   .minRocketCrossSectArea = 0.0082, // Gecko -> 0.0036 m^2 ; //Bluetongue ->
//   0.0082 m^2 .maxRocketCrossSectArea = 0.0082 + 0.004,  // Gecko ->
//   0.000484167 m^2  BT 0.004 m^2 .controllerGain =  -0.003,  // H195 ( G1,2
//   )-> ___, K650 (BT1)-> ___  , H550 (G3)-> ___, J270 (G4) -> ____, K455
//   (G5)->_____ , L1365( BT2 ) -> _____ .dragCoeffAreaGain = 0.0,
//   .dragCoeffVelocityGain = 0.0,
//   .dragCoeffAirDensityGain = 0.0,
//   .dragCoeffIntercept = 0.4
// };
}  // namespace AIRBRAKE_CONTROLLER_PROFILES
// Bluetongue open loop test
// Simmed up closed loop
#endif
