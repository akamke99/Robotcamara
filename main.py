# -*- coding: cp1252 -*-

##
import SPIComm as spi
import numpy as np
import ConfigParser
import robotControlforManual2 as robotControl
from blessed import *
import six
import time #SOLO PARA UNOS TESTEOS
import os
from os import listdir
from os.path import isfile, join
#sistema de coordenadas
y_source=430
x_source=0
y_offset=180
x_offset=380
L1 = 80
L2 = 145   
#array inicial
posicion_actual=[0,0,0]
# Menu initialization
class Menu:
    def __init__(self):
        self.title_pos = [1,1]
        self.comment_pos = [2,3]
        self.init_cursor_pos=[5,3]
        self.status_pos=[5,80]
        self.cursor_pos=0
        self.arrow_char = ">" 
        self.actual_file = ""
        ##########################################
        self.predefined_messages =  {}
        self.predefined_messages["wait"] =  "Esperando instrucciones"
        self.predefined_messages["ref"] = "Referenciando ejes"
        self.predefined_messages["X"] = "Moviendo eje X"
        self.predefined_messages["Y"] = "Moviendo eje Y"
        self.predefined_messages["Phi"] = "Moviendo eje Phi"
        self.predefined_messages["Theta"] = "Moviendo eje Theta"
	self.predefined_messages["Gamma"] = "Moviendo eje Gamma"
        self.predefined_messages["auto"] = "Realizando mediciones..."
        self.actual_status = self.predefined_messages["wait"]


        ########################################

        self.options_tree = {}
        self.options_tree["start"] = [["Mover maquina","move"],["Referenciar ejes", "ref"],["Recorrido esferico", "esf"],["Recorrido automatico", "auto"],["Salir", finish]]
        self.options_tree["move"] = [["X","X"],["Y","Y"],[ "Phi","Phi"],[ "Theta","Theta"],[ "Gamma","Gamma"] ,["Volver al menu principal", "start"]]
        self.options_tree["ref"] = [["Referenciar ejes X e Y", reference],["Volver al menu principal", "start"]]
        self.options_tree["auto"] = [["Ejecutar recorrido", "select_auto"],["Generar nuevo recorrido", new_auto],["Volver al menu principal", "start"]]
        self.options_tree["esf"] = [["Referenciar radio", ref_radio],["Mover angulo absoluto", move_sphere],["Volver al menu principal", "start"]]
        self.options_tree["X"] = [["Relativo",move_x_relative],["Absoluto", move_x_absolute],["Volver al menu de seleccion de ejes","move"]]
        self.options_tree["Y"] = [["Relativo", move_y_relative],["Absoluto",move_y_absolute],["Volver al menu de seleccion de ejes","move"]]
        self.options_tree["Phi"] = [["Relativo",move_phi_relative],["Absoluto",move_phi_absolute],["Volver al menu de seleccion de ejes","move"]]
        self.options_tree["Theta"] = [["Relativo",move_theta_relative],["Absoluto",move_theta_absolute],["Volver al menu de seleccion de ejes","move"]]
	self.options_tree["Gamma"] = [["Relativo",move_gamma_relative],["Absoluto",move_gamma_absolute],["Volver al menu de seleccion de ejes","move"]]
        self.options_tree["select_auto"] =[];
        for file in ([f for f in listdir(os.path.dirname(os.path.realpath(__file__))+"/routes") if isfile(join(os.path.dirname(os.path.realpath(__file__))+"/routes", f))]):
        	self.options_tree["select_auto"].append([ file , run_auto])
        	self.actual_file = file
        self.options_tree["select_auto"].append(["Volver al menu principal","start"])

        self.titles = {}
        self.titles["start"] = "MENU PRINCIPAL"
        self.titles["move"] = "MOVER EJES"
        self.titles["ref"] = "REFERENCIAR EJES"
        self.titles["auto"] = "MENU DE MEDICION AUTOMATIZADA"
        self.titles["X"] = "MOVIMIENTO DEL EJE X"
        self.titles["Y"] = "MOVIMIENTO DEL EJE Y"
        self.titles["Phi"] = "MOVIMIENTO DEL EJE PHI"
        self.titles["Theta"] = "MOVIMIENTO DEL EJE THETA"
	self.titles["Gamma"] = "MOVIMIENTO DEL EJE GAMMA"
        self.titles["esf"] = "Mover EN ESFERA"
        self.titles["select_auto"] = "SELECCION DE RUTA AUTOMATICA"

        self.comments = {}
        self.comments["start"] = "Robot CNC para caraterizacion de antenas.\n   Utilice las flechas del teclado para desplazarse por el menu"
        self.comments["move"] = "Seleccione un eje"
        self.comments["ref"] = "Al referenciar, revisar posibles colisiones o problemas con cables"
        self.comments["auto"] = "Para recorridos circulares en torno a un punto"
        self.comments["X"] = "Seleccione la referencia para el movimiento"
        self.comments["esf"] = "Para recorridos circulares"
        self.comments["Y"] = "Seleccione la referencia para el movimiento"
        self.comments["Phi"] = "Seleccione la referencia para el movimiento"
        self.comments["Theta"] = "Seleccione la referencia para el movimiento"
	self.comments["Gamma"] = "Seleccione la referencia para el movimiento"
        self.comments["select_auto"] = "Seleccione archivo de rutas para medicion automatico"
     	#########################################
        self.actual_options = self.options_tree['start'] 
        self.actual_title = self.titles['start'] 
        self.actual_comment = self.comments['start'] 

        self.n_options=len(self.actual_options)
        self.terminal = Terminal()
        self.update_options()
        self.update_cursor()
     

    def clear(self):
        with self.terminal.hidden_cursor():
            print self.terminal.move(0,0) + self.terminal.clear()     

    def update_cursor(self):
        with self.terminal.hidden_cursor():
	    for i in range(self.n_options):	
            	print self.terminal.move(self.init_cursor_pos[0]+i,self.init_cursor_pos[1])+ "  " +(self.actual_options[i])[0]        
            print self.terminal.move(self.init_cursor_pos[0]+self.cursor_pos,self.init_cursor_pos[1]) + self.terminal.bold_green(self.arrow_char) + " " + self.terminal.bold((self.actual_options[self.cursor_pos])[0])
    			
    def update_options(self):
        self.clear()
        with self.terminal.hidden_cursor():
            self.n_options = len(self.actual_options);
            with self.terminal.location():
                print self.terminal.move(self.title_pos[0],self.title_pos[1]) + self.terminal.bold(self.actual_title)
                print self.terminal.move(self.comment_pos[0],self.comment_pos[1]) + self.actual_comment
                #for i in range(len(self.actual_options)):6
                 #   if i!=self.cursor_pos:
                  #      print self.terminal.move(self.init_cursor_pos[0]+i, self.init_cursor_pos[1]+2) + (self.actual_options[i])[0]
                    
                    
         
    def update_status(self, robot):
        with self.terminal.hidden_cursor():
            print self.terminal.move(self.status_pos[0],self.status_pos[1]) + self.terminal.bold("Estado actual")
            print self.terminal.move(self.status_pos[0]+1,self.status_pos[1]+1) + self.terminal.underline("Posicion:")
            print self.terminal.move(self.status_pos[0]+2,self.status_pos[1]+3) + "X distancia tope de emergencia inferior: " + str(robot.MotorX.coord) + " mm"
            print self.terminal.move(self.status_pos[0]+3,self.status_pos[1]+3) + "Y distancia tope de emergencia inferior: " + str(robot.MotorY.coord) + " mm"
            print self.terminal.move(self.status_pos[0]+4,self.status_pos[1]+3) + "Phi"+": "+ str(robot.MotorPhi.coord) + " grados"
            print self.terminal.move(self.status_pos[0]+5,self.status_pos[1]+3) + "Theta"+": "+ str(robot.MotorTheta.coord) + " grados"
            print self.terminal.move(self.status_pos[0]+6,self.status_pos[1]+3) + "Eje X actuador respesto a la fuente: " + str(robot.MotorX.coord+x_offset-x_source) + " mm"
            print self.terminal.move(self.status_pos[0]+7,self.status_pos[1]+3) + "Eje Y actuador respecto a la fuente: " + str(robot.MotorY.coord+y_offset-y_source) + " mm"
            x_s=robot.MotorX.coord+x_offset-x_source-L2*np.cos(np.radians(-robot.MotorPhi.coord))-L1*np.sin(np.radians(-robot.MotorPhi.coord))
            y_s=robot.MotorY.coord+y_offset-y_source+L1*np.cos(np.radians(-robot.MotorPhi.coord))-L2*np.sin(np.radians(-robot.MotorPhi.coord))   
            print self.terminal.move(self.status_pos[0]+8,self.status_pos[1]+3) + "Eje X horn respesto a la fuente: " + str(x_s) + " mm"
            print self.terminal.move(self.status_pos[0]+9,self.status_pos[1]+3) + "Eje Y horn respecto a la fuente: " + str(y_s) + " mm"
            print self.terminal.move(self.status_pos[0]+10,self.status_pos[1]+1)+ self.terminal.clear_eol() + self.terminal.underline("Accion actual: ") + self.terminal.bold_blue(self.actual_status)
            posicion_actual[0]=(x_s)
            posicion_actual[1]=(y_s)
            posicion_actual[2]=(robot.MotorPhi.coord)
            print self.terminal.move(self.status_pos[0]+11,self.status_pos[1]+3) + "Radio horn respecto a la fuente: "+ str(np.sqrt(posicion_actual[0]**2+posicion_actual[1]**2))
    def input(self):
        with self.terminal.cbreak():
            key=self.terminal.inkey()
        if repr(key)=='KEY_DOWN':
            if self.cursor_pos<self.n_options-1:
                self.cursor_pos+=1;
            else:
                self.cursor_pos=0;
            self.update_cursor()
        elif repr(key)=='KEY_UP':
            if self.cursor_pos>0:
                self.cursor_pos-=1;
            else:
                self.cursor_pos=self.n_options-1;     
	    self.update_cursor()
       
        elif repr(key)=='KEY_ENTER':
            if isinstance((self.actual_options)[self.cursor_pos][1], six.string_types):
                self.change_menu(((self.actual_options)[self.cursor_pos])[1])
            else:
                (self.actual_options)[self.cursor_pos][1](self)

    def change_menu(self,name):
        self.actual_title = self.titles[name]
        self.actual_comment = self.comments[name]
        self.actual_options = self.options_tree[name]
        self.cursor_pos=0;
        self.update_options()
        self.update_cursor()


