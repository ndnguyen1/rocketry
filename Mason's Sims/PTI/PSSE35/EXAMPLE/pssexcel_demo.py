# pssexcel_demo.py  Use of pssexcel to export ACCC, PV and QV
# ====================================================================================================
'''
This is an example file showing how to use Python module "pssexcel"
to export ACCC, PV and QV solution results to excel spreadsheets.

Refer help(pssexcel) for details.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example, where XX could be 33 or 34:
    import psseXX

- call any of the function as below
    accc()
    accc(accfile='savnw.acc', show=True, cosep=True)

    pv()
    pv(pvfile='savnw.pv', show=True)

    qv()
    qv(qvfile='savnw.qv', show=True)

---------------------------------------------------------------------------------
Alternatively, use either of the following menu items.
- from Start>Programs>PSSExx>Export Results to Excel OR
- from Power Flow>Reports>Export Results to Excel

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

def accc(accfile='savnw.acc', outpath=None, show=True, cosep=True):
    import pssexcel

    if not os.path.exists(accfile):
        prgmsg = " Error: Input accfile '{0}' does not exist".format(accfile)
        print(prgmsg)
        return

    # Change these values as required.
    string  = ['s','e','b','i','v','l','g','p','a']
    colabel = [] #'base case', 'trip1nuclear', 'trip2nuclear']

    p, nx = os.path.split(accfile)
    n, x  = os.path.splitext(nx)

    xlsfile = get_output_filename(outpath, 'pssexcel_demo_accc_' + n)

    sheet = n + '_accc'
    overwritesheet = True

    baseflowvio = False
    basevoltvio = False
    flowlimit   = 0.0
    flowchange  = 0.0
    voltchange  = 0.0
    branchanglediff = True
    angdifmin=0.05

    pssexcel.accc(accfile,string,colabel=colabel,xlsfile=xlsfile,sheet=sheet,overwritesheet=overwritesheet,show=show,
                  baseflowvio=baseflowvio, basevoltvio=basevoltvio, flowlimit=flowlimit,
                  flowchange=flowchange, voltchange=voltchange, angdifmin=angdifmin, cosep=cosep, branchanglediff=branchanglediff)

# ====================================================================================================

def pv(pvfile='savnw.pv', outpath=None, show=True):
    import pssexcel

    if not os.path.exists(pvfile):
        prgmsg = " Error: Input pvfile '{0}' does not exist".format(pvfile)
        print(prgmsg)
        return

    # Change these values as required.
    string  = ['s','v','m','g','l','b','i']
    colabel = [] #'base case', 'trip1nuclear', 'trip2nuclear']

    p, nx = os.path.split(pvfile)
    n, x  = os.path.splitext(nx)

    xlsfile = get_output_filename(outpath, 'pssexcel_demo_pv_' + n)

    sheet = n + '_pv'
    overwritesheet = True

    pssexcel.pv(pvfile,string,colabel=colabel,xlsfile=xlsfile,sheet=sheet,overwritesheet=overwritesheet,show=show)

# ====================================================================================================

def qv(qvfile='savnw.qv', outpath=None, show=True):
    import pssexcel

    if not os.path.exists(qvfile):
        prgmsg = " Error: Input qvfile '{0}' does not exist".format(qvfile)
        print(prgmsg)
        return

    # Change these values as required.
    string  = ['s','v','m','g']
    colabel = [] #'base case', 'trip1nuclear', 'trip2nuclear']

    p, nx = os.path.split(qvfile)
    n, x  = os.path.splitext(nx)

    xlsfile = get_output_filename(outpath, 'pssexcel_demo_qv_' + n)

    sheet = n + '_qv'
    overwritesheet = True

    pssexcel.qv(qvfile,string,colabel=colabel,xlsfile=xlsfile,sheet=sheet,overwritesheet=overwritesheet,show=show)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':
    pass
    # change XX to 33, 34 or 35.
    #import psseXX

    #accc(accfile)
    #pv(pvfile)
    #qv(qvfile)

# ====================================================================================================

