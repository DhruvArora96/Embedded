from machine import Pin, I2C
import utime as time
from umqtt.simple import MQTTClient
import network
import machine
import ujson

#Constructing an I2C bus
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

#Defining broker address, SSID and broker password

#Details to connect to College broker
#BROKER_ADDRESS= "192.168.0.10"   
#SSID = 'EEERover'
#PASSWORD = 'exhibition'

#Details to connect to Thingspeak broker
BROKER_ADDRESS= "mqtt.thingspeak.com"
SSID = 'Xperia Z3_62d1'
PASSWORD = 'exhibition'

#Connecting to the network
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)

#Waiting for network to connect before proceeding with execution of code.
while not sta_if.isconnected():
  pass
print("Connected to network")

#Activating the real time clock and initialising its value.
rtc = machine.RTC()
rtc.datetime((2017, 2, 15, 10, 48, 0, 0, 0))

#Defining thingspeak channel information and connecting to it.
thingspeakChannelId = "227308" 
thingspeakChannelWriteapi = "D14PP8N2KQE082IJ"
c = MQTTClient("Dhruv",BROKER_ADDRESS, 1883)  
c.connect()

#Defining temperature threshold for abnormal temperature outside of cooking hours.
temp_threshold= 32
##Defining temperature threshold for oil fires.
temp_burning= 280

#Defining a function to fill an array of 48 elements, each corresponding to half an hour slots, 
#starting at midnight and ending at midnight of the next day.
#Time slots in which the user usually cooks are set to 1. Otherwise set to 0.
def set_array(array):
	array[0] = 0 #00:00 am
	array[1] = 0 #00:30 am
	array[2] = 0 #01:00 am
	array[3] = 0 #01:30 am
	array[4] = 0 #02:00 am
	array[5] = 0 #02:30 am
	array[5] = 0 #03:00 am
	array[7] = 0 #03:30 am
	array[8] = 0 #04:00 am
	array[9] = 0 #04:30 am
	array[10] = 0 #05:00 am
	array[11] = 0 #05:30 am
	array[12] = 0 #06:00 am
	array[13] = 0 #06:30 am
	array[14] = 0 #07:00 am
	array[15] = 1 #07:30 am
	array[16] = 0 #08:00 am
	array[17] = 0 #08:30 am
	array[18] = 0 #09:00 am
	array[19] = 0 #09:30 am
	array[20] = 0 #10:00 am
	array[21] = 0 #10:30 am
	array[22] = 0 #11:00 am
	array[23] = 1 #11:30 am
	array[24] = 1 #12:00 am
	array[25] = 1 #12:30 am
	array[26] = 1 #01:00 pm
	array[27] = 0 #01:30 pm
	array[28] = 0 #02:00 pm
	array[29] = 0 #02:30 pm
	array[30] = 0 #03:00 pm
	array[31] = 0 #03:30 pm
	array[32] = 0 #04:00 pm
	array[33] = 0 #04:30 pm
	array[34] = 0 #05:00 pm
	array[35] = 0 #05:30 pm
	array[36] = 0 #06:00 pm
	array[37] = 1 #06:30 pm
	array[38] = 1 #07:00 pm
	array[39] = 1 #07:30 pm
	array[40] = 1 #08:00 pm
	array[41] = 1 #08:30 pm
	array[42] = 0 #09:00 pm
	array[43] = 0 #09:30 pm
	array[44] = 0 #10:00 pm
	array[45] = 0 #10:30 pm
	array[46] = 0 #11:00 pm
	array[47] = 0 #11:30 pm

#Declaring a an array of 48 bytearray and fill that array through the set_array function.
time_array=bytearray(48)
set_array(time_array)
	
#Formatting the data (temperature and time) in json.
def output(TimeNow, cTemp):
	out= ujson.dumps({'time':TimeNow,'temperature': cTemp})
	return out

#Infinite loop enetered after the initialisations.
while True:
	
	#Reading temperature data from the object register on the sensor.
	raw= i2c.readfrom_mem(64,0x03,2)
	
	#Converting the temperature data in Celsius.
	cTemp = (raw[0]*256+raw[1])/ 4
	if cTemp > 8191 :
		cTemp -= 16384
	cTemp = cTemp * 0.03125
	
	#Reading temperature data from the die register on the sensor.
	raw1= i2c.readfrom_mem(64,0x01,2)
	
	#Converting the temperature data in Celsius.
	cTemp1 = (raw1[0]*256 + raw1[1])/4
	if cTemp1 > 8191 :
		cTemp1 -= 16384
	cTemp1 = cTemp1 * 0.03125
	
	
	#Returning seconds since clock was initialised as an integer.
	now=time.time()
	#Taking the seconds as input and formatting it into complete date and time format: 
	#[year month day hour minute second weekday yearday]
	#NOTE: last two variables set to 0.
	tm=time.localtime(now)
	
	#If 30 minutes have passed, flag is set to 1, else stays at 0.
	if tm[4]>30:
		thirty_mins_flag=1 
		
	else :
		thirty_mins_flag=0 
		
	#Counter to keep track of how many 30 mins slots have passed:
	#multiply hours passed by two and add the flag for the latest 30 mins passed.
	thirty_min_segment=(tm[3]*2)+thirty_mins_flag
	
	#Retrieving the value of the time_array index corresponding to the current 30 mins slot and storing it in a flag for cooking.
	cooking_flag=time_array[thirty_min_segment]
	
	#If the user is not expected to be cooking but the temperature sensed is above cooking threshold, publish an alert.
	if cooking_flag==0 and cTemp>temp_threshold :
				
		#Publishing to ThingSpeak.
		credentials = "channels/{:s}/publish/{:s}".format(thingspeakChannelId, thingspeakChannelWriteapi)  
		payload = "field1={:}&field3=1\n".format(output(now, cTemp))
		c.publish(credentials, payload)
		print(str(output(tm,cTemp)))
		
	#Regardless of whether the user is expected to be cooking, if the temperature sensed is above oil fire temperature, publish an alert.
	elif cTemp > temp_burning :
			
		#Publishing to ThingSpeak.
		credentials = "channels/{:s}/publish/{:s}".format(thingspeakChannelId, thingspeakChannelWriteapi)  
		payload = "field1={:}&field3=1\n".format(output(now, cTemp))
		c.publish(credentials, payload)
		print(str(output(tm,cTemp)))
				
	time.sleep(5)

	
