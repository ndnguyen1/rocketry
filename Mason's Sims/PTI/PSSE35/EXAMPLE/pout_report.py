#[pout_report.py]  POWER FLOW RESULTS REPORT
# ====================================================================================================
'''
This is an example file showing how to use "subsystem data retrieval APIs (API Manual, Chapter 8")
from Python to generate power flow results report.
    Input : Solved PSS(R)E saved case file name
    Output: Report file name to save
    When 'savfile' is provided, FNSL with default options is used to solve the case.
    When 'savfile' is not provided, it uses solved Case from PSS(R)E memory.
    When 'rptfile' is provided, report is saved in ASCII text file 'rptfile'.
    When 'rptfile' is not provided, it produces report in PSS(R)E report window.

The subsystem data retrieval APIs return values as List of Lists. For example:
When "abusint" API is called with "istrings" as defined below:
    istrings = ['number','type','area','zone','owner','dummy']
    ierr, idata = psspy.abusint(sid, flag_bus, istrings)
The returned list will have format:
    idata=[[list of 'number'],[list of 'type'],[],[],[],[list of 'dummy']]

This example is written such that, such returned lists are converted into dictionary with
keys as strings specified in "istrings". This makes it easier to refer and use these lists.
    ibuses = array2dict(istrings, idata)

So ibuses['number'] gives the bus numbers returned by "abusint".

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call funtion
    pout_report(savfile, outpath)
    or
    pout_report()  <-- savnw.sav and savnw.dfx must exist in working folder.

'''
# ----------------------------------------------------------------------------------------------------
import sys, os

# ----------------------------------------------------------------------------------------------------
def array2dict(dict_keys, dict_values):
    '''Convert array to dictionary of arrays.
    Returns dictionary as {dict_keys:dict_values}
    '''
    tmpdict = {}
    for i in range(len(dict_keys)):
        tmpdict[dict_keys[i].lower()] = dict_values[i]
    return tmpdict

# ----------------------------------------------------------------------------------------------------
def busindexes(busnum, busnumlist):
    '''Find indexes of a bus in list of buses.
    Returns list with indexes of 'busnum' in 'busnumlist'.
    '''
    busidxes = []
    startidx = 0
    buscounts = busnumlist.count(busnum)
    if buscounts:
        for i in range(buscounts):
            tmpidx = busnumlist.index(busnum,startidx)
            busidxes.append(tmpidx)
            startidx = tmpidx+1
    return busidxes

# ----------------------------------------------------------------------------------------------------
def splitstring_commaspace(tmpstr):
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

# -----------------------------------------------------------------------------------------------------

def get_output_dir(outpath):
    # if called from PSSE's Example Folder, create report in subfolder 'Output_Pyscript'

    if outpath:
        outdir = outpath
        if not os.path.exists(outdir): os.mkdir(outdir)
    else:
        outdir = os.getcwd()
        cwd = outdir.lower()
        i = cwd.find('pti')
        j = cwd.find('psse')
        k = cwd.find('example')
        if i>0 and j>i and k>j:     # called from Example folder
            outdir = os.path.join(outdir, 'Output_Pyscript')
            if not os.path.exists(outdir): os.mkdir(outdir)

    return outdir

# -----------------------------------------------------------------------------------------------------

def get_output_filename(outpath, fnam):

    p, nx = os.path.split(fnam)
    if p:
        retvfile = fnam
    else:
        outdir = get_output_dir(outpath)
        retvfile = os.path.join(outdir, fnam)

    return retvfile

