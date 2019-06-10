import pygpiolib as gpio
import time
import threading
import sys
import argparse


class LegButtonThread:
    """
    Класс инкапсулирующий запуск светодиода и управляющей интенсивностью его горения кнопки в разных потоках
    """
    def __init__(self, gpio_led: int, gpio_button: int, edge: str = 'rising', counter: float = 0.5, step: float = .025):
        """
        :param gpio_led: SYSFSID/GPIO линия соответствующие светодиоду
        :param gpio_button: SYSFSID/GPIO линия соответствующие кнопке
        :param edge: состояние edge -- rising, both и т.д.
        :param counter: стартовая интенсивность горения светодиода.
        :param step: шаг, на который уменьшится (ускорится) интенсивность горения светодиода после нажатия на кнопку
        """
        self.counter = counter
        self.step = step
        self.lock = threading.Lock()
        self.button = gpio.Button(gpio_button, edge)
        self.led = gpio.Led(gpio_led)

    def update(self):
        """Обработка нажатия на кнопку"""
        with self.button:
            while self.counter > self.step:
                if self.button.click():
                    with self.lock:
                        self.counter -= self.step

    def blink(self):
        """Изменение атрибута step после нажатия на кнопку и соответственно иетенсивности горения светодиода"""
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
            # Обработка Ctrl+C
            self.button.close()
            self.led.close(True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # -l аргумент соответствующий SYSFSID светодиода
    parser.add_argument('-l', '--led', type=int)
    # -b аргумент соответствующий SYSFSID кнопки
    parser.add_argument('-b', '--button', type=int)
    # -c аргумент соответствующий стартовой интенсивности горения светодиода
    parser.add_argument('-c', '--counter', type=float, default=0.5)
    #  -s агрумент соответствующий шагу, на который уменьшится (ускорится) интенсивность горения светодиода после
    #  нажатия на кнопку
    parser.add_argument('-s', '--step', type=float, default=0.025)
    arg = parser.parse_args(sys.argv[1:])
    job = LegButtonThread(arg.led, arg.button, counter=arg.counter, step=arg.step)
    job.start()
