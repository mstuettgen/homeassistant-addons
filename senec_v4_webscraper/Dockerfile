ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

# Setup base
RUN pip3 install requests

# Copy data
COPY data/start.sh /
COPY data/*.py /

RUN chmod a+x /*.sh
RUN chmod a+x /*.py

CMD ["/start.sh"]
