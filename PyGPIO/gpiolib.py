import select
import os
from abc import ABC


class Device(ABC):
    """
    Базовый класс для работы с GPIO
    """
    def __init__(self, gpio_line: int, direction: str = 'in', edge: str = None):
        self.gpio_line = gpio_line
        self.path = f"/sys/class/gpio/gpio{gpio_line}/"
        self.edge = edge
        self.direction = direction
        self.__value = 0

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, var):
        if var in ['in', 'out']:
            self.__direction = var
        else:
            raise ValueError("Invalid direction!")

    @property
    def edge(self):
        return self.__edge

    @edge.setter
    def edge(self, var):
        if var in ['both', 'falling', 'rising', 'none', None]:
            self.__edge = var
        else:
            raise ValueError("Invalid edge!")

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, var):
        if var in [0, 1]:
            self.__value = var
            self.gpio_write("value", self.value)
        else:
            raise ValueError("Invalid value!")

    def write(self, file):
        with open(f"/sys/class/gpio/{file}", "w") as wr:
            wr.write(str(self.gpio_line))

    def gpio_write(self, file, value):
        with open(f"self.path{file}", "w") as wr:
            wr.write(str(value))

    def open(self):
        gpio_open(self.gpio_line, self.direction, self.edge)

    def close(self):
        gpio_try_close(self.gpio_line)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line}"

    def __str__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line}"


class Led(Device):
    """
    Класс для управления подключенными по gpio светодиодами
    """
    def __init__(self, gpio_line: int, direction: str = 'out', edge: str = None):
        super().__init__(gpio_line, direction, edge)

    def switch(self):
        """
        Переключает состояние светодиода на противоположное -- если включен - выключит, если выключен - включит
        """
        self.value = 1 if self.value == 0 else 0

    def close(self):
        gpio_try_close(self.gpio_line, True)

    def __repr__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line} value : {self.value}"

    def __str__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line} value : {self.value}"


class Button(Device):
    """
    Класс для управления подключенными по gpio кнопками
    """
    def __init__(self, gpio_line: int, direction: str = 'in', edge: str = 'rising'):
        super().__init__(gpio_line, direction, edge)

    def click(self) -> bool:
        """
        Пассивное ожидание нажатия кнопки
        :return: Возвращает True если кнопка нажата
        Примечание: в следующей версии будет добавлен возврат False, в случае если кнопка не нажата в течении
        определенного промежутка времени
        """
        with open(f'{self.path}value', 'r') as reader:
            reader.read()
            with select.epoll() as event:
                event.register(reader.fileno(), select.EPOLLPRI)
                event.poll()
                return True

    def __enter__(self):
        self.open()
        return self

    def __str__(self):
        return f"Button GPIO/SYSFSID : {self.gpio_line}"
