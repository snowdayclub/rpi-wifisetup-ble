#!/usr/bin/env python3
import subprocess


class WPAManager:
    def __init__(self):
        self._config_file = '/etc/wpa_supplicant/wpa_supplicant.conf'
        self._load_config()

    def _default_config(self):
        self._ctrl_interface = 'DIR=/var/run/wpa_supplicant GROUP=netdev'
        self._update_config = '1'
        self._country = 'US'
        self._networks = []

    def _load_config(self):
        self._default_config()
        ntw = False
        with open(self._config_file, 'r') as f:
            for line in f:
                if 'ctrl_interface' in line:
                    self._ctrl_interface = line[line.find('=')+1:].rstrip()
                elif 'update_config' in line:
                    self._update_config = line[line.find('=')+1:].rstrip()
                elif 'country' in line:
                    self._country = line[line.find('=')+1:].rstrip()
                elif 'network' in line:
                    ntw = True
                    network = {}
                elif ntw:
                    if 'ssid' in line:
                        network['ssid'] = line[
                                line.find('\"')+1: line.rfind('\"')].rstrip()
                    elif 'psk' in line:
                        network['psk'] = line[
                                line.find('\"')+1: line.rfind('\"')].rstrip()
                    elif 'scan_ssid' in line:
                        network['scan_ssid'] = line[line.find('='):].rstrip()
                    elif 'proto' in line:
                        network['proto'] = line[line.find('='):].rstrip()
                    elif 'key_mgmt' in line:
                        network['key_mgmt'] = line[line.find('='):].rstrip()
                    elif 'pairwise' in line:
                        network['pairwise'] = line[line.find('='):].rstrip()
                    elif 'auth_alg' in line:
                        network['auth_alg'] = line[line.find('='):].rstrip()
                    elif '}' in line:
                        ntw = False
                        self._networks.append(network)

    def _save_config(self):
        with open(self._config_file, 'w') as f:
            f.write('ctrl_interface={}\n'.format(self._ctrl_interface))
            f.write('update_config={}\n'.format(self._update_config))
            f.write('country={}\n'.format(self._country))

            for network in  self._networks:
                f.write('\nnetwork={\n')
                f.write('\tssid=\"{}\"\n'.format(network['ssid']))
                f.write('\tpsk=\"{}\"\n'.format(network['psk']))

                if 'scan_ssid' in network:
                    f.write('\tscan_ssid=\"{}\"\n'.format(network['scan_ssid']))
                if 'proto' in network:
                    f.write('\tproto=\"{}\"\n'.format(network['proto']))
                if 'key_mgmt' in network:
                    f.write('\tkey_mgmt=\"{}\"\n'.format(network['key_mgmt']))
                if 'pairwise' in network:
                    f.write('\tpairwise=\"{}\"\n'.format(network['pairwise']))
                if 'auth_alg' in network:
                    f.write('\tauth_alg=\"{}\"\n'.format(network['auth_alg']))
                f.write('}\n')

    def _show_config(self):
        print('config file:', self._config_file)
        print('ctrl_interface:', self._ctrl_interface)
        print('update_config:', self._update_config)
        print('country:', self._country)
        print('networks:', self._networks)

    def get_network_list(self):
        return self._networks

    def reconfigure(self):
        self._save_config()
        subprocess.run(['wpa_cli', '-i', 'wlan0', 'reconfigure'])

    def set_network(self, new_network):
        if 'ssid' not in new_network:
            return False
        if 'psk' not in new_network:
            return False

        self.del_network_by_ssid(new_network['ssid'])
        self._networks.append(new_network)

    def del_network_by_ssid(self, ssid):
        for idx, network in enumerate(self._networks):
            if network['ssid'] == ssid:
                self._networks.pop(idx)
                break

    def clear_networks(self):
        self._networks = []

    def get_current_ssid(self):
        result = subprocess.run(['iwgetid'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        if 'ESSID' in output:
            ssid = output[output.find('\"')+1:output.rfind('\"')]
            if ssid != "":
                return ssid
            else:
                return None
        else:
            return None

    def get_current_ipaddress(self):
        result = subprocess.run(['hostname', '--all-ip-addresses'],
                stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8').rstrip()

