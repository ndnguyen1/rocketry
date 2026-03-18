"""Example RAS Definitions for savnw.sav

I. To test this file:

  1. Copy the following files into you study directory:
     -savnw.sav
     -savnw.sub
     -savnw.mon
     -savnw.con
     -this file (ras.py)
     -pssuserpf.py (The one in this directory)

  2. Run ACCC with the savnw case and the savnw sub/mon/con files

  3. view the log file raslog.txt for RAS results

# ===== Minimal contents of pssuserpf.py for RAS functionality ================

import pssras
import ras  # this should be the name of your ras definition module

def pre_ca_solution(conlabel):
    pre_ca_solution(conlabel)

def post_ca_soln_eval(conlabel, solved):
    return post_ca_soln_eval(conlabel, solved)

def post_ca_soln_adj(conlabel, solved):
    post_ca_soln_adj(conlabel, solved)


# ============= End of contents of pssuserpf.py ==================


"""
# import all functions from the psse ras api module:
from pssras import *

# -----------------------------------------------------------------------------
#                         RAS Settings
# -----------------------------------------------------------------------------

# set the maximum number of ras interations to perform during each contingency:
set_max_ras_iterations(20)

# enable logging to the specified log file:
enable_ras_logging("raslog.txt")

# enable reporting to the specified CSV report file:
enable_ras_csv_report("rasreport.csv")

# enable reporting to PSSE report stream:
enable_ras_psse_report()

# -----------------------------------------------------------------------------
#                         RAS Definition Examples
# -----------------------------------------------------------------------------


# Example 1: Trip line on line loading
# =============================================================================


def condition():
    """Check if 3004-152 C1 is loaded > 300 MVA"""
    return branch_mva(3004, 152, "1") > 300


def action():
    """Open line 3004-152 C1"""
    open_branch(3004, 152, "1")


define_ras("TRIP-UNDER-LOAD", condition, action)


# Example 2: Unit Trip on Interface flow and branch Status
# =============================================================================


def condition():
    """lines are heavily loaded or out-of-service"""
    a = branch_mva(151, 152, 1) + branch_mva(151, 152, 2) > 800.0
    b = branch_is_open(151, 152, 1)
    c = branch_is_open(151, 152, 2)
    return a or b or c


def action():
    """Trip unit"""
    trip_unit(102, 1)


define_ras("UNIT-TRIP", condition, action)


# Example 3: line tripping RAS with a complex condition:
# =============================================================================


def condition():
    """Check if 151-152 lines open, 152-3004 is open or 151 is low voltage"""
    a = branch_is_open(151, 152, 1)
    b = branch_is_open(151, 152, 2)
    c = branch_is_open(152, 3004, 1)
    d = bus_voltage(151) < 0.96
    return (a and b) or c or d


def action():
    """Open line 152-202"""
    open_branch(152, 202, 1)


define_ras("COMPLEX", condition, action)

