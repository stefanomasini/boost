# boost
Rotating bust

## Software

See [Development](./src/README.md)


## Provisioning the RaspberryPI

See [Provisioning](./provisioning/README.md)


## Shaft encoder

Generate the png/svg files with:

    pipenv run python generate_shaft_encoder
    
It will generate SVG files inside `shaft_encoder`:

 - `encoder_cut`: Used to laser-cut the disk with the encoder pattern
 - `encoder_mask`: Used to print the pattern on paper and glue it onto the disk
 - `sensors_cut`: Used to laser-cut holes for the reflective sensors
 - `sensors_engrave`: Used to engrave the shape of the sensors on the sensors support
 - `all`: Used to print as a reference
 
### Test sensors

    pipenv run python -m boost.sensors.sensors_adapter


## Reference

 - https://pinout.xyz/pinout/ground
 
