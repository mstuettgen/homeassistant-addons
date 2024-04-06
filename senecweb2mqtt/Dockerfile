ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
    apk add --no-cache \
    python3 \ 
    py3-paho-mqtt \
    py3-requests
  
# Copy data for add-on
COPY run.sh /
COPY senec_mqtt_device.py /
COPY senec_webgrabber.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
