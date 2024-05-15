"""
Rev 2 adds persitant variable storage. The user settings
can be stored in the ministry of silly walks archives.
It mimics the standard python pickel
class and stores files with open, close, read, write
clasic commands. For simplicity only strings ie .txt are allowed.
Based on ILI9341 demo (simple touch demo).
pump-time-pickle.txt
soak-time-pickle.txt
number_of_trys_pickle.txt
rev3 adds rounted buttons
"""

from ili9341 import Display, color565
from xpt2046 import Touch
from machine import idle, Pin, SPI  # type: ignore
import time
import ubinascii
import micropython
import esp
import dht
import sys
import machine
#import pickle does not work the way I want

esp.osdebug(None)
import gc
gc.collect()
from xglcd_font import XglcdFont
#from machine import Pin,disable_irq,enable_irq
from machine import Pin
import machine
pump_on=Pin(21,Pin.OUT)        #create pump on object from pin21,Set Pin21 to output
led=Pin(2,Pin.OUT)            #create led object from pin2,Set Pin2 to output
led.value(1)            #Set led turn on
pump_on.value(1)            #Set pump turn on
time.sleep(0.25)
led.value(0)            #Set led turn off
pump_on.value(0)            #Set pump turn off
time.sleep(0.25)
led.value(1)            #Set led turn on
pump_on.value(1)            #Set pump turn on
time.sleep(0.25)
led.value(0)            #Set led turn off
pump_on.value(0)            #Set pump turn off
time.sleep(0.25)
led.value(1)            #Set led turn on
time.sleep(0.25)
led.value(0)            #Set led turn off
time.sleep(0.25)
led.value(1)            #Set led turn on
time.sleep(0.25)
led.value(0)            #Set led turn off
time.sleep(0.25)
  
sensor = dht.DHT22(Pin(2))
last_message = 0
message_interval = 5
idle_state =True
start_stop_set_state = False
start_stop_set_state_flag = True
run_state = False
set_state = False

pump_cycled_flag = False
pump_on_flag = False
pump_elapse_time = 0
pump_start_time = 0

soak_on_flag = False
soak_elapse_time = 0
soak_start_time = 0

'''
pump-time-pickle.txt
soak-time-pickle.txt
number_of_trys_pickle.txt'''
print ('got to pickle')
'''target_humidity
target_humidity_pickle.txt'''
f = open('target_humidity_pickle.txt')
target_humidity_str = f.read()
#'some data'
f.close()
print ('target_humidity',target_humidity_str)
target_humidity = float(target_humidity_str)
print ('target_humidity ',target_humidity,type(target_humidity))

f = open('soak-time-pickle.txt')
soak_time_str = f.read()
#'some data'
f.close()
print ('soak',soak_time_str)
soak_time_seconds = int(soak_time_str)
print ('soak int',soak_time_seconds)

