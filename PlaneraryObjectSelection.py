"""
This module provides functionality to access celestial body identifiers for use with
JPL Horizons systems API.
"""

class PlanetaryObjectSelection:
    """
    A collection of celestial body identifiers for use with the PlanetaryObjectsFetcher class.
    
    This dictionary maps common names to their JPL Horizons system identifiers.
    """

    OBJECTS = {
        # The Sun
        "Sun": "10",
        
        # Inner Planets (Rocky/Terrestrial)
        "Mercury": "199",
        "Venus": "299",
        "Earth": "399",
        "Mars": "499",
        
        # Outer Planets (Gas Giants)
        "Jupiter": "599",
        "Saturn": "699",
        "Uranus": "799",
        "Neptune": "899",
        
        # Dwarf Planets
        "Pluto": "999",
        "Ceres": "2000001",
        
        # Earth's Moon
        "Moon": "301",
        
        # Moons of Mars
        "Phobos": "401",        # Larger moon of Mars
        "Deimos": "402",        # Smaller moon of Mars
        
        # Major Moons of Jupiter (Galilean Moons)
        "Io": "501",            # Innermost Galilean moon, volcanic
        "Europa": "502",        # Ice-covered moon with subsurface ocean
        "Ganymede": "503",      # Largest moon in the solar system
        "Callisto": "504",      # Heavily cratered outer Galilean moon
        
        # Major Moons of Saturn
        "Titan": "606",         # Largest moon of Saturn, thick atmosphere
        "Rhea": "605",          # Second-largest moon of Saturn
        "Iapetus": "608",       # Two-toned moon with distinctive coloring
        "Enceladus": "602",     # Icy moon with water geysers
        
        # Major Moons of Uranus
        "Titania": "703",       # Largest moon of Uranus
        "Oberon": "704",        # Second-largest moon of Uranus
        
        # Major Moons of Neptune
        "Triton": "801",        # Largest moon of Neptune, retrograde orbit
    }