

import pssras
import psspy

# ============================ EDIT HERE ======================================

# import your RAS definitions. The module does not have to be named ras:
import ras

#==============================================================================


def pre_ca_solution(conlabel):
    """This function is called before a contingency is applied in ACCC"""
    pssras.pre_ca_solution(conlabel)


def post_ca_soln_eval(conlabel, solved):
    """This function is called during the contingency solution after a
    contingency has been applied, and the post-contingency solution has been
    completed. This function is a hook wherein any post-contingency conditions
    should be checked. Return True if the adjustments need to be applied
    and the case re-solved. Return False otherwise.
    conlabel: The contingency label of the contingency that has been applied
    """

    # call the pssras function that checks all of the user defined conditions:
    solved = pssras.post_ca_soln_eval(conlabel, solved)

    # return the flag from the condition check. False means we need to
    # re-solve:
    return solved


def post_ca_soln_adj(conlabel, solved):
    """This function is called after conditions have been checked in the
    post_ca_soln_eval function. If the return from that function call was
    False, then system adjustments may be required and the system needs to be
    resolved. This is an interative process for each contingency that will
    terminate after the post_ca_soln_eval function call returns True (the
    'all clear' flag), or the maximum number of ca adjustment interations
    has been reached.
    conlabel: The contingency label of the contingency that has been applied
    """

    # call the ras perform_actions function to implement the triggered actions:
    pssras.post_ca_soln_adj(conlabel, solved)


# you may want to write a message to PSSE in order to announce that this file
# was loaded and therefore RAS definitions are enabled:

psspy.report("RAS functionality enabled.\n\n")
psspy.report(pssras.ras_summaries())

