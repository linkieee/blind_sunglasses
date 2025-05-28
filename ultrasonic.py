from gpiozero import DistanceSensor

class UltrasonicSensor:
    def __init__(self, echo_pin, trigger_pin, max_distance=2.0):
        self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin, max_distance=max_distance)

    def get_distance(self):
        print(self.sensor.distance )
        return round(self.sensor.distance * 100, 2) # Returns distance in meters
