import argparse
import re

import simplekml

def parse_args():
    """
    Parses arguments
    :return: The filename and the target variable
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", help='The data file\'s name')  # Adds filename and target attribute args

    args = parser.parse_args()  # Parses the args

    return args.filename


def to_kml(filename):

    # Creates KML file
    kml = simplekml.Kml()
    kml.style.linestyle

    linestring = kml.newlinestring(name='Test Path')

    linestring.extrude = 1
    linestring.tesselate = 1
    linestring.altitudemode = simplekml.AltitudeMode.absolute

    coords = []

    with open(filename, 'r') as file:

        line = file.readline()

        pattern = re.compile('(lng=)-?[0-9]+(\.)[0-9]+(, lat=)-?[0-9]+(\.)[0-9]+(, altitude=)-?[0-9]+(\.)[0-9]+'
                             '(, speed=)[0-9]+(\.)[0-9]+(, satellites=)[0-9]+(, angle=)[0-9]+(\.)[0-9]+'
                             '(, fixquality=)[0-9]+')

        while line:

            if(pattern.match(line)):  # Checks to make sure line is valid

                split_coords = line.split(', ')

                long = split_coords[0][4:]
                lat = split_coords[1][4:]
                speed = split_coords[3][6:]

                coords.append([float(long), float(lat), float(speed)])

            line = file.readline()

    linestring.coords = coords  # Sets kml coords to coords

    kml.save("test.kml")

    print()




def main():
    filename = parse_args()

    to_kml(filename)

if __name__ == '__main__':
    main()