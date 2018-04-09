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

No other flags: toggle the light on and off

`level=on/off` - turn the light on or off
`level=full` - turn on the light at 100% brightness

`dim=up/down` - increase/reduce brightness by 10%
`dim=true` - continue previous dim up/down (best guess if no previous found)

`white=warm/cool` - lower/raise light temperature by 500k
`white=nnnn` - set light temperature to `nnnn`
