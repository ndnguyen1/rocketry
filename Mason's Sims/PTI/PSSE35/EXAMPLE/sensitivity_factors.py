#[sensitivity_factors.py]  Sensitivity Analysis Report and Accesing them in Python Script
# ====================================================================================================
'''Sensitivity Factors of a branch flow to MW power at generator and load buses:
This is an example file showing how to generate sensitivity factors report or
access those factor values in Python script.

# ----------------------------------------------------------------------------------------------------

How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call any of the function as below
    run_demo()  OR
    run_demo(savfile='savnw.sav', dfxfile='savnw.dfx', outpath=None)
    You could modify various inputs in run)demo() as desired.
'''

# ====================================================================================================
import sys, os

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

# ====================================================================================================

def get_output_filename(outpath, fnam):

    p, nx = os.path.split(fnam)
    if p:
        retvfile = fnam
    else:
        outdir = get_output_dir(outpath)
        retvfile = os.path.join(outdir, fnam)

    return retvfile

# ====================================================================================================

def create_report(ibus,jbus,mainsys,dfxfile,kbus,ckt,netmod,brnflowtyp,transfertyp,oppsystyp,dispmod,toln,oppsys,rptfile):
    # Create Report
    import arrbox.sensitivity_flow_to_mw

    flow2mw = arrbox.sensitivity_flow_to_mw()

    ierr = flow2mw.sensitivity_flow_to_mw_report(ibus,jbus,mainsys,dfxfile,kbus=0,ckt='1',netmod='dc',brnflowtyp='mw',
        transfertyp='import',oppsystyp='slack bus',dispmod=1,toln=None,oppsys='',rptfile=rptfile)

# ====================================================================================================

def demo_access(ibus,jbus,mainsys,dfxfile,kbus,ckt,netmod,brnflowtyp,transfertyp,oppsystyp,dispmod,toln,oppsys):
    # Access factor results in Python script
    import arrbox.sensitivity_flow_to_mw

    flow2mw = arrbox.sensitivity_flow_to_mw()

    robj = flow2mw.sensitivity_flow_to_mw(ibus,jbus,mainsys,dfxfile,kbus=0,ckt='1',netmod='dc',brnflowtyp='mw',
        transfertyp='import',oppsystyp='slack bus',dispmod=1,toln=None,oppsys='')

    print("\n Returned dictionary object as is:")
    print(robj)
    print('\n')

    print("  Getting 'ngenbuses' value by different ways:")
    print("     robj.ngenbuses    = {0:d}".format(robj.ngenbuses))
    print("     robj.ngenBuses    = {0:d}".format(robj.ngenBuses))
    print("     robj['ngenbuses'] = {0:d}".format(robj['ngenbuses']))
    print("     robj['NGENbuses'] = {0:d}".format(robj['NGENbuses']))
    print('\n')

    print("  Bus names for which generator factors are calculated:")
    print(list(robj.genvalues.keys()))
    print('\n')

    print("  Generator factors:")
    for bus, vdict in list(robj.genvalues.items()):
        tdct = {'bus':bus, 'pmax':vdict.pmax, 'pmin':vdict.pmin, 'pgen':vdict.pgen, 'sftr':vdict.factor}
        print("{bus:s}  {pmax:8.2f}  {pmin:8.2f} {pgen:8.2f}  {sftr:8.5f}".format(**tdct))

# ====================================================================================================

def run_demo(savfile='savnw.sav', dfxfile='savnw.dfx', outpath=None):
    import psspy

    ibus        = 151
    jbus        = 152
    kbus        = 0
    ckt         = '1'
    mainsys     = 'STUDY'
    netmod      = 'dc'
    brnflowtyp  = 'mw'
    transfertyp = 'import'
    oppsystyp   = 'slack bus'
    dispmod     = 1
    toln        = None
    oppsys      = ''

    if not os.path.exists(savfile):
        prgmsg = " Error: Input savfile '{0}' does not exist".format(savfile)
        print(prgmsg)
        return

    if not os.path.exists(dfxfile):
        prgmsg = " Error: Input dfxfile '{0}' does not exist".format(dfxfile)
        print(prgmsg)
        return

    p, nx = os.path.split(dfxfile)
    n, x = os.path.splitext(nx)

    rptfile = get_output_filename(outpath, 'sensitivity_factors_' + n +'_report.txt')

    psspy.psseinit()

    psspy.case(savfile)

    create_report(ibus,jbus,mainsys,dfxfile,kbus,ckt,netmod,brnflowtyp,transfertyp,oppsystyp,dispmod,toln,oppsys,rptfile)

    demo_access(ibus,jbus,mainsys,dfxfile,kbus,ckt,netmod,brnflowtyp,transfertyp,oppsystyp,dispmod,toln,oppsys)

# ====================================================================================================
# ====================================================================================================

if __name__ == '__main__':

    import psse35
    run_demo()

# ====================================================================================================
