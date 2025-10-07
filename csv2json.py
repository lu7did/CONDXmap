#!/bin/phyton
# -*- coding: latin-1 -*-
from __future__ import with_statement
#*------------------------------------------------------------------------------------------------------
#* csv2json.py
#* Conector para transformar spot data en formato CSV a formato JSON
#*
#* La extracción de datos se realiza con
#
#*     https://pskreporter.info/cgi-bin/pskdata.pl?callsign={CALLSIGN}
#*
#* By Dr. Pedro E. Colla (LU7DZ)
#* License: MIT
#* Free for amateur uses
#*------------------------------------------------------------------------------------------------------
import sys
import csv
import time
import numpy as np
from datetime import datetime
import dateutil
import zipfile
import os
import glob
import tempfile
import shutil
import subprocess
import os
import imageio
import json
#*------------------------------------------------------------------------------------------
#* Print message utility (DEBUG mode)
#*------------------------------------------------------------------------------------------
def print_msg(msg):
    if v==True:
       print ('%s %s' % (datetime.datetime.now(), msg))
#*------------------------------------------------------------------------------------------
#* Convert frequency to band
#*------------------------------------------------------------------------------------------
def freq2band(freq):
    b=int(freq.split('.')[0])
    match b:
        case 1:
           b="160m"
        case 3:
           b="80m"
        case 7:
           b="40m"
        case 10:
           b="30m"
        case 14:
           b="20m"
        case 18:
           b="17m"
        case 21:
           b="15m"
        case 24:
           b="12m"
        case 28:
           b="10m"
        case 50:
           b="6m"
        case 144:
           b="2m"
        case 220:
           b="1.3m"
        case "430":
           b="70cm"
    return b
#*------------------------------------------------------------------------------------------------------
#* MAIN 
#*------------------------------------------------------------------------------------------------------


script = sys.argv[0]
i = 0
v=False
inpath='.'
outpath='.'
outGIF='.'
modeGIF='MARBLE'
nameGIF='CONDX'

scriptname   = os.path.basename(sys.argv[0])
r=0
VERSION="1.0"

now = datetime.now()
timestampStr = now.strftime("%Y-%m-%d %H:%M:%S")

#*-------------------------------------------------------------------------------------
#* Genera formato JSON con la salida
#*-------------------------------------------------------------------------------------

out="["
out=out+('{"program" : "%s",\n' % (scriptname))
out=out+('"version" : "%s",\n' % (VERSION))
out=out+('"time" : "%s",\n' % (timestampStr))
out=out+('"spot":[\n')

#*-------------------------------------------------------------------------------------
#* Barre archivo CSV de entrada (por Std Input) 
#*-------------------------------------------------------------------------------------
for row in csv.reader(iter(sys.stdin.readline, ''),delimiter=','):

#*--- Hace parse de la data 

    if r == 0:
       r=r+1
       continue

    r=r+1
    SNR=row[0]
    mode=row[1]
    freq=row[2]
    timestamp=row[3]
    day=timestamp.split(' ')[0]
    time=timestamp.split(' ')[1]
    fromCall=row[6]
    fromLocator=row[7]
    toCall=row[8]
    toLocator=row[9]    
    hour=int(time.split(':')[0])
    band=freq2band(freq)

    data_string=(f"call:{fromCall}, mode:{mode}, band:{band},freq:{freq},mycall:{toCall},date:{day},time:{time},migrid:{fromLocator},grid:{toLocator},SNR:{SNR}")
           
#*--- Inicializa un diccionario vacio y almacena los pares {clave/valor}
    data_dict = {}  

#*--- Hace split del string en valores individuales        

    pairs = data_string.split(',')
           
#*--- Itera en los pares

    for pair in pairs:
        key_value = pair.split(':', 1)
        if len(key_value) == 2:
           key = key_value[0].strip()
           value = key_value[1].strip()
           data_dict[key] = value
           
#*--- Convierte el diccionario Python en un string formateado con JSON

    json_output = json.dumps(data_dict, indent=4) # indent for pretty-printing
    out=out+json_output+",\n"

out= out[:-2]
out= out+"],"
out= out+('"records" : "%d"}]' % (r-1))
print(out)
sys.exit()

