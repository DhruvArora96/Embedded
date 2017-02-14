from machine import Pin, I2C
import time
from umqtt.simple import MQTTClient
import network
import machine
import ujson
# construct an I2C bus
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
# i2c.writeto_mem(64,0x02,conf0)
# CLIENT_ID =  b"esp8266_" + ubinascii.hexlify(machine.unique_id())
# broker = "192.168.0.10"
# client = MQTTClient(CLIENT_ID,broker)

    
SSID = 'Xperia Z3_62d1'
PASSWORD = 'e2341fb5c0ca'

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)

while not sta_if.isconnected():
  pass

rtc = machine.RTC()
rtc.datetime((2017, 2, 9, 4, 10, 40, 0, 0))
thingspeakChannelId = "227308" 
thingspeakChannelWriteapi = "D14PP8N2KQE082IJ"
c = MQTTClient("ESP8266","mqtt.thingspeak.com", 1883)  
c.connect()
    
	
def output(TimeNow, cTemp):
	out= ujson.dumps({'time':TimeNow,'temperature': cTemp})
	return out
while True:
	raw= i2c.readfrom_mem(64,0x03,2)
	cTemp = (raw[0]*256+raw[1])/ 4
	
	if cTemp > 8191 :
		cTemp -= 16384
	cTemp = cTemp * 0.03125
	print ("Object Temperature in Celsius : %.2f C" %cTemp)
	
	
	raw1= i2c.readfrom_mem(64,0x01,2)
	cTemp1 = (raw1[0]*256 + raw1[1])/4	
	TimeNow = rtc.datetime()
	
	if cTemp1 > 8191 :
		cTemp1 -= 16384
	cTemp1 = cTemp1 * 0.03125
	print ("Sensor Temperature in Celsius : %.2f C" %cTemp1)
	credentials = "channels/{:s}/publish/{:s}".format(thingspeakChannelId, thingspeakChannelWriteapi)  
	payload = "field1={:.1f}\n".format(cTemp1)
	c.publish(credentials, payload)
	time.sleep(5)