def reference(some_menu):
    self.actual_status= self.predefined_messages["ref"]
    some_menu.update_status(robotmmwave)
    time.sleep(5)
    #robotmmwave.start()  # go to (0,0)
    some_menu.change_menu("start")
    self.actual_status=self.predefined_messages["wait"]
    some_menu.update_status(robotmmwave)

def move_x_relative(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["X"][0][0])):
	print some_menu.terminal.bold("         mm")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["X"][0][0])):
    	str_in = raw_input(": ")
	if str_in == "":
		some_menu.change_menu("X")
        	some_menu.actual_status=some_menu.predefined_messages["wait"]
        	some_menu.update_status(robotmmwave)
		return
	mm = float(str_in)
    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["X"]
        some_menu.update_status(robotmmwave)
        robotmmwave.move('x',mm)
    	some_menu.change_menu("X")
    	some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)


def move_x_absolute(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["X"][0][0])):
        print some_menu.terminal.bold("         mm")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["X"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("X")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)

    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["X"]
        some_menu.update_status(robotmmwave)
        robotmmwave.moveTo('x',mm)
        some_menu.change_menu("X")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def move_y_relative(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Y"][0][0])):
        print some_menu.terminal.bold("         mm")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Y"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Y")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)
    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Y"]
        some_menu.update_status(robotmmwave)
        robotmmwave.move('y',mm)
        some_menu.change_menu("Y")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def move_y_absolute(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Y"][0][0])):
        print some_menu.terminal.bold("         mm")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Y"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Y")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)

    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Y"]
        some_menu.update_status(robotmmwave)
        robotmmwave.moveTo('y',mm)
        some_menu.change_menu("Y")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)




