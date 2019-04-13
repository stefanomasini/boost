from RPi import GPIO
from time import sleep


def main():
    GPIO.setmode(GPIO.BCM)

    left_sensor = 11
    right_sensor = 9

    GPIO.setup(left_sensor, GPIO.IN)
    GPIO.setup(right_sensor, GPIO.IN)

    try:
        while True:
            if not GPIO.input(left_sensor):
                print("Robot is straying off to the right, move left captain!")
            elif not GPIO.input(right_sensor):
                print("Robot is straying off to the left, move right captain!")
            else:
                print("Following the line!")
            sleep(0.2)
    except:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
