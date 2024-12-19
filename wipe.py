"""

  WInlink Position Extractor (WIPE).
  (c) Copyright 2022-2024, Nikolai Ozerov VE3NKL
  
  MIT License
  ----------------------------------------------------------------------
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  ----------------------------------------------------------------------
  
  Assuming that your winlink emails are represented by separate files 
  located in a certain directory, this program reads the files and extracts
  position-related fields from winlink forms of different types.
  The extracted position-related info is displayed in the form of the report
  and (optionally) this information is converted into a set of waypoints
  in the form of a GPX file (to be imported in a map software or GPS devices).
  
  Use case description. I am using Winlink Pat client on RPi4. All 'Inbox'
  emails are written into the following directory:
    ~/.local/share/pat/mailbox/VE3NKL/in
  To scan the Winlink forms in recent emails and extract the station position
  info the following command can be used:
  
    python wipe.py -d 1 ~/.local/share/pat/mailbox/VE3NKL/in 

"""

import argparse, sys
from os import scandir
from os.path import join
import re
import datetime
import xml.etree.ElementTree as ET
import SAGeo

"""

  The following class represent a single station info. 

"""
class Station:
  
  def __init__(self, callsign, lat, lon, when):
    if len(callsign) > 0:
      self.callsign = callsign
    else:
      raise Exception("Callsign is empty")
    if len(lat) > 0:
      try:
        self.lat = float(lat)
      except:
        self.lat = None
      if self.lat is None or self.lat > 90.0 or self.lat < -90.0:
        raise Exception("Invalid latitude value: <" + lat + ">")
    else:
      raise Exception("Latitude is empty")
    if len(lon) > 0:
      try:
        self.lon = float(lon)
      except:
        self.lon = None
      if self.lon is None or self.lon > 180.0 or self.lon < -180.0:
        raise Exception("Invalid longitude value: <" + lon + ">")
    else:
      raise Exception("Longitude is empty")
    if len(when) > 0:
      try: 
        self.when = datetime.datetime.strptime(when,'%Y-%m-%d %H:%M:%S')
        self.when.replace(tzinfo=datetime.timezone.utc)
      except:
        self.when = None
      if self.when is None:
        raise Exception("Date/Time value is invalid: <" + when + ">")
    else:
      raise Exception("Date/Time is empty")
    self.spot = SAGeo.Spot(self.lat,self.lon)
    
  @classmethod
  def verify_latitude_value(cls, lat):
    if len(str(lat)) > 0:
      err = None
      try:
        lat_value = float(str(lat))
      except Error as e:
        lat_value = None
        err = str(e)
      if err is not None:
        return (None, err)
      if lat_value > 90.0 or lat_value < -90.0:
        return (None, "Invalid latitude value: <" + str(lat) + ">")
      else:
        return (lat_value, None)
    else:
      return (None, "Latitude value is empty")
      
  @classmethod
  def verify_longitude_value(cls, lon):
    if len(str(lon)) > 0:
      err = None
      try:
        lon_value = float(str(lon))
      except Error as e:
        lon_value = None
        err = str(e)
      if err is not None:
        return (None, err)
      if lon_value > 180.0 or lon_value < -180.0:
        return (None, "Invalid longitude value: <" + str(lon) + ">")
      else:
        return (lon_value, None)
    else:
      return (None, "Longitude value is empty")
    
def qth_list(string):
   return string.split(',')
    
"""

  Define argument rules. The only mandatory argument is a path to the folder
  containing incoming WINLINK emails.

"""
parser = argparse.ArgumentParser(description='WInlink Position Extractor (WIPE)')
parser.add_argument('maildir', type=str, help='directory path where WINLINK mail is located')
parser.add_argument('-o', '--output', type=str, help='path and file name for the output GPX file')
parser.add_argument('-okml', '--output-kml', type=str, help='path and file name for the output KML file')
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-a', '--after', type=lambda s: datetime.datetime.strptime(s, '%Y/%m/%d'), 
                   help="process only emails with date more recent that the one specified")
group.add_argument('-d', '--last-days', type=int, 
                   help="process only emails sent in the sepcified last days (1 meaning last 24 hours)")
parser.add_argument('-v', '--verbose', action='count', help="request detailed output")
parser.add_argument('-q', '--qth', type=qth_list, help="your station lat,lon or maidenhead grid")
parser.add_argument('-s', '--sort-by', choices=["time", "t", "callsign", "c"], 
                   help="sorting stations by this parameter")

args = parser.parse_args()

"""

  If --qth parameter is specified, verify that it contains valid values.

"""

qth = None

