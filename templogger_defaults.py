
###########################################################
################ DEFAULT PARAMETERS #######################

ADDRESS = '/dev/ttyACM0'

### Save file default path
DEFAULTPATH = '/media/krbdata/logging/experimentTemperature/'


### Default PID parameters 
DEFAULTKP = 10
DEFAULTKI = 0.003
DEFAULTKD = 400

### Set Point [Note: Set point cannot be modified from the GUI]
DEFAULTSP = 22


### Plotting paramters
NPTSSHOW = 500 #Number of points to show
NPTSDEL = 50 #Number of points to remove at head of graph

### Time step [Note: This is for plotting only. Time step is set in digitalPID_tempservo.ino]
DT = 30
