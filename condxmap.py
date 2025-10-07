#!/bin/phyton
# -*- coding: latin-1 -*-
from __future__ import with_statement
#*------------------------------------------------------------------------------------------------------
#* condxmap.py
#* Plot PSKInformer reports at http://pskreporter.info
#*
#*
#*     python condxmap.py --input {json data} --gif {path to store graph files}
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
#import imageio
import imageio.v2 as imageio
from collections import defaultdict
import json

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

    return strStartLon,strStartLat
#*------------------------------------------------------------------------------------------------------
#* Transform band into a line of a pre-defined colour
#*------------------------------------------------------------------------------------------------------
def band2color(band):

    match band:
        case "40m":
            return 'c'
        case "20m":
            return 'y'
        case "15m":
            return 'g'
        case "10m":
            return 'm'
        case _:
            return 'c'
#*------------------------------------------------------------------------------------------------------
#* Draw a line in the map given initial and ending coordinates expressed as Maindenhead locator
#*------------------------------------------------------------------------------------------------------

def plotMap(map,band,gFrom,gTo,SNR):

    lonFrom,latFrom=GridToLatLong(gFrom.strip())
    lonTo,latTo=GridToLatLong(gTo.strip())


    loFrom=float(lonFrom)
    loTo=float(lonTo)
    laFrom=float(latFrom)
    laTo=float(latTo)

    lat = [laFrom,laTo] 
    lon = [loFrom,loTo] 

    r=band2color(band)
    x, y = map(lon, lat)
    map.plot(x, y, 'o-', color=r,markersize=1, linewidth=1) 
    return

#*------------------------------------------------------------------------------------------------------
#* Build a map (Mercator projection)
#*------------------------------------------------------------------------------------------------------
def buildMap():
    m = Basemap(projection='merc',llcrnrlon=-170,llcrnrlat=-75,urcrnrlon=170,urcrnrlat=75,resolution='l')


    #m.drawmeridians(np.arange(0,360,30))
    #m.drawparallels(np.arange(-90,90,30))
    #m.drawcoastlines(linewidth=0.25)
    #m.drawcountries(linewidth=0.25)
    return m


#*------------------------------------------------------------------------------------------------------
#* MAIN 
#*------------------------------------------------------------------------------------------------------
scriptname = sys.argv[0]
infile="condx_hour"
i = 0
v=False
VER="1.0"
BUILD="000"
gifpath='./out'
jsonfile=''

modeGIF='MARBLE'
nameGIF='CONDX'
n=0
filterband="all"
filtersnr=-30

#*----- Procesa argumentos
while i < len(sys.argv): 

   if sys.argv[i].upper() == '--H':
      print('condxmap versión %s build %s' % (VER,BUILD))
      print('      python condxmap.py [--v] [--h] --input {json file} --gif {graph files directory}')
      quit()
   if (sys.argv[i].upper() == '--V') or (sys.argv[i].upper() == '-V'):
      v=True
   if (sys.argv[i].upper() == '--INPUT'):
      jsonfile=sys.argv[i+1]
      i=i+1
   if (sys.argv[i].upper() == '--GIF'):
      gifpath=sys.argv[i+1]

   if (sys.argv[i].upper() == '--BAND'):
      filterband=sys.argv[i+1].upper()

   if (sys.argv[i].upper() == '--SNR'):
      filtersnr=int(sys.argv[i+1])
      
      i=i+1

   i=i+1

if jsonfile == '':
   print("Json file must be informed, see condxmap --help")

print(f'\n{scriptname} versión {VER} build {BUILD}')
print(f"Process input({jsonfile}) gif({gifpath}) filter({filterband}) filtersnr({filtersnr})\n")

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


with open(jsonfile, 'r') as f:
    data = json.load(f)

spots=data[0]["spot"]
for i, entry in enumerate(spots, start=1):

    call = entry["call"]
    band = entry["band"]
    toCall=entry["call"]
    fromCall=entry["mycall"]
    timestamp=entry["time"]
    freq=entry["freq"]
    toLocator=entry["migrid"]
    fromLocator=entry["grid"]
    SNR=entry["SNR"]
    if SNR == '':
       SNR=-30
    else:
       SNR=int(SNR)

#*-------------------------------------------------------------------------------------
#* Scan data and build datasets
#*-------------------------------------------------------------------------------------
    hour=int(timestamp.split(':')[0])
    qso = (timestamp, toCall, band, freq, toLocator, fromCall, fromLocator,SNR)
    if (filterband != 'ALL' and band.upper() == filterband) or (filterband == 'ALL'):
       print(f"SNR{SNR} filtersnr{filtersnr}")
       if SNR>=filtersnr:
          condx[hour].append(qso)
          print("stored")


for h in range(24):  # Iterates from 0 to 23
    qso = condx.get(h, [])

    if not qso:
       print(f"No hay spots guardados para la hora {h}.")
    else:
       n=n+1
       x = datetime.datetime.now(datetime.UTC)
       f = datetime.datetime(x.year,x.month,x.day,h,0,0)
       CS=map.nightshade(f)
       if (modeGIF=="SHADED"):
          map.shadedrelief(scale=0.1)
       else:
          map.bluemarble(scale=0.1)
       plt.title("Propagation Report Hour %d:00Z" % (h))
       if len(str(h)) == 1:
          stHour="0"+str(h)
       else:
          stHour=str(h)
       plt.savefig(gifpath+"/condx_"+stHour+".png")
       plt.close("all")
       map=None
       map=buildMap()

       for i, (timestamp, toCall, band, freq, toLocator, fromCall, fromLocator,SNR) in enumerate(qso, start=1):
           plotMap(map,band,toLocator,fromLocator,SNR)
           n=n+1

print(f"total number of spots {n} number of JSON records {data[0]["records"]}")

#*---------------------------------------------------------------------------------------------
#* Create GIF file 
#*---------------------------------------------------------------------------------------------
images = []

for file_name in sorted(os.listdir(gifpath)):
    if file_name.endswith('.png'):
       images.append(imageio.imread(gifpath+"/"+file_name))

imageio.mimsave(gifpath+'/'+nameGIF+'.gif', images, fps=0.5)
