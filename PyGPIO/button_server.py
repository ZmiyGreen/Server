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
    def __init__(self, port: int, client_ip: str, off_button, message_button, size: int = 1024):
        self.client_ip = client_ip
        self.size = size
        self.ip = get_ip()
        self.port = port
        self.power_on = True
        self.off_button = gpio.Button(off_button, 'rising')
        self.message_button = gpio.Button(message_button, 'rising')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def work(self):
        self.server.bind((self.ip, self.port))
        data, client = self.server.recvfrom(self.size)
        print(f"{data} {client}")
        print("server waiting!")
        with self.message_button:
            while self.power_on:
                if self.message_button.click():
                    print('click!')
                    self.server.sendto(b'1', client)
        self.server.close()
        print("server off")

    def power_off(self):
        with self.off_button:
            if self.off_button.click():
                self.power_on = False
                self.server.sendto(b'0', (self.client_ip, self.port))
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
            self.off_button.close(off_value=False)
            self.message_button.close(off_value=False)
            self.server.close()


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-p', '--port', type=int)
    args.add_argument('-f', '--off', type=int)
    args.add_argument('-m', '--message', type=int)
    args.add_argument('-c', '--client', type=str)
    values = args.parse_args(sys.argv[1:])
    stream = Architect(values.port, values.client, values.off, values.message)
    stream.start()
