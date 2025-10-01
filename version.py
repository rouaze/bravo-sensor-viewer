#!/usr/bin/env python3
"""
Version information for Bravo Sensor Viewer
Aligned with GitHub releases for consistent versioning
"""

__version__ = "2.0.0"
__build_date__ = "2025-01-10"
__author__ = "Pierre Rouaze"
__description__ = "Professional Force Calibration Tool for Bravo/Malacca/Spotlight 2 Devices"

# Version components for programmatic access
VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_TUPLE = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

def get_version_string():
    """Get formatted version string"""
    return f"v{__version__} ({__build_date__})"

def get_full_version_info():
    """Get complete version information dictionary"""
    return {
        "version": __version__,
        "build_date": __build_date__,
        "author": __author__,
        "description": __description__,
        "version_tuple": VERSION_TUPLE
    }

# For executable builds - can be imported to show version in --version flag
if __name__ == "__main__":
    print(f"Bravo Sensor Viewer {get_version_string()}")
    print(f"Description: {__description__}")
    print(f"Author: {__author__}")