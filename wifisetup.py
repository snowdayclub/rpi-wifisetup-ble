#!/usr/bin/env python3

import dbus
import subprocess

#
# Copy following files from https://github.com/Douglas6/cputemp into the folder
#
#   advertisement.py
#   bletools.py
#   service.py
#
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from wpamanager import WPAManager

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

class DeviceAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("RPi WiFi Setup")
        self.include_tx_power = True

        self.ssid = ''
        self.psk = ''
        self.ipaddr = ''


class DeviceService(Service):
    DEVICE_SERVICE_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):
        Service.__init__(self, index, self.DEVICE_SERVICE_UUID, True)
        self.add_characteristic(SSIDCharacteristic(self))
        self.add_characteristic(PSKCharacteristic(self))
        self.add_characteristic(IPAddrCharacteristic(self))
        self.add_characteristic(RestartWPACharacteristic(self))


class SSIDCharacteristic(Characteristic):
    SSID_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.SSID_CHARACTERISTIC_UUID,
                ["read", "write"], service)
        self.add_descriptor(SSIDDescriptor(self))

    def WriteValue(self, value, options):
        self.service.ssid = ''.join([str(v) for v in value])

    def ReadValue(self, options):
        value = []

        for c in self.service.ssid:
            value.append(dbus.Byte(c.encode()))

        return value


class SSIDDescriptor(Descriptor):
    SSID_DESCRIPTOR_UUID = "2901"
    SSID_DESCRIPTOR_VALUE = "SSID of the Access Point"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.SSID_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.SSID_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class PSKCharacteristic(Characteristic):
    PSK_CHARACTERISTIC_UUID = "00000003-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.PSK_CHARACTERISTIC_UUID,
                ["write"], service)
        self.add_descriptor(PSKDescriptor(self))

    def WriteValue(self, value, options):
        self.service.psk = ''.join([str(v) for v in value])


class PSKDescriptor(Descriptor):
    PSK_DESCRIPTOR_UUID = "2901"
    PSK_DESCRIPTOR_VALUE = "Pre-Shared Key of the Access Point"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.PSK_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.PSK_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class IPAddrCharacteristic(Characteristic):
    IPADDR_CHARACTERISTIC_UUID = "00000004-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
                self, self.IPADDR_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(IPAddrDescriptor(self))

    def get_ipaddr(self):
        value = []
        result = subprocess.run(['hostname', '--all-ip-addresses'],
                stdout=subprocess.PIPE)
        ipaddr = result.stdout.decode('utf-8').split(' ')[0].rstrip()

        for c in ipaddr:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_ipaddr_callback(self):
        if self.notifying:
            value = self.get_ipaddr()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True

        value = self.get_ipaddr()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_ipaddr_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_ipaddr()

        return value


class IPAddrDescriptor(Descriptor):
    IPADDR_DESCRIPTOR_UUID = "2901"
    IPADDR_DESCRIPTOR_VALUE = "IP Address"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.IPADDR_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.IPADDR_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class RestartWPACharacteristic(Characteristic):
    RSTWPA_CHARACTERISTIC_UUID = "00000005-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.RSTWPA_CHARACTERISTIC_UUID,
                ["write"], service)
        self.add_descriptor(RestartWPADescriptor(self))

    def WriteValue(self, value, options):
        if self.service.ssid == '':
            return

        wpa = WPAManager()
        wpa.set_network({'ssid':self.service.ssid,'psk':self.service.psk})
        wpa.reconfigure()


class RestartWPADescriptor(Descriptor):
    RSTWPA_DESCRIPTOR_UUID = "2901"
    RSTWPA_DESCRIPTOR_VALUE = "Restart WiFi Network"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.RSTWPA_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.RSTWPA_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value



#-------------------------------------------------------------------------------
if __name__ =='__main__':

    app = Application()
    app.add_service(DeviceService(0))
    app.register()

    adv = DeviceAdvertisement(0)
    adv.register()

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
