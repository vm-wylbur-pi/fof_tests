# This script is configured (in platformio.ini) to be run just before
# the flower firmware is built.
#
# General docs for pre/post actions are at
# https://docs.platformio.org/en/stable/scripting/actions.html

import datetime

print(f"Running pre-build script to register version naming callback.")

def generate_build_time_header():
    print("Running function to fill in the firmware build time.")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %-I:%M %p")

    header_filename = "include/autogenerated_build_timestamp.h"
    header_content = f"""
    // DO NOT EDIT
    //
    // This file is autogenerated by the set_build_timestamp.py
    // script located beside platformio.ini

    #ifndef BUILD_TIMESTAMP
        #define BUILD_TIMESTAMP "{timestamp}"
    #endif
    """

    with open(header_filename, 'w') as version_header_file:
        version_header_file.write(header_content)

# Runs unconditionally, not linked to any particular build target.
generate_build_time_header()