def move_phi_absolute(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Phi"][0][0])):
        print some_menu.terminal.bold("         grados")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Phi"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Phi")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)

    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Phi"]
        some_menu.update_status(robotmmwave)
        robotmmwave.moveTo('p',mm)
        some_menu.change_menu("Phi")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def move_gamma_absolute(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Gamma"][0][0])):
        print some_menu.terminal.bold("         grados")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Gamma"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Gamma")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)/4

    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Gamma"]
        some_menu.update_status(robotmmwave)
        robotmmwave.moveTo('p',mm)
        some_menu.change_menu("Gamma")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)


def move_phi_relative(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Phi"][0][0])):
        print some_menu.terminal.bold("         grados")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Phi"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Phi")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)
    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Phi"]
        some_menu.update_status(robotmmwave)
        robotmmwave.move('p',mm)
        some_menu.change_menu("Phi")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)


def move_gamma_relative(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Gamma"][0][0])):
        print some_menu.terminal.bold("         grados")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Gamma"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Gamma")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)/4
    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Gamma"]
        some_menu.update_status(robotmmwave)
        robotmmwave.move('p',mm)#Mientras tanto, cambiar lo antes posible 
        some_menu.change_menu("Gamma")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)


def move_theta_absolute(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Theta"][0][0])):
        print some_menu.terminal.bold("         grados")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Theta"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Theta")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)

    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Theta"]
        some_menu.update_status(robotmmwave)
        robotmmwave.moveTo('t',mm)
        some_menu.change_menu("Theta")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def move_theta_relative(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Theta"][0][0])):
        print some_menu.terminal.bold("         grados")
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["Theta"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("Theta")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        mm = float(str_in)
    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Theta"]
        some_menu.update_status(robotmmwave)
        robotmmwave.move('t',mm)
        some_menu.change_menu("Theta")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)


#def calcular_delta(r, angle):
#    beta_rad = np.arctan(L1 / L2)
#    H = np.sqrt(L1**2 + L2**2)

#    phi = np.radians(angle)  # Convertir a radianes

#    delta_y = r * np.sin(phi) + H * np.sin(phi - beta_rad) + L1
    
#    delta_x = -r * np.cos(phi) - H * np.cos(phi - beta_rad) + L2 + r
    
#    return delta_x, delta_y  

def calcular_delta(r, angle):

    phi = np.radians(angle)  # Convertir a radianes

    delta_y =  L1 +(L2+r)*np.sin(phi)-L1*np.cos(phi)

    delta_x =  - L2 - r + (L2+r)*np.cos(phi) + L1* np.sin(phi)

    return delta_x, delta_y  
def ref_radio(some_menu):
     # Parámetros iniciales

    # Posición inicial del sistema
     with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["esf"][0][0])):
        print some_menu.terminal.bold("          mm radio")
     with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["esf"][0][0])):
        str_in = raw_input(": ")
        if str_in == "":
                some_menu.change_menu("esf")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        r = float(str_in)
     with some_menu.terminal.raw():
        #some_menu.actual_status=some_menu.predefined_messages["Phi"]
        some_menu.update_status(robotmmwave)
        robotmmwave.moveTo('p', 0)
        robotmmwave.moveTo('x',r+x_source-x_offset+L2)
        robotmmwave.moveTo('y',y_source-y_offset-L1)
        some_menu.change_menu("esf")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def move_sphere(some_menu):
     # Parámetros iniciales
    # Posición inicial del sistema
     with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["esf"][0][0])):
        print some_menu.terminal.bold("         grados")
     with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.options_tree["esf"][0][0])):
        str_in = raw_input(": ")
        radio=np.sqrt(posicion_actual[0]**2+posicion_actual[1]**2)
        if str_in == "":
                some_menu.change_menu("esf")
                some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
        phimm = float(str_in)
        xmm,ymm = calcular_delta(radio, phimm)
        print some_menu.terminal.bold("{}".format(xmm))
        print some_menu.terminal.bold("{}".format(ymm))
     with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["Phi"]
        some_menu.update_status(robotmmwave)
        print 0-phimm
        print radio+x_source-x_offset+L2-xmm
        print y_source-y_offset-L1 + ymm
        robotmmwave.moveTo('p',0-phimm)
        robotmmwave.moveTo('x',radio+x_source-x_offset+L2+xmm)
        robotmmwave.moveTo('y', y_source-y_offset-L1 + ymm)
        some_menu.change_menu("esf")
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def run_auto(some_menu):
    with some_menu.terminal.location(y=some_menu.init_cursor_pos[0]+some_menu.cursor_pos,x=some_menu.init_cursor_pos[1]+ 2 + len(some_menu.actual_file)):
        str_in = raw_input(" - Nombre de medicion: ")
        if str_in == "":
        	some_menu.change_menu("select_auto")
               	some_menu.actual_status=some_menu.predefined_messages["wait"]
                some_menu.update_status(robotmmwave)
                return
    with some_menu.terminal.raw():
        some_menu.actual_status=some_menu.predefined_messages["auto"]
        automatic_meas.run(some_menu.actual_file, str_in);
        some_menu.change_menu("select_auto")
        some_menu.update_status(robotmmwave)
        some_menu.actual_status=some_menu.predefined_messages["wait"]
        some_menu.update_status(robotmmwave)

def new_auto(some_menu):
	pass



def finish(some_menu):
    some_menu.clear()
    exit()



robotmmwave = robotControl.init_robot("robotMMLab") 
automatic_meas = robotControl.AutomaticMeas(robotmmwave);

menu = Menu()
menu.update_status(robotmmwave)

while(1):
    	menu.input()
    	menu.update_status(robotmmwave)




        
