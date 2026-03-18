#[iecs_demo.py]   Fault Calculations using IECS
# =====================================================================================================
'''There are three different ways to calculate faults using IECS.
1) Using activity IECS (psspy.iecs_4)
   Runs all types of faults, creates text reports, but no access to results from Python script.

2) Using Python module arrbox.iecs.iecs_currents
   Runs all types of faults, creates text reports and returns results in python object that can be
   accessed from Python script.
   The returned python object
       a) contain both phase and sequence fault currents.
       b) contain faults currents for bus faults only.
       c) does not contain faults currents for linout and linend faults.

3) Using Python module arrbox.fault.FAULT_SUMMARY
   Runs all types of faults, creates text reports and returns results in python object that can be
   accessed from Python script.
   The returned python object
       a) contain only total fault currents for faults calculated.
       b) contain faults currents for bus, linout and linend faults.

This is an example file showing how to run IECS fault calculations using either of these methods.

---------------------------------------------------------------------------------
How to use this file?

A) As showed in __main__ (end of this file), enable PSSE version specific environment, as an example:
    import psseXX
    [Here XX is PSSE major version number.]

B) This file contain following functions that uses IEC 60909 Test Network file run IECS calculations.
    run_iecs_4(..)
    run_iecs_currents_txtrpt(..)
    run_iecs_currents_xls(..)
    run_fault_summary_iecs(..)

    Run either of these functions under  __main__ to see how they work.

C) Create similar functions for the network case and faults you want to run.

'''
# ========================================================================================
#
"""
Use any of these keywords to run psspy.iecs or arrbox.iecs.iecs_currents or arrbox.fault.FAULT_SUMMARY.
Keyword   Default   Description
                    # STATUS array
flt3ph   = 0        # 1 0=>omit, 1=>include
fltlg    = 0        # 2 0=>omit, 1=>include
fltllg   = 0        # 3 0=>omit, 1=>include
fltll    = 0        # 4 0=>omit, 1=>include
rptop    = 1        # 5  -1=>no report, 0=>summary, 1=>total, 2=>contributions 3=>total+contributions
rptlvl   = 0        # 6  number of contribution levels
fltloc   = 0        # 7  0=>network, 1=>LV bus of power station unit,
                    #    2=>AUX.XMER (connected to power station unit) LV bus
linout   = 0        # 8  0=>omit, 1=>include
linend   = 0        # 9  0=>omit, 1=>include
tpunty   = 0        # 10 0=>N and phi unchanged, 1=>N=1 and phi=0, 2=>N=1 and phi unchanged,
                    #    3=>N unchanged and phi=0
lnchrg   = 1        # 11 0=>unchanged, 1=>0.0 in +/- sequences, 2=>0.0 in all sequences (line charging)
shntop   = 1        # 12 0=>unchanged, 1=>0.0 in +/- sequences,
                    #    2=>0.0 in all sequences (line, fixed, swicthed shunts, xmer magnetization)
dcload   = 0        # 13 0=>blocked, 1=>represent as load (dc line and FACTS option)
zcorec   = 0        # 14 0=>ignore, 1=>apply  (zero sequence transformer impedance correction option)
cfactor  = 0        # 15 0=>Maximum fault current, 1=>Minimum fault current,
                    #    2=>User specified, maximum current, 3=>User specified, minimum current
loadop   = 0        # 16 0=>unchanged, 1=>0.0 in +/- sequences, 2=>0.0 in all sequences (load)
genxop   = 0        # 17 0=>X'' 1=>X', 2=>Xs
                    # VALUES array
brktime  = 0.1      # 0.1 seconds, breaker contact parting time
ucfactor = 1.0      # specified voltage factor c value (used when option cfactor= 2 or 3)
                    # File args
iecfile   = ''
fcdfile   = ''
scfile    = 'nooutput'
"""

# ========================================================================================

import sys, os, time, math

bsys_kwds = {'usekv':0, 'basekv':[0.0, 999.0], 'areas':[], 'buses':[],
             'owners':[], 'zones':[]}

