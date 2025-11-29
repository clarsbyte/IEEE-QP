"""
This module provides functionality to fetch ephemeris data (astronomical positions
and distances) for celestial bodies from NASA's JPL Horizons API.
"""


import requests
from datetime import datetime, timedelta
import serial
import numpy as np
from PlaneraryObjectSelection import PlanetaryObjectSelection

serial = serial.Serial(
        port='COM6',  
        baudrate=9600,
        timeout=1
    )

class PlanetaryObjectsFetcher:
    """
    A utility class for fetching astronomical ephemeris data from NASA's JPL Horizons system.
    
    This class provides methods to retrieve coordinates and distances for various celestial
    bodies such as planets, moons, asteroids, and comets. Coordinates are computed based on
    the user's geographic location (via IP geolocation).
    
    Attributes:
        BASE_REQUEST_URL (str): The base URL for the JPL Horizons API endpoint.
    """
    BASE_REQUEST_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"


    @staticmethod
    def get_user_location():
        """
        Get approximate user location using ipinfo.io.
        
        Returns:
            tuple: A tuple containing (latitude, longitude, elevation_meters).
                  Returns (0, 0, 0) if location lookup fails.
        """
        try:
            data = requests.get("https://ipinfo.io/json").json()

            loc = data.get("loc", "0,0")  # "lat,lon"
            lat_str, lon_str = loc.split(",")

            lat = float(lat_str)
            lon = float(lon_str)
            elev = 0  # no elevation data available iva ipinfo

            return lat, lon, elev
        except Exception as e:
            print("Location lookup failed:", e)
            return 0, 0, 0


    @staticmethod
    def get_current_date():
        """
        Get the current date in YYYY-MM-DD format.
        
        Returns:
            str: Current date formatted as 'YYYY-MM-DD'.
        """
        return datetime.now().strftime("%Y-%m-%d")


    @staticmethod
    def get_tomorrow_date():
        """
        Get tomorrow's date in YYYY-MM-DD format.
        
        Returns:
            str: Tomorrow's date formatted as 'YYYY-MM-DD'.
        """
        today = datetime.now()
        tomorrow = timedelta(days=1) + today
        return tomorrow.strftime("%Y-%m-%d")
    

    @staticmethod 
    def fetch_ephemeris_data(target_body, quantities):
        """
        Fetch ephemeris data for a specified celestial body from JPL Horizons API.
        
        This method queries the Horizons system for astronomical data over a 24-hour
        period starting from the current date, with hourly intervals. Data is computed
        from the user's geographic location obtained via IP geolocation.
        
        Args:
            target_body (str): The Horizons identifier for the target body.
                              Examples: '301' for Moon, '10' for Sun, '499' for Mars.
            quantities (str): The type of data to retrieve.
                            '4' = Azimuth & Elevation (local coordinates)
                            '20' = Observer range & range-rate (distance)
        
        Returns:
            list: A list containing the parsed ephemeris data line(s).
                 Returns empty list if the request fails.
        """
        current_date = PlanetaryObjectsFetcher.get_current_date()
        tomorrow_date = PlanetaryObjectsFetcher.get_tomorrow_date()

        # Get real user geolocation
        lat, lon, elev = PlanetaryObjectsFetcher.get_user_location()
        elev_km = elev / 1000.0
        
        # Convert longitude to East longitude (0-360) if negative
        if lon < 0:
            lon = lon + 360

        params = {
            "format": "json",
            "COMMAND": str(target_body),
            "CENTER": "coord@399",  # Coordinate-based observer on Earth
            "COORD_TYPE": "GEODETIC",
            "SITE_COORD": f"'{lon},{lat},{elev_km}'",
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "OUT_UNITS": "KM-S",
            "QUANTITIES": quantities,
            "START_TIME": current_date,
            "STOP_TIME": tomorrow_date,
            "STEP_SIZE": "1h"
        }

        response = requests.get(PlanetaryObjectsFetcher.BASE_REQUEST_URL, params=params)

        if response.status_code == 200:
            data_dict = response.json()  # Converts json into dictionary
            ephemeris_text = data_dict.get("result")  # Gets the text inside the result key

            return PlanetaryObjectsFetcher.parse_ephemeris_data(ephemeris_text)
        else:
            print(f"Error fetching coordinates: {response.status_code}")
            return []


    @staticmethod
    def parse_ephemeris_data(ephemeris_text):
        """
        Parse ephemeris data from the Horizons API text response.
        
        The Horizons API returns data in a text format with markers:
        - $SOE (Start Of Ephemeris) marks the beginning of data
        - $EOE (End Of Ephemeris) marks the end of data
        
        This method extracts only the first non-empty data line between these markers.
        
        Args:
            ephemeris_text (str): Raw text response from the Horizons API containing
                                 ephemeris data with $SOE and $EOE markers.
        
        Returns:
            list: A list containing the first data line as a string.
                 Returns empty list if no data is found between markers.
        """
        ephemeris_lines = ephemeris_text.split("\n")
        data_lines = []
        data_found = False
        
        for line in ephemeris_lines:
            if "$SOE" in line:
                data_found = True
                continue
            if "$EOE" in line:
                break
            if data_found and line.strip():
                data_lines.append(line.strip())
                break
        
        return data_lines


    @staticmethod   
    def fetch_coordinates(target_body):
        """
        Fetch the celestial coordinates (Azimuth and Elevation) for a target body.
        
        This is a convenience method that wraps fetch_ephemeris_data with quantities='4'
        to retrieve local coordinate data based on the user's geographic location.
        
        Args:
            target_body (str): The Horizons identifier for the target body.
                              Examples: '301' for Moon, '10' for Sun, '499' for Mars.
        
        Returns:
            list: Parsed ephemeris data containing Azimuth/Elevation coordinates.
        """
        return PlanetaryObjectsFetcher.fetch_ephemeris_data(target_body, quantities="4")


    @staticmethod
    def fetch_distance(target_body):
        """
        Fetch the distance (range) from the user's location to a target celestial body.

        This is a convenience method that wraps fetch_ephemeris_data with quantities='20'
        to retrieve distance data.

        Args:
            target_body (str): The Horizons identifier for the target body.
                              Examples: '301' for Moon, '10' for Sun, '499' for Mars.

        Returns:
            list: Parsed ephemeris data containing distance/range information.
        """
        return PlanetaryObjectsFetcher.fetch_ephemeris_data(target_body, quantities="20")


    @staticmethod
    def parse_coordinates(coord_string):
        """
        Parse azimuth and elevation from a coordinate string.

        Extracts the numerical azimuth and elevation values from the raw
        ephemeris coordinate data returned by fetch_coordinates().

        Args:
            coord_string (str): Raw coordinate string from Horizons API.
                               Example: "2025-Nov-29 00:00 *m  131.587713  38.069515"

        Returns:
            tuple: A tuple containing (azimuth, elevation) as floats.
                  - azimuth (float): Horizontal angle in degrees (0-360)
                  - elevation (float): Vertical angle in degrees (0-90)
        """
        parts = coord_string.split()
        azimuth = float(parts[-2])
        elevation = float(parts[-1])
        return azimuth, elevation
    
