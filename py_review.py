# NOTE: I need to get my editor set back up for ipynb editing - I've used them before though


# TASK 1: Variables and IO
#
# In this task, define:
#
#     A integer variable called foo, with your choice of value
#     A floating point variable called bar, with your choice of value
#     A string variable called myname, containing your name
#
# Using the print() function, print the names, values, and types of each of the variables. You can use either f-strings or string concatenation for the printing.
#
# Sample output:
#
# The value of foo is 3 and its type is <class 'int'>
#
# The value of bar is 3.14 and its type is <class 'float'>

# The value of myname is Colin and its type is <class 'str'>
#
# Code goes here
from math import floor, sqrt
from typing import Any

foo: int = 319
bar: float = 850027714969600
myname: str = "Isaac"


def var_show(x: Any):  # pyright: ignore[reportAny, reportExplicitAny]
    print(
        f"The value of {[n for n, v in list(globals().items()) if v == x][0]} is {x} and its type is {type(x)}"
    )


var_show(foo)
var_show(bar)
var_show(myname)


# TASK 2: Control Structures
#
# Jupyter notebooks are a different way to structure a Python project. Instead of the entire file running, notebooks allow you to run specific cells. You can go back and re-run any cell in any order, but need to be careful to ensure variables have been defined before being used. For example, if this cell had print(foo), but you had not already run the code cell above that defined foo, an error would occur.
#
# For this task:
#
#     Use a conditional to check whether the value of foo is smaller than the value of bar. If foo is smaller than bar, print a message to this effect. Otherwise, print a different message.
#     Use a loop to print the numbers 1 through 10, along with their squares.
#     Use another loop to print the numbers 1 through 10, along with their squares, except you should skip 7 and its square. (Hint: use the continue instruction. Look up what the difference is between continue and break.)
#
# Code goes here

if foo > bar:
    print("Foo bigger")
else:
    print("bar bigger")

[print(str(i) + " " + str(i**2)) for i in range(1, 11)]
[print(str(i) + " " + str(i**2)) for i in range(1, 11) if i != 7]


# TASK 3: Functions
#
# Write a function that accepts an integer. You may assume that the function will only ever get passed an integer 2 or larger, and so can ignore type checking. The function should, using a loop, determine if the integer given is prime. If so, it should return True. Otherwise, it should return False. (Hint: you can use the % operator to check the remainder upon division by various numbers. For primes, you need only check integers from 2 to the floor of the square root of the number.). Demonstrate that your function works correctly by passing it a few prime numbers and a few composite (non-prime) numbers.
#
# Sample output:
#
# Is the number 3 prime?: True
#


def isPrime(
    num: int,
) -> bool:
    if num % 2 == 1:
        return not any([num % x == 0 for x in range(2, floor(sqrt(num)) + 1)])
    return num == 2


def pr_print(x: int):
    print(f"The number {x} is {'prime' if isPrime(x) else 'not prime'}")


pr_print(3)
pr_print(5)
pr_print(12)
pr_print(17)
pr_print(21)


# TASK 4: Object-oriented Programming
#
# Define two objects, called Vertex and Triangle. A vertex will be a pair of coordinates, for its x and y coordinates. A triangle will be an object having three Vertex objects within it. The Triangle class should also have a property called Area, and a method to compute and return the area. To compute the area of a triangle given only its three vertices, you will need to write a Distance function that returns the distance between two vertices, then use Heron's formula: https://en.wikipedia.org/wiki/Heron%27s_formula


class Vertex:
    def __init__(self, xcoord: int, ycoord: int):
        self.x = xcoord
        self.y = ycoord


def Distance(v1: Vertex, v2: Vertex):
    x_dist = abs(v1.x - v2.x)
    y_dist = abs(v1.y - v2.y)

    return sqrt(x_dist**2 + y_dist**2)


class Triangle:
    def __init__(self, pt1: Vertex, pt2: Vertex, pt3: Vertex):
        self.v1 = pt1
        self.v2 = pt2
        self.v3 = pt3

    def area(self):
        a = Distance(self.v1, self.v2)
        b = Distance(self.v1, self.v3)
        c = Distance(self.v2, self.v3)
        s = (a + b + c) / 2
        return sqrt(s * (s - a) * (s - b) * (s - c))
