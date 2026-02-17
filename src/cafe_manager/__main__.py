import os
import argparse
from .storage import *
from .entities import CoffeeMachine

def __main__():
    c = CoffeeMachine("delonghi")
    print(c.make_coffee("capuchino"))
    
if __name__ == "__main__":
    __main__()