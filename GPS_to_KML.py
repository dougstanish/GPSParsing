import argparse
import glob
import os
from pathlib import Path

import pynmea2

from math import isclose
import simplekml


def parse_args():
    """
    Parses arguments
    :return: The filename and the target variable
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("GPS_Filename", help='The data file\'s name')  # Adds filename arg
    parser.add_argument('KML_Filename', help='The KML filename to output to') # Adds destination filename

    args = parser.parse_args()  # Parses the args

    return args.GPS_Filename, args.KML_Filename


def to_kml(filename):
    """
    Reads in GPS file, and outputs a KML file
    :param filename: The GPS file
    """
    # Creates KML file
    kml = simplekml.Kml()

    # Defines what altitude will represent
    linestring = kml.newlinestring(description='Speed in Knots, instead of altitude.')

    # Sets color and size of the line
    linestring.style.color = simplekml.Color.yellow
    linestring.style.width = 6

    # Line settings
    linestring.extrude = 1
    linestring.tesselate = 1

    # Needs to be relative to ground to ensure line is above ground
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground

    coords = []

    last_long = 0
    last_lat = 0
    last_speed = ''

    was_stop = False
    last_stop_long = 0
    last_stop_lat = 0

    school_zone_nw_lat = 43.087982
    school_zone_nw_long = -77.682416
    school_zone_se_lat = 43.085117
    school_zone_se_long = -77.678254

    school_zone = kml.newgroundoverlay(name='School')

    school_zone.latlonbox.north = 43.087982
    school_zone.latlonbox.south = 43.085117
    school_zone.latlonbox.east = -77.678254
    school_zone.latlonbox.west = -77.682416

    school_zone.color = '7F0000ff'

    school_zone.altitude = 300

    # Opens the file
    with open(filename, 'r') as file:

        line = file.readline()  # Reads line from file

        while line:

            # If line is valid
            if '$GPRMC' in line:  # Checks to make sure line is correct type TODO - Make more efficient

                try:
                    parsed_data = pynmea2.parse(line)  # Attempts to parse the line
                except pynmea2.ChecksumError:  # If line is corrupted
                    line = file.readline()
                    continue  # Skips to next line

                # Gets long, lat, and speed from parsed data
                long = parsed_data.longitude
                lat = parsed_data.latitude
                speed = parsed_data.spd_over_grnd

                direction = parsed_data.true_course  # Angle of travel in degrees, currently unused

                # Attempt to box school
                if not ((school_zone_se_long > long > school_zone_nw_long) and (
                        school_zone_se_lat < lat < school_zone_nw_lat)):

                    # If the car has moved based off of position difference
                    if last_long != long or last_lat != lat:

                        # If the car is moving based on speed
                        if speed != '0' or last_speed != speed:

                            was_stop = False  # Tells that the last point was not a stop

                            # Adds coords to kml
                            coords.append([float(long), float(lat), float(speed)])

                            # Saves point coords of last location, used to check for stops
                            last_lat = lat
                            last_long = long
                            last_speed = speed

                        else:

                            # Otherwise, if this is the first point of a stop
                            if not was_stop and not isclose(lat, last_stop_lat, abs_tol=10**-4) \
                                    and not isclose(long, last_stop_long, abs_tol=10**-4):

                                # Saves the stop as a point on the map
                                pnt = kml.newpoint(description='Stoplight', coords=[(long, lat)])

                                # Tracks that this was as top
                                was_stop = True
                                last_stop_long = long
                                last_stop_lat = lat

                    else:  # If not moving

                        # Otherwise, if this is the first point of a stop
                        if not was_stop and not isclose(lat, last_stop_lat, abs_tol=10 ** -4) \
                                and not isclose(long, last_stop_long, abs_tol=10 ** -4):

                            # Saves stop as point
                            pnt = kml.newpoint(description='Stoplight', coords=[(long, lat)])

                            # Tracks that this was as top
                            was_stop = True
                            last_stop_long = long
                            last_stop_lat = lat

            # Reads next line
            line = file.readline()

    # Saves all KML coords to the file
    linestring.coords = coords  # Sets kml coords to coords

    Path("./kml").mkdir(exist_ok=True)

    # Saves the KML file
    kml.save('./kml/' + os.path.basename(filename) + '.kml')


def main():

    # filename, kml_filename = parse_args()

    # Reads raw GPS files from a gps directory
    gps_files = glob.glob('./gps/*.txt')

    # For each GPS file
    for file in gps_files:

        print(f'Now parsing {file}')

        to_kml(file)  # Converts to kml file

    # TODO - Detect left turns, start and end boxes

    # TODO - Left Turns - keep track of last X points, keep track of headings


if __name__ == '__main__':
    main()
