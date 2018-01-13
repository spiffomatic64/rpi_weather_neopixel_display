import time
import forecastio
from neopixel import *
import sys
from datetime import datetime, timedelta
import logging

# LED strip configuration:
LED_COUNT      = 30      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
lat = 40.208087
lng = -74.807925
min_max_offset = 20
precip_mult = 5.0

def map_data( x, in_min, in_max, out_min, out_max):
    temp = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if (temp < out_min):
        temp = out_min
    if (temp > out_max):
        temp = out_max
    return temp



def wheel(pos, lum):
        """Generate rainbow colors across 0-255 positions."""
        if pos <= 255:
            r = 255-pos
            g = 0
            b = 255
        else:
            pos = pos-256
            if pos <= 255:
                r = 0
                g = pos
                b = 255
            else:
                pos = pos-256
                if pos <= 255:
                    r = 0
                    g = 255
                    b = 255-pos
                else:
                    pos = pos-256
                    if pos <= 255:
                        r = pos
                        g = 255
                        b = 0
                    else:
                        pos = pos-256
                        if pos <= 255:
                            r = 255
                            g = 255-pos
                            b = 0
                
        return Color(int(r * lum), int(g * lum), int(b * lum))

def update_weather():
    global forecast
    global hourly
    global byHour
    global print_next
    global daily
    global hours
    global precips
    global start
    
    now = time.time()
    diff = now - hourly
    
    if (diff > 3600):
        hourly = now
        logging.info( "Updating weather data" )
        logging.info( datetime.now().strftime("%Y-%m-%d %H:%M"))
        forecast.update()
        print_next = 1
        byHour = forecast.hourly()
        hours = []
        precips = []
        for hourlyData in byHour.data:
            hours.append(hourlyData.temperature *100)
            precips.append(hourlyData.precipProbability*precip_mult)
        hours = convert_to_30(hours)
        precips = convert_to_30(precips)
        start = map_data(hours[0],3200,9000,255,1023)    
            
    if (now - daily > 86400):
        daily = now
        update_daily()
        
    #elif (diff > 60):
    #    sys.stdout.write('.')
    #    sys.stdout.flush()
    
    
def update_daily():
    global temp_min
    global temp_max
    
    yesterday = datetime.now() - timedelta(hours=24)
    yesterday_forecast = forecastio.load_forecast(api_key, lat, lng, time=yesterday)
    byDay = yesterday_forecast.daily()
    temp_min = byDay.data[0].temperatureMin
    temp_max = byDay.data[0].temperatureMax
    logging.info( "Got new min: %d max: %d" % (temp_min,temp_max))
    
def convert_to_30(input):
    hours_30 = range(30)
        
    i = 1.0
    for x in range(30):
        hours_30[x] = input[int(i)]
        i = i + 1.6

    return hours_30
    
def convert_color(temp,lastcolor):
    global temp_min
    global temp_max
    global min_max_offset
    global start
    
    if x>0:
        color = start + (temp[x]-temp[x-1])
    else:
        color = start
        
    
    if color>1279:
        color = 1279
    if color<0:
        color = 0
    
    return int(color)
        
        #range start 3200 9000 255 1023
                
logging.basicConfig(filename='/var/log/leds', filemode='w', level=logging.DEBUG)
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()

hourly = time.time()
daily = hourly
bright = [-1.0] * LED_COUNT

#get min and max
yesterday = datetime.now() - timedelta(hours=24)
yesterday_forecast = forecastio.load_forecast(api_key, lat, lng, time=yesterday)
byDay = yesterday_forecast.daily()
temp_min = byDay.data[0].temperatureMin
temp_max = byDay.data[0].temperatureMax

#get data
forecast = forecastio.load_forecast(api_key, lat, lng)
byHour = forecast.hourly()

hours = []
precips = []
for hourlyData in byHour.data:
    hours.append(hourlyData.temperature * 100)
    precips.append(hourlyData.precipProbability*precip_mult)
hours = convert_to_30(hours)
precips = convert_to_30(precips)
start = map_data(hours[0],3200,9000,255,1023)  
if 7000-hours[0]>0:
    cold = 1  
else:
    cold = -1
    
print_next = 1


print 'Press Ctrl-C to quit.'
while True:
    update_weather()
    i = 0
    lastcolor = 0
        
    for x in range(30):
        if (i<LED_COUNT):
            temp = hours[x]
            
            if x>0:
                diff = hours[x]-hours[0]
                color = int(start + int(diff*abs(diff)/4000))
                    
            else:
                color = start
            lastcolor = color
            
            if color>1279:
                color = 1279
            if color<0:
                color = 0
            
                
            precip = precips[x]
            bright[i]=bright[i] + (precip/100.0*7.5)
            if bright[i]>1.0:
                bright[i]=-1.0
            if bright[i]<-1.0:
                bright[i]=-1.0
            
            if print_next:
                logging.info( "pin:%d temp:%d color:%d precip: %f min: %d max: %d" % (i,temp,color,precip,temp_min,temp_max))
            strip.setPixelColor(i, wheel(color,abs(bright[i])))
        i = i + 1
    if print_next:
        print_next = 0
    strip.show()
    sys.stdout.flush()
    time.sleep(0.05)
