#!/usr/bin/env python3
#
# it requires root priviledge to use WPAManager
#
from wpamanager import WPAManager
import socket
import time

#-------------------------------------------------------------------------------
if __name__=='__main__':

    wpa = WPAManager()

    print(wpa.get_network_list())
    wpa.set_network({'ssid':'my_ssid', 'psk':'my_ssid_secret', 'foo':'bar'})
    print(wpa.get_network_list())
    print('restarting wifi')
    wpa.reconfigure()

    for idx in range(30):
        ssid = wpa.get_current_ssid()
        if ssid is None:
            print('...connecting')
            time.sleep(1)
        else:
            print('\nconnected to: {}'.format(ssid))
            print('ip address:', wpa.get_current_ipaddress())
            break

    if idx == 30:
        print('failed to connect to AP')

