#!/usr/bin/python
# -*- coding: utf-8 -*- 
#by Alex 'apexad' Martin
#help from: muhkuh0815 & gaVRos

import re
import urllib2, urllib
import json
import random
import math

from plugin import *

from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.systemObjects import GetRequestOrigin,Location
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.localsearchObjects import Business, MapItem, MapItemSnippet, Rating
 
googleplaces_api_key = APIKeyForAPI("google")
 
class googlePlacesSearch(Plugin):
     #@register("en-US", "(find|show|where).* (nearest|nearby|closest) (.*)")
     @register("en-US", u"(搜尋附近的)(.*)")
     @register("en-GB", "(find|show|where).* (nearest|nearby|closest) (.*)")
     def googleplaces_search(self, speech, language, regex):
          self.say('Searching...',' ')
          mapGetLocation = self.getCurrentLocation()
          latitude = mapGetLocation.latitude
          longitude = mapGetLocation.longitude
          Title = regex.group(regex.lastindex).strip()
          Query = urllib.quote_plus(str(Title.encode("utf-8")))
          random_results = random.randint(2,15)
          googleurl = "https://maps.googleapis.com/maps/api/place/search/json?location={0},{1}&radius=5000&keyword={2}&sensor=true&key={3}".format(str(latitude),str(longitude),str(Query),str(googleplaces_api_key))
          try:
               jsonString = urllib2.urlopen(googleurl, timeout=20).read()
          except:
               jsonString = None
          if jsonString != None:
               response = json.loads(jsonString)
               if (response['status'] == 'OK') and (len(response['results'])):
                    googleplaces_results = []
                    response['results'] = sorted(response['results'], key=lambda result: self.haversine_distance(result['geometry']['location']['lat'],result['geometry']['location']['lng'],latitude,longitude))

                    for result in response['results']:
                         if "rating" in result:
                              avg_rating = result["rating"]
                         else:
                              avg_rating = 0.0
                         rating = Rating(value=avg_rating, providerId='Google Places', count=0)
                         details = Business(totalNumberOfReviews=0,name=result['name'],rating=rating)
                         if (len(googleplaces_results) < random_results):
                              mapitem = MapItem(label=result['name'], street=result['vicinity'], latitude=result['geometry']['location']['lat'], longitude=result['geometry']['location']['lng'])
                              mapitem.detail = details
                              googleplaces_results.append(mapitem)
                         else:
                              break
                    mapsnippet = MapItemSnippet(items=googleplaces_results)
                    count_min = min(len(response['results']),random_results)
                    count_max = max(len(response['results']),random_results)
                    view = AddViews(self.refId, dialogPhase="Completion")
                    view.views = [AssistantUtteranceView(speakableText='I found '+str(count_max)+' query results... '+str(count_min)+' of them are fairly close to you:', dialogIdentifier="googlePlacesMap"), mapsnippet]
                    self.sendRequestWithoutAnswer(view)
               else:
                    self.say("Sorry, I cannot found it. Your location is: ("+str(latitude)+","+str(longitude)+")")	
                    #self.say("I'm sorry but I did not find any results for "+str(Title)+" near you!")
          else:
               self.say('Could not establish a conenction to Googlemaps','Error')
               #self.say("I'm sorry but I did not find any results for "+str(Title)+" near you!")
          self.complete_request()
     def haversine_distance(self, lat1, lon1, lat2, lon2):
          RAD_PER_DEG = 0.017453293
          Rkm = 6371
          dlon = lon2-lon1
          dlat = lat2-lat1
          dlon_rad = dlon*RAD_PER_DEG
          dlat_rad = dlat*RAD_PER_DEG
          lat1_rad = lat1*RAD_PER_DEG
          lon1_rad = lon1*RAD_PER_DEG
          lat2_rad = lat2*RAD_PER_DEG
          lon2_rad = lon2*RAD_PER_DEG
        
          a = (math.sin(dlat_rad/2))**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * (math.sin(dlon_rad/2))**2
          c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
          return round(Rkm * c,2)
