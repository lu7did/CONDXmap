#!/bin/phyton
# -*- coding: latin-1 -*-
from __future__ import with_statement
#*------------------------------------------------------------------------------------------------------
#* grid2geo.py
#* Conector para transformar Maiden locator grid designator en [lat,long], continent & country
#*
#* La extracción de datos se realiza con
#* By Dr. Pedro E. Colla (LU7DZ)
#* License: MIT
#* Free for amateur uses
#*------------------------------------------------------------------------------------------------------
#* Requiere librerias maidenhead, geopy y pycountry_convert
#*------------------------------------------------------------------------------------------------------
import maidenhead as mh
from geopy.geocoders import Nominatim
from pycountry_convert import country_alpha2_to_continent_code, convert_continent_code_to_continent_name
from geopy.geocoders import Nominatim
import getopt
import sys
import argparse
from pyhamtools import LookupLib, Callinfo

#*-------------------------------------------------------------------------------
#* Extract continent given lat/long
#*------------------------------------------------------------------------------
def get_continent_from_lat_lon(latitude, longitude):

  try:
     geolocator = Nominatim(user_agent="my_geocoder_app") # Replace "my_geocoder_app" with a unique name
     location = geolocator.reverse(f"{latitude},{longitude}")
  except:
     location = "GF05"

  if location and location.raw and 'address' in location.raw:
     address = location.raw['address']
     if 'country_code' in address:
        country_code = address['country_code'].upper()
        try:
           continent_code = country_alpha2_to_continent_code(country_code)
           continent_name = convert_continent_code_to_continent_name(continent_code)
           return continent_name
        except KeyError:
           return "Continent not found for this country code."
        else:
               return "Country code not found in address details."
     else:
           return "Location details could not be retrieved."

#*---------------------------------------------------------------------------------------
#* Process arguments
#*---------------------------------------------------------------------------------------
if len(sys.argv) > 1:
      argument_string = sys.argv[1] # Access the first argument
else:
      print("No command-line arguments provided.")
      sys.exit()


# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='A sample program with command-line options.')

# Add arguments/options
parser.add_argument('-g', '--grid', type=str, help='Specify QRA Locator grid.')
parser.add_argument('-c', '--country', action='store_true', help='compute country.')
parser.add_argument('-C', '--continent', action='store_true', help='compute continent.')
parser.add_argument('-z', '--zone', action='store_true', help='compute CQ Zone')
parser.add_argument('-i', '--itu', action='store_true', help='compute ITU Zone')
parser.add_argument('--lat', action='store_true', help='compute latitude.')
parser.add_argument('--lon', action='store_true', help='compute longitude.')
parser.add_argument('--call',type=str, default='',help='call sign to compute.')
parser.add_argument('-v','--verbose', action='store_true', help='verbose output.')

# Parse the arguments
args = parser.parse_args()
if args.verbose:
   print(args)

#*---------------------------------------------------------------------------------------
#* Get QRA Locator from standard input
#*---------------------------------------------------------------------------------------
if args.grid == "":
   qra_locator = sys.stdin.readline()
   if args.verbose:
      print(f"Grid from Standard input: {qra_locator.strip()}") 
else:
   qra_locator=args.grid
   if args.verbose:
      print(f"Grid from Argument: {qra_locator.strip()}")
#*---------------------------------------------------------------------------------------
# Get the coordinates of the grid's center
#*---------------------------------------------------------------------------------------
try:
   center_coords = mh.to_location(qra_locator, center=True)
   lat = center_coords[0]
   lon = center_coords[1]

except:
   lat = "0.00"
   lon = "0.00"

if args.verbose:
   print(f"Grid {qra_locator} Latitude: {lat}, Longitude: {lon}")

#*---------------------------------------------------------------------------------------
#* Compute continent
#*---------------------------------------------------------------------------------------
if args.continent:
   continent = get_continent_from_lat_lon(lat, lon)
   if args.verbose:
      print(f"The continent for ({lat}, {lon}) is: {continent}")
   print(continent)
   sys.exit()


#*---------------------------------------------------------------------------------------
#* Compute address
#*---------------------------------------------------------------------------------------
if args.country:
   geolocator = Nominatim(user_agent="my_geopy_app")
   latitude = str(lat)
   longitude = str(lon)
   location = geolocator.reverse(latitude + "," + longitude)
   values = location.address.split(',')
   if args.verbose:
      print(values)
   print(values[6])
   sys.exit()

#*---------------------------------------------------------------------------------------
#* Compute latitude
#*---------------------------------------------------------------------------------------
if args.lat:
   print(lat)
   sys.exit()

#*---------------------------------------------------------------------------------------
#* Compute longitude
#*---------------------------------------------------------------------------------------
if args.lon:
   print(lon)
   sys.exit()

#*---------------------------------------------------------------------------------------
#* Compute cq zone
#*---------------------------------------------------------------------------------------
if args.zone:

   if args.call == '':
      print("Callsign must be informed --help for help")
      sys.exit()

   my_lookuplib = LookupLib(lookuptype="countryfile")
   cic = Callinfo(my_lookuplib)
   z=cic.get_all(args.call.upper())
   print(z)
   cqz = z['cqz']
   print(cqz)

#*---------------------------------------------------------------------------------------
#* Compute cq zone
#*---------------------------------------------------------------------------------------
if args.itu:

   if args.call == '':
      print("Callsign must be informed --help for help")
      sys.exit()
   my_lookuplib = LookupLib(lookuptype="countryfile")
   cic = Callinfo(my_lookuplib)
   z=cic.get_all(args.call.upper())
   cqz = z['ituz']
   print(cqz)


