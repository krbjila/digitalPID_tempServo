#include <stdio.h>

#define bridgeIn 0
#define vOut 13

float Kp = 9;
float Ki = 0.001;
float Kd = 0;

String kp;
String ki;
String kd;

int setPoint = 108; //110 nominally corresponds to a setPoint of 21.0C (R = 36.46k)
const int dt = 30000; //Update every dt ms
const int gainSign = -1;
const int windupError = 20;

int bridgeV = 0;
int error = 0;

int previousError;
int integral = 0;
int derivative = 0;
int output;

char* token;
const char sep = ',';

int dataOut;

void setup() {
  Serial.begin(9600);
  
  pinMode(vOut,OUTPUT);
  analogWrite(vOut,setPoint);
}

void loop() {
	delay(dt);
	bridgeV = analogRead(bridgeIn); //Read in the bridge voltage 
	error = setPoint - bridgeV/4; //Get current error (positive means too cold)(Division by 4 since the DAC is 10 bit)

	integral += error*dt; //Calculate integral

//Prevent integrator windup by turning integrator off when error is too large
	if (abs(error) > windupError){
		integral = 0;
	}

	derivative = (previousError - error)/dt; //Calculate derivative

	output = output + gainSign*(Kp*error + Ki*integral + Kd*derivative); //Generate new output (Division by 4 since the DAC is 10 bit)
	previousError = error;

	if (output > 255){
		output = 255;
	}
	else if (output < 0){
		output = 0;
	}
	analogWrite(vOut,output);

	//Serial printing for debugging 
	//char buffer [100];
	//long vBridgeActual = bridgeV*5000L*4/1024;
	//dataOut = sprintf(buffer, "Bridge: %d (%ld mV); error: %d; Output: %d \n",bridgeV,vBridgeActual,error,output);

	
	

	//Read Serial and change parameters
 if (Serial.available()>0){
  char buffer [30];
  Serial.readBytes(buffer, 30);

  token = strtok(buffer, &sep);

  Kp = String(token).toFloat();
  token = strtok(NULL,&sep);
  Ki = String(token).toFloat();
  token = strtok(NULL,&sep);
  Kd = String(token).toFloat();
  token = strtok(NULL,&sep);
  setPoint = atoi(token);

  Serial.print("Parameters successfully updated.\n");
  Serial.print("Proportional gain set to: ");
  Serial.println(Kp,4);
  Serial.print("Integral gain set to: ");
  Serial.println(Ki,4);
  Serial.print("Derivative gain set to: ");
  Serial.println(Kd,4);

 }
	//Serial.readBytes(buffer, 12)


  char buffer [12];
	//Serial printing for logging
	dataOut = sprintf(buffer, "%4d%4d%4d",bridgeV,setPoint,output);

	for(int i=0; i<dataOut; i++){
		Serial.print(buffer[i]);
	}
}
