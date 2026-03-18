# [preparer_transfomers_iec_data.py] 04/08/2009 Preparer Two and Three Winding Transformers IEC Data
# ==================================================================================================
'''
In some PSSE Saved Cases, especially some old sav files, all transformer data is provided on
System MVA base (SBASE). When this network data is to be used to calculate fault currents
according to "IEC 60909" standard, in order to calculate correct IEC impedance correction factors,
nameplate transformer winding MVA data is required.

This file is used to:
(1) Change working case to update transformers winding MVA derived from RATE A or B or C, and
    when winding MVA is 100 MVA and impedance data I/O code (CZ) is System MVA Base.
    Refer function: change_winding_mva(rating='')
    In some Saved case files, nameplate winding MVA data is stored as one of the ratings (RATE A, B, C),
    then this files can be used to change transformer winding MVA with selected Rating. 

(2) Create transformers IEC data file.
    Refer function: create_iecdata(wdgmva='',rptfile='')
    Create a text file with all transformer branches and then use this file to provide
    nameplate transformer winding MVA as part of transformer nameplate IEC data records.
    
---------------------------------------------------------------------------------
Functions:

(1) change_winding_mva(rating='')
    Change all Transformers Winding MVA to a MVA value derived from RATE A or B or C.

(2) create_iecdata(wdgmva='',rptfile='')
    Create IEC data file for all Transformers Winding MVA.
    Each IEC data record for a transformer has following format.
    IBUS, JBUS, KBUS, CKT, SBASE1-2, SBASE2-3, SBASE3-1

    Transformers IEC data records created here need to put in complete IEC data file.
        Refer POM Volume 1, API IECS for format of IEC data file.
        
    This function creates output file depending on the wndmva input provided.
    (1) If wndmva is not provided, it creates records in the following format.
    IBUS, JBUS, KBUS, CKT
    Then users would modify this file and manually input SBASE1-2, SBASE2-3, SBASE3-1 values.

    (2) If wndmva="SBASE", it creates records in the following format.
    IBUS, JBUS, KBUS, CKT, SBASE1-2, SBASE2-3, SBASE3-1
    Then users would modify this file and manually update SBASE1-2, SBASE2-3, SBASE3-1 values.

    (3) If wndmva="RATEA" or "RATEB" or "RATEC", it creates records in the following format.
    IBUS, JBUS, KBUS, CKT, SBASE1-2, SBASE2-3, SBASE3-1
    where SBASE1-2 = min(Winding 1 Selected Rating, Winding 2 Selected Rating)
          SBASE2-3 = min(Winding 2 Selected Rating, Winding 3 Selected Rating)
          SBASE3-1 = min(Winding 3 Selected Rating, Winding 1 Selected Rating)
          If any of the winding MVA is zero, it is ignored.
    Users could modify this file and manually update SBASE1-2, SBASE2-3, SBASE3-1 values.

---------------------------------------------------------------------------------
How to use this file?

(1) Open the Saved Case using PSS(R)E GUI

(2) Without PROMPT for inputing arguments:
    Call follwoing functions from CLI or another Python automation file:
    change_winding_mva(rating)
    or
    create_iecdata(wndmva, rptfile)

(3) With PROMPTS for inputing arguments:
    Call follwoing functions from CLI or another Python automation file:
    dochng()
    or
    docreate()
'''

import psspy, os


# ===========================================================================================

def _splitstring_commaspace(tmpstr):
    '''Split string first at comma and then by space. Example:
    Input  tmpstr = a1       a2,  ,a4 a5 ,,,a8,a9
    Output strlst = ['a1', 'a2', ' ', 'a4', 'a5', ' ', ' ', 'a8', 'a9']
    '''
    strlst = []
    commalst = tmpstr.split(',')
    for each in commalst:
        eachlst = each.split()
        if eachlst:
            strlst.extend(eachlst)
        else:
            strlst.extend(' ')

    return strlst

# ===========================================================================================

def _check_wdgmva(instr):
    '''check for valid wdgmva string.'''

    if type(instr) != str: instr = str(instr)
    instr0 = instr
    
    instr = instr.strip().lower()
    if not instr:
        retv = ''
    elif instr =='ratea':
        retv = "RATEA"
    elif instr =='rateb':
        retv = "RATEB"
    elif instr =='ratec':
        retv = "RATEC"
    elif instr =='sbase':
        retv = "SBASE"
    else:
        print(' Input value "%s" not recognized.\n' % str(instr0))
        retv = ''

    return retv

