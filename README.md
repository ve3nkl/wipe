# WI(nlink) P(osition) E(xtractor)
## Overview
Stations can send their location information using Check-In and other forms. Some Winlink clients have no ability to extract and use this information (for example, by displaying it on a map). If such a client saves the emails as separate text files in a specific directory, this python script can scan the emails, extract station positions and display this information in an easy to read form. It also can create waypoints file in the GPX or KML format. Both of them can be used by a variety of GPS/Mapping software to visually put the stations on a map. KML file, for example, can be used with Google Maps. 
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

