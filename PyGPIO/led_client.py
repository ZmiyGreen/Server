import socket
import argparse
import sys
import pygpiolib as gpio


class Client:
    def __init__(self, ip: int, port: int, led: int, size: int = 1024):
        self.led = gpio.Led(led)
        self.size = size
        self.ip = ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.client.sendto(b'9', (self.ip, self.port))
        while True:
            try:
                with self.led:
                    data = int(self.client.recv(self.size))
                    print(data)
                    if data == 1:
                        self.led.switch()
                    elif data == 0:
                        break
                    else:
                        raise ValueError("Invalid data from server!")
            except:
                self.client.close()
                self.led.close(off_value=True)
        self.client.close()


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-l', '--led', type=int)
    args.add_argument('-p', '--port', type=int)
    args.add_argument('-i', '--ip', type=str)
    values = args.parse_args(sys.argv[1:])
    orange = Client(values.ip, values.port, values.led)
    orange.start()
