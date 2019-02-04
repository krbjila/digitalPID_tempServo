from PyQt4.QtGui import *
from PyQt4.QtCore import *

from PyQt4 import QtGui, QtCore


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class Indicator(QWidget):
    RAD = 1

    # Initialize and set geometry
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(0,0,3*self.RAD,3*self.RAD)
        self.setMinimumSize(QSize(3*self.RAD,3*self.RAD))
        self.coords = [1.5*self.RAD, 1.5*self.RAD]        
        self.color = QColor(210,0,0,255)
        self.warning_flag = 0

    # Resize when stretched
    def resizeEvent(self, event):
        self.coords = [0.5*event.size().width(), 0.5*event.size().height()]
        self.RAD = 0.75*min(self.coords)
        event.accept()

    # Repaint the indicator on event
    def paintEvent(self, event):
        # Start the painter
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Set white backgrount
#        painter.setBrush(Qt.white)
#        painter.drawRect(event.rect())
        # Get radius of circle
        rad = self.RAD
        # Set no outline
        painter.setPen(Qt.lightGray)
        # Setup the gradient
        gradient = QRadialGradient(QPointF(self.coords[0], self.coords[1]), rad)
        gradient.setColorAt(0, self.color)
        gradient.setColorAt(0.8, self.color)
        gradient.setColorAt(1, Qt.lightGray)
        brush = QBrush(gradient)
        painter.setBrush(brush)
        # Draw the button
        painter.drawEllipse(QPoint(self.coords[0], self.coords[1]), rad, rad)
        painter.end()


class ImageWindow(QtGui.QWidget):
	def __init__(self,Parent=None):
		super(ImageWindow,self).__init__(Parent)
		self.setup()

	def setup(self):
		self.figure = Figure(facecolor="whitesmoke")
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas,self)

		self.layout = QtGui.QGridLayout()
		self.layout.addWidget(self.toolbar,0,0,1,4)
		self.layout.addWidget(self.canvas,1,0,4,4)
		self.setLayout(self.layout)

class listenerThread(QtCore.QThread):
	def __init__(self,arduino,parent=None):
		QtCore.QThread.__init__(self,parent)

		self.arduino = arduino
		self.data = []
		self.running = False


	def run(self):
		NBYTES = 12
		self.arduino.reset_input_buffer()
		while True:
			if self.running:
				try:
					x = self.arduino.read(NBYTES)

					if x:
						self.data = x
						self.emit(QtCore.SIGNAL('dataReceived'))

				except Exception as e:
					print e

def temp2integer(T):
	# Linear coefficients over relevant temperature range
	m = -1.53286
	b = 67.9881

	# Bridge fixed resistors
	R1 = 4.87
	R2 = 10.0
	R3 = 20.0

	# Instrumentation amp. gain and bridge voltage
	G = 16.0
	Vs = 5.0
	a = R2/(R1 + R2)

        S = a - (m*T+b)/(R3 + m*T+b)
        V = S*Vs*G

        return int(V/Vs*2**8)


def voltage2temp(V):
	# Linear coefficients over relevant temperature range
	m = -1.53286
	b = 67.9881

	# Bridge fixed resistors
	R1 = 4.87
	R2 = 10.0
	R3 = 20.0

	# Instrumentation amp. gain and bridge voltage
	G = 16.0
	Vs = 5.0


	S = V/(Vs*G)
	a = R2/(R1 + R2)
	T = ((a-S)*(b+R3)-b)/m/(1-(a-S))

	return T

def convertSerial(x):
	dBridge = int(x[0:4])
	dSetPoint = int(x[4:8])
	dOutput = int(x[8:12])
	dError = dSetPoint - dBridge/4
	
	vBridge = dBridge*5.0/1024.0
	T = voltage2temp(vBridge)
	vSetPoint = dSetPoint*5.0/256.0
	vOutput = dOutput*5.0/256.0
	vError = dError*5.0/256.0

	return T, voltage2temp(vSetPoint)



