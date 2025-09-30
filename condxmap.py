#!/bin/phyton
# -*- coding: latin-1 -*-
from __future__ import with_statement
#*------------------------------------------------------------------------------------------------------
#* condxmap.py
#* Plot PSKInformer reports at http://pskreporter.info
#*
#* By Dr. Pedro E. Colla (LU7DID)
#*------------------------------------------------------------------------------------------------------
import sys
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
import datetime
import zipfile
import os
import glob
import tempfile
import shutil
import subprocess
import os
import imageio
from collections import defaultdict
#*------------------------------------------------------------------------------------------
#* Print message utility (DEBUG mode)
#*------------------------------------------------------------------------------------------
def print_msg(msg):
    if v==True:
       print ('%s %s' % (datetime.datetime.now(), msg))

#*------------------------------------------------------------------------------------------
#* CreateFolder function 
#*------------------------------------------------------------------------------------------
def createFolder(directory):

    c=0    
    print_msg('createFolder: %s en %s' % (directory,os.getcwd())) 
    try:
        if not os.path.exists(directory):
           print_msg('createFolder: creando directorio %s ' % (directory))        
           os.makedirs(directory)
    except OSError:
        print_msg ('createFolder: excepcion mientras se creaba. %s ' % (directory))
#*------------------------------------------------------------------------------------------------------
#* Return Start and end Longitude as a string
#*------------------------------------------------------------------------------------------------------
def GetLon(ONE, THREE, FIVE):
    StrStartLon = ''
    StrEndLon = ''

    Field = ((ord(ONE.lower()) - 97) * 20) 
    Square = int(THREE) * 2
    SubSquareLow = (ord(FIVE.lower()) - 97) * (2/24)
    SubSquareHigh = SubSquareLow + (2/24)

    StrStartLon = str(Field + Square + SubSquareLow - 180 )
    StrEndLon = str(Field + Square + SubSquareHigh - 180 )

    return StrStartLon, StrEndLon
#*------------------------------------------------------------------------------------------------------
#* Return Start and end Latitude as a string
#*------------------------------------------------------------------------------------------------------

def GetLat(TWO, FOUR, SIX):
    StrStartLat = ''
    StrEndLat = ''

    Field = ((ord(TWO.lower()) - 97) * 10) 
    Square = int(FOUR)
    SubSquareLow = (ord(SIX.lower()) - 97) * (1/24)
    SubSquareHigh = SubSquareLow + (1/24)

    StrStartLat = str(Field + Square + SubSquareLow - 90)
    StrEndLat = str(Field + Square + SubSquareHigh - 90)    

    return StrStartLat, StrEndLat

#*------------------------------------------------------------------------------------------------------
#* Return Lat and long as a string starting from locator as QTH Maindenhead locator
#*------------------------------------------------------------------------------------------------------

def GridToLatLong(strMaidenHead):
    if len(strMaidenHead) < 6: strMaidenHead=strMaidenHead+"aa" 

    ONE = strMaidenHead[0:1]
    TWO = strMaidenHead[1:2]
    THREE = strMaidenHead[2:3]
    FOUR = strMaidenHead[3:4]
    FIVE = strMaidenHead[4:5]
    SIX = strMaidenHead[5:6]

    (strStartLon, strEndLon) = GetLon(ONE, THREE, FIVE)
    (strStartLat, strEndLat) = GetLat(TWO, FOUR, SIX)

    #print ('Start Lon = ' + strStartLon)
    #print ('End   Lon = ' + strEndLon)
    #print ()
    #print ('Start Lat = ' + strStartLat)
    #print ('End   Lat = ' + strEndLat)

    return strStartLon,strStartLat
#*------------------------------------------------------------------------------------------------------
#* Draw a line in the map given initial and ending coordinates expressed as Maindenhead locator
#*------------------------------------------------------------------------------------------------------

def plotMap(map,gFrom,gTo):

    lonFrom,latFrom=GridToLatLong(gFrom.strip())
    lonTo,latTo=GridToLatLong(gTo.strip())


    loFrom=float(lonFrom)
    loTo=float(lonTo)
    laFrom=float(latFrom)
    laTo=float(latTo)


    lat = [laFrom,laTo] 
    lon = [loFrom,loTo] 


    x, y = map(lon, lat)
    map.plot(x, y, 'o-', markersize=1, linewidth=1) 
    return

#*------------------------------------------------------------------------------------------------------
#* Build a map (Mercator projection)
#*------------------------------------------------------------------------------------------------------

def buildMap():
    m = Basemap(projection='merc',llcrnrlon=-170,llcrnrlat=-75,urcrnrlon=170,urcrnrlat=75,resolution='l')


    m.drawmeridians(np.arange(0,360,30))
    m.drawparallels(np.arange(-90,90,30))
    m.drawcoastlines(linewidth=0.25)
    m.drawcountries(linewidth=0.25)
    return m


#*------------------------------------------------------------------------------------------------------
#* MAIN 
#*------------------------------------------------------------------------------------------------------


lastHour=0
c=0
MH= 'GF05te'
VER='1.6'
BUILD='10'
script = sys.argv[0]
i = 0
v=False
inpath='.'
outpath='.'
outGIF='.'
modeGIF='MARBLE'
nameGIF='CONDX'
n=0