# ===========================================================================================

def _min_rate(r1,r2):
    if not r1:
        retv = r2
    elif not r2:
        retv = r1
    else:
        retv = min(r1,r2)

    return retv

# ===========================================================================================

def _get_xmer_data(wdgmva=''):

    '''
    wdgmva = 0 or ''    # return just transfomrer buses and ckt id
           = 'sbase'    # return transfomrer buses, ckt id with winding MVA as SBASE
           
           = 'ratea'    # return transfomrer buses, ckt id with winding MVA derived from
           = 'rateb'    # winding rating A or B or C
           = 'ratec'    # Example: sbase1-2 = min(winding 1 Rate A, winding 2 Rate A)
    '''
    
    sid   = -1       # all buses
    owner = 1        # ignored
    ties  = 1        # ignored

    # Get Two Winding Transformer Specified Rating
    flag  = 2        # =1 in-service transformers, =2 all
    entry = 1        # each branch once only

    ierr, tmplist1 = psspy.atrnint (sid, owner, ties, flag, entry, string=['FROMNUMBER','TONUMBER'])
    ierr, tmplist2 = psspy.atrnchar(sid, owner, ties, flag, entry, string=['ID'])
    if wdgmva:
        if wdgmva == "SBASE":
            strval = "SBASE1"
        else:
            strval = wdgmva
        ierr, tmplist3 = psspy.atrnreal(sid, owner, ties, flag, entry, string=[strval])

    two_wdg_xmers = {}
    for i in range(len(tmplist1[0])):
        busi  = tmplist1[0][i]
        busj  = tmplist1[1][i]
        cktid = tmplist2[0][i]
        if wdgmva:
            val = tmplist3[0][i]
        else:
            val = ''
        two_wdg_xmers[(busi,busj,cktid)] = {'sbase12':val}

    # Three Winding Transformer Specified Rating
    flag  = 3        # =2 all windings of in-service transformers
                     # =3 all transformers
    entry = 2        # transformer name order, don't make this 1, following assignments (ratea_w1 etc.)
                     # need to be done differently when entry = 1

    ierr, tmplist1 = psspy.awndint (sid, owner, ties, flag, entry, string=['WIND1NUMBER','WIND2NUMBER','WIND3NUMBER'])
    ierr, tmplist2 = psspy.awndchar(sid, owner, ties, flag, entry, string=['ID'])
    if wdgmva:
        ierr, tmplist3 = psspy.awndreal(sid, owner, ties, flag, entry, string=[wdgmva])

    three_wdg_xmers = {}
    nwdgs = len(tmplist1[0])
    for i in range(0,nwdgs,3):
        busi     = tmplist1[0][i]
        busj     = tmplist1[1][i]
        busk     = tmplist1[2][i]
        cktid    = tmplist2[0][i]
        if wdgmva == 'SBASE':
            val1 = tmplist3[0][i]
            val2 = tmplist3[0][i+1]
            val3 = tmplist3[0][i+2]
        elif wdgmva in ['RATEA', 'RATEB', 'RATEC']:
            ratea_w1 = tmplist3[0][i]
            ratea_w2 = tmplist3[0][i+1]
            ratea_w3 = tmplist3[0][i+2]
            val1 = _min_rate(ratea_w1,ratea_w2)
            val2 = _min_rate(ratea_w2,ratea_w3)
            val3 = _min_rate(ratea_w3,ratea_w1)
        else:
            val1 = ''
            val2 = ''
            val3 = ''
            
        three_wdg_xmers[(busi,busj,busk,cktid)] = {'sbase12':val1, 'sbase23':val2, 'sbase31':val3}
   
    return two_wdg_xmers, three_wdg_xmers

# ===========================================================================================

