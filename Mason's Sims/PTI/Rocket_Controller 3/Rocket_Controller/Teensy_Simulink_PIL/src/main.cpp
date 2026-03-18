/*****************************
  Libraries
******************************/
#include <Arduino.h>
#include "required_Variables.h" // Required for PIL
#include "uC2Simulink.h"        // Required for PIL
#include <vector>
#include <cmath>


#include <AirbrakeController.hpp>
#include <AirbrakeControllerProfiles.hpp>
#include <memory>
#include <Atmosphere.hpp>

/*****************************
  Static Variables  (Constants)
******************************/
#define baud_rate 115200 // bits per second

/*****************************
   Global Variables
******************************/
float in1 = 0;
float in2 = 0;
float in3 = 0;
float in4 = 0;

// System variables
float y_ref = 0;
float altitude = 0;
float velocity = 0;
float u_k = 0;
float u_k_1 = 0;
float e_k = 0;
float e_k_1 = 0;

float targetRocketVelocity = 0;
float targetVelocity_simu = 0;
float targetRocketVelocity_function = 0;
float rocketArea = 0;
float rho = 0;
float u_kk = 0;

// Controller coefficients
float Ka;
float Kb;
bool direction = 0;

// CasSystem casSystem;
std::unique_ptr<AirbrakeController> airbrakeControllerV2;

namespace APP_GLOBALS
{
  bool shouldReInitialise = false;
}

//___________________________________________________________________________
//                             Setup
//
//            Complete desired initializations on startup
//___________________________________________________________________________
void setup()
{
  // put your setup code here, to run once:
  Serial.begin(baud_rate); // opens serial port, sets data rate

  // Create and initialise Airbrake Controller
  airbrakeControllerV2 = std::make_unique<AirbrakeController>(AIRBRAKE_CONTROLLER_PROFILES::BT);
}
//
//___________________________________________________________ ________________
//                              Controller
//
//    The code inside this section will be VIRTUALLY run at every Ts
//    This will depends on the time Simulink takes to simulate your model
//    and the time required to interchange data between Simulink and Arduino
//___________________________________________________________________________
//
void Controller()
{
  //   // Receive from Simulink
  //   // in1_ADC, in2_ADC, in3_ADC, in4_ADC (12bits unsigned int )
  //   // extra_in1, extra_in2, extra_in3, extra_in4 (float)
  read_Simulink();

  //   //ADC to voltage
  //   //inx_ADC has the integer value ofter the conversion
  //   //this is transformed into a voltage value
  in1 = in1_ADC * 0.004884 - 10; // 0 to 20
  in2 = in2_ADC * 0.004884 - 10; // 0 to 20
  in3 = in3_ADC * 0.004884 - 10; //-10 to 10
  in4 = in4_ADC * 0.004884 - 10; //-10 to 10



  //targetVelocity_simu = extra_in6 * 60.0;

  //   // Associate board inputs to states
  // altitude = 400.0 * in1; // 0 to 4000;
  velocity = 40.0 * in2;  // 0 to 400;
  altitude = extra_in4 * 400;

  // altitude = in1;
  // velocity = in2;
  //   // CONTROLLER  BEGINS

  const float optimalAirbrakeArea = airbrakeControllerV2->update(altitude, velocity);
  const float targetVelocity = airbrakeControllerV2->getTargetVelocity();
  //const float optimalAirbrakeArea = airbrakeControllerV2->getOptimalCrossSectionalArea();
 // const float estimatedApogee = airbrakeControllerV2->getEstimatedApogee();

  // const float airDensity = Atmosphere::airDensityAtAltitude(altitude);

  // float rocketCrossArea = airbrakeControllerV2->calculateRocketCrossArea();

  // float Cd = airbrakeControllerV2->calculateCoeffientOfDrag(velocity, airDensity, rocketCrossArea);


  // See the estimated apogee graph on simulink

  // Optimal Area Extension
  //  Calculate optimal airbrake cross sectional area to track velocity.
  u_k = (airbrakeControllerV2->computeControlEffort(targetVelocity, velocity) / (300));
  //optimalAirbrakeArea;
  // u_k = optimalAirbrakeArea;
 // Serial.print(u_k);
  // // CONTROLLER ENDS
  // //time shifting for next sampling time
  // u_k_1 = u_k;
  // e_k_1 = e_k;

  // // Apply the control input to the system to be controlled
  // // board outputs: out1, out2, out3, and out4
  // // extra outputs; extra_out1 to extra_out6

  out1 = u_k; // 0 to  ulim.
  out2 = 1;//altitude/400;
  out3 = 3;//targetVelocity/60;
  out4 = 4;

float airdensity = extra_in3/6.6667;
float dragCoefficient = airbrakeControllerV2->calculateCoeffientOfDrag(extra_in1*40,extra_in3/6.6667,extra_in2/833.3333);


  extra_out1 = extra_in1; //extra_in1
  extra_out2 = extra_in2;  //extra_in2
  extra_out3 = extra_in3; //extra_in4
  extra_out4 = (airbrakeControllerV2->computeOptimumVelocityTrajectory(altitude,airdensity,dragCoefficient)/400); //extra_in4
  extra_out5 = airbrakeControllerV2->calculateTerminalVelocity(dragCoefficient,airdensity,extra_in2/833.3333)/30; //
  extra_out6 = airbrakeControllerV2->calculateCoeffientOfDrag(extra_in1*40,airdensity,extra_in2/833.3333);

  // // Send out1, out2, out3, out4 to Simulink
  write_Simulink();
}
// End of the Control Algorithm

