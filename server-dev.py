import os
import sys


class CONFIG(object):
    server_port = 4000

    # Sensors
    sensor_pins = [11, 9, 10, 22, 27, 17]
    gpio_read_delay_in_ms = 5  # Wait before reading the sensor value after an interrupt, for reliability

    # Shaft encoder
    sensor_devices = {
        'A': [0, 1, 2, 3, 4, 5],    # MSB to LSB - indexes refer to "sensor_pins", above
    }
    stasis_timeout_in_sec = 1.0     # Time to wait on the same sector before assuming speed is null
    max_speed_in_deg_per_sec = 800  # If speed is higher, assume a fault in the sensors read

    # Motors
    motors_apply_power_every_ms = 50  # Max 250, otherwise the ThunderBorg protection mechanism will kick in and stop the motors


if __name__ == '__main__':
    src_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')
    sys.path.append(src_dirpath)
    from boost.main import run_application
    run_application(CONFIG)
