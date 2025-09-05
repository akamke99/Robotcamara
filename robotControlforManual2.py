# -*- coding: cp1252 -*-

import Adafruit_BBIO.GPIO as GPIO
import SPIComm as spi
import ConfigParser
import os
import n9020b as sa
import numpy as np
import sys
import json
import time

configFile = ConfigParser.ConfigParser()
configFile.read(os.path.dirname(os.path.realpath(__file__))+"/configRobot.txt")

GPIO.setup("P9_12",GPIO.OUT)
GPIO.output("P9_12",GPIO.LOW)

###############################
##########  CLASES  ###########
###############################


class Motor:
    def __init__(self, ID):
        self.ID = ID
        self.steps=0;   #Contador de steps para posicion, inicia en 0
        self.ms = 32


class LinearMotor(Motor):
    def __init__(self, ID, max_steps, res_fullstep):
        Motor.__init__(self,ID)
        self.max_steps = max_steps
        self.res_fullstep = res_fullstep
        self.coord = 0


    def sendSteps(self, n):
        spi.sendCommand(self.ID, n)
        self.steps += n
        self.coord += n*self.res_fullstep/self.ms
        #print 'New position:   '+self.ID+'   '+str(self.coord)

    def move(self, dist):
        if ((self.coord+dist) >= 0):
                self.sendSteps(dist/(self.res_fullstep/self.ms))
        else:
                print 'WARNING: You are trying to go out of the limits'

    def moveTo(self, to):
        if (to>=0):
                self.sendSteps((to-self.coord)/(self.res_fullstep/self.ms))
                self.sendSteps(0)
                #GPIO.output("P9_12",GPIO.HIGH)
                #time.sleep(0.5)
                #GPIO.output("P9_12",GPIO.LOW)

        else:
                print 'WARNING: That coordinate is out of the limits'




class RotationMotor(Motor):
    def __init__(self, ID, res_fullstep):
        Motor.__init__(self, ID)
        self.res_fullstep = res_fullstep
        self.coord = 0

    def sendSteps(self, n):
        spi.sendCommand(self.ID, n)
        self.steps += n

        self.coord += n*self.res_fullstep/self.ms
        print 'New angle:   '+self.ID+'   '+str(self.coord)


    def move(self, angle):
        self.sendSteps(angle/(self.res_fullstep/self.ms))

    def moveTo(self, to):
        self.sendSteps((to-self.coord)*1/(self.res_fullstep/self.ms))
        self.sendSteps(0)
        #GPIO.output("P9_12",GPIO.HIGH)
        #time.sleep(0.5)
        #GPIO.output("P9_12",GPIO.LOW)





class System:
    def __init__(self, MotorX, MotorY, MotorPhi, MotorTheta,config_section_robot):
        self.MotorX = MotorX
        self.MotorY = MotorY
        self.MotorPhi = MotorPhi
        self.MotorTheta = MotorTheta
        self.IDs =  [self.MotorX.ID,
                       self.MotorY.ID,
                       self.MotorPhi.ID,
                       self.MotorTheta.ID]
        self.Motors =  {self.MotorX.ID: self.MotorX,
                       self.MotorY.ID: self.MotorY,
                       self.MotorPhi.ID: self.MotorPhi,
                       self.MotorTheta.ID: self.MotorTheta }

        self.x_offset = configFile.getint(config_section_robot, "x_offset")
        self.y_min = configFile.getint(config_section_robot, "y_min")
        self.y_source = configFile.getint(config_section_robot, "y_source")
        self.y_offset = self.y_source - self.y_min
        self.phi_offset = configFile.getint(config_section_robot, "phi_offset")
        self.positionSaver = ConfigParser.ConfigParser()
        self.positionSaver.read(os.path.dirname(os.path.realpath(__file__))+"/robotPosData.ini")
        if self.positionSaver.has_section("steps"):
                #print 'Actual initial positions:'
                for id_motor in self.IDs:
                        self.Motors[id_motor].steps = self.positionSaver.getint("steps", id_motor)
                        self.Motors[id_motor].coord = self.Motors[id_motor].steps*self.Motors[id_motor].res_fullstep/self.Motors[id_motor].ms
            #           print id_motor+':  '+str(self.Motors[id_motor].coord)
                #print ' '
        else:
                self.positionSaver.add_section("steps")
                self.savePos()


        #########



    def moveTo(self, ID , to):
        self.Motors[ID].moveTo(to)
        self.savePos()

    def move(self, ID , dist_ang):
        self.Motors[ID].move(dist_ang)
        self.savePos()


    def savePos(self):
        #GPIO.setup("P9_12",GPIO.OUT)
        posfile = open(os.path.dirname(os.path.realpath(__file__))+"/robotPosData.ini",'w')
        for id_motor in self.IDs:
                self.positionSaver.set("steps",id_motor,int(self.Motors[id_motor].steps))
        self.positionSaver.write(posfile)
        posfile.close()
        #GPIO.output("P9_12",GPIO.HIGH)
        #time.sleep(5)
        #GPIO.output("P9_12",GPIO.LOW)
        #GPIO.cleanup()

    def start(self):
        spi.sendCommand('0',np.int16(0))
        for id_motor in ['x','y']:
            self.Motors[id_motor].steps = 0
            self.Motors[id_motor].coord = 0
        self.savePos()

    def aim_to(self, coord_X, coord_Y):
        # Rotar eje Phi para que apunte hacia cierto punto
        d_Y = coord_Y-self.MotorY.coord
        d_X = coord_X+self.MotorX.coord
        if not ((d_Y==0) and (d_X==0)):
                angle = np.arcsin(d_Y/ (  np.sqrt(d_Y**2 + d_X**2) )  )*(180/np.pi)
                self.MotorPhi.moveTo(angle)
        print 'Aiming to (', str(coord_X) + ', ' + str(coord_Y) , ')'

    def rotated_x_y(self, angle,distance):
        pos_x = (distance+self.phi_offset)*np.cos(angle*(np.pi/180))-self.x_offset
        pos_y = (distance+self.phi_offset)*np.sin(angle*(np.pi/180))+self.y_source
        return pos_x,pos_y


