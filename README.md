# rpi_weather_neopixel_display
Displays the weather on a strip of neopixels
48 hours in the future, across 30 leds
Color indicates temp (blues=cold red=hot)
BLinking indicates precipitation

Example: 
![Example](https://i.imgur.com/sjlOBR5.jpg)


# Setup
# Install GPIO library

sudo apt-get update
sudo apt-get -y install build-essential python-dev git scons swig

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

cd python
sudo python setup.py install

# Install Python libraries

apt-get install python-pip
pip install python-forecastio


Wiring instructions:
https://learn.adafruit.com/neopixels-on-raspberry-pi/overview

Using the 74AHCT125 


# To run on boot
Throw this in your rc.local:

/usr/bin/python /root/weather.py &> /root/error.log &