def fault_bsys(sid, **kwds):
    import psspy

    if sid==0: return

    actv_kwds = {}  # activity keywords
    for k, v in bsys_kwds.items():
        if k in kwds:
            actv_kwds[k] = kwds[k]
        else:
            actv_kwds[k] = v

    actv_kwds['sid']      = sid
    actv_kwds['numarea']  = len(actv_kwds['areas'])
    actv_kwds['numbus']   = len(actv_kwds['buses'])
    actv_kwds['numowner'] = len(actv_kwds['owners'])
    actv_kwds['numzone']  = len(actv_kwds['zones'])

    ierr = psspy.bsys(**actv_kwds)

    return ierr

# ========================================================================================

def set_prg_rpt(prgfile='', rptfile=''):
    import psspy
    psspy.lines_per_page_one_device(1,10000000)
    if prgfile: psspy.progress_output(2,prgfile,[0,0])
    if rptfile: psspy.report_output(2,rptfile,[0,0])

# ========================================================================================

def reset_prg_rpt():
    import psspy
    psspy.lines_per_page_one_device(2,10000000)
    psspy.progress_output(1,'',[0,0])
    psspy.report_output(1,'',[0,0])

# ========================================================================================

class IECS_DEMO:
    """ Run PSSE IECS Calculations"""

    def __init__(self):
        import psspy
        self.ierr = psspy.psseinit(buses=150000)

    # ------------------------------------------------------------------------------------
    def _frmted_z(self, cnum):
        r=cnum.real
        x=cnum.imag
        csign='+j'
        if x<0:
            csign='-j'
            x=abs(x)

        if r==0:
            rstr=''
        else:
            rstr="%9.6f" % r

        if x==0:
            xstr=''
            csign=''
        else:
            xstr="%9.6f" % x

        zstr = "%(rstr)s%(csign)s%(xstr)s" % vars()

        return zstr

    # ------------------------------------------------------------------------------------
    def _frmted_z_xbyr(self, cnum):

        zstr = self._frmted_z(cnum)

        r=cnum.real
        x=abs(cnum.imag)
        if r==0:
            xbyr=''
        else:
            xbyr="%9.6f" % (x/r)

        cstr="%(zstr)s, %(xbyr)s" % vars()

        return cstr

    # ------------------------------------------------------------------------------------

    def _crnt_mag(self, fmt, cval):
        if fmt=='rectangular':
            return abs(cval)
        else:
            return cval.real

    # ------------------------------------------------------------------------------------

    def _crnt_mva_mag(self, scfmt, scunit, cval, basekv, sbase):
        if scfmt=='rectangular':
            if scunit=='pu':
                baseamp = (1000.0*sbase)/(math.sqrt(3.0)*basekv)
                crnt = cval*baseamp
            else:
                crnt = cval
            crnt = abs(crnt)
        else:
            cval = cval.real
            if scunit=='pu':
                baseamp = (1000.0*sbase)/(math.sqrt(3.0)*basekv)
                crnt = cval*baseamp
            else:
                crnt = cval

        mva  = math.sqrt(3.0)*basekv*crnt/1000.0

        return crnt, mva

    # ------------------------------------------------------------------------------------
    def run_iecs_api(self, sid, allbus, **kwds):
        import psspy
        ierr = psspy.iecs_4(sid, allbus, **kwds)

    # ------------------------------------------------------------------------------------
    def run_iecs_currents(self, sid, allbus, **kwds):
        import psspy, arrbox.iecs

        rlst = arrbox.iecs.iecs_currents(sid, allbus, **kwds)

        if rlst.ierr!=0:
            raise Exception("arrbox.iecs.iecs_currents error= {}\n".format(rlst.ierr))

        return rlst

    # ------------------------------------------------------------------------------------
    def run_fault_summary(self, sid, allbus, **kwds):
        import psspy, arrbox.fault

        fltobj = arrbox.fault.FAULT_SUMMARY('IECS', sid, allbus, **kwds)

        if fltobj.ierr!=0:
            raise Exception("arrbox.fault.FAULT_SUMMARY error= {}\n".format(fltobj.ierr))

        return fltobj

    # ------------------------------------------------------------------------------------
    def report_iecs_currents(self, rlst, rptfile=''):
        import psspy

        if rlst.ierr: return

        if rptfile:
            p, nx = os.path.split(rptfile)
            n, x = os.path.splitext(nx)
            if not x:
                x = '.txt'
                nx = n + x
            if p:
                rptfile = os.path.join(p, nx)
            else:
                rptfile = os.path.join(os.getcwd(), nx)
            rptfile_h = open(rptfile,'w')
            report    = rptfile_h.write
        else:
            psspy.beginreport()
            report = psspy.report

        flt3ph = rlst.flt3ph
        fltlg  = rlst.fltlg
        fltllg = rlst.fltllg
        fltll  = rlst.fltll

        nfbus=len(rlst.fltbus)

        txtlst = []
        if not rptfile: txtlst.append('')

        ttlstr="PSS(R)E IECS SHORT CIRCUIT CURRENTS" + 10*' ' + time.ctime()
        ln1str,ln2str=psspy.titldt()
        maxlen=max(len(ttlstr),len(ln1str),len(ln2str))
        txtlst.append(ttlstr.center(maxlen))
        txtlst.append(ln1str.center(maxlen))
        txtlst.append(ln2str.center(maxlen))
        txtlst.append('')
        txtall = "\n".join(txtlst)
        report(txtall)

        scunit = rlst.scunit
        scfmt  = rlst.scfmt

        scunit_z = rlst.scunit_z
        scfmt_z  = rlst.scfmt_z

        if scunit == 'pu':
            units = 'PU'
        else:
            units = 'AMP'
        unitstr   = units.center(10)
        clnhdr    = "   BUS     " + 6*unitstr

        for i in range(nfbus):
            txtlst = []
            txtlst.append('')
            txtlst.append("           <--ia1--> <--ia2--> <--ia0--> <--ia---> <--ib---> <--ic--->")
            txtlst.append(clnhdr)
            fbus   = rlst.fltbus[i]
            if flt3ph:
                ttxt   = "%6d" % fbus
                spc    = '3PH'
                ia1    = self._crnt_mag(scfmt,rlst.flt3ph[i].ia1)
                ia2    = self._crnt_mag(scfmt,rlst.flt3ph[i].ia2)
                ia0    = self._crnt_mag(scfmt,rlst.flt3ph[i].ia0)
                ia     = self._crnt_mag(scfmt,rlst.flt3ph[i].ia)
                ib     = self._crnt_mag(scfmt,rlst.flt3ph[i].ib)
                ic     = self._crnt_mag(scfmt,rlst.flt3ph[i].ic)
                tmptxt = "%(ttxt)s %(spc)s %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f" % vars()
                txtlst.append(tmptxt)

            if fltlg:
                if flt3ph:
                    ttxt = 6*' '
                else:
                    ttxt = "%6d" % fbus
                spc    = ' LG'
                ia1    = self._crnt_mag(scfmt,rlst.fltlg[i].ia1)
                ia2    = self._crnt_mag(scfmt,rlst.fltlg[i].ia2)
                ia0    = self._crnt_mag(scfmt,rlst.fltlg[i].ia0)
                ia     = self._crnt_mag(scfmt,rlst.fltlg[i].ia)
                ib     = self._crnt_mag(scfmt,rlst.fltlg[i].ib)
                ic     = self._crnt_mag(scfmt,rlst.fltlg[i].ic)
                tmptxt = "%(ttxt)s %(spc)s %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f" % vars()
                txtlst.append(tmptxt)

            if fltllg:
                if flt3ph or fltlg:
                    ttxt = 6*' '
                else:
                    ttxt = "%6d" % fbus
                spc    = 'LLG'
                ia1    = self._crnt_mag(scfmt,rlst.fltllg[i].ia1)
                ia2    = self._crnt_mag(scfmt,rlst.fltllg[i].ia2)
                ia0    = self._crnt_mag(scfmt,rlst.fltllg[i].ia0)
                ia     = self._crnt_mag(scfmt,rlst.fltllg[i].ia)
                ib     = self._crnt_mag(scfmt,rlst.fltllg[i].ib)
                ic     = self._crnt_mag(scfmt,rlst.fltllg[i].ic)
                tmptxt = "%(ttxt)s %(spc)s %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f" % vars()
                txtlst.append(tmptxt)

            if fltll:
                if flt3ph or fltlg or fltllg:
                    ttxt = 6*' '
                else:
                    ttxt = "%6d" % fbus
                spc     = ' LL'
                ia1    = self._crnt_mag(scfmt,rlst.fltll[i].ia1)
                ia2    = self._crnt_mag(scfmt,rlst.fltll[i].ia2)
                ia0    = self._crnt_mag(scfmt,rlst.fltll[i].ia0)
                ia     = self._crnt_mag(scfmt,rlst.fltll[i].ia)
                ib     = self._crnt_mag(scfmt,rlst.fltll[i].ib)
                ic     = self._crnt_mag(scfmt,rlst.fltll[i].ic)
                tmptxt = "%(ttxt)s %(spc)s %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f" % vars()
                txtlst.append(tmptxt)

            txtlst.append("\nTHEVENIN IMPEDANCE (pu), X/R")

            z1str = self._frmted_z_xbyr(rlst.thevzpu[i].z1)
            z1str ="Z1: " + z1str
            if fltlg or fltllg or fltll:
                z2str = self._frmted_z_xbyr(rlst.thevzpu[i].z2)
                z2str ="Z2: " + z2str
                z0str = self._frmted_z_xbyr(rlst.thevzpu[i].z0)
                z0str ="Z0: " + z0str
                tmptxt="%(z1str)s    %(z2str)s    %(z0str)s" % vars()
            else:
                tmptxt="%(z1str)s" % vars()
            txtlst.append(tmptxt)

            if scunit_z!='pu':
                txtlst.append("\nTHEVENIN IMPEDANCE (ohms), X/R")
                z1str = self._frmted_z_xbyr(rlst.thevz[i].z1)
                z1str ="Z1: " + z1str
                if fltlg or fltllg or fltll:
                    z2str = self._frmted_z_xbyr(rlst.thevz[i].z2)
                    z2str ="Z2: " + z2str
                    z0str = self._frmted_z_xbyr(rlst.thevz[i].z0)
                    z0str ="Z0: " + z0str
                    tmptxt="%(z1str)s    %(z2str)s    %(z0str)s" % vars()
                else:
                    tmptxt="%(z1str)s" % vars()
                txtlst.append(tmptxt)

            tmptxt=110*'-'
            txtlst.append(tmptxt)
            txtlst.append('')

            txtall = "\n".join(txtlst)
            report(txtall)

        # Maximum Fault Currents
        inam = ['ia1', 'ia2', 'ia0', 'ia', 'ib', 'ic']
        unitstr   = units.center(11)
        unitstr = ''
        for each in ['ia1', 'ia2', 'ia0', ' ia', ' ib', ' ic']:
            t = each+'('+units+')'
            t = ' ' + t.center(9) + ' '
            unitstr += t

        txtlst = []
        txtlst.append('')

        clnhdr    = "   BUS  " + unitstr + "  Description"
        txtlst.append("BREAKER DUTY CURRENTS")
        txtlst.append(clnhdr)
        txtall = "\n".join(txtlst)
        report(txtall)

        for i in range(nfbus):
            fbus   = rlst.fltbus[i]
            ia1    = self._crnt_mag(scfmt,rlst.maxflt[i].ia1)
            ia2    = self._crnt_mag(scfmt,rlst.maxflt[i].ia2)
            ia0    = self._crnt_mag(scfmt,rlst.maxflt[i].ia0)
            ia     = self._crnt_mag(scfmt,rlst.maxflt[i].ia)
            ib     = self._crnt_mag(scfmt,rlst.maxflt[i].ib)
            ic     = self._crnt_mag(scfmt,rlst.maxflt[i].ic)
            dsc    = rlst.maxfltdsc[i]
            if rptfile: report('\n')
            tmptxt = "%(fbus)6d   %(ia1)9.2f  %(ia2)9.2f  %(ia0)9.2f  %(ia)9.2f  %(ib)9.2f  %(ic)9.2f   %(dsc)s" % vars()
            report(tmptxt)

        # ------------------------------------------------------------------------------------------------
        if rptfile:
            rptfile_h.close()
            print('\n Done .... IECS FAULT Report saved to file %s' % rptfile)

    # ------------------------------------------------------------------------------------
    def excel_iecs_currents(self, rlst, faults_applied, xlsfile=''):
        import psspy
        import excelpy

        if rlst.ierr: return

        # bus data
        sid  = -1   # consider subsystem of all buses
        flag = 1    # consider only in-service buses
        ierr,(busnums,)   = psspy.abusint(sid,flag,['NUMBER'])
        ierr,(busbasevs,) = psspy.abusreal(sid,flag,'BASE')
        ierr,(busvlt,)    = psspy.abuscplx(sid,flag,'VOLTAGE') # pre-fault bus voltages in pu
        ierr,(busname,)   = psspy.abuschar(sid,flag,'NAME')

        bus_data = {}
        for bnum, bbasev, bvlt, bnam in zip(busnums,busbasevs,busvlt,busname):
            bus_data[bnum] = {'prefltv': bvlt, 'basekv': bbasev, 'name': bnam}

        flt3ph = rlst.flt3ph
        fltlg  = rlst.fltlg
        fltllg = rlst.fltllg
        fltll  = rlst.fltll

        scunit   = rlst.scunit
        scfmt    = rlst.scfmt
        scunit_z = rlst.scunit_z
        scfmt_z  = rlst.scfmt_z

        nfbus=len(rlst.fltbus)

        xlswbk = excelpy.workbook(xlsfile)
        xlswbk.show()

        savfile, snpfile = psspy.sfiles()
        line1, line2 = psspy.titldt()

        ttl      = r"PSSE Short Circuit Calculations Using IECS"
        ttl      = ttl + 5*' ' + time.ctime()
        ttl_file = savfile
        ttl_line1= line1.strip()
        ttl_line2= line2.strip()

        cln_mrglst = []
        cln_heads_r1 = ['BUS', '', 'BASE', 'PREFLT']
        cln_heads_r2 = ['NUMBER', 'NAME', 'kV', 'kV']
        for fltok, clnnam in zip([flt3ph, fltlg, fltllg, fltll],
                                 ['3-PH FAULT', 'LG FAULT', 'LLG FAULT', 'LL FAULT']):
            if fltok:
                cln_mrglst.append(len(cln_heads_r1)+1)
                cln_heads_r1.extend([clnnam, ''])
                cln_heads_r2.extend(['MVA', 'AMP'])

        cln_heads_r1.extend(['THEVENIN IMPEDANCE (PU on 100 MVA and bus base KV)','', ''])
        cln_heads_r2.extend(['Positive Sequence', 'Negative Sequence', 'Zero Sequence'])

        colheads = [cln_heads_r1, cln_heads_r2]

        row = 7
        cln = 1

        sbase = psspy.sysmva()

        for i in range(nfbus):
            rowdata = []
            fbus    = rlst.fltbus[i]
            basekv  = bus_data[fbus]['basekv']
            prefltv = bus_data[fbus]['prefltv']

            rowdata.append(fbus)
            rowdata.append(bus_data[fbus]['name'])
            rowdata.append(basekv)
            rowdata.append(basekv*abs(prefltv))

            if flt3ph:
                cval = rlst.flt3ph[i].ia1   # Ifault=Ia1=Ia
                crnt, mva = self._crnt_mva_mag(scfmt, scunit, cval, basekv, sbase)
                rowdata.extend([mva, crnt])

            if fltlg:
                cval = rlst.fltlg[i].ia0    # Ifault=3*Ia0=Ia
                crnt, mva = self._crnt_mva_mag(scfmt, scunit, cval, basekv, sbase)
                rowdata.extend([3*mva, 3*crnt])

            if fltllg:
                cval = rlst.fltllg[i].ia0   # Ifault=3*Ia0
                crnt, mva = self._crnt_mva_mag(scfmt, scunit, cval, basekv, sbase)
                rowdata.extend([3*mva, 3*crnt])

            if fltll:
                cval = rlst.fltll[i].ib   # Ifault=Ib
                crnt, mva = self._crnt_mva_mag(scfmt, scunit, cval, basekv, sbase)
                rowdata.extend([mva, crnt])

            zpos  = rlst.thevzpu[i].z1
            zneg  = rlst.thevzpu[i].z2
            zzero = rlst.thevzpu[i].z0

            s_zpos  = self._frmted_z(zpos)
            s_zneg  = self._frmted_z(zneg)
            s_zzero = self._frmted_z(zzero)

            rowdata.extend([s_zpos, s_zneg, s_zzero])

            brow,rcln = xlswbk.set_range(row,cln,rowdata)
            row = brow + 1

        xlswbk.font((6,3,brow,8),numberFormat="0.00")
        xlswbk.autofit_columns((6,9,brow,rcln))
        xlswbk.align((6,9,brow,rcln),'right')

        # headings and column titles
        xlswbk.set_cell((1,1),ttl,fontStyle="Bold",fontSize=12, fontColor="red")
        xlswbk.merge((1,1,1,rcln))

        xlswbk.set_cell((2,1),ttl_file,fontStyle="Bold",fontSize=10, fontColor="red")
        xlswbk.merge((2,1,2,rcln))

        xlswbk.set_cell((3,1),ttl_line1,fontStyle="Bold",fontSize=10, fontColor="red")
        xlswbk.merge((3,1,3,rcln))

        xlswbk.set_cell((4,1),ttl_line2,fontStyle="Bold",fontSize=10, fontColor="red")
        xlswbk.merge((4,1,4,rcln))

        brow,rcln = xlswbk.set_range(5,1,colheads,fontSize=11, fontColor="blue")

        xlswbk.merge((5,1,5,2))
        for cln in cln_mrglst:
            xlswbk.merge((5,cln,5,cln+1))
        xlswbk.merge((5,rcln-2,5,rcln))

        xlswbk.align((1,1),'h_center')
        xlswbk.align_rows((1,1,6,1),'h_center')

        if xlsfile: xlswbk.save(xlsfile)

