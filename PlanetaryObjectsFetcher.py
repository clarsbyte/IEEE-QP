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
    bodies such as planets, moons, asteroids, and comets. All data is geocentric (Earth-centered).
    
    Attributes:
        BASE_REQUEST_URL (str): The base URL for the JPL Horizons API endpoint.
    """
    BASE_REQUEST_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"


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
    def fetch_ephemeris_data(target_body, quantities, start_date=None, stop_date=None,
                           step_size="1h", center="399"):
        """
        Fetch ephemeris data for a specified celestial body from JPL Horizons API.

        This method queries the Horizons system for astronomical data over a specified
        time period with configurable intervals.

        Args:
            target_body (str): The Horizons identifier for the target body.
                              Examples: '301' for Moon, '10' for Sun, '499' for Mars.
            quantities (str): The type of data to retrieve.
                            '2' = Apparent RA & DEC (coordinates)
                            '20' = Observer range & range-rate (distance)
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
                                       Defaults to current date.
            stop_date (str, optional): Stop date in 'YYYY-MM-DD' format.
                                      Defaults to tomorrow's date.
            step_size (str, optional): Time interval between data points.
                                      Examples: '1h' (1 hour), '30m' (30 minutes), '1d' (1 day)
                                      Defaults to '1h'.
            center (str, optional): Observer location code.
                                   '399' = Earth Geocentric (default)
                                   '500@399' = Earth's center

        Returns:
            list: A list containing the parsed ephemeris data line(s).
                 Returns empty list if the request fails.
        """
        if start_date is None:
            start_date = PlanetaryObjectsFetcher.get_current_date()
        if stop_date is None:
            stop_date = PlanetaryObjectsFetcher.get_tomorrow_date()

        params = {
            "format": "json",
            "COMMAND": str(target_body),
            "CENTER": center,  # Observer location
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "OUT_UNITS": "KM-S",
            "QUANTITIES": quantities,
            "START_TIME": start_date,
            "STOP_TIME": stop_date,
            "STEP_SIZE": step_size
        }

        response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=params)

        if (response.status_code == 200):
            data_dict = response.json() # Converts json into dictionary
            ephemeris_text = data_dict.get("result") # Gets the text inside the result key

            return PlanetaryObjectsFetcher.parse_ephemeris_data(ephemeris_text)
        else:
            print(f"Error fetching ephemeris data: {response.status_code}")
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
    def fetch_coordinates(target_body, start_date=None, stop_date=None, step_size="1h"):
        """
        Fetch the celestial coordinates (Right Ascension and Declination) for a target body.

        This is a convenience method that wraps fetch_ephemeris_data with quantities='2'
        to retrieve coordinate data.

        Args:
            target_body (str): The Horizons identifier for the target body.
                              Examples: '301' for Moon, '10' for Sun, '499' for Mars.
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
            stop_date (str, optional): Stop date in 'YYYY-MM-DD' format.
            step_size (str, optional): Time interval (e.g., '1h', '30m', '1d').

        Returns:
            list: Parsed ephemeris data containing RA/DEC coordinates.
        """
        return PlanetaryObjectsFetcher.fetch_ephemeris_data(
            target_body, quantities="2",
            start_date=start_date, stop_date=stop_date, step_size=step_size
        )


    @staticmethod
    def fetch_distance(target_body, start_date=None, stop_date=None, step_size="1h"):
        """
        Fetch the distance (range) from Earth to a target celestial body.

        This is a convenience method that wraps fetch_ephemeris_data with quantities='20'
        to retrieve distance data.

        Args:
            target_body (str): The Horizons identifier for the target body.
                              Examples: '301' for Moon, '10' for Sun, '499' for Mars.
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
            stop_date (str, optional): Stop date in 'YYYY-MM-DD' format.
            step_size (str, optional): Time interval (e.g., '1h', '30m', '1d').

        Returns:
            list: Parsed ephemeris data containing distance/range information.
        """
        return PlanetaryObjectsFetcher.fetch_ephemeris_data(
            target_body, quantities="20",
            start_date=start_date, stop_date=stop_date, step_size=step_size
        )

    @staticmethod
    def radian_to_degree(radian):
        """
        Convert an angle from radians to degrees.

        Args:
            radian (float): Angle in radians.
        Returns:
            float: Angle in degrees (0-360 range).
        """
        degree = radian * (180.0 / np.pi)
        if degree < 0:
            degree = 360 + degree
        return degree
    
    @staticmethod
    def hms_to_degrees(hours, minutes, seconds):
        """
        Convert Right Ascension from hours, minutes, seconds to degrees.

        Args:
            hours (float): Hours (0-24)
            minutes (float): Minutes (0-60)
            seconds (float): Seconds (0-60)

        Returns:
            float: Angle in degrees (0-360).
        """
        return (hours + minutes/60.0 + seconds/3600.0) * 15.0

    @staticmethod
    def dms_to_degrees(degrees, arcminutes, arcseconds):
        """
        Convert Declination from degrees, arcminutes, arcseconds to decimal degrees.

        Args:
            degrees (float): Degrees
            arcminutes (float): Arcminutes (0-60)
            arcseconds (float): Arcseconds (0-60)

        Returns:
            float: Angle in decimal degrees.
        """
        sign = 1 if degrees >= 0 else -1
        return sign * (abs(degrees) + arcminutes/60.0 + arcseconds/3600.0)

    @staticmethod
    def parse_ra_dec(coordinate_data):
        """
        Parse Right Ascension and Declination from JPL Horizons coordinate data.

        Args:
            coordinate_data (list): List containing coordinate string from fetch_coordinates

        Returns:
            dict: Dictionary with 'ra_deg' and 'dec_deg' in decimal degrees,
                  or None if parsing fails.
        """
        if not coordinate_data or len(coordinate_data) == 0:
            return None

        try:
            # Split the data line by whitespace
            parts = coordinate_data[0].split()

            # RA is typically in format HH MM SS.ss
            # DEC is typically in format +/-DD MM SS.s
            # The exact positions may vary, so we'll look for the pattern

            ra_hours = float(parts[3])
            ra_minutes = float(parts[4])
            ra_seconds = float(parts[5])

            dec_degrees = float(parts[6])
            dec_arcminutes = float(parts[7])
            dec_arcseconds = float(parts[8])

            ra_deg = PlanetaryObjectsFetcher.hms_to_degrees(ra_hours, ra_minutes, ra_seconds)
            dec_deg = PlanetaryObjectsFetcher.dms_to_degrees(dec_degrees, dec_arcminutes, dec_arcseconds)

            return {
                'ra_deg': ra_deg,
                'dec_deg': dec_deg,
                'ra_hms': f"{ra_hours:02.0f}h {ra_minutes:02.0f}m {ra_seconds:05.2f}s",
                'dec_dms': f"{dec_degrees:+03.0f}° {dec_arcminutes:02.0f}' {dec_arcseconds:04.1f}\""
            }
        except (IndexError, ValueError) as e:
            print(f"Error parsing coordinate data: {e}")
            print(f"Data: {coordinate_data}")
            return None

    @staticmethod
    def get_coordinates_degrees(target_body, start_date=None, stop_date=None, step_size="1h"):
        """
        Get Right Ascension and Declination in degrees for a target body.

        Args:
            target_body (str): The Horizons identifier for the target body.
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
            stop_date (str, optional): Stop date in 'YYYY-MM-DD' format.
            step_size (str, optional): Time interval (e.g., '1h', '30m', '1d').

        Returns:
            dict: Dictionary with 'ra_deg' and 'dec_deg' in decimal degrees.
        """
        coords = PlanetaryObjectsFetcher.fetch_coordinates(
            target_body,
            start_date=start_date,
            stop_date=stop_date,
            step_size=step_size
        )
        return PlanetaryObjectsFetcher.parse_ra_dec(coords)
    
#serial.write(PlanetaryObjectsFetcher.fetch_distance("301")[0])
    
if __name__ == "__main__":
    # Example: Get Moon coordinates in degrees (default: current time)
    print("Moon coordinates in degrees (current time):")
    moon_data = PlanetaryObjectsFetcher.get_coordinates_degrees("301")
    if moon_data:
        print(f"   Right Ascension:  {moon_data['ra_deg']:.4f}° ({moon_data['ra_hms']})")
        print(f"   Declination:      {moon_data['dec_deg']:.4f}° ({moon_data['dec_dms']})")
    
    print("Available objects:", ", ".join(PlanetaryObjectSelection.OBJECTS.keys()))

    while True:
        if serial.in_waiting > 0:
            choice = serial.readline()
            choice = choice.decode('utf-8').strip()
            print(f"\nReceived: {choice}")

            if choice in PlanetaryObjectSelection.OBJECTS:
                object_id = PlanetaryObjectSelection.OBJECTS[choice]
                data = PlanetaryObjectsFetcher.get_coordinates_degrees(object_id)
                message = f"{data['ra_deg']:.4f},{data['dec_deg']:.4f}\n"
                serial.write(message.encode('utf-8'))
                print(f"Sent coordinates for {choice}: {message.strip()}")
            elif choice.isdigit():
                # List all objects
                all_objects = "\n".join([f"{name}: {obj_id}"
                                        for name, obj_id in PlanetaryObjectSelection.OBJECTS.items()])
                serial.write(all_objects.encode('utf-8'))
                print("Sent all object names and IDs")
            else:
                error_msg = f"Unknown object: {choice}\n"