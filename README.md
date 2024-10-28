# WI(nlink) P(osition) E(xtractor)
## Overview
Stations can send their location information using Check-In and other forms. Some Winlink clients have no ability to extract and use this information (for example, by displaying it on a map). If such a client saves the emails as separate text files in a specific directory, this python script can scan the emails, extract station positions and display this information in an easy to read form. It also can create waypoints file in the GPX or KML format. Both of them can be used by a variety of GPS/Mapping software to visually put the stations on a map. KML file, for example, can be used with Google Maps. 
## An Example of a Produced Report
If you specify your own position, the report will include direction and distance info for each of the Winlink stations. An example below is based on an actual report with call signs partially scrambled and latitude/longitude positions rounded for privacy reasons.

    $ python wipe.py -d 7 -q FN03gu $PATINBOX
    
    Specified QTH coordinates are: 
       Latitude: 43.80000  
      Longitude: -79.40000  
    Scanning emails sent on or later than 2024/10/21 13:47 (UTC) ...  
  
              Total emails processed: 154  
    Emails scanned for position info: 15  
          Position entries extracted: 10  
     Callsign      Date / Time     Latitude  Lognitude   M.Grid  Dist(km)  Azimuth   
    ------------ ---------------- ---------- ---------- -------- -------- ---------  
    VE3XX        2024/10/23 13:14      43.80  -79.00000 FN03ht59      7.5  111 E-SE
    VE3XXX       2024/10/22 21:57   43.90000  -79.00000 FN03gx09     16.3  350 N   
    VA3XXX       2024/10/23 20:56    43.6000    -79.000 FN03hq55     19.7  160 S-SE
    VA3XX        2024/10/23 19:27   44.00000  -79.00000 FN04di76     59.0  342 N-NW
    VE3XX        2024/10/22 12:16    44.0000  -78.00000 FN04no50     93.8   30 N-NE
    VE3XXX       2024/10/23 19:35   43.00000  -80.20000 EN93vd54     99.4  217 SW  
    VE3XXX       2024/10/23 21:55   44.00000  -78.20000 FN04ve16    104.8   69 E-NE
    VE3XX        2024/10/24 09:28     46.000   -77.0000 FN16fd25    295.6   31 N-NE
    VE3XXX       2024/10/23 21:21   45.00000  -75.60000 FN25dg86    339.2   64 E-NE
    VE6XXX       2024/10/23 14:22   53.00000  -113.7000 DO33di37   2706.1  279 W

Note, that one of the parameters for calling the wipe script includes an environment variable \$PATINBOX. I found it convenient to set it up pointing at the PAT inbox directory. That way you can reference it without the need to remember its location.

## License 
The code is released under the MIT License.
## Installing the Script
The script is called *wipe.py* and it supposed to run under Python 3. There is no special installation necessary, just copy the script into the directory of your choice. You will also need SAGeo package which can be found here: [https://github.com/ve3nkl/satellite-passes/tree/main/satools]. You won't need the entire *satools* directory, just copy SAGeo.py from the location above to the same directory where you downloaded *wipe.py*. The other packages used by the script are most likely already available in your Python 3 installation. You might need to install the *geographiclib* package which is needed by SAGeo.py.
## Using the Script
The only mandatory parameter to run the script is a path to the directory where Winlink emails are located. As an example, my PAT (Winlick client) installation saves the incoming emails in the following directory:
> ~/.local/share/pat/mailbox/VE3NKL/in

To avoid typing this long path every time I appended the following line to *~/.bash_profile*:

> export PATINBOX=~/.local/share/pat/mailbox/VE3NKL/in

Now to run the script I can issue the following command in my home directory:
> python3 ./wipe.py $PATINBOX

This will result in scanning all emails in the PAT's inbox directory. If a station reported more different locations at different times the last reported location will be taken and the older ones will be ignored. It is useful to set some date/time filtering for the scanning process, i.e. to scan only emails that were sent after certain date/time. This can be used by using either *-a* or *-d* parameters:
> python3 ./wipe.py -a 2022/06/01 $PATINBOX

or
> python3 ./wipe.py -d 2 $PATINBOX

The first example above will only scan emails sent after midnight on June 01, 2022 (UTC) and the second  one will scan emails sent no longer than 2*24=48 hours ago.

Another useful parameter is *--qth*. Is can be used to specify your own location. If it is used, the script will automatically calculate a distance and azimuth information relative to the location you specified. There two formats for this parameter value:
> --qth FN03gu

specifies the maidenhead grid square. Either 6 character or 8 character grids are accepted (I recommend to use 8 character ones for better precision). Another form is latitude, longitude as degrees and their fractions. For example:
> --qth "43.86,-79.46"

To find out all supported parameters issue:
> python3 ./wipe.py --help

## Advanced Features
One optional parameter is -o that can be used to specify an output file name where waypoints representing the station locations will be written. The format of the file is GPX and it is supported by a variety of GPS/Mapping related software. For instance:
> python3 ./wipe.py -o test.gpx -d 2 $PATINBOX

will produce a test.gpx file which could be imported into the Garmin BaseCamp software which will display the stations on any available map. There are also some online products that support GPX format files. One of them is:
> https://opentopomap.org 

