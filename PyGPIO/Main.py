import pygpiolib as gpio
import time
import threading
import socket
from http import client


class LegButtonThread:
    def __init__(self, gpio_led: int, gpio_button: int, edge: str = 'rising', counter: float = 0.5, step: float = .025):
        self.counter = counter
        self.step = step
        self.lock = threading.Lock()
        self.button = gpio.Button(gpio_button, edge=edge)
        self.led = gpio.Led(gpio_led)

    def update(self):
        with self.button:
            while self.counter > self.step:
                if self.button.click():
                    with self.lock:
                        self.counter -= self.step

    def blink(self):
        with self.led:
            while self.counter > self.step:
                self.led.switch()
                time.sleep(self.counter)

    def start(self):
        try:
            led_thread = threading.Thread(target=self.blink)
            button_thread = threading.Thread(target=self.update)
            led_thread.start()
            button_thread.start()
            led_thread.join()
            button_thread.join()
        except KeyboardInterrupt:
            self.button.close()
            self.led.close(True)


def get_ip():
    ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip.connect(("8.8.8.8", 80))
    return ip.getsockname()[0]


def http_func():
    ip = client.HTTPConnection("ifconfig.me")
    ip.request("GET","/ip")
    return ip.getresponse().read()


if __name__ == '__main__':
    a = b'1'
    b = 4
    c = int(a) + b
    print(c)
    # print(f"socket: {get_ip()}")
    # print(f"http: {http_func()}")
    # print(gpio.__version__)
    # my_thread = LegButtonThread(110, 0, counter=0.25, step=0.01)
    # my_thread.start()