f = open('pump-time-pickle.txt')
pump_time_str = f.read()
#'some data'
f.close()
print ('pump',pump_time_str)
pump_time_seconds = int(pump_time_str)
#soak_time_seconds = 20
#number_of_trys = 4
'''temp variables used by the save routine
temp_soak_time_seconds = 0
temp_pump_time_seconds = 0
temp_target_humidity = 0'''
#roxyladoucevr720@gmail.com
current_time = 0
set_screen_displayed_flag = False
#pump_time_seconds = 10
#soak_time_seconds = 20
#target_humidity = 65.0
got_new_soak_time_from_user_flag = False
Set_soak_time_flag = False
number_of_trys = 4
try_number = 0
number_from_user = 0
get_number_state = False
set_screen_displayed_flag = False
Set_pump_time_flag = False
got_new_pump_time_from_user_flag = False
output_string = ' '
hum_raw = 0.0
done_flag = False
Set_target_humidity_flag = False
espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
print('Loading fixed_font')
class HumidtyControler(object):
    """Based on Touchscreen simple demo.HumidtyControler is a program
       that dries a sample of moist herbs to a specific relative humidity
       an air pump adds dry air and waits till humidity is at desired set
       point. To acomplish this, a "state machine" is implemented:
       the states are:
       
       1. idle - the machine is just reading humidity and temperature
       2. pump_on - the machine is pumping dry air.
                    var pump_on_time
       3. soak - the machine is waiting for moisture to difuse into dry air
                 var soak_time,target_humidity
       4. done   set point has been reached.
       5. run   -machine is doing algorythm
       6. start_stop_set -user chooses mode
       7. set_pump_time -user sets time pump is on
       8. set_soak_time -user set how long dry air desicates
       9. set_target    -user sets target relative humidity
       10 set_trys      -user sets number of attemps to soak
       
       
       """
    
    
    CYAN = color565(0, 255, 255)
    PURPLE = color565(255, 0, 255)
    WHITE = color565(255, 255, 255)

    def __init__(self, display, spi2):
        """Initialize box.

        Args:
            display (ILI9341): display object
            spi2 (SPI): SPI bus
        """
        self.display = display
        self.touch = Touch(spi2, cs=Pin(5), int_pin=Pin(27),
                           int_handler=self.touchscreen_press)
        print('int pin3')
        mem_before = gc.mem_free()
        print ('free mem',mem_before)
        #espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
        #print('Loading fixed_font')
        mem_after = gc.mem_free()
        print ('free mem',mem_after)
        #print('int pin3',int_pin)
        # Display initial message
        self.display.draw_text(55, 66, 'Temperature', espresso_dolce,
                      color565(0, 255, 255))
        self.display.draw_text(74, 166, 'Humidity', espresso_dolce,
                      color565(0, 255, 255))
        self.display.draw_text(57, 270, 'Cycle', espresso_dolce,
                      color565(150, 255, 255))
        self.display.draw_text(140, 270, 'Idle', espresso_dolce,
                      color565(150, 255, 255))
        self.display.draw_button(40, 260, 80, 40,11, color565(255, 0, 255))
        pump_sting = 'Pump Time '  + str(pump_time_seconds)    
        self.display.draw_text8x8(10,
                                  10,
                                  str(pump_sting),
                                  self.CYAN)
        soak_sting = 'Soak Time '  + str(soak_time_seconds)    
        self.display.draw_text8x8(120,
                                  10,
                                  str(soak_sting),
                                  self.CYAN)
        target_sting = 'Target '  + str(target_humidity)    
        self.display.draw_text8x8(10,
                                  30,
                                  str(target_sting),
                                  self.CYAN)

        """self.display.draw_text8x8(self.display.width // 2 - 32,
                                  self.display.height - 9,
                                  "TOUCH ME",
                                  self.WHITE,
                                  background=self.PURPLE)
        """
        # A small 5x5 sprite for the dot
        self.dot = bytearray(b'\x00\x00\x07\xE0\xF8\x00\x07\xE0\x00\x00\x07\xE0\xF8\x00\xF8\x00\xF8\x00\x07\xE0\xF8\x00\xF8\x00\xF8\x00\xF8\x00\xF8\x00\x07\xE0\xF8\x00\xF8\x00\xF8\x00\x07\xE0\x00\x00\x07\xE0\xF8\x00\x07\xE0\x00\x00')
    def cycle_pump(self):
        print('got to cycle_pump')
        global pump_time_seconds,pump_cycled_flag
        
        
        pump_cycled_flag = True
    def touchscreen_press(self, x, y):
        print('got to touchscreen')
        global set_state,get_number_state,got_new_pump_time_from_user_flag
        global set_screen_displayed_flag,start_stop_set_state_flag
        """Process touchscreen press events."""
        # Y needs to be flipped   display.width
        #y = (self.display.height - 1) - y
        x = (self.display.width - 1) - x
        # Display coordinates
        '''
        #user has touched the screen, so they want to enter the cheese shop and
        #select a kind of cheese to their choseing. The three options are:
        1. Run   -disicate sample at current settings #a perfectly aged cheese
        2. Stop  -cease and desist, initiate idle, reset screen and variables #exit cheese shop
        3. Set   -user wants to enter the ministry of silly walks and change the settings
        '''
        #get_number_state = True
        #self.display.clear()
        print('get_number_state line 118',get_number_state)
        print('got_new_pump_time_from_user_flag',got_new_pump_time_from_user_flag)
        if get_number_state == True:
          self.Get_number_routine(x,y)
          print('got back from get number line 119')
          #start_stop_set_state_flag = True
        '''if got_new_pump_time_from_user_flag == True:
                pump_time_seconds = 20 #int(output_string)
                print('got back from get number pump',pump_time_seconds)
                set_screen_displayed_flag = False
                got_new_pump_time_from_user_flag = False
                start_stop_set_state_flag = True'''
        if set_state ==True:
            print('set 2nd pass')
            '''print('got_new_pump_time_from_user_flag 2nd pass',got_new_pump_time_from_user_flag)
            if got_new_pump_time_from_user_flag == True:
                pump_time_seconds = 20 #int(output_string)
                print('got back from get number pump',pump_time_seconds)
                set_screen_displayed_flag = False
                got_new_pump_time_from_user_flag = False'''
            self.Set_routine( x, y)
          
        #if set_state == False and get_number_state == False:
        print('start_stop_set_state_flag',start_stop_set_state_flag)    
        if start_stop_set_state_flag == True:      
            self.start_stop_set_routine(x,y)
        self.display.draw_text8x8(self.display.width // 2 - 32,
                                  self.display.height - 9,
                                  "{0:03d}, {1:03d}".format(x, y),
                                  self.CYAN)
        # Draw dot
        self.display.draw_sprite(self.dot, x - 2, y - 8, 5, 5)
    def Run_routine(self, x, y):
        global run_state , start_stop_set_state
        print('got to Run_routine')
        """Process Run_routine press event. Ask clerk at ministry kiosk to alter
        state variables to start the artificial inteligence"""
        self.display.clear()
        run_state = True
        
        print(x,y)
        '''espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
        print('Loading fixed_font')'''

        #print('int pin3',int_pin)
        # Display initial message
        self.display.draw_text(55, 66, 'Temperature', espresso_dolce,
                      color565(0, 255, 255))
        self.display.draw_text(74, 166, 'Humidity', espresso_dolce,
                      color565(0, 255, 255))
        self.display.draw_text(50, 266, 'Cycle', espresso_dolce,
                      color565(150, 255, 255))
        self.display.draw_text(140, 266, 'Run', espresso_dolce,
                      color565(0, 255, 0))
        self.display.draw_rectangle(40, 260, 80, 40, color565(255, 0, 255))
        start_stop_set_state = False
    def Stop_routine(self, x, y):
        global run_state,start_stop_set_state, idle_state
        global start_stop_set_state_flag,Set_pump_time_flag
        global pump_time_seconds,output_string
        global Set_soak_time_flag,soak_time_seconds,target_humidity
        global soak_on_flag,hum_raw,try_number,number_of_trys,done_flag
        global Set_target_humidity_flag,pump_on_flag 
        done_flag = False
        number_of_trys = 4
        try_number = 0
        print('got to Stop_routine')
        """Process Stop_routine press event. Ask clerk at ministry kiosk to alter
        state variables to stop the artificial inteligence"""
        idle_state =True
        if Set_pump_time_flag == True:
            pump_time_seconds = int(output_string)
            #number_from_user = 0
            Set_pump_time_flag = False
        if Set_soak_time_flag == True:
            soak_time_seconds = int(output_string)
            #number_from_user = 0
            
            Set_soak_time_flag = False
        if Set_target_humidity_flag == True:
            
            target_humidity = float(output_string)
            Set_target_humidity_flag = False
        #make sure oump is off    
        pump_on.value(0)
        pump_on_flag = False
    
        print(x,y)
        self.display.clear()
        run_state = False
        start_stop_set_state = False
        print(x,y)
        #espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
        #print('Loading fixed_font')

        #print('int pin3',int_pin)
        # Display initial message
        self.display.draw_text(55, 66, 'Temperature', espresso_dolce,
                      color565(0, 255, 255))
        self.display.draw_text(74, 166, 'Humidity', espresso_dolce,
                      color565(0, 255, 255))
        self.display.draw_text(50, 266, 'Cycle', espresso_dolce,
                      color565(150, 255, 255))
        self.display.draw_text(140, 266, 'Idle', espresso_dolce,
                      color565(150, 255, 255))
        
       
        
        self.display.draw_button(40, 260, 80, 40,11, color565(255, 0, 255))
        pump_sting = 'Pump Time '  + str(pump_time_seconds)    
        self.display.draw_text8x8(10,
                                  10,
                                  str(pump_sting),
                                  self.CYAN)
        soak_sting = 'Soak Time '  + str(soak_time_seconds)    
        self.display.draw_text8x8(120,
                                  10,
                                  str(soak_sting),
                                  self.CYAN)
        target_sting = 'Target '  + str(target_humidity)    
        self.display.draw_text8x8(10,
                                  30,
                                  str(target_sting),
                                  self.CYAN)