def yes_or_no(ins):
        yes = {'s','si','yes','y', 'ye', ''}
        no = {'no','n'}
        while (1):
            choice = raw_input(ins).lower()
            if choice in yes:
                return True
            elif choice in no:
                return False
            else:
                print "Por favor responder con 'si' o 'no'"


def init_robot(config_section):
        # Inicializacion de motores
        x_axis = LinearMotor(ID='x', max_steps=configFile.getint(config_section, "max_steps_x"), res_fullstep=configFile.getfloat(config_section, "linear_res"))
        y_axis = LinearMotor(ID='y',  max_steps=configFile.getint(config_section, "max_steps_y"), res_fullstep=configFile.getfloat(config_section, "linear_res"))
        phi_axis = RotationMotor(ID='p', res_fullstep = configFile.getfloat(config_section, "angular_res_p"))
        theta_axis = RotationMotor(ID='t', res_fullstep = configFile.getfloat(config_section, "angular_res_t"))

        # Inicializacion de sistema usando los motores
        return System(x_axis, y_axis, phi_axis, theta_axis,config_section)




#####################################################################################################


class AutomaticMeas:
    def __init__(self, robot):
        self.paramParser = ConfigParser.ConfigParser()
        self.robot=robot;

    def update_parameters(self, fileName):
        self.paramParser.read(fileName)
        # parametros experimentos iniciales
        self.d_ang_theta = self.paramParser.getfloat("theta parameters", "d_ang")
        self.init_ang_theta = self.paramParser.getfloat("theta parameters", "init_ang")
        self.final_ang_theta = self.paramParser.getfloat("theta parameters", "final_ang")
        self.d_ang_phi = self.paramParser.getfloat("phi parameters", "d_ang")
        self.init_ang_phi = self.paramParser.getfloat("phi parameters", "init_ang")
        self.final_ang_phi = self.paramParser.getfloat("phi parameters", "final_ang")

        self.d_distance = self.paramParser.getfloat("distance parameters", "d_distance")
        self.init_distance = self.paramParser.getfloat("distance parameters", "init_distance")
        self.final_distance = self.paramParser.getfloat("distance parameters", "final_distance")

        self.n_samples = self.paramParser.getint("general parameters", "n_samples")
        self.dt_samp = self.paramParser.getfloat("general parameters", "dt_samp")
        self.sleep = self.paramParser.getint("general parameters", "sleep")

        #Metodo de medicion
        self.adc = self.paramParser.getboolean("general parameters", "adc")
        self.lockin = self.paramParser.getboolean("general parameters", "lockin")
        self.keysight = self.paramParser.getboolean("general parameters", "keysight")

    def run(self,filename, exp_name):
        #filename = raw_input("Experiment's parameters file name: ")
        self.update_parameters(filename)
        route = self.get_experiment_route()
        #exp_name= raw_input("Measurement name: ")
        if self.keysight:
            #out_file = sys.argv[1]
            out_file = '../../measurement/'+ filename.replace(".txt", "_") + exp_name+".txt"
            measurement_span = 20 #MHz
            dev = sa.N9020B()
            sa.center_gunn(dev)
            sa.setup_gunn_power_meas(dev)
            ##
            for i in route:
                self.robot.moveTo('x',i[0])
                self.robot.moveTo('y',i[1])
                self.robot.moveTo('p',-i[2])
                self.robot.moveTo('t',i[3])
                time.sleep(self.sleep)
                data = take_measurement(dev, span=measurement_span)
                pos = {'x':i[0], 'y':i[0], 'theta':i[3],'phi':-i[2]}
                write_data(out_file, pos, data)

        elif self.lockin:
            lockin = p5209.Princeton5209()
            state = lockin.getMachineState()
            with open('../../measurement/'+ filename.replace(".txt", "_") + exp_name+".txt", 'a') as f:
                f.write(state.__repr__())
                f.write('\n##\n')
                for i in route:
                    self.robot.moveTo('x',i[0])
                    self.robot.moveTo('y',i[1])
                    self.robot.moveTo('p',-i[2])
                    self.robot.moveTo('t',i[3])
                    time.sleep(self.sleep)
                    data = lockin.getFastOutputLoop(self.n_samples,self.dt_samp)
                    f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(i[0],i[1],i[2],i[3], data))
                    f.flush()






        elif self.adc:
            adc = Adafruit_ADS1x15.ADS1115()

            # Or create an ADS1015 ADC (12-bit) instance.
            #adc = Adafruit_ADS1x15.ADS1015()

            # Note you can change the I2C address from its default (0x48), and/or the I2C
            # bus by passing in these optional parameters:
            #adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

            # Choose a gain of 1 for reading voltages from 0 to 4.09V.
            # Or pick a different gain to change the range of voltages that are read:
            #  - 2/3 = +/-6.144V
            #  -   1 = +/-4.096V
            #  -   2 = +/-2.048V
            #  -   4 = +/-1.024V
            #  -   8 = +/-0.512V
            #  -  16 = +/-0.256V
            # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.

            GAIN = 16

            # Open file for writing
            #out_file = open( '/mnt/adc_data/output.txt', 'w' )

            # Start continuous ADC conversions on channel 0 using the previously set gain
            # value.  Note you can also pass an optional data_rate parameter, see the simpletest.py
            # example and read_adc function for more infromation.
            adc.start_adc(0, gain=GAIN, data_rate=860)
            start = time.clock()
            with open('../../measurement/'+ filename.replace(".txt", "_") + exp_name+".txt", 'a') as f:
                for i in route:
                    self.robot.moveTo('x',i[0])
                    self.robot.moveTo('y',i[1])
                    self.robot.moveTo('p',-i[2])
                    self.robot.moveTo('t',i[3])
                    time.sleep(self.sleep)
                    t = time.clock() - start
                    data = adc.read_adc_difference(0, gain=GAIN)
                    f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(i[0],i[1],i[2],i[3], data))
                    f.flush()
                    os.fsync( f )

            # Stop continuous conversion.  After this point you can't get data from get_last_result!
            adc.stop_adc()
            out_file.close()


    def get_experiment_route(self): #entrega los pasos a seguir por el experimento
        route_list = deque([])
        for distance in frange(self.init_distance, self.final_distance, self.d_distance):
            for phi in frange(self.init_ang_phi, self.final_ang_phi, self.d_ang_phi):
                for theta in frange(self.init_ang_theta, self.final_ang_theta, self.d_ang_theta):
                    x,y=self.robot.rotated_x_y(phi,distance)
                    command = [x, y, phi, theta]
                    route_list.append(command)
        return route_list


def frange(start, stop, step):
    i = start
    while (i <= stop):
        yield i
        if (step==0):
            break
        i += step

###################################

def take_measurement(device, span, num_samples=5):

    times = []
    freqs = []
    amps = []
    sa.setup_gunn_power_meas(device)

    for i in range(num_samples):
        time, (freq,amp) = sa.measure_with_time(device, return_amp = True)
        times.append(time)
        freqs.append(freq)
        amps.append(amp)
        data = {'times':times, 'freqs':freqs, 'amps':amps}
    return data


def write_data(fName, pos, data):

    output_dict = {'pos':pos, 'data':data}
    print output_dict
    output = json.dumps(output_dict)
    with open(fName, 'a') as f:
        f.write(output)
        f.write('\\\n')


