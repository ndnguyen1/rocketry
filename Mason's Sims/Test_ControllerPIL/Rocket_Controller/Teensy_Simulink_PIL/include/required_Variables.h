/**************************************************************************************************
 * This file contains configuration parameters
 * 
 *************************************************************************************************/
#ifndef REQUIRED_VARIABLES_H
#define REQUIRED_VARIABLES_H

byte data_in_byte[22]; // for incoming serial data in bytes (8 bits)
byte data_out_byte[22]; // for outgoing serial data in bytes (8 bits)
byte PIL_start = 0;

// Inputs to the board
unsigned int  in1_ADC = 0;
unsigned int  in2_ADC = 0;
unsigned int  in3_ADC = 0;
unsigned int  in4_ADC = 0;

float extra_in1 = 0;
float extra_in2 = 0;
float extra_in3 = 0;
float extra_in4 = 0;
float extra_in5 = 0;
float extra_in6 = 0;

// Outputs from the board
float out1 = 0;
float out2 = 0;
float out3 = 0;
float out4 = 0;

float extra_out1 = 0;
float extra_out2 = 0;
float extra_out3 = 0;
float extra_out4 = 0;
float extra_out5 = 0;
float extra_out6 = 0;

#endif // REQUIRED_VARIABLES_H
