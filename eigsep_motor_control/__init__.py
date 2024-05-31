__author__ = "EIGSEP Team"
__version__ = "0.0.1"

from .limit_switch_hit import reverse_limit

try:
    from .motor import PololuMotor, QwiicMotor
except ImportError:
    pass
from .motor import DummyMotor
from .potentiometer import Potentiometer, DummyPotentiometer
