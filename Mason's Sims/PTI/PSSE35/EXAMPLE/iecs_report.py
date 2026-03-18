#[iecs_report.py]    Get IEC fault currents in arrays and create custom report
# =====================================================================================================
'''
This is an example file showing how to use "iecs_currents" function from pssarrays module.

IECS_CURRENTS function returns IEC 60909 standard fault currents for each faulted bus and
each type of fault applied. They are:
    ia1   = Positive Sequence Current
    ia2   = Negative Sequence Current
    ia0   = Zero Sequence Current
    ia    = Phase A current
    ib    = Phase B current
    ic    = Phase C current
    ipb   = peak Current - Method B, ip(B)
    ipc   = peak Current - Method C, ip(C)
    idc   = DC component of asymmetrical breaking current, idc
    ibsym = symmetrical breaking current (r.m.s.), ib(sym)
    ibuns = asymmetrical breaking current (r.m.s.), ib(uns)

The APIs used in this program are part of python "pssarrays" module.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call funtion
    run_iecs_report()

    You may want to change inputs specified in this function.
    run_iecs_report(savfile, iecfile, fltbuses, rptfile)
    Defaults:
        savfile  = 'iec60909_testnetwork_50Hz.sav'
        iecfile  = 'iec60909_testnetwork.iec'
        fltbuses = [1,2,3,4,5,6,7,8]
        rptfile  = 'iecs_report_iec60909_testnetwork_50Hz.txt'
                   When this script is called from PSSE's Example Folder,
                   report is created in subfolder 'Output_Pyscript'
'''

# =====================================================================================================

import os, time

# =====================================================================================================

def encode_complex_number_xbyr(cnum):
    r=cnum.real
    x=cnum.imag
    csign='+j'
    if x<0:
        csign='-j'
        x=abs(x)

    if r==0:
        rstr=''
        xbyr=''
    else:
        rstr="%9.6f" % r
        xbyr="%9.6f" % (x/r)

    if x==0:
        xstr=''
        csign=''
    else:
        xstr="%9.6f" % x

    cstr="%(rstr)s%(csign)s%(xstr)s, %(xbyr)s" % vars()

    return cstr

# =====================================================================================================

def current_magnitude(fmt,cmplxvalue):
    if fmt == 'rectangular':
        return abs(cmplxvalue)
    else:
        return cmplxvalue.real

# =====================================================================================================

