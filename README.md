# boost
Rotating bust

## Software

### Pre-requisites

- Python 3.5
    - Use PyEnv to set up the specific python version: 
        - `pyenv local 3.5.7`
        - `pyenv shell`
- NodeJS
- Yarn

### Install dependencies

    pipenv install (or maybe pipenv install --skip-lock)
    cd frontend
    yarn

### Run tests

    pipenv run python run-tests.py


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


## Reference

 - https://pinout.xyz/pinout/ground
 
