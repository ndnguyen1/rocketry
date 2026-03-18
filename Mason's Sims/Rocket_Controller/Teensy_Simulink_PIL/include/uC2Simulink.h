/**************************************************************************************************
 * This file contains configuration parameters
 * 
 *************************************************************************************************/
#ifndef UC2SIMULINK_H
#define UC2SIMULINK_H
#include <math.h>
#include "required_Variables.h"


//___________________________________________________________________________
//
//                Communication Functios
//
//    Make possible to interchange data between Simulink and Arduino
//___________________________________________________________________________
void read_Simulink(void);
void write_Simulink(void);
float saturate(float nosat, float lb, float ub);
void clear_all_outputs(void);

//Receive data from Simulink
void read_Simulink() {
  byte Header;
  float data_in[10];
  unsigned int data_in_int[10];
  for (int i = 0; i<22; i++){
    data_in_byte[i] = Serial.read();
    delay(1);
  }
  
  Header=data_in_byte[0];

  if (Header==0xAA){ 
    for (int i = 0; i<4; i++){
      data_in_int[i] =  (data_in_byte[2*i+1]<<8)+data_in_byte[2*i+2];
    }
    for (int i = 4; i<10; i++){
      data_in_int[i] =  (data_in_byte[2*i+1]<<8)+data_in_byte[2*i+2];
      data_in[i] = (float)(data_in_int[i]*0.001)-10;
    }
    in1_ADC=data_in_int[0];
    in2_ADC=data_in_int[1];
    in3_ADC=data_in_int[2];
    in4_ADC=data_in_int[3];

    extra_in1=data_in[4];
    extra_in2=data_in[5];
    extra_in3=data_in[6];
    extra_in4=data_in[7];
    extra_in5=data_in[8];
    extra_in6=data_in[9];

    PIL_start = data_in_byte[21];
    
  }
  
}


//Send data to Simulink
void write_Simulink() {
  byte Header = 0x5A;  //0x5A = 90 in decimal and "Z" in ASCII
  byte LSB, MSB;
  float out[10], out_pos;
  unsigned int out_int;

  if (PIL_start==0)
    clear_all_outputs();
  
  out[0] = out1;
  out[1] = out2;
  out[2] = out3;
  out[3] = out4;

  out[4] = extra_out1;
  out[5] = extra_out2;
  out[6] = extra_out3;
  out[7] = extra_out4;
  out[8] = extra_out5;
  out[9] = extra_out6;

  for (int i = 0; i<10; i++){
    if (out[i]<-10)
      out[i]=-10;
    if (out[i]>10)
      out[i]=10;
  }
  
  data_out_byte[0]=Header;
  data_out_byte[21]=PIL_start;
  
  for (int i = 0; i<10; i++){
    out_pos=out[i]+10;     
    out_int = 1000*(out_pos);
    LSB=out_int;
    MSB=(out_int >>8);

    data_out_byte[2*i+1]=MSB;
    data_out_byte[2*i+2]=LSB;
  }
  
  for (int i = 0; i<22; i++){
    Serial.write(data_out_byte[i]);
  }
}

//Saturation funciton to add limits to a variable
float saturate(float nosat, float lb, float ub){
  //nosat:  original variable; 
  //lb: lower bound; ub: upper bound
  float sat, aux;
  if (ub<lb){//To ensure that ub > lb
    aux=lb;
    lb=ub;
    ub=aux;
  }

  sat = min(nosat,ub);
  sat = max(sat,lb);
  return sat;
}
void clear_all_outputs() {
  out1=0;
  out2=0;
  out3=0;
  out4=0;
}


#endif // UC2SIMULINK_H