# ========================================================================================
def run_iecs_4(**kwds):
    import psspy
    psspy.psseinit(buses=150000)

    savfile = 'iec60909_testnetwork_50Hz.sav'
    iecfile = 'iec60909_testnetwork.iec'
    buses = [1,2,3,4,5,6,7,8]
    sid, allbus = 3, 0

    ierr = psspy.case(savfile)
    ierr = fault_bsys(sid, buses=buses)

    nam_unt = {0:'pu', 1:'amp'}
    unt=1

    rptfile = "z_iec60909_testnetwork_iecs_4_{}_rpt{}_report.txt".format(nam_unt[unt], kwds['rptop'])

    set_prg_rpt(rptfile=rptfile)

    # set short circuit options
    psspy.short_circuit_units(unt)          # 0=PU, 1=Physical
    psspy.short_circuit_z_units(unt)        # 0=PU, 1=Physical
    psspy.short_circuit_coordinates(1)      # 0=rectangular, 1=polar
    psspy.short_circuit_z_coordinates(0)    # 0=rectangular, 1=polar
    psspy.short_circuit_warning(0)          # 0= disable, printing of of RESQ/TRSQ/solution warnings

    kwds['iecfile'] = iecfile
    iecsobj = IECS_DEMO()
    iecsobj.run_iecs_api(sid, allbus, **kwds)

    reset_prg_rpt()