//___________________________________________________________________________
//                        Main loop
//
//              Wait until Simulink send data
//___________________________________________________________________________
void loop()
{
  if (Serial.available() > 0)
  {
    // When data is received from Simulink, code jumps to the Controller Section
    Controller();
  }
}

// #include <Arduino.h>

// /*****************************
//   Libraries
// ******************************/
// #include "required_Variables.h" // Required for PIL
// #include "uC2Simulink.h"        // Required for PIL
// /*****************************
//   Function Declarations
// ******************************/
// void Controller();

// /*****************************
//   Static Variables  (Constants)
// ******************************/
// #define baud_rate 115200  //bits per second

// /*****************************
//    Global Variables
// ******************************/
// float in1 = 0;
// float in2 = 0;
// float in3 = 0;
// float in4 = 0;

// //System variables
// float y_k = 0;
// float y_ref = 0;
// float u_k = 0;
// float u_k_1 = 0;
// float e_k = 0;
// float e_k_1 = 0;

// //Controller coefficients
// float Ka;
// float Kb;

// //___________________________________________________________________________
// //                             Setup
// //
// //            Complete desired initializations on startup
// //___________________________________________________________________________
// void setup() {
//   // put your setup code here, to run once:
//   Serial.begin(baud_rate); // opens serial port, sets data rate

//   //Initialize controller parameters
//   //Ka = 1.9000;
//   //Kb = -1.7276;

//   Ka = 5.0;
//   Kb = -2.0;

// }

// //___________________________________________________________________________
// //                        Main loop
// //
// //              Wait until Simulink send data
// //___________________________________________________________________________
// void loop() {
//   if (Serial.available() > 0) {
// //When data is received from Simulink, code jumps to the Controller Section
//       Controller();
//     }
// }

// //___________________________________________________________________________
// //                              Controller
// //
// //    The code inside this section will be VIRTUALLY run at every Ts
// //    This will depends on the time Simulink takes to simulate your model
// //    and the time required to interchange data between Simulink and Arduino
// //___________________________________________________________________________
// void Controller() {
//   // Receive from Simulink
//   // in1_ADC, in2_ADC, in3_ADC, in4_ADC (12bits unsigned int )
//   // extra_in1, extra_in2, extra_in3, extra_in4 (float)
//   read_Simulink();

//   //ADC to voltage
//   //inx_ADC has the integer value ofter the conversion
//   //this is transformed into a voltage value
//   in1 = in1_ADC*0.004884-10; //-10 to 10
//   in2 = in2_ADC*0.004884-10;//-10 to 10

//   // Associate board inputs to states
//   y_k=in1;

//   // Output reference from Simulink
//   y_ref=extra_in1; //Output references is provided from Simulink

//   // Tracking Error
//   e_k = y_ref - y_k;

//   //PI controller
//   u_k = Ka*e_k + Kb*e_k_1 + u_k_1;

//   //time shifting for next sampling time
//   u_k_1 = u_k;
//   e_k_1 = e_k;

//   // Apply the control input to the system to be controlled
//   // board outputs: out1, out2, out3, and out4
//   // extra outputs; extra_out1 to extra_out6

//   out1 = u_k;
//   out2 = 2;
//   out3 = 3;
//   out4 = 4;

//   extra_out1 = 1.2345;
//   extra_out2 = y_ref;

//   // Send out1, out2, out3, out4 to Simulink
//   write_Simulink();
// }
// // End of the Control Algorithm
