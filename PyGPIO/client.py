import socket
import argparse
import sys


class Client:
    def __init__(self, ip: int, port: int, size: int = 1024):
        self.size = size
        self.ip = ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        with self.client as c:
            while True:
                while True:
                    try:
                        message = input("Number: ")
                        if -1 <= int(message) <= 100:
                            break
                        else:
                            print("Invalid value!")
                    except ValueError:
                        print("Invalid value!")
                c.sendto(message.encode('utf-8'), (self.ip, self.port))
                if int(c.recv(self.size).decode("utf-8")) == -1:
                    break


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-p', '--port', type=int)
    args.add_argument('-i', '--ip', type=str)
    values = args.parse_args(sys.argv[1:])
    orange = Client(values.ip, values.port)
    orange.start()
