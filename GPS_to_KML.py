import argparse
import glob
import os
from pathlib import Path

import pynmea2

from math import isclose
import simplekml


def read_file(filename):
    """

    :param filename:
    :return:
    """
    raw_data = []

    with open(filename, 'r') as file:

        line = file.readline()

        while line:

            if '$GPRMC' in line:

                try:
                    parsed_data = pynmea2.parse(line)
                except pynmea2.ChecksumError:
                    line = file.readline()
                    continue

                if parsed_data.status == 'A':

                    angle = parsed_data.true_course
                    date = parsed_data.datestamp
                    lat = parsed_data.latitude
                    long = parsed_data.longitude
                    speed = parsed_data.spd_over_grnd
                    time = parsed_data.timestamp

                    raw_data.append({
                        'Angle': float(angle),
                        'Date': date,
                        'Lat': float(lat),
                        'Long': float(long),
                        'Speed': float(speed),
                        'Time': time
                    })

            line = file.readline()

        return raw_data


def clean_datapoints(datapoints):
    """

    :param datapoints:
    :return:
    """
    clean_data = {
        'Coords': [],
        'Points': []
    }

    last_lat = 0
    last_long = 0
    last_speed = 0
    was_stop = False
    last_stop_long = 0
    last_stop_lat = 0

    for point in datapoints:
        if last_long != point['Long'] or last_lat != point['Lat']:
            if point['Speed'] != 0 or last_speed != point['Speed']:
                was_stop = False
                clean_data['Coords'].append(point)
                last_lat = point['Lat']
                last_long = point['Long']
                last_speed = point['Speed']
            else:
                if not was_stop and not isclose(point['Lat'], last_stop_lat, abs_tol=10**-4) \
                        and not isclose(point['Long'], last_stop_long, abs_tol=10**-4):
                    clean_data['Points'].append(point)
                    was_stop = True
                    last_stop_long = point['Long']
                    last_stop_lat = point['Lat']
        else:
            if not was_stop and not isclose(point['Lat'], last_stop_lat, abs_tol=10 ** -4) \
                    and not isclose(point['Long'], last_stop_long, abs_tol=10 ** -4):
                clean_data['Points'].append(point)
                was_stop = True
                last_stop_long = point['Long']
                last_stop_lat = point['Lat']

    return clean_data


def create_paths(datapoints):
    """

    :param datapoints:
    :return:
    """
    path = {
        'Description': 'Altitude information is replaced with speed in knots',
        'Color': '7F00ff00',
        'Coords': []
    }

    for point in datapoints:
        path['Coords'].append((point['Long'], point['Lat'], point['Speed']))

    return path


def detect_left_turns(datapoints):
    """

    :param datapoints:
    :return:
    """


def process_gps(filename):
    """

    :param filename: The GPS file
    :return: A dictionary of relevant data to be written to KML
    """
    raw_data = read_file(filename)
    clean_data = clean_datapoints(raw_data)
    path = create_paths(clean_data['Coords'])
    write_path(path, filename)
    write_hazards(clean_data['Points'], filename)


def write_path(path_data, filename):
    """
    Take processed path data and write to the '_Path.kml' file
    :param path_data:
    :return:
    """
    kml = simplekml.Kml()
    ls = kml.newlinestring(description=path_data['Description'])
    ls.extrude = 1
    ls.tesselate = 1
    ls.altitudemode = simplekml.AltitudeMode.relativetoground
    ls.coords = path_data['Coords']
    ls.style.linestyle.width = 6
    ls.style.linestyle.color = path_data['Color']

    Path("./kml").mkdir(exist_ok=True)

    kml.save('./kml/' + os.path.basename(os.path.splitext(filename)[0]) + '_Path.kml')


def write_hazards(hazard_data, filename):
    """
    Take processed hazard data and write to the '_Hazards.kml' file
    :param hazard_data:
    :return:
    """
    kml = simplekml.Kml()
    for point in hazard_data:
        kml.newpoint(
            name='Stop',
            description=f"{point['Time']} {point['Date']}",
            coords=[(point['Long'], point['Lat'])]
        )

    Path("./kml").mkdir(exist_ok=True)

    kml.save('./kml/' + os.path.basename(os.path.splitext(filename)[0]) + '_Hazards.kml')


def main():

    # filename, kml_filename = parse_args()

    # Reads raw GPS files from a gps directory
    gps_files = glob.glob('./gps/*.txt')

    # For each GPS file
    for file in gps_files:

        print(f'Now parsing {file}')
        process_gps(file)


if __name__ == '__main__':
    main()