# ========================================================================================
def run_iecs_currents_txtrpt(**kwds):
    import psspy
    psspy.psseinit(buses=150000)

    savfile = 'iec60909_testnetwork_50Hz.sav'
    iecfile = 'iec60909_testnetwork.iec'
    buses = [1,2,3,4,5,6,7,8]
    sid, allbus = 3, 0

    nam_unt = {0:'pu', 1:'amp'}
    unt=1

    rptfile = "z_iecs_currents_{}.txt".format(nam_unt[unt])

    ierr = psspy.case(savfile)
    ierr = fault_bsys(sid, buses=buses)

    # set short circuit options
    psspy.short_circuit_units(unt)          # 0=PU, 1=Physical
    psspy.short_circuit_z_units(unt)        # 0=PU, 1=Physical
    psspy.short_circuit_coordinates(1)      # 0=rectangular, 1=polar
    psspy.short_circuit_z_coordinates(0)    # 0=rectangular, 1=polar
    psspy.short_circuit_warning(0)          # 0= disable, printing of of RESQ/TRSQ/solution warnings

    kwds['iecfile'] = iecfile
    iecsobj = IECS_DEMO()
    rlst = iecsobj.run_iecs_currents(sid, allbus, **kwds)
    iecsobj.report_iecs_currents(rlst, rptfile)

