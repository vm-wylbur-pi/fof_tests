FOF Server HowTo
******************************

Powering Up!!!!
--------------------------
1.  Turn on Power Strip, wait 2 minutes, do a rain dance
2.  Open page http://192.168.1.72 in Web browser on Laptop or iPad
3.  Confirm MQTT and GSA icons on top-right of screen are green.  Flowers on the page's field view begin turning green.
4.  Click on the DoJ link in the top of the page and begin playing with the field!



Hands-Off Mode - pretty indefinitely
------------------------------------
1.  Click on DoJ link in the top of the http://192.168.1.72
2.  Click the Field Idle button


Viz System Go - let's watch some peeps
--------------------------------------
The Viz System is an optional component that drives location-specific games.  
You can run the field without it.

Lights
* throw the orange knife switch under the flower batteries to the right
* confirm that the lights have an eery green red color coming out of them

Camera
* Remove the camera lens cap - or everything will be dark and scary
* Raise the pole, point it towards the field

Action
* Ensure the USB cable from the camera is plugged in
* Double-click the viz.bat icon on theViz System Laptop 


What **should** happen
A black box should open on the screen, do nothing for a disconcerting amount of time, then begin scrolling text past very quickly
If you look closely you should see that some of the text says things like "Detected # Person"

On the FCC click on the Mock People link at the top of the page and you should see grey numbered squares that roughly correspond to locations of people in the field
The squares will blink in and out.  This is the expected behavior.

If the squares are in the wrong place, try rotating the camera pole to reposition it.




Troubleshooting - Uh Oh
======================================

Have you tried turning it off and on again?
* Turn off the power strip, say a prayer to the playa gods, turn the power back on, wait two minutes, start again



The Components
--------------------------
Power Strip - the six plug power trip mounted at the top-back of the box, has lots of power cables coming out of it
Raspberry Pi - 3x4in micro-computer, runs the server software that talks to the flowers
WiFi Router - black box with antennas sticking out, manages the network and provides back-up wifi
Ethernet Switch - 4x6in box with network cables coming out, provides power and internet to the Access Points
Access Points - 4 white space-ship disks that provide Internet to the flowers, two are mounted on the light poles, two are in the box
Laptop - you're looking at it, runs the viz system and provides a convenient web browser
FCC - a web interface for the field on web page http://192.168.1.72


Light Check - Are the lights blinking?
--------------------------------------
WiFi Router - green power light on front, various other lights on front interface blinking
Raspberry Pi - ethernet network cable lights blinking, two tiny lights opposite cable side blinking one red, one green
Ethernet Switch - each port with a network cable should be blinking, green status light on left of box should be solid green
Laptop - Should light up and work


Cable Check - Is the cable plugged in?
--------------------------------------
Power Strip
* Raspberry Pi - black square power adapter -> usb-c plugged into raspberry pi
* Laptop power adapter - black brick, with three-prong power plug, circular connector with a white light on it
* Ethernet Power - three prong

Ethernet Router Network Cables
* Power strip - three prong adapter plugged into power strip
* 4 Ethernet cables in ports 1-4, each going to an access point
* 1 Ethernet cable connected to Raspberry Pi

Laptop
* Power cable
* USB cable from the camera
