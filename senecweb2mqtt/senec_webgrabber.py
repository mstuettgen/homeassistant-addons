'''
Logs in to Senec website and reads all specified information from SENEC WEB API
'''

import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
     w = SenecWebGrabber()
     w.update()

class SenecWebGrabber:
    def __init__(self) -> None:

        #SENEC API
        self._SENEC_USERNAME = "" # your senec login username
        self._SENEC_PASSWORD = "" # your senec password
        self._SENEC_AUTH_URL = "https://mein-senec.de/auth/login"
        self._SENEC_API_OVERVIEW_URL = "https://mein-senec.de/endkunde/api/status/getstatusoverview.php?anlageNummer=0"
        self._SENEC_API_URL_START="https://mein-senec.de/endkunde/api/status/getstatus.php?type="
        self._SENEC_API_URL_END="&period=all&anlageNummer=0"
        
        #can be used in all api calls, names come from senec website
        self._API_KEYS = [
            "accuimport",  # what comes OUT OF the accu
            "accuexport",  # what goes INTO the accu         
            "gridimport",  # what comes OUT OF the grid
            "gridexport",  # what goes INTO the grid 
            "powergenerated", # power produced
            "consumption" # power used
        ]

        #can only be used in some api calls, names come from senec website
        self._API_KEYS_EXTRA = [
            "acculevel" #accu level
        ]

        #WEBDATA STORAGE
        self._energy_entities = {}
        self._power_entities = {}
        self._battery_entities = {}
        self.isAuthenticated = False

        #WEBSESSION
        self._session = requests.Session()


    def authenticate(self) -> None:
        auth_payload = {
            "username" : self._SENEC_USERNAME,
            "password" : self._SENEC_PASSWORD
        }
        r = self._session.post(self._SENEC_AUTH_URL, auth_payload)
        if r.status_code == 200:
            logger.info("Login successful")
            self.isAuthenticated=True
        else:
            logger.info("Login failed with Code " + str(r.status_code))
    


    def update(self) -> None:
        logger.debug("***** update(self) ********")

        if self.isAuthenticated:
            self.update_now_kW_stats()
            self.update_full_kWh_stats()

            logger.debug("Results:")
            logger.debug("********* energy_entities ***************")
            for key in self._energy_entities:
                logger.debug(str(key) + ": "+ str(self._energy_entities[key]))
                
            logger.debug("********* power_entities *****************")
            for key in self._power_entities:
                logger.debug(str(key) + ": "+ str(self._power_entities[key]))

            logger.debug("********* battery_entities *****************")
            for key in self._battery_entities:
                logger.debug(str(key) + ": "+ str(self._battery_entities[key]))
        else:
            self.authenticate()
            self.update()


    def update_now_kW_stats(self) -> None:
        logger.debug("***** update_now_kW_stats(self) ********")
        
        #grab NOW and TODAY stats
        r=self._session.get(self._SENEC_API_OVERVIEW_URL)
        
        if r.status_code==200:
            r_json = json.loads(r.text)
            #logger.debug(r_json)
            
            for key in (self._API_KEYS+self._API_KEYS_EXTRA):
                if(key!="acculevel"):
                    value_now = r_json[key]["now"]
                    entity_now_name = str(key + "_now")
                    self._power_entities[entity_now_name]=value_now

                    value_today = r_json[key]["today"]
                    entity_today_name = str(key + "_today")
                    self._energy_entities[entity_today_name]=value_today
                else:
                    value_now = r_json[key]["now"]
                    entity_now_name = str(key + "_now")
                    self._battery_entities[entity_now_name]=value_now

                    #value_today = r_json[key]["today"]
                    #entity_today_name = str(key + "_today")
                    #self._battery_entities[entity_today_name]=value_today
        else:
            self._isAuthenticated=False
            self.update()
        
    def update_full_kWh_stats(self) -> None:
        #grab TOTAL stats
        for key in self._API_KEYS:
            api_url = self._SENEC_API_URL_START + key + self._SENEC_API_URL_END
            r=self._session.get(api_url)
            if r.status_code==200:
                r_json = json.loads(r.text)
                value = r_json["fullkwh"]
                entity_name = str(key + "_total")
                self._energy_entities[entity_name]=value
            else:
                self.isAuthenticated=False
                self.update()


if __name__=="__main__":
    main()
