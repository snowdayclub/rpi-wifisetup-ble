# What It Does

It creates a GATT server and exposes characteristics through which you can
set up WiFi connection of the Raspberry Pi.


# Dependencies

This python program relies on the python GATT server example for the Raspberry
Pi by [Douglas Otwell.](https://github.com/Douglas6/cputemp)

Once you clond this repo, you need to copy following files from the above
repository into the folder:

* advertisement.py
* bletools.py
* service.py

# Exposed Characteristics

* SSID of the Access Point: read, write
* PSK of the Access Point: write
* IP Address: read, notify
* Restart WiFi Network: write

# How to Use

Be sure to meet the dependency requirements above.
Run the script with root privilege:
```
$ sudo python3 wifisetup.py
```

Use [nRF Connect app](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp&hl=en_CA&gl=US), set SSID and PSK of the access point.
Then write any value, e.g. `0x00` to `Restart WiFi Network` characteristic.
You can read periodically `IP Address` characteristics to monitor the
connection state.
