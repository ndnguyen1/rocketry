'run_idle.py - This script starts up the IDLE interpreter (for Python 2.3).'

import sys

# Import IDLE's PyShell and run its main()
sys.argv=['','-n','-t','PSS/E-Python Shell'] #Arguments for IDLE
import idlelib.PyShell                       #Import the PyShell module
idlelib.PyShell.main()                       #Start IDLE

