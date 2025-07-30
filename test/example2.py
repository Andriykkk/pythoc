from typing import Annotated
from typing import List, Union

def greet(name: List[Annotated[float, "float", "str"]]) -> None:
    message = f"Hello, {name}!"
    print(message)
    return message

class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        return greet(self.name)

if __name__ == "__main__":
    person = Person("Alice")
    person.say_hello()
