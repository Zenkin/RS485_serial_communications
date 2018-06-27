#!/usr/bin/python2

import rospy
from std_msgs.msg import String
from temperature_sensor.msg import temperature as temperature_msg
from temperature_sensor.msg import humidity as humidity_msg
from temperature_sensor.srv import temperature_service, temperature_serviceResponse
from temperature_sensor.srv import humidity_service, humidity_serviceResponse
from temperature_sensor.srv import update_service, update_serviceResponse
import threading
from HTT100 import *

debug = True
lock = threading.Lock()

class Node:

    repeat = False


    def publication_period_controll(self):
        if self.publication_period == 0:
            Node.repeat = False
        else:
            Node.repeat = True
            if debug:
                rospy.loginfo("publication_period_controll:repeat: True")
        

    def clear_parameters(self):
        if debug:
            rospy.loginfo("Clear all parameters [Used when parameters were not set]")
        try:
            rospy.delete_param("/temperature_sensor")
        except KeyError:
            if debug:
                rospy.loginfo("Nothing to clean [parameters were not set]")


    def init(self):
        rospy.init_node('sensor', anonymous=True)
        try:
            self.port = rospy.get_param("/temperature_sensor/port")
            error_get_param = False
        except:
            error_get_param = True
        try:
            self.slave_adress = rospy.get_param("/temperature_sensor/slave_adress")
            error_get_param = False
        except:
            error_get_param = True
        try:
            self.baudrate = rospy.get_param("/temperature_sensor/baudrate")
            error_get_param = False
        except:
            error_get_param = True
        try:
            self.capture_time = rospy.get_param("/temperature_sensor/capture_time")
            error_get_param = False
        except:
            error_get_param = True
        try:
            self.publication_period = rospy.get_param("/temperature_sensor/publication_period")
            error_get_param = False
        except:
            error_get_param = True
        if error_get_param:
            self.clear_parameters()
            if debug:
                rospy.loginfo("Can't find parameters. Set default values ...")
            self.set_default_parameters()
            self.get_parameters()
        if debug:
            self.print_loginfo()

        self.sensor = HTT100(self.port, self.slave_adress, self.baudrate, parity, bytesize, stopbits, timeout)


    def print_loginfo(self):
        rospy.loginfo("port: " + self.port)
        rospy.loginfo("slave adress: " + str(self.slave_adress))
        rospy.loginfo("baudrate: " + str(self.baudrate))
        rospy.loginfo("capture time: " + str(self.capture_time))
        rospy.loginfo("publicationp period: " + str(self.publication_period))        


    def set_default_parameters(self):
        rospy.set_param("/temperature_sensor/port", "/dev/ttyUSB1")
        rospy.set_param("/temperature_sensor/slave_adress", 16)
        rospy.set_param("/temperature_sensor/baudrate", 9600)
        rospy.set_param("/temperature_sensor/capture_time", 10)
        rospy.set_param("/temperature_sensor/publication_period", 30)


    def get_parameters(self):
        self.port = rospy.get_param("/temperature_sensor/port")
        self.slave_adress = rospy.get_param("/temperature_sensor/slave_adress")
        self.baudrate = rospy.get_param("/temperature_sensor/baudrate")
        self.capture_time = rospy.get_param("/temperature_sensor/capture_time")
        self.publication_period = rospy.get_param("/temperature_sensor/publication_period")          


    def start_publication(self):
        temperature_message = temperature_msg()
        humidity_message = humidity_msg()
        self.publication_period_controll()
        temperature_publication = rospy.Publisher('HTT100/temperature', temperature_msg, queue_size=10)
        humidity_publication = rospy.Publisher('HTT100/humidity', humidity_msg, queue_size=10)
        if Node.repeat:
            while not rospy.is_shutdown():
                # form a message with temperature
                temperature_message.port = self.port
                temperature_message.header.stamp = rospy.Time.now()
                temperature_message.header.frame_id = "temperure_sensor"
                lock.acquire()
                temperature_value = self.get_temperature()
                lock.release()
                if temperature_value == "error_get_temperature":
                    temperature_message.success = False
                    temperature_message.temperature = 0
                else:
                    temperature_message.success = True
                    temperature_message.temperature = temperature_value
                # form a message with humidity
                humidity_message.port = self.port
                humidity_message.header.stamp = rospy.Time.now()
                humidity_message.header.frame_id = "humidity_sensor"
                lock.acquire()
                humidity_value = self.get_humidity()
                lock.release()
                if humidity_value == "error_get_humidity":
                    humidity_message.success = False
                    humidity_message.humidity = 0
                else:
                    humidity_message.success = True
                    humidity_message.humidity = humidity_value
                # publish messages with temperature and humidity
                temperature_publication.publish(temperature_message)
                humidity_publication.publish(humidity_message)
                time.sleep(self.publication_period)
        else:
            rospy.loginfo("Repear = False")
            lock.acquire()
            temperature_message.port = self.port
            lock.release()
            temperature_message.header.stamp = rospy.Time.now()
            temperature_message.header.frame_id = "temperure_sensor"
            lock.acquire()
            temperature_value = self.get_temperature()
            lock.release()
            if temperature_value == "error_get_temperature":
                temperature_message.success = False
                temperature_message.temperature = 0
            else:
                temperature_message.success = True
                temperature_message.temperature = temperature_value
            lock.acquire()
            humidity_message.port = self.port
            lock.release()
            humidity_message.header.stamp = rospy.Time.now()
            humidity_message.header.frame_id = "humidity_sensor"
            lock.acquire()
            humidity_value = self.get_humidity()
            lock.release()
            if humidity_value == "error_get_humidity":
                humidity_message.success = False
                humidity_message.humidity = 0
            else:
                humidity_message.success = True
                humidity_message.humidity = humidity_value
            time.sleep(0.1)
            
            temperature_publication.publish(temperature_message)
            humidity_publication.publish(humidity_message)


    def get_temperature(self):
        return self.sensor.get_temperature()


    def get_humidity(self):
        return self.sensor.get_humidity()


    def temperature_service_callback(self, request):
        temperature_message_response = temperature_serviceResponse()
        lock.acquire()
        temperature_message_response.temperature = 25
        #temperature_message_response.temperature = self.get_temperature()
        temperature_message_response.port = self.port
        temperature_message_response.header.stamp = rospy.Time.now()
        temperature_message_response.header.frame_id = "temperure_sensor"
        lock.release()

        return temperature_message_response


    def humidity_service_callback(self, request):
        humidity_message_response = humidity_serviceResponse()
        lock.acquire()
        humidity_message_response.humidity = 25
        #humidity_message_response.humidity = self.get_humidity()
        humidity_message_response.port = self.port
        humidity_message_response.header.stamp = rospy.Time.now()
        humidity_message_response.header.frame_id = "temperure_sensor"
        lock.release()

        return humidity_message_response


    def update_service_callback(self, request):
        update_message_response = update_serviceResponse()
        lock.acquire()
        self.get_parameters()
        lock.release()
        update_message_response.header.stamp = rospy.Time.now()
        update_message_response.header.frame_id = "update_service"
        lock.acquire()
        self.sensor = HTT100(self.port, self.slave_adress, self.baudrate, parity, bytesize, stopbits, timeout)
        lock.release()
        update_message_response.log = "Parameters have been changed successfully"

        return update_message_response


if __name__ == '__main__':
    try:
        node = Node()
    except rospy.ROSInterruptException:
        pass
    try:
        node.init()
    except rospy.ROSInterruptException:
        pass
    try:
        rospy.Service('get_temperature', temperature_service, node.temperature_service_callback)
    except:
        rospy.loginfo("Failed to start the temperature server")
    try:
        rospy.Service('get_humidity', humidity_service, node.humidity_service_callback)
    except:
        rospy.loginfo("Failed to start the humidity server")
    try:
        rospy.Service('update_parameters', update_service, node.update_service_callback)
    except:
        rospy.loginfo("Failed to start the humidity server")
    try:
        node.start_publication()
    except rospy.ROSInterruptException:
        pass
