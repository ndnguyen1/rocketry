# qv_export.py  Exporting QV Solution Results to Excel Spreadsheet
# ====================================================================================================
'''
This is an example file showing how to export PV solution results to excel spreadsheets.

Refer help(arrbox.qv_pp) for details.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call any of the function as below
    excel_report()
    excel_report(qvfile='savnw.qv', show=True)

    text_report()
    text_report(qvfile='savnw.qv')

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

def excel_report(qvfile='savnw.qv', outpath=None, show=True):
    import pssexcel

    if not os.path.exists(qvfile):
        prgmsg = " Error: Input qvfile '{0}' does not exist".format(qvfile)
        print(prgmsg)
        return

    # Change these values as required.
    string  = ['s','v','m','g']
    colabel = [] #['base case', 'trip1nuclear', 'trip2nuclear']

    p, nx = os.path.split(qvfile)
    n, x  = os.path.splitext(nx)

    xlsfile = get_output_filename(outpath, 'qv_export_' + n)

    sheet = n + '_qv'
    overwritesheet = True

    pssexcel.qv(qvfile,string,colabel=colabel,xlsfile=xlsfile,sheet=sheet,overwritesheet=overwritesheet,show=show)

# ====================================================================================================

def text_report(qvfile='savnw.qv', outpath=None):

    import arrbox.qv_pp

    if not os.path.exists(qvfile):
        prgmsg = " Error: Input qvfile '{0}' does not exist".format(qvfile)
        print(prgmsg)
        return

    qvobj = arrbox.qv_pp.QV_PP(qvfile)

    p, nx = os.path.split(qvfile)
    n, x  = os.path.splitext(nx)

    smryfile = get_output_filename(outpath, 'qv_export_' + n +'_summary.txt')
    solnfile = get_output_filename(outpath, 'qv_export_' + n +'_solution.txt')

    ierr = qvobj.summary_report(smryfile)

    ierr = qvobj.solution_report(colabels=None,rptfile=solnfile)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':

    import psse35

    #excel_report()
    #text_report()
    #excel_report(qvfile='savnw.qv', show=True)
    #text_report(qvfile='savnw.qv')

# ====================================================================================================

