###### END #####

import os
import sys
import termios
import tty
import pigpio
import time
import threading
import itertools

#def isColorUpdateNeeded(current_color_range, des_color_range):
#        if()

pi = pigpio.pi()
        
# The Pins. Use Broadcom numbers.
PIN_NAMES = [["RED_PIN", 17], ["GREEN_PIN", 24], ["BLUE_PIN", 22]]

# LIGHTS CONFIURATION - USE RGB IN LIST 
lights = {"default": [0,0,0], "room_light1" : [140, 50, 0]}
        
def updateColor(color, step):
	color += step
	
	if color > 255:
		return 255
	if color < 0:
		return 0
		
	return color

def fadeLights(colors_from, colors_to, colors_increment, direction):
        if(direction == "up"):
                print("going up")
                while colors_from != colors_to:
                        for i,rgb_color in enumerate(colors_to):
                                #print(i, colors_from[i])
                                if colors_from[i] < rgb_color and colors_from[i] < 255:
                                        setLights(PIN_NAMES[i][1], colors_from[i]);
                                        colors_from[i] += colors_increment[i]
                                else:
                                        setLights(PIN_NAMES[i][1], rgb_color);
                                        colors_from[i] = rgb_color                                      
                        time.sleep(0.05)
        elif(direction == "down"):
                print("going down")
                #print(colors_increment)
                while colors_from != colors_to:
                        for i,rgb_color in enumerate(colors_to):
                                #print(i, colors_from[i])
                                if colors_from[i] > rgb_color and colors_from[i] > 0:
                                        setLights(PIN_NAMES[i][1], colors_from[i]);
                                        colors_from[i] -= colors_increment[i]
                                else:
                                        setLights(PIN_NAMES[i][1], rgb_color);
                                        colors_from[i] = rgb_color                                      
                        time.sleep(0.05)

        else:
                print("fadeLights must be given a correct direction of up or down")
        return colors_from


def setLights(pin, brightness):
        #realBrightness = (float(brightness) / float(255))
        #print(pin, brightness)
        pi.set_PWM_dutycycle(pin, brightness)


def main(argv):
        global lights
        # Max number of color changes per step (more is faster, less is slower).
        # You also can use 0.X floats. 30 is normal, 60 is max
        DEFAULT_STEPS = 60
        if len(argv) < 2:
                STEPS = float(DEFAULT_STEPS/2)
        else:
                if(int(argv[1]) == 100): argv[1] = 99
                STEPS = float(DEFAULT_STEPS-DEFAULT_STEPS*(float(argv[1])/100))
        
        brightChanged = False
        abort = False
        state = True

        try:
                current_color = [int(pi.get_PWM_dutycycle(PIN_NAMES[0][1])),
                                 int(pi.get_PWM_dutycycle(PIN_NAMES[1][1])),
                                 int(pi.get_PWM_dutycycle(PIN_NAMES[2][1]))]
        except:
                print("Error getting current pin values, defaulting to 0")
                current_color = [0,0,0]
                
        print("Current color:")
        print(current_color)
        selected_light = argv[0]
        counter = 0

        if(len(argv) >= 3):
                # modify for brightness
                lights[selected_light] = [round(x*(float(argv[2])/100),2) for x in lights[selected_light]]

        if(current_color < lights[selected_light]):
                # Fade up
                rgb_increment = [round((y-x)/STEPS,2) for x,y in zip(current_color, lights[selected_light])]
                current_color = fadeLights(current_color, lights[selected_light], rgb_increment, "up")
        elif(current_color > lights[selected_light]):
                # Fade down
                rgb_increment = [round((x-y)/STEPS,2) for x,y in zip(current_color, lights[selected_light])]
                current_color = fadeLights(current_color, lights[selected_light], rgb_increment, "down")

if __name__ == "__main__":
        if len (sys.argv) <= 2:
                #print("Please enter a room light configuation i.e. $light_config $speed_percent")
                main(["default"])
        elif not sys.argv[2].isdigit() or (1 > sys.argv[2] >= 100):
                print("Please enter a number from 1-100 as the speed percentage")
                # todo, default on purpose?
        else:
                main(sys.argv[1:])
                pi.stop()