def create_report(units,fmt,fltbuses,flt3ph,fltlg,fltllg,fltll,linout,linend,tpunty,
                  lnchrg,shntop,dcload,zcorec,optnftrc,loadop,genxop,brktime,vfactorc,
                  savfile,iecfile,fcdfile,scfile,rptfile,rprtyp,rprlvl):

    import psspy, arrbox.iecs

    # open case
    if savfile: psspy.case(savfile)

    # set sc units and format
    psspy.short_circuit_units(units)
    psspy.short_circuit_coordinates(fmt)

    sid = 3
    if fltbuses:
        psspy.bsys(sid,0,[0.0,0.0],0,[],len(fltbuses),fltbuses,0,[],0,[])
        busall = 0
    else:
        busall = 1

    # call pssarrays routine
    rlst=arrbox.iecs.iecs_currents(sid=sid, all=busall, flt3ph=flt3ph, fltlg=fltlg, fltllg=fltllg,
            fltll=fltll, linout=linout, linend=linend, tpunty=tpunty, lnchrg=lnchrg,
            shntop=shntop, dcload=dcload, zcorec= zcorec, optnftrc=optnftrc, loadop=loadop,
            genxop=genxop, brktime=brktime, vfactorc=vfactorc,
            iecfile=iecfile, fcdfile=fcdfile, scfile=scfile, rprtyp=rprtyp, rprlvl=rprlvl)
    if rlst.ierr!=0:
        raise Exception("arrbox.iecs.iecs_currents error= %d\n" % rlst.ierr)

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

    nfbus=len(rlst.fltbus)

    ttlstr="PSS(R)E IEC 60909 SHORT CIRCUIT CURRENTS" + 10*' ' + time.ctime()
    ln1str,ln2str=psspy.titldt()
    maxlen=max(len(ttlstr),len(ln1str),len(ln2str))
    report(ttlstr.center(maxlen))
    report("\n")
    report(ln1str.center(maxlen))
    report("\n")
    report(ln2str.center(maxlen))
    report("\n\n")

    scunit = rlst.scunit
    scfmt  = rlst.scfmt
    if scunit == 'pu':
        units = 'PU'
    else:
        units = 'AMP'
    unitstr   = units.center(10)
    clnhdr    = "   BUS     " + 6*unitstr + "\n"

    for i in range(nfbus):
        report("           <-i''k--> <-ip(B)-> <-ip(C)-> <--idc--> <ib(sym)> <ib(uns)>\n")
        report(clnhdr)
        fbus   = rlst.fltbus[i]
        if flt3ph:
            ttxt   = "%6d" % fbus
            spc    = '3PH'
            ia1    = current_magnitude(scfmt,rlst.flt3ph[i].ia1)
            ia2    = current_magnitude(scfmt,rlst.flt3ph[i].ia2)
            ia0    = current_magnitude(scfmt,rlst.flt3ph[i].ia0)
            ia     = current_magnitude(scfmt,rlst.flt3ph[i].ia)
            ib     = current_magnitude(scfmt,rlst.flt3ph[i].ib)
            ic     = current_magnitude(scfmt,rlst.flt3ph[i].ic)
            ipb    = current_magnitude(scfmt,rlst.flt3ph[i].ipb)
            ipc    = current_magnitude(scfmt,rlst.flt3ph[i].ipc)
            idc    = current_magnitude(scfmt,rlst.flt3ph[i].idc)
            ibsym  = current_magnitude(scfmt,rlst.flt3ph[i].ibsym)
            ibuns  = current_magnitude(scfmt,rlst.flt3ph[i].ibuns)
            tmptxt = "%(ttxt)s %(spc)s %(ia1)9.2f %(ipb)9.2f %(ipc)9.2f %(idc)9.2f %(ibsym)9.2f %(ibuns)9.2f \n" % vars()
            report(tmptxt)

        if fltlg:
            if flt3ph:
                ttxt = 6*' '
            else:
                ttxt = "%6d" % fbus
            spc    = ' LG'
            ia1    = current_magnitude(scfmt,rlst.fltlg[i].ia1)
            ia2    = current_magnitude(scfmt,rlst.fltlg[i].ia2)
            ia0    = current_magnitude(scfmt,3*rlst.fltlg[i].ia0)
            ia     = current_magnitude(scfmt,rlst.fltlg[i].ia)
            ib     = current_magnitude(scfmt,rlst.fltlg[i].ib)
            ic     = current_magnitude(scfmt,rlst.fltlg[i].ic)
            ipb    = current_magnitude(scfmt,rlst.fltlg[i].ipb)
            ipc    = current_magnitude(scfmt,rlst.fltlg[i].ipc)
            idc    = current_magnitude(scfmt,rlst.fltlg[i].idc)
            ibsym  = current_magnitude(scfmt,rlst.fltlg[i].ibsym)
            ibuns  = current_magnitude(scfmt,rlst.fltlg[i].ibuns)
            tmptxt = "%(ttxt)s %(spc)s %(ia0)9.2f %(ipb)9.2f %(ipc)9.2f %(idc)9.2f %(ibsym)9.2f %(ibuns)9.2f \n" % vars()
            report(tmptxt)

        if fltllg:
            if flt3ph or fltlg:
                ttxt = 6*' '
            else:
                ttxt = "%6d" % fbus
            spc    = 'LLG'
            ia1    = current_magnitude(scfmt,rlst.fltllg[i].ia1)
            ia2    = current_magnitude(scfmt,rlst.fltllg[i].ia2)
            ia0    = current_magnitude(scfmt,3*rlst.fltllg[i].ia0)
            ia     = current_magnitude(scfmt,rlst.fltllg[i].ia)
            ib     = current_magnitude(scfmt,rlst.fltllg[i].ib)
            ic     = current_magnitude(scfmt,rlst.fltllg[i].ic)
            ipb    = current_magnitude(scfmt,rlst.fltllg[i].ipb)
            ipc    = current_magnitude(scfmt,rlst.fltllg[i].ipc)
            idc    = current_magnitude(scfmt,rlst.fltllg[i].idc)
            ibsym  = current_magnitude(scfmt,rlst.fltllg[i].ibsym)
            ibuns  = current_magnitude(scfmt,rlst.fltllg[i].ibuns)
            tmptxt = "%(ttxt)s %(spc)s %(ia0)9.2f %(ipb)9.2f %(ipc)9.2f %(idc)9.2f %(ibsym)9.2f %(ibuns)9.2f \n" % vars()
            report(tmptxt)

        if fltll:
            if flt3ph or fltlg or fltllg:
                ttxt = 6*' '
            else:
                ttxt = "%6d" % fbus
            spc     = ' LL'
            ia1    = current_magnitude(scfmt,rlst.fltll[i].ia1)
            ia2    = current_magnitude(scfmt,rlst.fltll[i].ia2)
            ia0    = current_magnitude(scfmt,rlst.fltll[i].ia0)
            ia     = current_magnitude(scfmt,rlst.fltll[i].ia)
            ib     = current_magnitude(scfmt,rlst.fltll[i].ib)
            ic     = current_magnitude(scfmt,rlst.fltll[i].ic)
            ipb    = current_magnitude(scfmt,rlst.fltll[i].ipb)
            ipc    = current_magnitude(scfmt,rlst.fltll[i].ipc)
            idc    = current_magnitude(scfmt,rlst.fltll[i].idc)
            ibsym  = current_magnitude(scfmt,rlst.fltll[i].ibsym)
            ibuns  = current_magnitude(scfmt,rlst.fltll[i].ibuns)
            tmptxt = "%(ttxt)s %(spc)s %(ib)9.2f %(ipb)9.2f %(ipc)9.2f %(idc)9.2f %(ibsym)9.2f %(ibuns)9.2f \n" % vars()
            report(tmptxt)

        report("\nTHEVENIN IMPEDANCE (pu), X/R\n")
        z1str = encode_complex_number_xbyr(rlst.thevzpu[i].z1)
        z1str ="Z1: " + z1str
        if fltlg or fltllg or fltll:
            z2str = encode_complex_number_xbyr(rlst.thevzpu[i].z2)
            z2str ="Z2: " + z2str
            z0str = encode_complex_number_xbyr(rlst.thevzpu[i].z0)
            z0str ="Z0: " + z0str
            tmptxt="%(z1str)s    %(z2str)s    %(z0str)s\n" % vars()
        else:
            tmptxt="%(z1str)s\n" % vars()
        report(tmptxt)

        if scunit != 'pu':
            report("\nTHEVENIN IMPEDANCE (ohms), X/R\n")
            z1str = encode_complex_number_xbyr(rlst.thevz[i].z1)
            z1str ="Z1: " + z1str
            if fltlg or fltllg or fltll:
                z2str = encode_complex_number_xbyr(rlst.thevz[i].z2)
                z2str ="Z2: " + z2str
                z0str = encode_complex_number_xbyr(rlst.thevz[i].z0)
                z0str ="Z0: " + z0str
                tmptxt="%(z1str)s    %(z2str)s    %(z0str)s\n" % vars()
            else:
                tmptxt="%(z1str)s\n" % vars()
            report(tmptxt)

        tmptxt=110*'-'
        report(tmptxt)
        report("\n")

    # Maximum Fault Currents
    inam = ['ia1', 'ia2', 'ia0', 'ia', 'ib', 'ic']
    unitstr   = units.center(11)
    unitstr = ''
    for each in ['ia1', 'ia2', 'ia0', ' ia', ' ib', ' ic']:
        t = each+'('+units+')'
        t = ' ' + t.center(9) + ' '
        unitstr += t

    clnhdr    = "   BUS  " + unitstr + "  Description\n"
    report("\nBREAKER DUTY CURRENTS\n")
    report(clnhdr)
    for i in range(nfbus):
        fbus   = rlst.fltbus[i]
        ia1    = current_magnitude(scfmt,rlst.maxflt[i].ia1)
        ia2    = current_magnitude(scfmt,rlst.maxflt[i].ia2)
        ia0    = current_magnitude(scfmt,rlst.maxflt[i].ia0)
        ia     = current_magnitude(scfmt,rlst.maxflt[i].ia)
        ib     = current_magnitude(scfmt,rlst.maxflt[i].ib)
        ic     = current_magnitude(scfmt,rlst.maxflt[i].ic)
        dsc    = rlst.maxfltdsc[i]
        tmptxt = "%(fbus)6d   %(ia1)9.2f  %(ia2)9.2f  %(ia0)9.2f  %(ia)9.2f  %(ib)9.2f  %(ic)9.2f   %(dsc)s\n" % vars()
        report(tmptxt)

    # ------------------------------------------------------------------------------------------------
    if rptfile:
        rptfile_h.close()
        print('\n Done .... IECS FAULT Report saved to file %s' % rptfile)
    else:
        print('\n Done .... IECS FAULT Report created in Report window.')