#*----- Procesa argumentos
while i < len(sys.argv): 
   print_msg('Argument(%d) --> %s' % (i,sys.argv[i].upper()))
   if sys.argv[i].upper() == '--H':
      print('condxmap versión %s build %s' % (VER,BUILD))
      print('   condxmap [--v] [--h]')
      quit()
   if (sys.argv[i].upper() == '--V') or (sys.argv[i].upper() == '-V'):
      print_msg('main: Verbose mode activated')
      v=True

   i=i+1

print_msg('version es %s' % (sys.version))
print_msg('verbose status %s ' % v)
print_msg("*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
createFolder(outpath)

#map = Basemap(projection='ortho',lat_0=-34.6,lon_0=-58.4,resolution='c')

#*------ Estructura para almacenar los spots por banda horaria
condx = {i: [] for i in range(0, 24)}

#*---------------------------------------------------------------------------------------------------
# Process WSPRNet dataset with awk '{print "plotMap(map,\""$7"\",\""$10"\")"}' wsprdata.lst > set.py
#*---------------------------------------------------------------------------------------------------

hour=0

f = datetime.datetime.now()
x = datetime.datetime.now(datetime.UTC)
print("Initialization of maps LOCAL  %s -- UTC %s" % (f.strftime("%b %d %Y %H:%M:%S"),x.strftime("%b %d %Y %H:%M:%S")))
map=buildMap();
print("Creating graphics at (%s) GIF(%s)" % (outpath,outGIF)) 

import json

filename = './data/test.json'

with open(filename, 'r') as f:
    data = json.load(f)

spots=data[0]["spot"]
for i, entry in enumerate(spots, start=1):

    call = entry["call"]
    band = entry["band"]
    toCall=entry["call"]
    fromCall=entry["mycall"]
    timestamp=entry["time"]
    freq=entry["freq"]
    toLocator=entry["grid"]
    fromLocator=entry["migrid"]

#*-------------------------------------------------------------------------------------
#* Scan data and build datasets
#*-------------------------------------------------------------------------------------
    hour=int(timestamp.split(':')[0])
    qso = (timestamp, toCall, band, freq, toLocator, fromCall, fromLocator)
    condx[hour].append(qso)
    print("Hour(%s) Time(%s) toCall(%s) freq(%s) locatorTo(%s) fromCall(%s) locatorFrom(%s)" % (hour,timestamp,toCall,freq,toLocator,fromCall,fromLocator))


for h in range(24):  # Iterates from 0 to 23
    print(h)
    qso = condx.get(h, [])
    if not qso:
       print(f"No hay spots guardados para la hora {h}.")
    else:
       n=n+1
       print(f"\nSpots para la  hora {h} datetime UTC{f}")
       x = datetime.datetime.now(datetime.UTC)
       f = datetime.datetime(x.year,x.month,x.day,h,0,0)
       CS=map.nightshade(f)
       if (modeGIF=="SHADED"):
          map.shadedrelief(scale=0.1)
       else:
          map.bluemarble(scale=0.1)
       plt.title("Hour %d:00Z" % (h))
       if len(str(h)) == 1:
          stHour="0"+str(h)
       else:
          stHour=str(h)
       plt.savefig(outpath+"/condx"+stHour+".png")
       plt.close("all")
       print("Image generation for hour %s:00Z has been completed" % (h))
       map=None
       map=buildMap()



       for i, (timestamp, toCall, band, freq, toLocator, fromCall, fromLocator) in enumerate(qso, start=1):
           print(f"       {i}. ({timestamp!r}, {toCall!r}, {band!r}, {freq!r},{toLocator!r},{fromCall},{fromLocator})")
           plotMap(map,toLocator,fromLocator)


    print(f"total number of spots {n} number of JSON records {data[0]["records"]}")
#*--- Identify change of the hour
#    while hour!=lastHour:
#
#
#
#      lastHour=lastHour+1
#      c=0
#      if lastHour>23:
#          break
#    if hour==lastHour:
#       c=c+1
#
#*---- Completes till midnight is CONDX ends before

#while lastHour<24:
#   x = datetime.datetime.now(datetime.UTC)
#
#   print_msg("----> Band %sMHz Processing spots for hour %d Spots(%d)" % (band,lastHour,c))
#   f = datetime.datetime(x.year,x.month,x.day,lastHour,0,0)
#
#   CS=map.nightshade(f)
#   if modeGIF == "SHADED":
#      map.shadedrelief(scale=0.10)
#   else:
#      map.bluemarble(scale=0.10)
#
#   plt.title("Band %s MHz Hour %d:00Z" % (band,lastHour))
#   if len(str(lastHour)) == 1:
#      stHour="0"+str(lastHour)
#   else:
#      stHour=str(lastHour)
#   print_msg("main: saving file %s" % (outpath+"/condx"+stHour+".png"))
#   plt.savefig(outpath+"/condx"+stHour+".png")
#   plt.close("all")
#   print("Image generation for hour %s:00Z has been completed Spot(0)" % (lastHour))
#   lastHour=lastHour+1
#   map=None
#   map=buildMap()

#*---------------------------------------------------------------------------------------------
#* Create GIF file 
#*---------------------------------------------------------------------------------------------
#print_msg("Creating GIF at path: %s" % outGIF)
#images = []
#for file_name in sorted(os.listdir(outGIF)):
#    if file_name.endswith('.png'):
#        file_path = os.path.join(outGIF, file_name)
#        print("GIF Generation including file %s" % file_path)
#        images.append(imageio.imread(file_path))
#imageio.mimsave(outGIF+'/'+nameGIF+'.gif', images, duration=0.5)