# ----------------------------------------------------------------------------------------------------
def pout_report(savfile='savnw.sav', outpath=None):
    '''Generates power flow result report.
    When 'savfile' is provided, FNSL with default options is used to solve the case.
    When 'savfile' is not provided, it uses solved Case from PSS(R)E memory.
    When 'rptfile' is provided, report is saved in ASCII text file 'rptfile'.
    When 'rptfile' is not provided, it produces report in PSS(R)E report window.
    '''

    import psspy

    psspy.psseinit()

    # Set Save and Report files according to input file names
    if savfile:
        ierr = psspy.case(savfile)
        if ierr != 0: return
        fpath, fext = os.path.splitext(savfile)
        if not fext: savfile = fpath + '.sav'
        #ierr = psspy.fnsl([0,0,0,1,1,0,0,0])
        #if ierr != 0: return
    else:   # saved case file not provided, check if working case is in memory
        ierr, nbuses = psspy.abuscount(-1,2)
        if ierr == 0:
            savfile, snapfile = psspy.sfiles()
        else:
            print('\n No working case in memory.')
            print(' Either provide a Saved case file name or open Saved case in PSS(R)E.')
            return

    p, nx = os.path.split(savfile)
    n, x  = os.path.splitext(nx)
    rptfile = get_output_filename(outpath, 'pout_'+n+'.txt')

    rptfile_h = open(rptfile,'w')
    report    = rptfile_h.write

    # ================================================================================================
    # PART 1: Get the required results data
    # ================================================================================================

    # Select what to report
    if psspy.bsysisdef(0):
        sid = 0
    else:   # Select subsytem with all buses
        sid = -1

    flag_bus     = 1    # in-service
    flag_plant   = 1    # in-service
    flag_load    = 1    # in-service
    flag_swsh    = 1    # in-service
    flag_brflow  = 1    # in-service
    owner_brflow = 1    # use bus ownership, ignored if sid is -ve
    ties_brflow  = 5    # ignored if sid is -ve

    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    # Case Title
    titleline1, titleline2 = psspy.titldt()

    # ------------------------------------------------------------------------------------------------
    # Bus Data
    # Bus Data - Integer
    istrings = ['number','type','area','zone','owner','dummy']
    ierr, idata = psspy.abusint(sid, flag_bus, istrings)
    if ierr:
        print('(1) psspy.abusint error = %d' % ierr)
        return
    ibuses = array2dict(istrings, idata)
    # Bus Data - Real
    rstrings = ['base','pu','kv','angle','angled','mismatch','o_mismatch']
    ierr, rdata = psspy.abusreal(sid, flag_bus, rstrings)
    if ierr:
        print('(1) psspy.abusreal error = %d' % ierr)
        return
    rbuses = array2dict(rstrings, rdata)
    # Bus Data - Complex
    xstrings = ['voltage','shuntact','o_shuntact','shuntnom','o_shuntnom','mismatch','o_mismatch']
    ierr, xdata = psspy.abuscplx(sid, flag_bus, xstrings)
    if ierr:
        print('(1) psspy.abuscplx error = %d' % ierr)
        return
    xbuses = array2dict(xstrings, xdata)
    # Bus Data - Character
    cstrings = ['name','exname']
    ierr, cdata = psspy.abuschar(sid, flag_bus, cstrings)
    if ierr:
        print('(1) psspy.abuschar error = %d' % ierr)
        return
    cbuses = array2dict(cstrings, cdata)

    # Store bus data for all buses
    ibusesall={};rbusesall={};xbusesall={};cbusesall={};
    if sid == -1:
        ibusesall=ibuses
        rbusesall=rbuses
        xbusesall=xbuses
        cbusesall=cbuses
    else:
        ierr, idata = psspy.abusint(-1, flag_bus, istrings)
        if ierr:
            print('(2) psspy.abusint error = %d' % ierr)
            return
        ibusesall = array2dict(istrings, idata)

        ierr, rdata = psspy.abusreal(-1, flag_bus, rstrings)
        if ierr:
            print('(2) psspy.abusreal error = %d' % ierr)
            return
        rbusesall = array2dict(rstrings, rdata)

        ierr, xdata = psspy.abuscplx(-1, flag_bus, xstrings)
        if ierr:
            print('(2) psspy.abuscplx error = %d' % ierr)
            return
        xbusesall = array2dict(xstrings, xdata)

        ierr, cdata = psspy.abuschar(-1, flag_bus, cstrings)
        if ierr:
            print('(2) psspy.abuschar error = %d' % ierr)
            return
        cbusesall = array2dict(cstrings, cdata)

    # ------------------------------------------------------------------------------------------------
    # Plant Bus Data
    # Plant Bus Data - Integer
    istrings = ['number','type','area','zone','owner','dummy', 'status','ireg']
    ierr, idata = psspy.agenbusint(sid, flag_plant, istrings)
    if ierr:
        print('psspy.agenbusint error = %d' % ierr)
        return
    iplants = array2dict(istrings, idata)
    # Plant Bus Data - Real
    rstrings = ['base','pu','kv','angle','angled','iregbase','iregpu','iregkv','vspu','vskv','rmpct',
                'pgen',  'qgen',  'mva', 'percent', 'pmax',  'pmin',  'qmax',  'qmin',  'mismatch',
                'o_pgen','o_qgen','o_mva','o_pmax','o_pmin','o_qmax','o_qmin','o_mismatch']
    ierr, rdata = psspy.agenbusreal(sid, flag_plant, rstrings)
    if ierr:
        print('psspy.agenbusreal error = %d' % ierr)
        return
    rplants = array2dict(rstrings, rdata)
    # Plant Bus Data - Complex
    xstrings = ['voltage','pqgen','mismatch','o_pqgen','o_mismatch']
    ierr, xdata = psspy.agenbuscplx(sid, flag_plant, xstrings)
    if ierr:
        print('psspy.agenbusreal error = %d' % ierr)
        return
    xplants = array2dict(xstrings, xdata)
    # Plant Bus Data - Character
    cstrings = ['name','exname','iregname','iregexname']
    ierr, cdata = psspy.agenbuschar(sid, flag_plant, cstrings)
    if ierr:
        print('psspy.agenbuschar error = %d' % ierr)
        return
    cplants = array2dict(cstrings, cdata)

    # ------------------------------------------------------------------------------------------------
    # Load Data - based on Individual Loads Zone/Area/Owner subsystem
    # Load Data - Integer
    istrings = ['number','area','zone','owner','status']
    ierr, idata = psspy.aloadint(sid, flag_load, istrings)
    if ierr:
        print('psspy.aloadint error = %d' % ierr)
        return
    iloads = array2dict(istrings, idata)
    # Load Data - Real
    rstrings = ['mvaact','mvanom','ilact','ilnom','ylact','ylnom','totalact','totalnom','o_mvaact',
                'o_mvanom','o_ilact','o_ilnom','o_ylact','o_ylnom','o_totalact','o_totalnom']
    ierr, rdata = psspy.aloadreal(sid, flag_load, rstrings)
    if ierr:
        print('psspy.aloadreal error = %d' % ierr)
        return
    rloads = array2dict(rstrings, rdata)
    # Load Data - Complex
    xstrings = rstrings
    ierr, xdata = psspy.aloadcplx(sid, flag_load, xstrings)
    if ierr:
        print('psspy.aloadcplx error = %d' % ierr)
        return
    xloads = array2dict(xstrings, xdata)
    # Load Data - Character
    cstrings = ['id','name','exname']
    ierr, cdata = psspy.aloadchar(sid, flag_load, cstrings)
    if ierr:
        print('psspy.aloadchar error = %d' % ierr)
        return
    cloads = array2dict(cstrings, cdata)

    # ------------------------------------------------------------------------------------------------
    # Total load on a bus
    totalmva={}; totalil={}; totalyl={}; totalys={}; totalysw={}; totalload={}; busmsm={}
    for b in ibuses['number']:
        ierr, ctmva = psspy.busdt2(b,'MVA','ACT')
        if ierr==0: totalmva[b]=ctmva

        ierr, ctil = psspy.busdt2(b,'IL','ACT')
        if ierr==0: totalil[b]=ctil

        ierr, ctyl = psspy.busdt2(b,'YL','ACT')
        if ierr==0: totalyl[b]=ctyl

        ierr, ctys = psspy.busdt2(b,'YS','ACT')
        if ierr==0: totalys[b]=ctys

        ierr, ctysw = psspy.busdt2(b,'YSW','ACT')
        if ierr==0: totalysw[b]=ctysw

        ierr, ctld = psspy.busdt2(b,'TOTAL','ACT')
        if ierr==0: totalload[b]=ctld

        #Bus mismstch
        ierr, msm = psspy.busmsm(b)
        if ierr != 1: busmsm[b]=msm

    # ------------------------------------------------------------------------------------------------
    # Switched Shunt Data
    # Switched Shunt Data - Integer
    istrings = ['number','type','area','zone','owner','dummy','mode','ireg','blocks',
                'stepsblock1','stepsblock2','stepsblock3','stepsblock4','stepsblock5',
                'stepsblock6','stepsblock7','stepsblock8']
    ierr, idata = psspy.aswshint(sid, flag_swsh, istrings)
    if ierr:
        print('psspy.aswshint error = %d' % ierr)
        return
    iswsh = array2dict(istrings, idata)
    # Switched Shunt Data - Real (Note: Maximum allowed NSTR are 50. So they are split into 2)
    rstrings = ['base','pu','kv','angle','angled','vswhi','vswlo','rmpct','bswnom','bswmax',
                'bswmin','bswact','bstpblock1','bstpblock2','bstpblock3','bstpblock4','bstpblock5',
                'bstpblock6','bstpblock7','bstpblock8','mismatch']
    rstrings1 = ['o_bswnom','o_bswmax','o_bswmin','o_bswact','o_bstpblock1',
                 'o_bstpblock2','o_bstpblock3','o_bstpblock4','o_bstpblock5','o_bstpblock6',
                 'o_bstpblock7','o_bstpblock8','o_mismatch']
    ierr, rdata = psspy.aswshreal(sid, flag_swsh, rstrings)
    if ierr:
        print('(1) psspy.aswshreal error = %d' % ierr)
        return
    rswsh = array2dict(rstrings, rdata)
    ierr, rdata1 = psspy.aswshreal(sid, flag_swsh, rstrings1)
    if ierr:
        print('(2) psspy.aswshreal error = %d' % ierr)
        return
    rswsh1 = array2dict(rstrings1, rdata1)
    for k, v in rswsh1.items():
        rswsh[k]=v
    # Switched Shunt Data - Complex
    xstrings = ['voltage','yswact','mismatch','o_yswact','o_mismatch']
    ierr, xdata = psspy.aswshcplx(sid, flag_swsh, xstrings)
    if ierr:
        print('psspy.aswshcplx error = %d' % ierr)
        return
    xswsh = array2dict(xstrings, xdata)
    # Switched Shunt Data - Character
    cstrings = ['vscname','name','exname','iregname','iregexname']
    ierr, cdata = psspy.aswshchar(sid, flag_swsh, cstrings)
    if ierr:
        print('psspy.aswshchar error = %d' % ierr)
        return
    cswsh = array2dict(cstrings, cdata)

    # ------------------------------------------------------------------------------------------------
    # Branch Flow Data
    # Branch Flow Data - Integer
    istrings = ['fromnumber','tonumber','status','nmeternumber','owners','own1','own2','own3','own4']
    ierr, idata = psspy.aflowint(sid, owner_brflow, ties_brflow, flag_brflow, istrings)
    if ierr:
        print('psspy.aflowint error = %d' % ierr)
        return
    iflow = array2dict(istrings, idata)
    # Branch Flow Data - Real
    rstrings = ['amps','pucur','pctrate','pctratea','pctrateb','pctratec','pctmvarate',
                'pctmvaratea','pctmvarateb',#'pctmvaratec','fract1','fract2','fract3',
                'fract4','rate','ratea','rateb','ratec',
                'p','q','mva','ploss','qloss',
                'o_p','o_q','o_mva','o_ploss','o_qloss'
                ]
    ierr, rdata = psspy.aflowreal(sid, owner_brflow, ties_brflow, flag_brflow, rstrings)
    if ierr:
        print('psspy.aflowreal error = %d' % ierr)
        return
    rflow = array2dict(rstrings, rdata)
    # Branch Flow Data - Complex
    xstrings = ['pq','pqloss','o_pq','o_pqloss']
    ierr, xdata = psspy.aflowcplx(sid, owner_brflow, ties_brflow, flag_brflow, xstrings)
    if ierr:
        print('psspy.aflowcplx error = %d' % ierr)
        return
    xflow = array2dict(xstrings, xdata)
    # Branch Flow Data - Character
    cstrings = ['id','fromname','fromexname','toname','toexname','nmetername','nmeterexname']
    ierr, cdata = psspy.aflowchar(sid, owner_brflow, ties_brflow, flag_brflow, cstrings)
    if ierr:
        print('psspy.aflowchar error = %d' % ierr)
        return
    cflow = array2dict(cstrings, cdata)

    # ================================================================================================
    # PART 2: Write acquired results to Report file
    # ================================================================================================

    # Case Title
    report("%(tx1)s %(tx2)s %(tx1)s\n" %{'tx1':41*'=','tx2':"POWER FLOW OUTPUT REPORT"})
    report("Case File: %s\n" %savfile)
    report("%s\n" %titleline1)
    report("%s\n" %titleline2)
    report("\n")

    # Column Headings
    head1 = "%(tx1)s\n" % {'tx1':108*'-'}
    head2 = "%(tx1)2s %(tx2)6s %(tx3)-18s %(tx4)-3s %(tx5)9s %(tx6)9s %(tx7)9s %(tx8)6s %(tx9)9s \
%(tx10)8s %(tx11)8s %(tx12)4s %(tx13)4s\n" % {'tx1':'','tx2':'BUS','tx3':'BUS NAME','tx4':'CKT',
'tx5':'MW','tx6':'MVAR','tx7':'MVA','tx8':'%I','tx9':'VOLTAGE','tx10':'MWLOSS','tx11':'MVARLOSS',
'tx12':'AREA','tx13':'ZONE'}
    heading = head1 + head2 + head1
    report(heading)
    for i, bus in enumerate(ibuses['number']):

        # select bus
        report("%(tx1)2s %(bnum)6d %(bname)18s %(tx1)40s %(pu)7.3FPU %(tx1)17s %(area)4s \
%(zone)4s\n" %
{'tx1':'','bnum':bus, 'bname':cbuses['exname'][i],'pu':rbuses['pu'][i],'area':ibuses['area'][i],
'zone':ibuses['zone'][i]})

        # check generation on selected bus
        plantbusidxes=busindexes(bus,iplants['number'])
        for idx in plantbusidxes:
            pcti = rplants['percent'][idx]
            if pcti == 0.0:
                pcti = ''
            else:
                pcti = str("%6.2F" % pcti)
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pgen)9.2F %(qgen)9.2F %(mva)9.2F %(pcti)6s \
%(kv)7.3FKV\n" %
{'tx1':'FROM','tx2':'GENERATION','tx3':'','pgen':rplants['pgen'][idx],'qgen':rplants['qgen'][idx],
'mva':rplants['mva'][idx],'pcti':pcti,'kv':rplants['kv'][idx]})

        # check total load on selected bus
        if bus in totalmva:
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                {'tx1':'TO','tx2':'LOAD-PQ','tx3':'','pload':totalmva[bus].real,
                 'qload':totalmva[bus].imag,'mvaload':abs(totalmva[bus])})
        if bus in totalil:
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                {'tx1':'TO','tx2':'LOAD-I','tx3':'','pload':totalil[bus].real,
                 'qload':totalil[bus].imag,'mvaload':abs(totalil[bus])})
        if bus in totalyl:
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                {'tx1':'TO','tx2':'LOAD-Y','tx3':'','pload':totalyl[bus].real,
                 'qload':totalyl[bus].imag,'mvaload':abs(totalyl[bus])})
        '''
        if bus in totalload:
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                {'tx1':'TO','tx2':'LOAD-TOTAL','tx3':'','pload':totalload[bus].real,
                 'qload':totalload[bus].imag,'mvaload':abs(totalload[bus])})
        '''
        if bus in totalys:
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                {'tx1':'TO','tx2':'SHUNT','tx3':'','pload':totalys[bus].real,
                 'qload':totalys[bus].imag,'mvaload':abs(totalys[bus])})
        if bus in totalysw:
            report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                {'tx1':'TO','tx2':'SWITCHED SHUNT','tx3':'','pload':totalysw[bus].real,
                 'qload':totalysw[bus].imag,'mvaload':abs(totalysw[bus])})

        """
        # Sometimes load/shunt/switch shunt area/owner/zone's could be different than the bus
        # to which it is connected. So when producing subsystem based reports, these equipment
        # might get excluded.

        # check loads on selected bus
        loadbusidxes=busindexes(bus,iloads['number'])
        pq_p = 0; pq_q = 0
        il_p = 0; il_q = 0
        yl_p = 0; yl_q = 0
        for idx in loadbusidxes:
            pq_p += xloads['mvaact'][idx].real
            pq_q += xloads['mvaact'][idx].imag
            il_p += xloads['ilact'][idx].real
            il_q += xloads['ilact'][idx].imag
            yl_p += xloads['ylact'][idx].real
            yl_q += xloads['ylact'][idx].imag

        pq_mva = abs(complex(pq_p,pq_q))
        il_mva = abs(complex(il_p,il_q))
        yl_mva = abs(complex(yl_p,yl_q))
        if pq_mva:  #PQ Loads
            report("%(tx1)-9s %(tx2)-18s %(ckt)-3s %(p)9.2F %(q)9.2F %(mva)9.2F\n" %
                        {'tx1':'TO','tx2':'LOAD-PQ','ckt':'','p':pq_p,'q':pq_q,'mva':pq_mva})
        if il_mva:   #I Loads
            report("%(tx1)-9s %(tx2)-18s %(ckt)-3s %(p)9.2F %(q)9.2F %(mva)9.2F\n" %
                        {'tx1':'TO','tx2':'LOAD-I','ckt':'','p':il_p,'q':il_q,'mva':il_mva})
        if yl_mva:   #Y Loads
            report("%(tx1)-9s %(tx2)-18s %(ckt)-3s %(p)9.2F %(q)9.2F %(mva)9.2F\n" %
                        {'tx1':'TO','tx2':'LOAD-Y','ckt':'','p':yl_p,'q':yl_q,'mva':yl_mva})

        # check shunts on selected bus
        if abs(xbuses['shuntact'][i]):
            report("%(tx1)-9s %(tx2)-18s %(tx3)-3s %(p)9.2F %(q)9.2F %(mva)9.2F\n" %
                    {'tx1':'TO','tx2':'SHUNT','tx3':'','p':xbuses['shuntact'][i].real,
                     'q':xbuses['shuntact'][i].imag,'mva':abs(xbuses['shuntact'][i])})

        # check switched shunts on selected bus
        swshbusidxes=busindexes(bus,iswsh['number'])
        pswsh = 0; qswsh = 0
        for idx in swshbusidxes:
            pswsh += xswsh['yswact'][idx].real
            qswsh += xswsh['yswact'][idx].imag
        mvaswsh = abs(complex(pswsh,qswsh))
        if mvaswsh:
            report("%(tx1)-9s %(tx2)-18s %(ckt)-3s %(p)9.2F %(q)9.2F %(mva)9.2F\n" %
               {'tx1':'TO','tx2':'SWITCHED SHUNT','ckt':'','p':pswsh,'q':qswsh,'mva':mvaswsh})
        """

        # check connected branches to selected bus
        flowfrombusidxes=busindexes(bus,iflow['fromnumber'])
        for idx in flowfrombusidxes:
            if iflow['tonumber'][idx]<10000000: #don't process 3-wdg xmer star-point buses
                tobusidx=busindexes(iflow['tonumber'][idx],ibusesall['number'])
                tobusVpu=rbusesall['pu'][tobusidx[0]]
                tobusarea=ibusesall['area'][tobusidx[0]]
                tobuszone=ibusesall['zone'][tobusidx[0]]
                pcti = rflow['pctrate'][idx]
                if pcti == 0.0:
                    pcti = ''
                else:
                    pcti = str("%6.2F" % pcti)
                report("%(tx1)-2s %(tonum)6d %(toexname)18s %(ckt)3s %(p)9.2F %(q)9.2F \
%(mva)9.2F %(pcti)6s %(pu)7.3FPU %(ploss)8.2F %(qloss)8.2F %(area)4d %(zone)4d \n" %
{'tx1':'TO', 'tonum':iflow['tonumber'][idx], 'toexname':cflow['toexname'][idx],
'ckt':cflow['id'][idx],'p':rflow['p'][idx],'q':rflow['q'][idx],
'mva':rflow['mva'][idx],'pcti':pcti,'pu':tobusVpu, 'ploss':rflow['ploss'][idx],
'qloss':rflow['qloss'][idx],'area':tobusarea,'zone':tobuszone})

        # Bus Mismatch
        if bus in busmsm:
            if abs(busmsm[bus]):
                report("%(tx1)-9s %(tx2)-18s %(tx3)3s %(pload)9.2F %(qload)9.2F %(mvaload)9.2F\n" %
                    {'tx1':'','tx2':'BUS MISMATCH','tx3':'','pload':busmsm[bus].real,
                     'qload':busmsm[bus].imag,'mvaload':abs(busmsm[bus])})


        report("%(tx1)s\n" % {'tx1':108*'-'})
        # int(round(rflow['pctrate'][idx]))
    # ------------------------------------------------------------------------------------------------
    rptfile_h.close()
    txt = '\n Power Flow Results Report (POUT) saved to file %s' % rptfile
    sys.stdout.write(txt)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':

    import psse35
    pout_report()
    #OR
    #pout_report(savfile)

# ====================================================================================================