#serial.write(PlanetaryObjectsFetcher.fetch_distance("301")[0])
    
if __name__ == "__main__":
    print("Arduino-Python Celestial Object Tracker")
    print("========================================")
    print(f"Serial port: {serial.port}")
    print(f"Baudrate: {serial.baudrate}")
    print("Available objects:", ", ".join(PlanetaryObjectSelection.OBJECTS.keys()))
    print("\nWaiting for Arduino commands...\n")

    while True:
        if serial.in_waiting > 0:
            raw_data = serial.readline()
            raw_data = raw_data.decode('utf-8').strip()
            print(f"Received: {raw_data}")

            # Parse "STAR:ObjectName" format from Arduino
            if raw_data.startswith("STAR:"):
                object_name = raw_data[5:]  # Remove "STAR:" prefix

                if object_name in PlanetaryObjectSelection.OBJECTS:
                    object_id = PlanetaryObjectSelection.OBJECTS[object_name]
                    print(f"Fetching coordinates for {object_name} (ID: {object_id})...")

                    try:
                        data = PlanetaryObjectsFetcher.fetch_coordinates(object_id)
                        if data:
                            azimuth, elevation = PlanetaryObjectsFetcher.parse_coordinates(data[0])
                            message = f"{azimuth:.6f},{elevation:.6f}\n"
                            serial.write(message.encode('utf-8'))
                            print(f"✓ Sent: Az={azimuth:.2f}° El={elevation:.2f}°\n")
                        else:
                            print(f"✗ No data returned for {object_name}\n")
                    except Exception as e:
                        print(f"✗ Error fetching data: {e}\n")
                else:
                    print(f"✗ Unknown object: {object_name}\n")