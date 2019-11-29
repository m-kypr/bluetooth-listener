#!/usr/bin/python

import os
import sys
import signal
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject

import RPi.GPIO as GPIO
import time

BLUEZ_DEV = "org.bluez.MediaControl1"
AUX_PIN = 40
CBLSAT_PIN = 38


def trigger_pin(pin):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pin, GPIO.LOW) 


def device_property_changed_cb(property_name, value, path, interface, device_path):
    global bus
    if property_name != BLUEZ_DEV:
        return

    device = dbus.Interface(bus.get_object("org.bluez", device_path), "org.freedesktop.DBus.Properties")
    properties = device.GetAll(BLUEZ_DEV)

#    print(properties)
    if properties["Connected"]:
        print('Connected!')
        trigger_pin(AUX_PIN)

    else:
       	print('Disconnected!')
        trigger_pin(CBLSAT_PIN)

def shutdown(signum, frame):
    mainloop.quit()


if __name__ == "__main__":

    # Setup GPIO pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(AUX_PIN, GPIO.OUT)
    GPIO.setup(CBLSAT_PIN, GPIO.OUT)
    
    # shut down on a TERM signal
    signal.signal(signal.SIGTERM, shutdown)
    
    print('Monitoring Bluetooth Connections... ')

    # Get the system bus
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
    except Exception as ex:
       sys.exit(1)
    
    # listen for signals on the Bluez bus
    bus.add_signal_receiver(device_property_changed_cb, bus_name="org.bluez", signal_name="PropertiesChanged", path_keyword="device_path", interface_keyword="interface")

    try:
        mainloop = gobject.MainLoop()
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except:
       sys.exit(1)

    sys.exit(0)

