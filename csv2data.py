#*------------------------------------------------------------------------------------------------------
#* csv2data.py
#* Convierte CSV extract de PSKReporter en CSV reducido con información de continente y CQ Zone
#*
#* La extracción de datos se realiza con
#*
#*          https://pskreporter.info/cgi-bin/pskdata.pl?callsign={CALLSIGN}
#*
#* By Dr. Pedro E. Colla (LU7DZ)
#* License: MIT
#* Free for amateur uses
#*------------------------------------------------------------------------------------------------------

import csv
import subprocess
import sys
from datetime import datetime
import maidenhead as mh
from geopy.geocoders import Nominatim
from pycountry_convert import country_alpha2_to_continent_code, convert_continent_code_to_continent_name
from geopy.geocoders import Nominatim
import argparse
from pyhamtools import LookupLib, Callinfo
#*------------------------------------------------------------------------------------------------------
def separar_fecha_hora(fecha_hora_str: str):
    """
    Recibe una fecha en formato 'YYYY-MM-DD HH:MM:SS' y retorna
    dos strings: (fecha, hora).
    """
    fecha, hora = fecha_hora_str.split(" ")
    return fecha, hora
#*------------------------------------------------------------------------------------------------------
def convertir_timestamp(ts: str):
    """
    Convierte un timestamp del formato:
    '15/11/2025  11:24:27 p. m.'
    a:
      - fecha (YYYY-MM-DD)
      - hora en formato 0-24 (HH:MM:SS)

    Retorna una tupla (fecha, hora24)
    """

    # Normalizar AM/PM (caracteres raros) eliminando espacios no estándar
    ts = ts.replace("p. m.", "PM").replace("a. m.", "AM")
    ts = ts.replace("p. m.", "PM").replace("a. m.", "AM")

    # Parsear usando formato día/mes/año + hora 12h
    dt = datetime.strptime(ts, "%d/%m/%Y %I:%M:%S %p")

    fecha = dt.date().isoformat()       # YYYY-MM-DD
    hora24 = dt.strftime("%H:%M:%S")    # HH:MM:SS en formato 24h

    return fecha, hora24

#*------------------------------------------------------------------------------------------------------
def freq2band(freq : str) -> str:

  try:
    f=freq.split(".")
    fx=int(f[0])
    if (fx == 3): 
       return "80m"
    if (fx == 7): 
       return "40m"
    if (fx == 14): 
       return "20m"
    if (fx == 21): 
       return "15m"
    if (fx == 28): 
       return "10m"
    if (fx == 50): 
       return "6m"
    if (fx == 144): 
       return "2m"
    if (fx == 3): 
       return "80m"
    return "oth"
  except:
    return "oth"
#*------------------------------------------------------------------------------------------------------
def leer_csv(infile, outfile):

    flagFirst=True

#*----- Define CSV input and creates a reader for it

    inCSV = open(infile, "r")
    lector = csv.reader(inCSV)

#*----- Creates the output file

    out=open(outfile, 'w')

#*----- Read Ham data to complete continent and CQ Zone

    my_lookuplib = LookupLib(lookuptype="countryfile")
    cic = Callinfo(my_lookuplib)

#*----- Iterate CSV Reader

    for fila in lector:

        # First just process headers

        if flagFirst:
           flagFirst=False
           print(f"\"dia\",\"hora\",\"GMT\",\"MHz\",\"Band\",\"senderCallsign\",\"senderLocator\",\"senderContinent\",\"receiverCallsign\",\"receiverLocator\",\"receiverContinent\",\"mode\",\"sNR\",\"CQZone\"")
        else:

        # Else process continent and CQ Zone

           dia,hora=separar_fecha_hora(fila[3])
           h=hora.split(":")

           CQZ="13"
           if fila[6] == "LU7DZ":
              senderContinent="SA"

              try:
                 z=cic.get_all(fila[8].upper())
                 receiverContinent= z['continent']
                 print(f"Callsign {fila[8]} senderContinent{senderContinent} CQ{CQZ} receiverContinent{receiverContinent}")
                 CQZ= z['cqz']
              except:
                 receiverContinent="None"
                 CQZ="None"

           if fila[8] == "LU7DZ":
              try:
                 receiverContinent="SA"
                 z=cic.get_all(fila[6].upper())
                 senderContinent= z['continent']
                 CQZ= z['cqz']
              except:
                 senderContinent="None"
                 CQZ="None"
              print(f"Callsign {fila[8]} receiverContinent{receiverContinent} senderContinent {senderContinent} CQ{CQZ}")


           band=freq2band(fila[2])

           #* Write output file and standard out

           outstr=(f"\"{dia}\",\"{hora}\",\"{h[0]}\",\"{fila[2]}\",\"{band}\",\"{fila[6]}\",\"{fila[7]}\",\"{senderContinent}\",\"{fila[8]}\",\"{fila[9]}\",\"{receiverContinent}\",\"{fila[1]}\",\"{fila[0]}\",\"{CQZ}\"")
           out.write(outstr+"\n")
           print(outstr) 

# Ejecucion de main
if __name__ == "__main__":


#*---------------------------------------------------------------------------------------
#* Process arguments
#*---------------------------------------------------------------------------------------
   if len(sys.argv) > 2:  
         argument_string = sys.argv[1] # Access the first argument
   else:
         print("No command-line arguments provided.")
         sys.exit()


# Create an ArgumentParser object
   parser = argparse.ArgumentParser(description='A sample program with command-line options.')

# Add arguments/options
   parser.add_argument('--out', type=str, default="csv2continent.txt", help='Output file')
   parser.add_argument('--csv', type=str, default="psk_data.csv", help='Input file')

# Parse the arguments

   args = parser.parse_args()
   leer_csv(args.csv,args.out)

