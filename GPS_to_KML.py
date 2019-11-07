import argparse
import re

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

    last_long = ''
    last_lat = ''
    last_speed = ''

    with open(filename, 'r') as file:

        line = file.readline()

        # Regex to make sure line being parsed is not corrupted or incomplete
        pattern = re.compile('(lng=)-?[0-9]+(\.)[0-9]+(, lat=)-?[0-9]+(\.)[0-9]+(, altitude=)-?[0-9]+(\.)[0-9]+'
                             '(, speed=)[0-9]+(\.)[0-9]+(, satellites=)[0-9]+(, angle=)[0-9]+(\.)[0-9]+'
                             '(, fixquality=)[0-9]+')

        while line:

            # If line is valid
            if pattern.match(line):  # Checks to make sure line is valid

                # Splits line into long, lat, and speed
                split_coords = line.split(', ')
                long = split_coords[0][4:]
                lat = split_coords[1][4:]
                speed = split_coords[3][6:]

                # If the car has moved
                if last_long != long or last_lat != lat:

                    # If the car is moving
                    if speed != '0' or last_speed != speed:

                        # Adds coords to kml
                        coords.append([float(long), float(lat), float(speed)])

                        last_lat = lat
                        last_long = long
                        last_speed = speed

            line = file.readline()

    linestring.coords = coords  # Sets kml coords to coords

    kml.save(kml_filename)


def main():
    
    filename, kml_filename = parse_args()

    to_kml(filename, kml_filename)


if __name__ == '__main__':
    main()
