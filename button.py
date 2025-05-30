import lgpio
import time

class Button:
    def __init__(self, pin):
        self.h = lgpio.gpiochip_open(0)
        self.pin = pin
        lgpio.gpio_claim_input(self.h, self.pin)

    def read_state_button(self):
        return lgpio.gpio_read(self.h, self.pin)
    
    def close(self):   
        lgpio.gpiochip_close(self.h)