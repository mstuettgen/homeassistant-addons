# Senec Web2MQTT
Reads stats from Senec Web API and publishes them as MQTT device to home assistant

## Getting started
I is not really an "addon" at this point, it's more of a working prototype.

### Requirements
- An MQTT Broker, e.g. mosquitto. Can be installed by going to Settings -> Addons -> Addon Store -> Mosquitto
- The HA MQTT Integration. Can be installed by going to Settings -> Devices and Services -> Add Integration -> MQTT. 
When setting up the MQTT integration, use "core-mosquitto" as MQTT broker when you are using the Mosquitto-Addon. Else use te IP adress of your own MQTT broker

### Configuration
in "senec_webgrabber.py" :
enter your senec credentials in the following lines:
```
self._SENEC_USERNAME = "" # your senec login username
self._SENEC_PASSWORD = "" # your senec password
```

in "senec_mqtt_device.py" :
enter your device information in te following lines:
```
self._MQTT_USERNAME = ""  # your mqtt username
self._MQTT_PASSWORD =  "" # your mqtt password
self._MQTT_HOST = "" # IP adress of homeassitant when using home assistant mqtt broker, else IP adress of broker
self._MQTT_PORT = "1883" # default MQTT port

self._SENSOR_NAME_PREFIX = "senec" #arbitrary, used for sensor name generation. results in e.g. "senec_acculevel_now" as sensorname
self._DEVICE_NAME = "Senec Home V4" #arbitrary, used to generate the name of the MQTT device in HA
self._DEVICE_IDENFIER = "XXXXXXXXXXXXXXX" #serial number of your senec (can be looked up in app), used for generation of entity unique ids
self._DEVICE_MANUFACTURER = "Senec" #arbitrary, will be shown in MQTT device information
self._DEVICE_MODEL = "Home V4" #arbitrary, will be shown in MQTT device information
```

## Manual start/stop
run
```bash
python3 senec_mqtt_device.py
``` 

## Setting up a systemd service (Debian)
create a file 
```
/etc/systemd/system/senecweb2mqtt.service
```
with content
```
[Unit]
Description=Senec Web2MQTT
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=30
TimeoutStopSec=15
User=pi <- Change this to your actual username
ExecStart=python3 <abs_path_to>/senec_mqtt_device.py <- change path here accordingly

[Install]
WantedBy=multi-user.target
```

then
```
sudo systemctl enable senecweb2mqtt.service
sudo systemctl start senecweb2mqtt.service
sudo systemctl status senecweb2mqtt.service
```

![grafik](https://github.com/mstuettgen/homeassistant-addons/assets/10927858/a0d2c28b-7ee6-4267-847b-80b5509108c0)


