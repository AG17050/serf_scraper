import os
import sys
# sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
from downloading import SerfFile, DLRelocator