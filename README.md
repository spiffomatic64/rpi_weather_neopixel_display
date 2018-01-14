# rpi_weather_neopixel_display
Displays the weather on a strip of neopixels


# Setup
# Install GPIO library

sudo apt-get update
sudo apt-get -y install build-essential python-dev git scons swig

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

cd python
sudo python setup.py install


