__author__ = "EIGSEP Team"
__version__ = "0.0.1"

from .encoder import Encoder, Potentiometer
from .motor import Motor, QwiicMotor, PoluluMotor
#try: 
#    from .motor import PoluluMotor
#except:
#    pass
from .limit_switch_hit import reverse_limit

