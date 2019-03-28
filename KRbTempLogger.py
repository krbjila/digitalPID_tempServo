from PyQt4 import QtCore, QtGui
from templogger_helpers import *
from templogger_defaults import *
from datetime import datetime

import serial, os

class userInterface(QtGui.QWidget):

	def __init__(self):
		super(userInterface,self).__init__(None)
		self.setup()

		self.arduino = serial.Serial(ADDRESS,baudrate=9600,timeout=1)
                if self.arduino:
                    print(self.arduino)
                    print("Successfully connected to Ardunio at address: " + ADDRESS + ".")


		self.listener = listenerThread(self.arduino)
		self.listener.connect(self.listener,QtCore.SIGNAL("dataReceived"),self.dataReceived)

		self.ax = self.imageWindow.figure.add_subplot(111)
                
                self.firstRun = True
		self.n = 0
		self.recentT = [None]*NPTSSHOW
                self.recentE = [None]*NPTSSHOW

	def setup(self):

		self.setWindowTitle("KRb Temperature Logger")
		self.resize(450,680)

		self.imageWindow = ImageWindow()

		self.temperatureStatic = QtGui.QLabel('Temperature (C)',self)
                self.temperatureStatic.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.temperature = QtGui.QLineEdit('',self)
		self.temperature.setReadOnly(True)

		self.setpointStatic = QtGui.QLabel('Set Point (C)',self)
                self.setpointStatic.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.setpoint = QtGui.QLineEdit('',self)
		self.setpoint.setReadOnly(True)

		self.saveStatic = QtGui.QLabel('Save path:',self)
                self.saveStatic.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.save = QtGui.QLineEdit(DEFAULTPATH,self)
		self.save.setReadOnly(True)

		self.kpStatic = QtGui.QLabel('Kp',self)
                self.kpStatic.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.kiStatic = QtGui.QLabel('Ki',self)
                self.kiStatic.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.kdStatic = QtGui.QLabel('Kd',self)
                self.kdStatic.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

		self.kp = QtGui.QLineEdit(str(DEFAULTKP),self)
		self.ki = QtGui.QLineEdit(str(DEFAULTKI),self)
		self.kd = QtGui.QLineEdit(str(DEFAULTKD),self)

		self.buttonRun = QtGui.QPushButton('Start Logging!')
		self.buttonRun.clicked.connect(self.changeState)

                self.buttonUpdateParams = QtGui.QPushButton('Update Parameters')
                self.buttonUpdateParams.clicked.connect(self.updateParameters)

                self.plotGroup = QtGui.QButtonGroup()
                self.TGroup = QtGui.QRadioButton("Temperature")
                self.EGroup = QtGui.QRadioButton("Error")
                self.plotGroup.addButton(self.TGroup)
                self.plotGroup.addButton(self.EGroup)

                self.TGroup.setChecked(True)

                self.indicator = Indicator()

		### Layout

		self.layout = QtGui.QGridLayout()
		self.layout.addWidget(self.imageWindow,0,0,1,6)
                
                self.layout.addWidget(self.TGroup,2,5,1,1)
                self.layout.addWidget(self.EGroup,3,5,1,1)

		self.layout.addWidget(self.temperatureStatic,2,0,1,1)
		self.layout.addWidget(self.temperature,2,1,1,1)

		self.layout.addWidget(self.setpointStatic,3,0,1,1)
		self.layout.addWidget(self.setpoint,3,1,1,1)

		self.layout.addWidget(self.saveStatic,4,0,1,1)
		self.layout.addWidget(self.save,4,1,1,5)

		self.layout.addWidget(self.kpStatic,5,0,1,1)
		self.layout.addWidget(self.kp,5,1,1,1)
		self.layout.addWidget(self.kiStatic,5,2,1,1)
		self.layout.addWidget(self.ki,5,3,1,1)
		self.layout.addWidget(self.kdStatic,5,4,1,1)
		self.layout.addWidget(self.kd,5,5,1,1)

		self.layout.addWidget(self.buttonRun,6,2,1,2)
                self.layout.addWidget(self.buttonUpdateParams,7,2,1,2)

                self.layout.addWidget(self.indicator,6,0,2,1)

		self.setLayout(self.layout)

	def changeState(self):
                
                if self.firstRun:
                        print("PID parameters must be updated upon initiation.")
                        self.firstRun = False
                        self.updateParameters()

		self.listener.running = not self.listener.running

		if self.listener.running:
			self.listener.start()
			self.buttonRun.setText('Stop Logging!')
                        self.indicator.color = QtGui.QColor(0,128,0,255)
                        self.indicator.update() 
		else:
                        self.listener.wait()
			self.buttonRun.setText('Start Logging!')
                        self.indicator.color = QtGui.QColor(210,0,0,255)
                        self.indicator.update() 
		


	def dataReceived(self):
		T, SP = convertSerial(self.listener.data)
		
		self.temperature.setText('{:.2f}'.format(T))
		self.setpoint.setText('{:.2f}'.format(SP))


		self.recentT[self.n] = T
                self.recentE[self.n] = SP - T

                if (self.n + NPTSDEL) < NPTSSHOW:
                    self.recentT[self.n+1:self.n+NPTSDEL] = [None]*(NPTSDEL-1)
                    self.recentE[self.n+1:self.n+NPTSDEL] = [None]*(NPTSDEL-1)
                else:
                    self.recentT[self.n+1:] = [None]*len(self.recentT[self.n+1:])
                    self.recentE[self.n+1:] = [None]*len(self.recentE[self.n+1:])

                if self.n < NPTSSHOW-1:
                    self.n += 1
                else:
                    self.n = 0


                self.ax.cla()
                self.ax.set_xlim((0,(NPTSSHOW-1)*DT))
                self.ax.set_xlabel("Time (s)")

                if self.TGroup.isChecked() == True:
		    self.ax.plot([i*DT for i in range(NPTSSHOW)], self.recentT,'k')
		    self.ax.set_ylim((20,25))
                    self.ax.set_ylabel("Temperature (C)")
                elif self.EGroup.isChecked() == True:
                    self.ax.plot([i*DT for i in range(NPTSSHOW)],self.recentE,'k')
                    self.ax.set_ylabel("Error (C)")
		self.imageWindow.canvas.draw()

                self.arduino.reset_input_buffer()

                if os.path.isdir(DEFAULTPATH):
        		fileName = 'krbTemperature_' + datetime.now().strftime('%Y%m%d') + '.dat'
	        	file = open(DEFAULTPATH + fileName, 'a')
		        file.write('{}\t{:.2f}\n'.format(datetime.now().strftime('%X'),T))
        		file.close()

        def updateParameters(self):

            errEnc = False 

            try:
                kp = float(self.kp.text())
            except:
                errEnc = True
                print('Proportional gain must be set to an integer. Value reverted to default.')
                self.kp.setText(str(DEFAULTKP))

            try:
                ki = float(self.ki.text())
            except:
                errEnc = True
                print('Integral gain must be set to an integer. Value reverted to default.')
                self.ki.setText(str(DEFAULTKI))

            try:
                kd = float(self.kd.text())
            except:
                errEnc = True
                print('Derivative gain must be set to an integer. Value reverted to default.')
                self.kd.setText(str(DEFAULTKD))

            self.buttonUpdateParams.setEnabled(False)
            self.buttonRun.setEnabled(False)

            if not errEnc:
                self.firstRun = False
                transmit = "{0:.2E},{1:.2E},{2:.2E},{3:03d}".format(kp,ki,kd,temp2integer(DEFAULTSP))
                

                if self.listener.running:
                    self.changeState()
                    print("Temperature logging stopped.")

                print("Updating PID parameters. Waiting for Arduino to respond...")

                self.repaint()

                self.arduino.reset_input_buffer()
                self.arduino.write(transmit)

                self.arduino.timeout = DT*3
                print(self.arduino.read_until('\n').rstrip())
                print(self.arduino.read_until('\n').rstrip())
                print(self.arduino.read_until('\n').rstrip())
                print(self.arduino.read_until('\n').rstrip())

                self.arduino.timeout = 1
                self.buttonUpdateParams.setEnabled(True)
                self.buttonRun.setEnabled(True)

if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	ui = userInterface()
	ui.show()
	sys.exit(app.exec_())
