# lifxlocalcontrol
Physical control of LIFX lights using a local Python server and an Arduino.

Installation (python server)
-----

* Install python 2.7
* `pip install -r requirements.txt`
* `python lifxlancontrol.py`


Usage (python server)
-----

With the default configuration, head to `YOURSERVER:7990/lights` in a browser to poll for lights on your LAN and save them in a cached dict.
Also displays current label, IP, mac and color settings for any lights found.

POST `form_data` to the same address with either `mac=aa:bb:cc:dd:ee:ff&ip=192.168.x.x` or `light=LIGHT_NAME`

* No other flags: toggle the light on and off
* on/off:
    * `level=on/off` - turn the light on or off
    * `level=full` - turn on the light at 100% brightness

* Brightness:
    * `dim=up/down` - increase/reduce brightness by 10%
    * `dim=true` - continue previous dim up/down (best guess if no previous found)

* Light temperature:
    * `white=warm/cool` - lower/raise light temperature by 500k
    * `white=nnnn` - set light temperature to `nnnn`

Installation (arduino w/ Wifi)
-----
Edit LANSwitch.ino to set:

* Your Wifi credentials (lines 8 and 9)
* IP address, gateway and subnet of your arduino (lines 34 to 36)

* Python server IP and port (lines 13 and 14)
* Name of light to control (line 16)

**Please Note:** the server values are not currently used in the http calls. Find/replace all references to `YOURHOSTIP` (lines 79, 93, 115) and `LIGHT_NAME` (lines 81, 95, 118)

Thanks to salsaman for the [multi-function button code](http://forum.arduino.cc/index.php?topic=14479.0)

Usage (arduino)
-----
1. Flash code onto the arduino
2. Connect a momentary button between `buttonPin` and ground

* single click toggles light
* double click (tricky to get) sets light to 100%
* hold dims

Optional additional steps:

1. Remove an existing light switch
2. Wire the fitting to permanent live (if permissible by building regulations where you live)
3. Wire in a 5V USB port behind the switch (if permissible by building regulations where you live)
4. Shave the edges off your arduino board to fit it in the back box (so close to the perfect size)
5. Connect a nice looking momentary switch
6. Screw it all back together