def change_winding_mva(rating=''):
    '''Change all Transformers Winding MVA to a MVA value derived from RATE A or B or C.'''

    wdgmva = _check_wdgmva(rating)
    
    if wdgmva not in ['RATEA', 'RATEB', 'RATEC']:
        print(" No need to update working case.")
        return
    
    two_wdg_xmers, three_wdg_xmers = _get_xmer_data(wdgmva)

    lst2wdg = list(two_wdg_xmers.keys())
    lst2wdg.sort()

    lst3wdg = list(three_wdg_xmers.keys())
    lst3wdg.sort()

    for brn in lst2wdg:
        ibus = brn[0]
        jbus = brn[1]
        ckt  = brn[2]
        sbase12 = two_wdg_xmers[brn]['sbase12']
        ierr,realaro = psspy.two_winding_data(ibus, jbus, ckt, realari3=sbase12)

    for brn in lst3wdg:
        ibus = brn[0]
        jbus = brn[1]
        kbus = brn[2]    
        ckt  = brn[3]
        sbase12 = three_wdg_xmers[brn]['sbase12']
        sbase23 = three_wdg_xmers[brn]['sbase23']
        sbase31 = three_wdg_xmers[brn]['sbase31']    
        ierr,realaro = psspy.three_wnd_impedance_data(ibus, jbus, kbus, ckt, realari7=sbase12,
                                                      realari8=sbase23, realari9=sbase31)
    
# ===========================================================================================

def create_iecdata(wdgmva='',rptfile=''):
    '''Create IEC data file for all Transformers Winding MVA.'''

    wdgmva = _check_wdgmva(wdgmva)

    two_wdg_xmers, three_wdg_xmers = _get_xmer_data(wdgmva)

    if rptfile:     # open report file to write
        p,nx = os.path.split(rptfile)
        if not p: p = os.getcwd()
        n,x = os.path.splitext(nx)
        if not x or x.lower() != '.txt': x = '.txt'
        nx = n + x
        rptfile = os.path.join(p,nx)
        rptfile_h = open(rptfile,'w')
        report       = rptfile_h.write
    else:           # send results to PSS(R)E report window
        psspy.beginreport()
        report = psspy.report

    # printing
    report('/  BUS I   BUS J   BUS K  CKT  SBASE1-2  SBASE2-3  SBASE3-1\n')

    # Two Winding Transformers
    lst2wdg = list(two_wdg_xmers.keys())
    lst2wdg.sort()
    for brn in lst2wdg:
        ibus = brn[0]
        jbus = brn[1]
        kbus = 0
        ckt  = brn[2].strip()
        sbase12 = two_wdg_xmers[brn]['sbase12']
        if sbase12:
            sbase12 = "%8.2f" % sbase12
        else:
            sbase12 = ''
        report('%(ibus)8d  %(jbus)6d  %(kbus)6d  %(ckt)3s  %(sbase12)s\n' % vars())

    # Three Winding Transformers
    lst3wdg = list(three_wdg_xmers.keys())
    lst3wdg.sort()

    for brn in lst3wdg:
        ibus = brn[0]
        jbus = brn[1]
        kbus = brn[2]    
        ckt  = brn[3].strip()
        sbase12  = three_wdg_xmers[brn]['sbase12']
        sbase23  = three_wdg_xmers[brn]['sbase23']
        sbase31  = three_wdg_xmers[brn]['sbase31']    
        if sbase12:
            sbase12 = "%8.2f" % sbase12
            sbase23 = "%8.2f" % sbase23
            sbase31 = "%8.2f" % sbase31
        else:
            sbase12 = ''
            sbase23 = ''
            sbase31 = ''

        report('%(ibus)8d  %(jbus)6d  %(kbus)6d  %(ckt)3s  %(sbase12)s  %(sbase23)s  %(sbase31)s\n' % vars())

    if rptfile:
        print(" Transformers IEC Data records saved in file %s." % rptfile)

# ====================================================================================================

def dochng():
    psspy.prompt("PROVIDE RATING TO SELECT:\n\n\
        - TYPE ratea for RATE A or\n\
        - TYPE rateb for RATE B or\n\
        - TYPE ratec for RATE C")
    
    ierr, rating = psspy.userin()

    change_winding_mva(rating)
    
# ====================================================================================================

def docreate():
    psspy.prompt("PROVIDE WINDING MVA selection string and IEC DATA output text file name:\n\n\
        - ALLOWED WINDING MVA selection string\n\
             sbase, ratea, rateb, ratec or ''(empty string) \n")
    psspy.prompt("        - OPTIONAL OUTPUT text file name (when not provided, output created in PSS(R)E report window)\n")
    psspy.prompt("TYPE inputs separated either by comma or space.")
    
    ierr, instr = psspy.userin()
    wndmva  = ''
    rptfile = ''

    if instr:
        instrlst = _splitstring_commaspace(instr)
        wndmva = instrlst[0]
        try:
            rptfile = instrlst[1]
        except:
            pass

    create_iecdata(wndmva, rptfile)
    
# ====================================================================================================

if __name__ == '__main__':
    #dochng()
    docreate()

# ====================================================================================================
   