MHG_value = re.compile("^[A-Ra-r][A-Ra-r][0-9][0-9][a-xA-X][a-xA-X]([0-9][0-9])?$")
L_value   = re.compile("^(\-?[0-9]+\.[0-9]+)$")
if args.qth:
  if len(args.qth) == 1:
    m = MHG_value.search(args.qth[0])
    if m:
      qth = SAGeo.MHGridSquare(m.group(0)).getCenterSpot()
    else:
      print("Invalid -qth value, must be maidenhead grid (6 or 8 characters) or 'lattitude,longitude'.")
      sys.exit(1)
  elif len(args.qth) == 2:
    m = L_value.search(args.qth[0])
    if m:
      lat = m.group(1)
      lat_value, error = Station.verify_latitude_value(lat)
      if error:
        print("Invalid --qth latitude value: " + error)
        sys.exit(1)
      m = L_value.search(args.qth[1])
      if m:
        lon = m.group(1)
        lon_value, error = Station.verify_longitude_value(lon)
        if error:
          print("Invalid --qth latitude value: " + error)
          sys.exit(1)
        qth = SAGeo.Spot(lat_value,lon_value)
      else:
        print("Invalid -qth value, must be maidenhead grid (6 or 8 characters) or 'lattitude,longitude'.")
        sys.exit(1)
    else:
      print("Invalid -qth value, must be maidenhead grid (6 or 8 characters) or 'lattitude,longitude'.")
      sys.exit(1)
  else:
    print("Invalid -qth value, must be maidenhead grid (6 or 8 characters) or 'lattitude,longitude'.")
    sys.exit(1)
    
  print("Specified QTH coordinates are:")
  print("   Latitude: " + str(round(qth.latitude,5)))
  print("  Longitude: " + str(round(qth.longitude,5)))

"""

  Initialize parsing patterns and working variables

"""

t_date = re.compile("^Date: ([0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]) [0-9][0-9]:[0-9][0-9]")
t_form = re.compile("(\<\?xml.+\>\n+\<RMS_Express_Form\>.+\<\/RMS_Express_Form\>)", re.MULTILINE | re.DOTALL)

stations = {}

today = datetime.datetime.utcnow()
only_after = None
if args.last_days:
  only_after = today - datetime.timedelta(days=args.last_days)
if args.after:
  only_after = args.after
  only_after.replace(tzinfo=datetime.timezone.utc)

n_emails_total   = 0
n_emails_scanned = 0

"""

  Scan all emails. If a date filtering is used (argument -a or -d), for
  most of the emails it will be enough to read just the first few lines.
  The entire email is read only if satisfies the filtering requirement.

"""

if only_after is not None:
  print("Scanning emails sent on or later than " + only_after.strftime("%Y/%m/%d %H:%M") + " (UTC) ...")
else:
  print("Scanning all emails ...")

for entry in scandir(args.maildir):
      
  if entry.is_file(follow_symlinks=False):
    
    n_emails_total += 1
    
    process = True
    
    """
      Check email's date if date filtering is used
    """
    if args.after or args.last_days:
      
      process = False
      with open(join(args.maildir, entry.name), "r", encoding='latin-1') as f:
        
        for ix in range(0,500):
          line = f.readline()
          if not line:
            break
          m = t_date.search(line)
          if m:
            date_time = m.group(1)
            try:
              email_datetime = datetime.datetime.strptime(date_time, '%Y/%m/%d')
              email_datetime.replace(tzinfo=datetime.timezone.utc)
              if email_datetime >= only_after:
                process = True
                break
            except Exception as e:
              pass
    
    """
      If email is eligible for processing, read it and scan for an embedded XML document
      (a Winlink form).
    """          
    if process:
      
      n_emails_scanned += 1
      
      with open(join(args.maildir, entry.name), "r", encoding='latin-1') as f:
        data = f.read()
      for m in t_form.finditer(data):
        form = m.group(1)
        root = ET.fromstring(form)
        e_variables = root.findall(".//variables/msgsender/..")
        if e_variables:
          e_sender = e_variables[0].find("msgsender")
          e_datetime = e_variables[0].find("datetime")
          e_lat = e_variables[0].find("maplat")
          e_lon = e_variables[0].find("maplon")
          if e_sender is not None and e_datetime is not None and e_lat is not None and e_lon is not None:
            try: 
              s = Station(e_sender.text, e_lat.text, e_lon.text, e_datetime.text)
            except Exception as e: 
              s = None
              if args.verbose:
                print("Error during parsing station data: " + str(e))
            if s is not None:
              if s.callsign in stations:
                if s.when > stations[s.callsign].when:
                  stations[s.callsign] = s             # Replace with more recent info
              else:
                stations[s.callsign] = s               # Add new info

print("          Total emails processed: " + str(n_emails_total))
print("Emails scanned for position info: " + str(n_emails_scanned))
print("      Position entries extracted: " + str(len(stations)))

"""

  Get the collected info on stations in certain order

"""
if args.sort_by:
  if args.sort_by == "t" or args.sort_by == "time":        # Sorting by date/time requested
    stations_in_order = sorted(list(stations.values()), key=lambda x: x.when)
  elif args.sort_by == "c" or args.sort_by == "callsign":  # Sorting by callsign requested
    stations_in_order = sorted(list(stations.values()), key=lambda x: x.callsign)
