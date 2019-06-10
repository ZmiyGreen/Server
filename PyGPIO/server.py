import socket
import pygpiolib as gpio
import threading
import argparse
import sys


def get_ip():
    ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip.connect(("8.8.8.8", 80))
    return ip.getsockname()[0]


class Architect:
    def __init__(self, port: int, gpio_button, size: int = 1024):
        self.size = size
        self.ip = get_ip()
        self.port = port
        self.power_on = True
        self.button = gpio.Button(gpio_button, 'rising')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def work(self):
        self.server.bind((self.ip, self.port))
        print("server waiting!")
        while self.power_on:
            data, client = self.server.recvfrom(self.size)
            data = int(data.decode('utf-8'))
            print(f"{data} {client}")
            # -1 отключить клиент, -2 - отключить клиент затем выключить сервер
            if data == -1:
                self.server.sendto(b'-1', client)
            elif data == -2:
                print("stop!")
            else:
                self.server.sendto(b'1', client)
        self.server.close()
        print("server off")

    def power_off(self):
        with self.button:
            if self.button.click():
                self.power_on = False
                self.server.sendto(b'-2', (self.ip, self.port))
                print("power button off")

    def start(self):
        try:
            work_stream = threading.Thread(target=self.work)
            button_stream = threading.Thread(target=self.power_off)
            work_stream.start()
            button_stream.start()
            work_stream.join()
            button_stream.join()
        except:
            self.button.close(off_value=False)
            self.server.close()


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-p', '--port', type=int)
    args.add_argument('-b', '--button', type=int)
    values = args.parse_args(sys.argv[1:])
    stream = Architect(values.port, values.button)
    stream.start()