#start_stop_set_state_flag = True       
    def Set_routine(self, x, y):
        print('got to Set_routine')
        """Process Set_routine press events. Ask clerk at ministry kiosk to alter
        state variables to alter the artificial inteligence. Insist the archives
        behind the kiosk are changed to the current whim of the user"""
        print(x,y)
        
        global run_state,start_stop_set_state, idle_state
        global got_new_pump_time_from_user_flag,set_state
        global set_screen_displayed_flag,start_stop_set_state_flag
        set_state = True
        if got_new_pump_time_from_user_flag == True:
            set_state = False
            #got_new_pump_time_from_user_flag = False
            
        gc.collect()
        mem_before = gc.mem_free()
        print ('free mem',mem_before)
        #if set_screen_displayed_flag == False:
            
            #espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
            #print('Loading fixed_font')
        print(x,y)
        #idle_state = False  
        #start_stop_set_state = True
        print('Idle state',idle_state)
        print('start_stop_set_state',start_stop_set_state)
        #if start_stop_set_state == False and (idle_state == True or run_state == True):
        if set_state == True and set_screen_displayed_flag == False:
            self.display.clear()
            #display botons with name
            box_size_x = 80
            box_size_y = 40
            box_left_margin_x = 80
            text_left_margin_x = 90
            
            self.display.draw_button(box_left_margin_x, 20, box_size_x, box_size_y,10, color565(0, 255, 0))
            self.display.draw_text(text_left_margin_x, 26, 'Pump', espresso_dolce,
                          color565(0, 255, 255))
            self.display.draw_text8x8(90,
                                  10,
                                  str(pump_time_seconds),
                                  self.CYAN)
            
            self.display.draw_button(box_left_margin_x, 90, box_size_x, box_size_y,10, color565(255, 0, 0))
            self.display.draw_text(text_left_margin_x, 96, 'Soak', espresso_dolce,
                          color565(0, 255, 255))
            self.display.draw_text8x8(90,
                                  80,
                                  str(soak_time_seconds),
                                  self.CYAN)
            
            self.display.draw_button(box_left_margin_x, 160, box_size_x, box_size_y,10, color565(255, 0, 255))
            self.display.draw_text(text_left_margin_x, 166, 'Target', espresso_dolce,
                          color565(0, 255, 255))
            
            self.display.draw_text8x8(90,
                                  150,
                                  str(number_of_trys),
                                  self.CYAN)
            start_stop_set_state = False
            idle_state = False
            set_screen_displayed_flag = True
            
            self.display.draw_button(box_left_margin_x, 230, box_size_x, box_size_y,10, color565(0, 0, 255)),
            self.display.draw_text(text_left_margin_x, 236, 'Save', espresso_dolce,
                          color565(0, 255, 255))
            
            self.display.draw_text8x8(90,
                                  220,
                                  'Saved',
                                  self.CYAN)
            start_stop_set_state = False
            idle_state = False
            set_screen_displayed_flag = True
            #y=311
            
        if set_state == True and set_screen_displayed_flag == True:
            if y > 10 and y < 75:
                 print('got pump')
                 start_stop_set_state_flag = False
                 self.Set_pump_time_routine(x,y)
                 #start_stop_set_state_flag = True
            if y > 76 and y < 145:
                 print('got soak')
                 start_stop_set_state_flag = False
                 self.Set_soak_time_routine(x,y)
                 #self.Stop_routine( x, y)
            if y > 146 and y <215:
                 print('got target')
                 start_stop_set_state_flag = False
                 self.Set_target_humidity_routine(x, y)

            if y > 216 and y <280:
                 print('got save')
                 start_stop_set_state_flag = False
                 self.Save_routine(x, y)
    def Save_routine(self,x,y):
        print('got to Save_routine')
        global number_from_user,get_number_state,idle_state, set_screen_displayed_flag
        global output_string ,espresso_dolce,set_state, start_stop_set_state_flag
        global target_humidity,soak_time_seconds,pump_time_seconds
        #check to see if variables have change to save eerom cycles
        '''temp variables used by the save routine
        temp_soak_time_seconds = 0
        temp_pump_time_seconds = 0
        temp_target_humidity = 0'''
        f = open('target_humidity_pickle.txt')
        target_humidity_str = f.read()
        #'some data'
        f.close()
        print ('target_humidity',target_humidity_str)
        temp_target_humidity = float(target_humidity_str)
        if temp_target_humidity != target_humidity:
            print ('target_humidity has changed to ...',target_humidity,type(target_humidity))
            with open('target_humidity_pickle.txt', 'w') as f:
                f.write(str(target_humidity))
        else:
            print ('target_humidity has not changed ...',temp_target_humidity,type(temp_target_humidity))            
        
        f = open('soak-time-pickle.txt')
        soak_time_str = f.read()
        #'some data'
        f.close()
        print ('soak str',soak_time_str)
        temp_soak_time_seconds = int(soak_time_str)
        print ('soak int',soak_time_seconds)
        if temp_soak_time_seconds != soak_time_seconds:
            print ('soak_time_seconds has changed to ...',soak_time_seconds,type(soak_time_seconds))
            with open('soak-time-pickle.txt', 'w') as f:
                f.write(str(soak_time_seconds))
        else:
            print ('soak_time_seconds has not changed ...',temp_soak_time_seconds,type(temp_soak_time_seconds))            
        


        f = open('pump-time-pickle.txt')
        pump_time_str = f.read()
        #'some data'
        f.close()
        print ('pump str',pump_time_str)
        temp_pump_time_seconds = int(pump_time_str)
        if temp_pump_time_seconds != pump_time_seconds:
            print ('pump_time_seconds has changed to ...',pump_time_seconds,type(pump_time_seconds))
            with open('pump-time-pickle.txt', 'w') as f:
                f.write(str(pump_time_seconds))
        else:
            print ('pump_time_seconds has not changed ...',temp_pump_time_seconds,type(temp_pump_time_seconds))            

        #set_screen_displayed_flag = False
        self.Stop_routine(x,y)
        
    def Get_number_routine(self,x,y):
        print('got to Get_number_routine')
        global number_from_user,get_number_state,idle_state, set_screen_displayed_flag
        global output_string ,espresso_dolce,set_state, start_stop_set_state_flag
        get_number_state = True
        idle_state = False
        set_state = False
        """Process Get_number_routine press events. Ask clerk at ministry kiosk to alter
        state variables to alter the artificial inteligence. Insist the archives
        behind the kiosk are changed to the current whim of the user"""
        print(x,y)
        
        box_width = 40
        box_height = 40
        spacing = 20
        user_number = ''
        if set_screen_displayed_flag == False:
            self.display.clear()
            output_string = ''
            #espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
            #print('Loading fixed_font')
            
            #Top display box
            self.display.draw_rectangle(50, 10, 140, 40, color565(255, 255, 255))
            self.display.draw_text(58, 18, output_string, espresso_dolce,
                              color565(255, 255, 255))
            #Row one
            self.display.draw_rectangle(40, 60, 40, 40, color565(255, 255, 255))
            self.display.draw_text(58, 68, '1', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(100, 60, 40, 40, color565(255, 255, 255))
            self.display.draw_text(112, 68, '2', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(160, 60, 40, 40, color565(255, 255, 255))
            self.display.draw_text(172, 68, '3', espresso_dolce,
                              color565(255, 255, 255))
            #Row two
            self.display.draw_rectangle(40, 120, 40, 40, color565(255, 255, 255))
            self.display.draw_text(58, 128, '4', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(100, 120, 40, 40, color565(255, 255, 255))
            self.display.draw_text(112, 128, '5', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(160, 120, 40, 40, color565(255, 255, 255))
            self.display.draw_text(172, 128, '6', espresso_dolce,
                              color565(255, 255, 255))
            #Row three
            self.display.draw_rectangle(40, 180, 40, 40, color565(255, 255, 255))
            self.display.draw_text(58, 188, '7', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(100, 180, 40, 40, color565(255, 255, 255))
            self.display.draw_text(112, 188, '8', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(160, 180, 40, 40, color565(255, 255, 255))
            self.display.draw_text(172, 188, '9', espresso_dolce,
                              color565(255, 255, 255))
            #Row fou
            self.display.draw_rectangle(40, 240, 40, 40, color565(255, 255, 255))
            self.display.draw_text(57, 254, '*', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(100, 240, 40, 40, color565(255, 255, 255))
            self.display.draw_text(112, 248, '0', espresso_dolce,
                              color565(255, 255, 255))
            self.display.draw_rectangle(160, 240, 40, 40, color565(255, 255, 255))
            self.display.draw_text(172, 248, '#', espresso_dolce,
                              color565(255, 255, 255))
            set_screen_displayed_flag = True
            y = 291
        if y > 60 and y < 100:
            print ('got row 1')
            if x < 80:
                print ('got col 1')
                user_number = '1'
            elif  x < 150 and x > 90 :
                print ('got col 2')
                user_number = '2'
            elif x > 160:
                print ('got col 3')
                user_number = '3'
        if y > 110 and y < 170:
            print ('got row 2')
            if x < 80:
                print ('got col 1')
                user_number = '4'
            elif  x < 150 and x > 90 :
                print ('got col 2')
                user_number = '5'
            elif x > 160:
                print ('got col 3')
                user_number = '6'
        if y > 170 and y < 250:
            print ('got row 3')
            if x < 80:
                print ('got col 1')
                user_number = '7'
            elif  x < 150 and x > 90 :
                print ('got col 2')
                user_number = '8'
            elif x > 160:
                print ('got col 3')
                user_number = '9'
        if y > 250 and y < 290:
            print ('got row 4')
            if x < 80:
                print ('got col 1')
                user_number = '*'
            elif  x < 150 and x > 90 :
                print ('got col 2')
                user_number = '0'
            elif x > 160:
                print ('got col 3')
                user_number = '#'                
        print ('User number is...',user_number)
        if user_number == '*':
            user_number = ''
            output_string = '           '
            self.display.draw_text(58, 18, output_string, espresso_dolce,
                              color565(255, 255, 255))
            output_string = ' '
        if user_number == '#':
            print ("got return")
            get_number_state = False
            idle_state =True
            
            set_screen_displayed_flag = False
            self.Stop_routine( x, y)
            start_stop_set_state_flag = False
            print ('output_string number is.2..',output_string)
            #return output_string
        if get_number_state == True:    
            output_string = output_string + user_number
            print ('output_string number is...',output_string)
            self.display.draw_text(58, 18, output_string, espresso_dolce,
                              color565(255, 255, 255))
            
            
            
    def Set_soak_time_routine(self,x,y):
        global soak_time_seconds, number_from_user,set_screen_displayed_flag
        global got_new_soak_time_from_user_flag,Set_soak_time_flag  
        print('got to Set_soak_time_routine')
        """Process Set_soak_time_routine press events. Ask clerk at ministry kiosk to alter
        state variables to alter the artificial inteligence. Insist the archives
        behind the kiosk are changed to the current whim of the user"""
        get_number_state = True
        Set_soak_time_flag = True
        set_screen_displayed_flag = False
        #got_new_pump_time_from_user_flag = True
        self.Get_number_routine(x,y)            
            
    def Set_pump_time_routine(self,x,y):
        global pump_time_seconds, number_from_user,set_screen_displayed_flag
        global got_new_pump_time_from_user_flag,Set_pump_time_flag  
        print('got to Set_pump_time_routine')
        """Process Set_pump_time_routine press events. Ask clerk at ministry kiosk to alter
        state variables to alter the artificial inteligence. Insist the archives
        behind the kiosk are changed to the current whim of the user"""
        get_number_state = True
        Set_pump_time_flag = True
        set_screen_displayed_flag = False
        #got_new_pump_time_from_user_flag = True
        self.Get_number_routine(x,y)
    def Set_target_humidity_routine(self,x,y):
        global pump_time_seconds, number_from_user,set_screen_displayed_flag
        global got_new_pump_time_from_user_flag,Set_pump_time_flag
        global Set_target_humidity_flag  
        print('got to Set_target_humidity_routine')
        """Process Set_pump_time_routine press events. Ask clerk at ministry kiosk to alter
        state variables to alter the artificial inteligence. Insist the archives
        behind the kiosk are changed to the current whim of the user"""
        get_number_state = True
        Set_target_humidity_flag = True
        set_screen_displayed_flag = False
        #got_new_pump_time_from_user_flag = True
        self.Get_number_routine(x,y)        
        
    def start_stop_set_routine(self, x, y):
        global idle_state,run_state,start_stop_set_state_flag
        global start_stop_set_state,espresso_dolce
        print('got to start_stop_set')
        """Process start_stop_set_routine press events. Tell the  clerk at the cheese
        shop which option user wants
        """
        #espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
        #print('Loading fixed_font')
        print(x,y)
        #idle_state = False
        #start_stop_set_state_flag =True
        #start_stop_set_state = True
        print('Idle state',idle_state)
        print('start_stop_set_state',start_stop_set_state)
        #if set_state == True:
        #    self.Set_routine( x, y)
        if start_stop_set_state == False and ( idle_state == True or run_state == True ):
            self.display.clear()
            #got_new_pump_time_from_user_flag = False
             #display botons with name
            box_size_x = 80
            box_size_y = 40
            box_left_margin_x = 80
            text_left_margin_x = 90
            
            self.display.draw_button(box_left_margin_x, 20, box_size_x, box_size_y,11, color565(0, 255, 0))
            self.display.draw_text(text_left_margin_x, 30, 'Start', espresso_dolce,
                          color565(0, 255, 255))
            self.display.draw_button(box_left_margin_x, 90, box_size_x, box_size_y,11, color565(255, 0, 0))
            self.display.draw_text(text_left_margin_x, 100, 'Stop', espresso_dolce,
                          color565(0, 255, 255))
            self.display.draw_button(box_left_margin_x, 160, box_size_x, box_size_y,11, color565(255, 0, 255))
            self.display.draw_text(text_left_margin_x, 170, 'Set', espresso_dolce,
                          color565(0, 255, 255))
            start_stop_set_state = True
            idle_state = False
            y=311
        if start_stop_set_state == True and idle_state == False:
            if y > 10 and y < 75:
                 print('got start')
                 y=311 
                 self.Run_routine(x, y)
            if y > 76 and y < 145:
                 print('got stop')
                 y=311 
                 self.Stop_routine( x, y)
            if y > 146 and y < 215:
                 print('got set')
                 y=311  
                 self.Set_routine(x, y)
               
def read_sensor():
  global hum_raw
  try:
    gc.collect()
    mem = gc.mem_free()
    #print('got to read sensor')
    try:
        sensor.measure()
    except ValueError:
                  print('got value error in read sensor sleep then try again..')    
    temp = sensor.temperature()
    #print ('temp',type(temp))
    # uncomment for Fahrenheit
    #temp = temp * (9/5) + 32.0
    hum = sensor.humidity()
    '''print ('hum',type(temp))'''
    hum_raw = hum
    temp_raw = temp
    #print ('Data from read sensor...',temp_raw,hum_raw)
    #print ("hum_raw", hum_raw ,type (hum_raw))
    if (isinstance(temp, float) and isinstance(hum, float)) or (isinstance(temp, int) and isinstance(hum, int)):
      temp = (b'{0:3.1f},'.format(temp))
      hum =  (b'{0:3.1f},'.format(hum))
      return temp, hum
    else:
      return('Invalid sensor readings.')
  except OSError as e:
    return('Failed to read sensor.')


def test():
    """Test code."""
    global start_stop_set_state_flag,pump_cycled_flag,pump_on_flag
    global soak_on_flag,hum_raw,try_number,number_of_trys,done_flag
    global get_number_state ,set_state
    last_message = 0
    message_interval = 2
    espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
    print('Loading fixed_font')

 
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(4), cs=Pin(16), rst=Pin(17))
    spi2 = SPI(2, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
    print('got to test')
    HumidtyControler(display, spi2)
    loop_counter = 0

    #try:
    while True:
        #idle()
        try:
            if (time.time() - last_message) > message_interval:
              gc.collect()
              #mem = gc.mem_free()
              #state = machine.disable_irq()
              if get_number_state != True:
                  try:
                      #state = machine.disable_irq()
                      #print ('state irq',state,type(state))
                      temp, hum = read_sensor()
                      time.sleep(0.1)
                      print('sensor ok')
                      #machine.enable_irq(state)
                  except ValueError:
                      print('No sensor detected...')
                      display.clear()
                      #time.sleep(2.5)
                      display.draw_text(0,0,'No sensor detected', espresso_dolce,
                           color565(0, 255, 255))
                      #temp, hum = read_sensor()
                      time.sleep(2.5)
                      machine.reset()
#                       sys.exit()
                      with open("main.py") as file:
                        exec(file.read())
                      


              temp_striped = str(temp)
              hum_striped = str(hum)
              #temp_striped = temp.replace('b',' ')
              temp_striped = temp_striped[2:6]
              temp_striped = temp_striped + ' C'
              hum_striped = hum_striped[2:6]
              hum_striped = hum_striped + ' %'
              #temp_striped = temp_striped[4]
              hum_str = str(hum)
              #hum_float = abs(hum)
              '''print(temp_striped,type(temp_striped))
              print(temp,type(temp))
              print(hum)''' 
              #print(hum_float,type(hum_float))
              #print('Idle state2',idle_state)
              if idle_state == True:
                  print('Idleing ',loop_counter)
                  loop_counter = loop_counter + 1
              
              
              
              if idle_state == True or run_state ==True:
                display.draw_text(94, 115, str(temp_striped), espresso_dolce,
                              color565(0, 255, 255))
                display.draw_text(84, 215, str(hum_striped), espresso_dolce,
                              color565(0, 255, 255))
                ''''''
                start_stop_set_state_flag = True
                '''if   run_state == True:
                  self.cycle_pump()
                  pump_on_flag = False
                pump_elapse_time = 0
                pump_start_time = 0
                current_time = 0'''
                if   run_state == True:
                  #self.cycle_pump()
                  
                  print ('running',loop_counter)                  
                  loop_counter = loop_counter + 1
                  
                  if pump_cycled_flag == False and pump_on_flag == False:
                      pump_start_time = time.time() 
                      pump_on_flag = True
                      print('turning pump on')
                      pump_on.value(1)
                  if pump_on_flag == True:
                      current_time = time.time()
                      pump_elapse_time =  current_time - pump_start_time
                      
                      pump_sting = 'Pump Time '  + str(pump_elapse_time) + " of " + str(pump_time_seconds)   
                      display.draw_text8x8(10,
                                  10,
                                  str(pump_sting),
                                  color565(0, 255, 255))
                      
                  if pump_elapse_time > pump_time_seconds and soak_on_flag == False:
                        print ('pumping over turn off pump')
                        #turn off pump
                        pump_on.value(0)
                        pump_on_flag = False
                        pump_cycled_flag = True
                        soak_on_flag =True
                        soak_start_time = time.time()
                        pump_sting = '                      '    
                        display.draw_text8x8(10,
                                  10,
                                  str(pump_sting),
                                  color565(0, 255, 255))
                  if soak_on_flag == True :
                      print('got to soak')
                      current_time = time.time()
                      soak_elapse_time = current_time - soak_start_time
                      soak_sting = 'Soak Time '  + str(soak_elapse_time) + " of " + str(soak_time_seconds)   
                      display.draw_text8x8(10,
                                  10,
                                  str(soak_sting),
                                  color565(0, 255, 255))
                      if soak_elapse_time > soak_time_seconds:
                          print ('Soak done')
                          soak_on_flag = False
                          pump_sting = '                      '    
                          display.draw_text8x8(10,
                                  10,
                                  str(pump_sting),
                                  color565(0, 255, 255))
                          
                          if hum_raw > target_humidity:
                              print('Humidty is above target')
                              #humidity still too high so try again
                              pump_cycled_flag = False
                          else:
                              print('Humidty is below target')
                              #hunidity is at target range so soak again the number
                              #of trys
                              pump_cycled_flag = True
                              try_number = try_number + 1
                              soak_on_flag = False
                              try_sting = 'Try number '  + str(try_number) + " of " + str(number_of_trys)   
                              display.draw_text8x8(10,
                                      30,
                                      str(try_sting),
                                      color565(0, 255, 255))
                              
                              if try_number > number_of_trys:
                                  print ('Drying done')
                                  done_flag = True
                                  soak_on_flag = False
                                  pump_cycled_flag = True
                              if done_flag ==True:
                                  print ('Drying done')
                                   
                                  done_sting = 'Done!!! '     
                                  display.draw_text8x8(10,
                                          50,
                                          str(done_sting),
                                          color565(0, 255, 255))
                                      
                                  
                              
                          
                  '''soak_on_flag = False
                    soak_elapse_time = 0
                    soak_start_time = 0
                    done_flag = False
                    try_number
                    number_of_trys'''
              #print('while ',x,y)
              #client.publish(topic_pub_temp, temp)
              #client.publish(topic_pub_hum, hum)
              last_message = time.time()
              gc.collect()
              #mem = gc.mem_free()
              #print ('free ram memory...',mem)
              #start_stop_set_state_flag = True
              '''print('start_stop_set_state_flag',start_stop_set_state_flag)
              print('start_stop_set_state',start_stop_set_state)
              print('run_state',run_state)
              print('set_state',set_state)
              print('get_number_state',get_number_state)      '''                        
              '''#print('set_screen_displayed_flag',set_screen_displayed_flag)
              print('pump_cycled_flag',pump_cycled_flag)
              print('get_number_state',get_number_state)
              print('got_new_pump_time_from_user_flag',got_new_pump_time_from_user_flag)
              print('Set_pump_time_flag',Set_pump_time_flag)
              print('Set_soak_time_flag',Set_soak_time_flag)'''
              #print('soak_on_flag',soak_on_flag)
              #print ('Try number ', try_number, type(try_number))
              #print ('Done flag...',done_flag)
              #gc.collect()
              led.value(not led.value())
        except KeyboardInterrupt:
            print("\nCtrl-C pressed.  Cleaning up and exiting...")
            sys.exit()
        #finally:
        
            #display.cleanup()
            #print('Got keyboard interupt')
            #

test()

