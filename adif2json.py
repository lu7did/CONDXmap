
#!/usr/bin/python
#*--------------------------------------------------------------------------------------------------*
#* adif2json
#* Reads a file in ADIF format and converts it to JSON format
#*
#*
#* format:
#*
#*     adif2json {ADIF filename} > jsonFile
#*
#*
#*
#* (c) 2020,2025 Dr. Pedro E. Colla (LU7DZ)
#* License: MIT
#* Free for radioamateur uses
#*--------------------------------------------------------------------------------------------------*
import requests
import dateutil
from datetime import datetime
import sys
import json
from subprocess import PIPE,Popen
import adif_io
from html.parser import HTMLParser
import syslog
import os
#*-------------------------------------------------------------------------------------
#* float2int
#* Returns the integer part of a float number expressed as a string
#*-------------------------------------------------------------------------------------
def float2int(float_string):
    try:
        # Convert the string to a float
        float_value = float(float_string)
        # Convert the float to an integer (truncates the decimal part)
        integer_part = int(float_value)
        return integer_part
    except ValueError:
        return "Error: Invalid float string"
#*-------------------------------------------------------------------------------------
#* removelines, strip \r\n from a string
#*-------------------------------------------------------------------------------------
def removelines(value):
    return value.replace('\n','')
#*-------------------------------------------------------------------------------------
#* convert from freq to ham radio band
#*-------------------------------------------------------------------------------------
def freq2band(freq):
    b="10m"
    match freq.split('.')[0]:
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

#*-------------------------------------------------------------------------------------
#* HTML Parser
#*-------------------------------------------------------------------------------------
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        z=tag.rstrip().find("body")
        if z>=0:
           bFirst=False

    def handle_endtag(self, tag):
        z=tag.rstrip().find("body")
        if z>=0:
           bFirst=True

    def handle_data(self, data):
        data=removelines(data)
        data=data.rstrip()
        if data:
           p=data.find("Warning:")
           if p>=0:
              return data.replace('\n','').replace('\r','')
           p=data.find("Information:")
           if p>=0:
              return data.replace('\n','').replace('\r','')

#*===================================================================================================
#*                                  M A I N
#*===================================================================================================
VERSION="1.0"
#*---------------------------------------------------*
#* Process arguments and format the query to qrz.com *
#*---------------------------------------------------*
if len(sys.argv) < 2:
   print("%s: No ADIF file to process, terminating!\n" % pgm)
   sys.exit()

scriptname   = os.path.basename(sys.argv[0])
adifFile     = sys.argv[1]                                  # First argument is the adifFile to process
dateTimeObj  = datetime.now()
timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")

parser=MyHTMLParser()
#*---------------------------------------------------*
#* Access the ADIF file and extract  pseudo XML data *
#*-------------------------------------------------- *
try:
   qso, adif_header = adif_io.read_from_file(adifFile)
except Exception as ex:
   template = scriptname+": An exception of type {0} reading file occurred. Arguments:\n{1!r}"
   message = template.format(type(ex).__name__, ex.args)
   print(scriptname+": ReadADIF: "+message)
   sys.exit()

#*---------------------------------------------------*
#* Process the ADIF records                          *
#*-------------------------------------------------- *
n=0
bFirst=True 
msg=''
n28=0
#*---------------------------------------------------*
#* Inicializa JSON structure                         *
#*-------------------------------------------------- *
out="["
out=out+('{"program" : "%s",\n' % (scriptname))
out=out+('"version" : "%s",\n' % (VERSION))
out=out+('"adif" : "%s",\n' % (adifFile))
out=out+('"time" : "%s",\n' % (timestampStr))
out=out+('"spot":[\n')

try:
   for x in qso:
     try:
        sucall=x['OPERATOR']
     except Exception as ex:
       template = "An exception of type {0} reading file occurred. Arguments:\n{1!r}"
       message = template.format(type(ex).__name__, ex.args)
       syslog.syslog(syslog.LOG_ERR, "TIME_ON: "+message)
       break

     modo=x['MODE']
     micall=x['CALL']
     fecha=x['QSO_DATE']
     hora=x['TIME_ON']
     miGrid=x['MY_GRIDSQUARE']
     Grid=x['GRIDSQUARE']     

#*---------------------------------------------------*
#* Convert date and time into string objects         *
#*---------------------------------------------------*
     datetime_object = datetime.strptime(fecha, "%Y%m%d")
     date_yyyy_mm_dd = datetime_object.strftime("%Y-%m-%d")
     dt_object = datetime.strptime(hora, "%H%M%S")
     time_formatted = dt_object.strftime("%H:%M:%S")

#*---------------------------------------------------*
     freq=float2int(x['FREQ'])
     band=freq2band(freq)
#*---------------------------------------------------*
#* Create a JSON payload based on request            *
#*-------------------------------------------------- *

     data_string=(f"call:{sucall}, mode:{modo}, band:{band},freq:{freq},mycall:{micall},date:{date_yyyy_mm_dd},time:{time_formatted},migrid:{miGrid},grid:{Grid}")

# Initialize an empty dictionary to store the key-value pairs
     data_dict = {}

# Split the string into individual key-value pairs
     pairs = data_string.split(',')

# Iterate through each pair, split it into key and value, and add to the dictionary
     for pair in pairs:
       key_value = pair.split(':', 1) # Split only on the first colon to handle values containing colons
       if len(key_value) == 2:
          key = key_value[0].strip()
          value = key_value[1].strip()
          data_dict[key] = value

# Convert the Python dictionary to a JSON formatted string
     json_output = json.dumps(data_dict, indent=4) # indent for pretty-printing
     out=out+json_output+",\n"

     n=n+1
except Exception as ex:
     template = scriptname+": An exception of type {0} reading file occurred. Arguments:\n{1!r}"
     message = template.format(type(ex).__name__, ex.args)
     print(message)

#*---------------------------------------------------*
#* Post processing                                   *
#*-------------------------------------------------- *

#out= out[:-2]+"]}]"
out= out[:-2]
out= out+"],"
out= out+('"records" : "%d"}]' % (n))
print(out)
sys.exit()

