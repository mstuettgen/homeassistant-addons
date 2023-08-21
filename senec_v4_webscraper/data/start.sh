#!/usr/bin/env bashio

#INTERVAL=$(bashio::config 'interval')

bashio::log.info '======================================'
bashio::log.info '====== Start Senec Web Scraper ======='
bashio::log.info '======================================'

while true; do
    bashio::log.info "starting senec webscraper"
    python3 /hello_world.py
    bashio::log.info "Completedd one cycle" 
    sleep(1)
done
