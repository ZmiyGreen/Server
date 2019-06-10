import pygpiolib as gpio
import time
import threading


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


def start(led, button, counter, step):
    job = LegButtonThread(led, button, counter=counter, step=step)
    job.start()


if __name__ == "__main__":
    try:
        first = LegButtonThread(110, 0)
        second = LegButtonThread(64, 1)
        first_stream = threading.Thread(target=first.start)
        second_stream = threading.Thread(target=second.start)
        first_stream.start()
        second_stream.start()
        first_stream.join()
        second_stream.join()
    except:
        first.button.close()
        first.led.close(off_value=True)
        second.button.close()
        second.led.close(off_value=True)

    first = threading.Thread(target=start, args=(110, 0, 0.5, 0.02))
    second = threading.Thread(target=start, args=(64, 1, 0.5, 0.02))
    first.start()
    second.start()
    first.join()
    second.join()
