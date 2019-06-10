class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value if len(value) <= 15 else value[0:15]

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, value):
        if 18 <= value <= 100:
            self.__age = value
        else:
            raise ValueError("Недопустимое значение!")

    def __str__(self):
        return f"{self.name} {self.age}"

    def __repr__(self):
        return f"{self.name} {self.age}"


class Student(Person):
    def __init__(self, name, age, ball):
        super().__init__(name, age)
        self.ball = ball

    @property
    def ball(self):
        return self.__ball

    @ball.setter
    def ball(self, value):
        self.__ball = value if 0.0 <= value <= 5.0 else 0

    def __str__(self):
        return f"{super().__repr__()} {self.ball}"

    def __repr__(self):
        return f"{super().__repr__()} {self.ball}"