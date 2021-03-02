# Authors: Renato Anderegg

from RMParserFramework.rmParser import RMParser
from RMUtilsFramework.rmTimeUtils import *


import json

import datetime, time
import random


class METEOSWISS(RMParser):
    parserName = "MeteoSwiss"
    parserDescription = "Swiss weather service from Federal Office of Meteorology and Climatology MeteoSwiss https://www.meteoswiss.admin.ch"
    parserForecast = True
    parserHistorical = False
    parserEnabled = False
    parserDebug = False
    parserInterval = 3 * 3600
    plz6 = None
    params = {"plz6": plz6}



    def isEnabledForLocation(self, timezone, lat, long):
        if METEOSWISS.parserEnabled and timezone:
            return timezone.startswith("Europe")
        return False

    def perform(self):
        if self.plz6 is None:
            self.plz6 = self.params["plz6"]


        s = self.settings
        headers = [{"User-Agent": "RainMachine.com v2"},
                   {
                       "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}]

        URL = "https://app-prod-ws.meteoswiss-app.ch/v1/forecast"

        URLParams = [("plz", self.plz6)]

        # -----------------------------------------------------------------------------------------------
        #
        # Get hourly data.
        #
        try:
            d = self.openURL(URL, URLParams, headers=headers[random.randint(0, 1)])
            if d is None:
                return
            forecast = json.loads(d.read())
            self.__getDailyData(forecast)
        except Exception, e:
            log.error("*** Error running MeteoSwiss parser")
            log.exception(e)

    def __getDailyData(self, forecast):
        daily = forecast["regionForecast"]
        graph = forecast["graph"]

        timestampStart = graph.get("start")
        tempMin = graph.get("temperatureMin1h")
        tempMax = graph.get("temperatureMax1h")
        tempMean = graph.get("temperatureMean1h")
        rainMean = graph.get("precipitationMean1h")
        # rainMin = graph.get("precipitationMin1h")
        # rainMax = graph.get("precipitationMax1h")

        for entry in daily:
            timestamp = time.mktime(datetime.datetime.strptime(entry.get("dayDate"), "%Y-%m-%d").timetuple())
            iconDay = entry.get("iconDay")
            self.addValue(RMParser.dataType.CONDITION, timestamp, self.conditionConvert(iconDay))


        hourMillis = 60 * 60
        i = 0
        numOFEntries = len(tempMean)
        entryTime = timestampStart / 1000
        while i < numOFEntries:
            entryTime = entryTime + hourMillis
            self.addValue(RMParser.dataType.MINTEMP, entryTime, tempMin[i])
            self.addValue(RMParser.dataType.MAXTEMP, entryTime, tempMax[i])
            self.addValue(RMParser.dataType.TEMPERATURE, entryTime, tempMean[i])
            self.addValue(RMParser.dataType.QPF, entryTime, rainMean[i])
            i = i + 1


    def conditionConvert(self, symbol):
        if symbol in [5, 35]:
            return RMParser.conditionType.MostlyCloudy  # a
        elif symbol in [1]:
            return RMParser.conditionType.Fair  # b
        elif symbol in [2, 26, 27]:
            return RMParser.conditionType.FewClouds  # c
        elif symbol in [3]:
            return RMParser.conditionType.PartlyCloudy  # d
        elif symbol in [4, 5, 33]:
            return RMParser.conditionType.Overcast  # e
        elif symbol in [28]:
            return RMParser.conditionType.Fog  # f
        elif symbol in [999]:
            return RMParser.conditionType.Smoke  # g
        elif symbol in [999]:
            return RMParser.conditionType.FreezingRain  # h
        elif symbol in [999]:
            return RMParser.conditionType.IcePellets  # i
        elif symbol in [999]:
            return RMParser.conditionType.RainIce  # j
        elif symbol in [7, 10, 15, 18, 21, 31]:
            return RMParser.conditionType.RainSnow  # k
        elif symbol in [17]:
            return RMParser.conditionType.RainShowers  # l
        elif symbol in [23, 24, 25]:
            return RMParser.conditionType.Thunderstorm  # m
        elif symbol in [8, 11, 16, 19, 22, 30, 34]:
            return RMParser.conditionType. Snow  # n
        elif symbol in [999]:
            return RMParser.conditionType.Windy  # o
        elif symbol in [6, 29, 32, 33]:
            return RMParser.conditionType.ShowersInVicinity  # p
        elif symbol in [999]:
            return RMParser.conditionType.HeavyFreezingRain  # q
        elif symbol in [12, 13]:
            return RMParser.conditionType.ThunderstormInVicinity  # r
        elif symbol in [9, 14]:
            return RMParser.conditionType.LightRain  # s
        elif symbol in [17, 20]:
            return RMParser.conditionType.HeavyRain  # t
        elif symbol in [999]:
            return RMParser.conditionType.FunnelCloud  # u
        elif symbol in [999]:
            return RMParser.conditionType.Dust  # v
        elif symbol in [999]:
            return RMParser.conditionType.Haze  # w
        elif symbol in [999]:
            return RMParser.conditionType.Hot  # x
        elif symbol in [999]:
            return RMParser.conditionType.Cold # y
        else:
            return RMParser.conditionType.Unknown  # z

    def logtrace(self, msg, *args, **kwargs):
        if self.parserDebug:
            log.info(msg, *args, **kwargs)


# if __name__ == "__main__":
#     parser = METEOSWISS()
#     parser.plz6 = 814200
#     parser.perform()