# ========================================================================================
def run_iecs_currents_xls(**kwds):
    import psspy
    psspy.psseinit(buses=150000)

    savfile = 'iec60909_testnetwork_50Hz.sav'
    iecfile = 'iec60909_testnetwork.iec'
    buses = [1,2,3,4,5,6,7,8]
    sid, allbus = 3, 0

    nam_unt = {0:'pu', 1:'amp'}
    unt=1

    xlsfile = "z_iecs_currents_{}".format(nam_unt[unt])

    ierr = psspy.case(savfile)
    ierr = fault_bsys(sid, buses=buses)

    # set short circuit options
    psspy.short_circuit_units(unt)          # 0=PU, 1=Physical
    psspy.short_circuit_z_units(unt)        # 0=PU, 1=Physical
    psspy.short_circuit_coordinates(1)      # 0=rectangular, 1=polar
    psspy.short_circuit_z_coordinates(0)    # 0=rectangular, 1=polar
    psspy.short_circuit_warning(0)          # 0= disable, printing of of RESQ/TRSQ/solution warnings

    kwds['iecfile'] = iecfile
    iecsobj = IECS_DEMO()
    rlst = iecsobj.run_iecs_currents(sid, allbus, **kwds)
    iecsobj.excel_iecs_currents(rlst, xlsfile)

