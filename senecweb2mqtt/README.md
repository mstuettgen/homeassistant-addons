# Senec Web2MQTT
Reads stats from Senec Web API and publishes them as MQTT device to home assistant

## DISCLAIMER
I is not really an "addon" at this point, it's more of a working prototype.

### Requirements
- An MQTT Broker, e.g. mosquitto. Can be installed by going to Settings -> Addons -> Addon Store -> Mosquitto
- The HA MQTT Integration. Can be installed by going to Settings -> Devices and Services -> Add Integration -> MQTT. 
When setting up the MQTT integration, use "core-mosquitto" as MQTT broker when you are using the Mosquitto-Addon. Else use te IP adress of your own MQTT broker

### Configuration 
The configuration is done in the .env file. Change everything accordingly to your setup. Example Configuration:
#### ".env" :
```
# MQTT parameters
MQTT_USERNAME='your-mqtt-username'
MQTT_PASSWORD='your-mqtt-password'
MQTT_HOST='192.168.1.2'
MQTT_PORT=1883
MQTT_TOPIC_PREFIX='homeassistant/sensor/'
MQTT_SENSOR_NAME_PREFIX='senec' #arbitrary, results in e.g. "senec_acculevel_now" as sensorname
MQTT_DEVICE_NAME='Senec Home V4' #arbitrary, name of MQTT device in home assistant
MQTT_DEVICE_IDENTIFIER='xx-xxxxxxxx' #serial number of device, used for unique entity ids
MQTT_DEVICE_MANUFACTURER='Senec' #arbitrary, mqtt device information
MQTT_DEVICE_MODEL='Home V4' #arbitrary, mqtt device information

# Credentials for Senec Website
SENEC_USERNAME='mail@example.com'
SENEC_PASSWORD='supersafepassword'
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


