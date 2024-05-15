# Complete project details at https://RandomNerdTutorials.com

from machine import Pin
from time import sleep
import dht 
p2 = Pin(22, Pin.IN,Pin.PULL_UP)
#sensor = dht.DHT22(Pin(22))
#sensor = dht.DHT11(Pin(14))
     # create input pin on GPIO2
print(p2.value())       # get value, 0 or 1
while True:
  try:
    sleep(2)
    print(p2.value()) 
    '''sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    print('Temperature: %3.1f C' %temp)
    print('Temperature: %3.1f F' %temp_f)
    print('Humidity: %3.1f %%' %hum)'''
  except OSError as e:
    print('Failed to read sensor.')
