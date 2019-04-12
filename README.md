# boost
Rotating bust

## Install dependencies

    pipenv install

## Run tests

    pipenv run python run-tests.py


## Raspberry PI

Raspbian Stretch Lite
  - Version: April 2019
  - Release date: 2019-04-08
  - Kernel version: 4.14
  - [Image download page](https://www.raspberrypi.org/downloads/raspbian/)
  - [Installation instructions](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)


## Shaft encoder

Generate the png/svg files with:

    pipenv run python generate_shaft_encoder
    
It will generate SVG files inside `shaft_encoder`:

 - `encoder_cut`: Used to laser-cut the disk with the encoder pattern
 - `encoder_mask`: Used to print the pattern on paper and glue it onto the disk
 - `sensors_cut`: Used to laser-cut holes for the reflective sensors
 - `sensors_engrave`: Used to engrave the shape of the sensors on the sensors support
 - `all`: Used to print as a reference
