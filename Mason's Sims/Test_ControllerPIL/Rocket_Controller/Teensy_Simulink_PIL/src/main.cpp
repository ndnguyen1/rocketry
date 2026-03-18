#include <Arduino.h>

/*****************************
  Libraries
******************************/
#include "required_Variables.h" // Required for PIL
#include "uC2Simulink.h"        // Required for PIL
/*****************************
  Function Declarations
******************************/
void Controller();

/*****************************
  Static Variables  (Constants)
******************************/
#define baud_rate 115200  //bits per second

/*****************************
   Global Variables
******************************/
float in1 = 0;
float in2 = 0;
float in3 = 0;
float in4 = 0;

//System variables
float y_k = 0;
float y_ref = 0;
float u_k = 0;
float u_k_1 = 0;
float e_k = 0;
float e_k_1 = 0;

//Controller coefficients
float Ka;
float Kb;

//___________________________________________________________________________
//                             Setup
//          
//            Complete desired initializations on startup
//___________________________________________________________________________
void setup() {
  // put your setup code here, to run once:
  Serial.begin(baud_rate); // opens serial port, sets data rate

  //Initialize controller parameters
  Ka = 1.9000;
  Kb = -1.7276;

}


//___________________________________________________________________________
//                        Main loop
//
//              Wait until Simulink send data
//___________________________________________________________________________
void loop() {
  if (Serial.available() > 0) {
//When data is received from Simulink, code jumps to the Controller Section 
      Controller();
    }
}


//___________________________________________________________________________
//                              Controller
//          
//    The code inside this section will be VIRTUALLY run at every Ts
//    This will depends on the time Simulink takes to simulate your model
//    and the time required to interchange data between Simulink and Arduino
//___________________________________________________________________________
void Controller() {
  // Receive from Simulink
  // in1_ADC, in2_ADC, in3_ADC, in4_ADC (12bits unsigned int )
  // extra_in1, extra_in2, extra_in3, extra_in4 (float)
  read_Simulink(); 

  //ADC to voltage 
  //inx_ADC has the integer value ofter the conversion
  //this is transformed into a voltage value
  in1 = in1_ADC*0.004884-10; //-10 to 10
  in2 = in2_ADC*0.004884-10;//-10 to 10
  
  // Associate board inputs to states
  y_k=in1;
  
  // Output reference from Simulink
  y_ref=extra_in1; //Output references is provided from Simulink

  // Tracking Error
  e_k = y_ref - y_k;
  
  //PI controller
  u_k = Ka*e_k + Kb*e_k_1 + u_k_1;
  
  //time shifting for next sampling time
  u_k_1 = u_k;
  e_k_1 = e_k;
  
  // Apply the control input to the system to be controlled
  // board outputs: out1, out2, out3, and out4
  // extra outputs; extra_out1 to extra_out6

  out1 = u_k; 
  out2 = 2;
  out3 = 3;
  out4 = 4;

  extra_out1 = 1.2345;
  extra_out2 = y_ref;
    
  // Send out1, out2, out3, out4 to Simulink
  write_Simulink(); 
}
// End of the Control Algorithm
