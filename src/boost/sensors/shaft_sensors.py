from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)


def main():
    left_sensor = 11
    right_sensor = 9

    GPIO.setup(left_sensor, GPIO.IN)
    GPIO.setup(right_sensor, GPIO.IN)

    def my_callback(channel):
        print("edge detected on left", channel)

    # def my_callback2(channel):
    #     print("rising edge detected on left")

    GPIO.add_event_detect(left_sensor, GPIO.BOTH, callback=my_callback, bouncetime=300)

    # GPIO.add_event_detect(left_sensor, GPIO.RISING, callback=my_callback2, bouncetime=300)

    try:
        while True:
            # if not GPIO.input(left_sensor):
            #     print("Robot is straying off to the right, move left captain!")
            # elif not GPIO.input(right_sensor):
            #     print("Robot is straying off to the left, move right captain!")
            # else:
            #     print("Following the line!")
            sleep(1)
    except:
        pass

    GPIO.cleanup()


if __name__ == '__main__':
    main()
