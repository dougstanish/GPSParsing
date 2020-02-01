import argparse
import glob
import os

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


def to_kml(filename, kml_filename):

    # Creates KML file
    kml = simplekml.Kml()

    linestring = kml.newlinestring(description='Speed in Knots, instead of altitude.')

    linestring.style.color = simplekml.Color.yellow
    linestring.style.width = 6



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

    print(f'Filename = {filename}')

    with open(filename, 'r') as file:

        line = file.readline()  # Reads line from file

        while line:

            # If line is valid
            if '$GPRMC' in line:  # Checks to make sure line is correct type TODO - Make more efficient

                try:
                    parsed_data = pynmea2.parse(line)
                except pynmea2.ChecksumError:  # If line is corrupted
                    line = file.readline()
                    continue  # Skips to next line

                # Gets long, lat, and speed from parsed data
                long = parsed_data.longitude
                lat = parsed_data.latitude
                speed = parsed_data.spd_over_grnd

                # If the car has moved
                if last_long != long or last_lat != lat:

                    # If the car is moving
                    if speed != '0' or last_speed != speed:

                        was_stop = False

                        # Adds coords to kml
                        coords.append([float(long), float(lat), float(speed)])

                        last_lat = lat
                        last_long = long
                        last_speed = speed

                    else:

                        if not was_stop and not isclose(lat, last_stop_lat, abs_tol=10**-4) and not isclose(long, last_stop_long, abs_tol=10**-4):
                            pnt = kml.newpoint(description='Stoplight', coords=[(long, lat)])
                            was_stop = True
                            last_stop_long = long
                            last_stop_lat = lat

                else:
                    if not was_stop and not isclose(lat, last_stop_lat, abs_tol=10 ** -4) and not isclose(long,
                                                                                                          last_stop_long,
                                                                                                          abs_tol=10 ** -4):
                        pnt = kml.newpoint(description='Stoplight', coords=[(long, lat)])
                        was_stop = True
                        last_stop_long = long
                        last_stop_lat = lat

            line = file.readline()

    linestring.coords = coords  # Sets kml coords to coords

    kml.save('./kml/' + os.path.split(os.path.basename(filename))[0] + '.kml')


def main():

    filename, kml_filename = parse_args()

    print("Got here")

    gps_files = glob.glob('./gps/*.txt')

    print(gps_files)

    for file in gps_files:
        print(file)
        to_kml(file, None)

    # to_kml(filename, kml_filename)

    # TODO - Detect left turns, start and end boxes


if __name__ == '__main__':
    main()
