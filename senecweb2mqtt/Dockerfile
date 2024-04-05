ARG BUILD_FROM
FROM $BUILD_FROM

# Copy data for add-on
COPY run.sh /
COPY .env /
COPY senec_mqtt_device.py /
COPY senec_webgrabber.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]