# ========================================================================================
def run_fault_summary_iecs(**kwds):
    import psspy
    psspy.psseinit(buses=150000)

    savfile = 'iec60909_testnetwork_50Hz.sav'
    iecfile = 'iec60909_testnetwork.iec'
    buses = [1,2,3,4,5,6,7,8]
    sid, allbus = 3, 0

    nam_unt = {0:'pu', 1:'amp'}
    unt=1

    rptfile = "z_iecs_fault_summary_{}.txt".format(nam_unt[unt])

    ierr = psspy.case(savfile)
    ierr = fault_bsys(sid, buses=buses)

    # set short circuit options
    psspy.short_circuit_units(unt)          # 0=PU, 1=Physical
    psspy.short_circuit_z_units(unt)        # 0=PU, 1=Physical
    psspy.short_circuit_coordinates(1)      # 0=rectangular, 1=polar
    psspy.short_circuit_z_coordinates(0)    # 0=rectangular, 1=polar
    psspy.short_circuit_warning(0)          # 0= disable, printing of of RESQ/TRSQ/solution warnings

##    kwds = {
##        'flt3ph'   : 1, 'fltlg'    : 1, 'fltllg'   : 1, 'fltll'    : 1,
##        'rptop'    : 1, 'rptlvl'   : 0, 'fltloc'   : 0, 'linout'   : 0,
##        'linend'   : 0, 'tpunty'   : 0, 'lnchrg'   : 1, 'shntop'   : 1,
##        'dcload'   : 0, 'zcorec'   : 0, 'cfactor'  : 0, 'loadop'   : 0,
##        'genxop'   : 0, 'brktime'  : 0.1, 'ucfactor' : 1.0 }

    kwds['iecfile'] = iecfile
    iecsobj = IECS_DEMO()
    fltobj = iecsobj.run_fault_summary(sid, allbus, **kwds)
    fltobj.text_report(rptfile)

# ========================================================================================
def _temp():
    # Run either of these functions under  __main__ to see how they work.
    run_iecs_4(flt3ph=1, fltlg=1, fltllg=1, fltll=1, rptop=1)

    run_iecs_currents_txtrpt(flt3ph=1, fltlg=1, fltllg=1, fltll=1, rptop=1)
    run_iecs_currents_xls(flt3ph=1, fltlg=1, fltllg=1, fltll=1)

    run_fault_summary_iecs(flt3ph=1, fltlg=1, fltllg=1, fltll=1, rptop=1)
    run_fault_summary_iecs(flt3ph=1, fltlg=1, fltllg=0, fltll=1, rptop=0, linout=1, linend=1)

# ========================================================================================
if __name__=='__main__':
    pass
