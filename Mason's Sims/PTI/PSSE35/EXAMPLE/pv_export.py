# pv_export.py  Exporting PV Solution Results to Excel Spreadsheet
# ====================================================================================================
'''
This is an example file showing how to export PV solution results to excel spreadsheets.

Refer help(arrbox.pv_pp) for details.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call any of the function as below
    excel_report()
    excel_report(pvfile='savnw.pv', show=True)

    text_report()
    text_report(pvfile='savnw.pv')

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

def excel_report(pvfile='savnw.pv', outpath=None, show=True):
    import pssexcel

    if not os.path.exists(pvfile):
        prgmsg = " Error: Input pvfile '{0}' does not exist".format(pvfile)
        print(prgmsg)
        return

    # Change these values as required.
    string  = ['s','v','m','g','l','b','i']
    colabel = [] #['base case', 'trip1nuclear', 'trip2nuclear']

    p, nx = os.path.split(pvfile)
    n, x  = os.path.splitext(nx)

    xlsfile = get_output_filename(outpath, 'pv_export_' + n)

    sheet = n + '_pv'
    overwritesheet = True

    pssexcel.pv(pvfile,string,colabel=colabel,xlsfile=xlsfile,sheet=sheet,overwritesheet=overwritesheet,show=show)

# ====================================================================================================

def text_report(pvfile='savnw.pv', outpath=None):

    import arrbox.pv_pp

    if not os.path.exists(pvfile):
        prgmsg = " Error: Input pvfile '{0}' does not exist".format(pvfile)
        print(prgmsg)
        return

    pvobj = arrbox.pv_pp.PV_PP(pvfile)

    p, nx = os.path.split(pvfile)
    n, x  = os.path.splitext(nx)

    smryfile = get_output_filename(outpath, 'pv_export_' + n +'_summary.txt')
    solnfile = get_output_filename(outpath, 'pv_export_' + n +'_solution.txt')

    ierr = pvobj.summary_report(smryfile)

    ierr = pvobj.solution_report(colabels=None,rptfile=solnfile)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':

    import psse35

    #excel_report()
    #text_report()
    #excel_report(pvfile='savnw.pv', show=True)
    #text_report(pvfile='savnw.pv')

# ====================================================================================================

