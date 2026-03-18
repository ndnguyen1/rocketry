#[nlevel_buses.py]   Get N level buses from Home Bus
# =====================================================================================================
'''This script returns a dictionary of N level buses from Home (starting) Bus.
The next level bus is found from its branch and transformer connections [and not its electrical length].

---------------------------------------------------------------------------------
How to use this file?
    Refer "test_me()" function.
'''

# ========================================================================================

def get_nlevel_buses(homebus, nlevels):
    """
    Python Syntax:
        lvl_busdict = get_nlevel_buses(savfile, homebus, nlevels)

    Arguments:
        homebus(integer) : Home (starting) bus number to start finding next buses
        nlevels(integer) : Number of levels of buses from Home Bus
    """
    import psspy
    psspy.psseinit()

    lvl_list = [n+1 for n in range(nlevels)]

    lvl_busdict = {}
    lvl_busdict[0] = [homebus]

    do_buslist = [homebus]
    done_busdict = {}

    for lvl in lvl_list:
        if not do_buslist: break
        tmp_busdict = {}

        # Search for branches and two winding transformers
        for ibus in do_buslist:
            ierr = psspy.inibrn(ibus, single=2)
            #print("0 inibrn: ierr={}, ibus={}".format(ierr, ibus))
            if ierr == 0:
                while True:
                    ierr,jbus,ickt = psspy.nxtbrn(ibus)
                    #print("1 nxtbrn: ierr={}, jbus={}".format(ierr, jbus))
                    if ierr: break
                    tmp_busdict[jbus] = 1

        # Search for three winding transformers
        for ibus in do_buslist:
            ierr = psspy.inibrn(ibus, single=2)
            if ierr == 0:
                while True:
                    ierr,jbus,kbus,ickt = psspy.nxtbrn3(ibus)
                    #print("2 nxtbrn3: ierr={}, jbus={}, kbus={}".format(ierr, jbus, kbus))
                    if ierr: break
                    tmp_busdict[jbus] = 1
                    if (kbus>0): tmp_busdict[kbus] = 1

        tmp_buslist = list(tmp_busdict.keys())
        tmp_buslist.sort()

        for ibus in do_buslist:
            done_busdict[ibus] = 1

        do_buslist = []
        for ibus in tmp_buslist:
            if ibus not in done_busdict:
                do_buslist.append(ibus)

        lvl_busdict[lvl] = do_buslist[:]

    # all done
    return lvl_busdict

# ========================================================================================
def test_me():
    import psse3502
    import psspy
    psspy.psseinit()
    savfile = "sample.sav"
    psspy.case(savfile)
    lvl_busdict = get_nlevel_buses(151, 3)
    #lvl_busdict = get_nlevel_buses(206, 10)
    #lvl_busdict = get_nlevel_buses(101, 10)
    print("N Level Buses")
    for lvl, buslist in lvl_busdict.items():
        print("Level={}, Buses={}".format(lvl, buslist))

# ========================================================================================

if __name__=="__main__":
    pass