# =====================================================================================================

def check_psse_example_folder(rptfile):
    # if called from PSSE's Example Folder, create report in subfolder 'Output_Pyscript'
    rptpath, rptfnam = os.path.split(rptfile)
    if not rptpath:
        rptpath = os.getcwd()
        cwd = rptpath.lower()
        i = cwd.find('pti')
        j = cwd.find('psse')
        k = cwd.find('example')
        if i>0 and j>i and k>j:     # called from Example folder
            outdir = os.path.join(os.getcwd(), 'Output_Pyscript')
            if not os.path.exists(outdir): os.mkdir(outdir)
        else:
            outdir = os.getcwd()
        rptfile  = os.path.join(outdir, rptfnam)

    return rptfile

# =====================================================================================================

def run_iecs_report(savfile='iec60909_testnetwork_50Hz.sav', iecfile='iec60909_testnetwork.iec',
                    fltbuses=[1,2,3,4,5,6,7,8], rptfile='iecs_report_iec60909_testnetwork_50Hz.txt'):

    import psspy

    psspy.psseinit()

    # Inputs, change as required

    units    = 1       # 0=per unit,    1=physical
    fmt      = 0       # 0=rectangular, 1=polar coordinates

    flt3ph   = 1       #
    fltlg    = 1       #
    fltllg   = 1       #
    fltll    = 1       #
    linout   = 0       #
    linend   = 0       #
    tpunty   = 0       #
    lnchrg   = 1       #
    shntop   = 1       #
    dcload   = 0       #
    zcorec   = 0       #
    optnftrc = 0       #
    loadop   = 1       #
    genxop   = 0       # 0=X", 1=X', 2=Xs (generator reactance)

    brktime  = 0.1     # 0.1 seconds
    vfactorc = 1.0     #

    rptfile  = check_psse_example_folder(rptfile)

    fcdfile  = ""
    scfile   = ""

    rprtyp   = -1      # no report
    rprlvl   = 0       # number of contribution levels

    create_report(units,fmt,fltbuses,flt3ph,fltlg,fltllg,fltll,linout,linend,tpunty,
                  lnchrg,shntop,dcload,zcorec,optnftrc,loadop,genxop,brktime,vfactorc,
                  savfile,iecfile,fcdfile,scfile,rptfile,rprtyp,rprlvl)

# ====================================================================================================
if __name__ == '__main__':

    import psse35
    run_iecs_report()

# ====================================================================================================