else:
  if qth is None:                                          # Default sorting when no qth info provided
    stations_in_order = sorted(list(stations.values()), key=lambda x: x.callsign)
  else:                                                    # Default sorting, qth info provided
    stations_in_order = sorted(list(stations.values()), key=lambda x: qth.distanceAzimuthToAnotherSpot(x.spot))

"""
 
  If an output argument was specified, generate the waypoint file (GPX type) from the 
  collected station info.

"""
if args.output:
  
  with open(args.output, "w", encoding='latin-1') as fo:

    fo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fo.write('<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtrx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:trp="http://www.garmin.com/xmlschemas/TripExtensions/v1" xmlns:adv="http://www.garmin.com/xmlschemas/AdventuresExtensions/v1" xmlns:prs="http://www.garmin.com/xmlschemas/PressureExtension/v1" xmlns:tmd="http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1" xmlns:vptm="http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1" xmlns:ctx="http://www.garmin.com/xmlschemas/CreationTimeExtension/v1" xmlns:gpxacc="http://www.garmin.com/xmlschemas/AccelerationExtension/v1" xmlns:gpxpx="http://www.garmin.com/xmlschemas/PowerExtension/v1" xmlns:vidx1="http://www.garmin.com/xmlschemas/VideoExtension/v1" creator="Garmin Desktop App" version="1.1">\n')
    for s in stations_in_order:
      fo.write('  <wpt lat="' + str(s.lat) + '" lon="' + str(s.lon) + '">\n')
      fo.write('    <name>' + s.callsign + '</name>\n')
      fo.write('  </wpt>\n')
    fo.write('  <wpt lat="' + str(s.latitude) + '" lon="' + str(s.longitude) + '">\n')
    fo.write('    <name>HOME STATION</name>\n')
    fo.write('  </wpt>\n')
    fo.write('</gpx>\n')            
    
"""
 
  If an output-kml argument was specified, generate the waypoint file (KML type) from the 
  collected station info.

"""
if args.output_kml:
  
  with open(args.output_kml, "w", encoding='latin-1') as fo:

    fo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fo.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    fo.write('<Document>\n')
    for s in stations_in_order:
      fo.write('<Placemark>\n')
      fo.write('  <name>' + s.callsign + '</name>\n')
      fo.write('  <description>' + s.callsign + ' Winlink Station</description>\n')
      fo.write('  <Point>\n')
      fo.write('    <coordinates>' + str(round(s.lon,5)) + ',' + str(round(s.lat,5)) + ',0</coordinates>\n')
      fo.write('  </Point>\n')
      fo.write('</Placemark>\n')
    fo.write('<Placemark>\n')
    fo.write('  <name>HOME STATION</name>\n')
    fo.write('  <description> Home Winlink Station</description>\n')
    fo.write('  <Point>\n')
    fo.write('    <coordinates>' + str(round(qth.longitude,5)) + ',' + str(round(qth.latitude,5)) + ',0</coordinates>\n')
    fo.write('  </Point>\n')
    fo.write('</Placemark>\n')
    fo.write('</Document>\n')
    fo.write('</kml>')

"""

  Print out the info we collected. 

"""
if qth is None:
  print(" Callsign      Date / Time     Latitude  Lognitude   M.Grid  ")
  print("------------ ---------------- ---------- ---------- -------- ")
else:
  print(" Callsign      Date / Time     Latitude  Lognitude   M.Grid  Dist(km)  Azimuth ")
  print("------------ ---------------- ---------- ---------- -------- -------- ---------")

sectors = [ 11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75, 191.25, 213.75, 236.25, 258.75, 281.25, 303.75, 326.25, 348.75 ]
s_names = [ "N   ","N-NE","NE  ","E-NE","E   ","E-SE","SE  ","S-SE","S   ","S-SW","SW  ","W-SW","W   ","W-NW","NW  ","N-NW" ]  

for s in stations_in_order:
  if qth:
    az_name = None
    distance, azimuth = qth.distanceAzimuthToAnotherSpot(s.spot)
    if azimuth < 0:
      azimuth += 360.0
    az = round(azimuth)
    if az >= 360:
      az = 0
    for degree, name in zip(sectors, s_names):
      if az < degree:
        az_name = name
        break
    if az_name is None:
      az_name = "N   "
    
      
  print(s.callsign.ljust(12) + " " + 
        s.when.strftime("%Y/%m/%d %H:%M") + " " + 
        str(round(s.lat,5)).rjust(10) + " " + 
        str(round(s.lon,5)).rjust(10) + " " + 
        s.spot.get_MHGrid() + " " +
        ("" if qth is None else str(round(distance/1000,1)).rjust(8) + " " + 
           str(az).rjust(4) + " " + az_name)
  )
