#!/usr/bin/python

import os
import sys
import signal
# import logging
# import logging.handlers
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject

import subprocess

# LOG_LEVEL = logging.INFO
# LOG_LEVEL = logging.DEBUG
# LOG_FILE = "/dev/log"
# LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
BLUEZ_DEV = "org.bluez.MediaControl1"
AUX_FILE = "switch-to-aux"
CBLSAT_FILE = "switch-to-cblsat"


def exec_bash_command(bash_command):
    process = subprocess.Popen(bash_command.split(), stout=subprocess.PIPE)
    output, error = process.communicate()


def device_property_changed_cb(property_name, value, path, interface, device_path):
    global bus
    if property_name != BLUEZ_DEV:
        return

    device = dbus.Interface(bus.get_object("org.bluez", device_path), "org.freedesktop.DBus.Properties")
    properties = device.GetAll(BLUEZ_DEV)

#    logger.info("Getting dbus interface for device: %s interface: %s property_name: %s" % (
#        device_path, interface, property_name))

    print(properties)
    if properties["Connected"]:
        print('he connected!')
        exec_bash_command(f'./{AUX_FILE}')	
#        bt_addr = "_".join(device_path.split('/')[-1].split('_')[1:])
#        cmd = "pactl load-module module-loopback source=bluez_source.%s" % bt_addr
#        logger.info("Running cmd: %s" % cmd)
#        os.system(cmd)
    else:
       	print('he disconnected!')
        exec_bash_command(f'./{CBLSAT_FILE}')
#        bt_addr = "_".join(device_path.split('/')[-1].split('_')[1:])
#        logger.info("Device: %s has disconnected" % bt_addr)
#        cmd = "for i in $(pactl list short modules | grep module-loopback | grep source=bluez_source.%s | cut -f 1); do pactl unload-module $i; done" % bt_addr
#        logger.info("Running cmd: %s" % cmd)
#        os.system(cmd)


def shutdown(signum, frame):
    mainloop.quit()


if __name__ == "__main__":
    # shut down on a TERM signal
    signal.signal(signal.SIGTERM, shutdown)

    # start logging
#    logger = logging.getLogger("bt_auto_loader")
#    logger.setLevel(LOG_LEVEL)
#    logger.addHandler(logging.handlers.SysLogHandler(address="/dev/log"))
#    logger.info("Starting to monitor Bluetooth connections")
    print('Monitoring Bluetooth Connections... ')

    # Get the system bus
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
    except Exception as ex:
#        logger.error(
#            "Unable to get the system dbus: '{0}'. Exiting. Is dbus running?".format(ex.message))
        sys.exit(1)

    # listen for signals on the Bluez bus
    bus.add_signal_receiver(device_property_changed_cb, bus_name="org.bluez", signal_name="PropertiesChanged", path_keyword="device_path", interface_keyword="interface")

    try:
        mainloop = gobject.MainLoop()
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except:
#        logger.error("Unable to run the gobject main loop")
        sys.exit(1)

#    logger.info("Shutting down")
    sys.exit(0)