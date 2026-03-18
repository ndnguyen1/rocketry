#[otdffactors_excel.py]  OTDF FACTORS Exported to Excel Spreadsheet
# ====================================================================================================
'''
This is an example file showing how to use DFAX_PP object's method "otdf_factors" from
PSSARRAYS module to export OTDF factors to excel spreadsheet.

You need to have Win32 extensions for Python installed.
(http://sourceforge.net/projects/pywin32)

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call funtion
    otdf_excel(savfile, dfxfile, outpath, show)
    or
    otdf_excel()  <-- savnw.sav and savnw.dfx must exist in working folder.
'''
# ----------------------------------------------------------------------------------------------------

import sys, os

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

def otdf_excel(savfile='savnw.sav', dfxfile='savnw.dfx', outpath=None, show=True):

    import psspy, arrbox.dfax_pp

    import excelpy

    if not os.path.exists(savfile):
        print("\n SAV file '%s' not found." % savfile)
        return

    if not os.path.exists(dfxfile):
        print("\n DFAX file '%s' not found." % dfxfile)
        return

    p, nx = os.path.split(dfxfile)
    n, x  = os.path.splitext(nx)
    xlfile = get_output_filename(outpath, 'otdffactors_'+n)

    psspy.psseinit()

    psspy.case(savfile)

    dfxobj = arrbox.dfax_pp.DFAX_PP(dfxfile)

    otdfobj = dfxobj.otdf_factors()
    if otdfobj.ierr != 0: return

    otdfxls = excelpy.workbook(xlfile, 'OTDF FACTORS', overwritesheet=True)
    if show: otdfxls.show()
    otdfxls.show_alerts(0) # do not show pop-up alerts

    otdfxls.page_format(orientation="landscape",left=1.0,right=1.0,
                       top=0.5,bottom=0.5,header=0.25,footer=0.25)
    otdfxls.page_footer(left='page number of page total', right='date, time')
    otdfxls.page_header(center='file name:sheet name')
    otdfxls.font_sheet()

    # Report Title
    col = 1
    row = 1
    tmplst = (["OTDF Factors Report"],[dfxfile])
    bottomRow,rightCol = otdfxls.set_range(row,col,tmplst)
    otdfxls.font((1,1),fontColor='red',fontSize=14)
    otdfxls.font_color((2,1),'blue')

    row = bottomRow + 1

    tmplst = [
        otdfobj.casetitle.line1,                                       #
        otdfobj.casetitle.line2,                                       #
        ''
        'Saved Case file              = %s' % otdfobj.file.sav,         #
        'DFAX file                    = %s' % otdfobj.file.dfx,         #
        'Subsystem file               = %s' % otdfobj.file.sub,         #
        'Monitored Element file       = %s' % otdfobj.file.mon,         #
        'Contingency Description file = %s' % otdfobj.file.con,         #
        ]

    bottomRow,rightCol = otdfxls.set_range(row,col,tmplst,transpose=True)
    row = bottomRow + 2 # one blank row

    txt = "'*** OTDF Contingency Description ***"
    otdfxls.set_cell((row,col),txt,fontStyle="Bold",fontSize=12, fontColor="red")
    row = row + 1

    tmplst=[]
    for i in range(otdfobj.size.ncase):
        lbl  = otdfobj.colabel[i]
        desc = otdfobj.codesc[i]
        tmplst.append([lbl,desc])
    bottomRow,rightCol = otdfxls.set_range(row,col,tmplst)
    otdfxls.align((row,col,bottomRow,col),'right')
    otdfxls.font_color((row,col,bottomRow,col),'dgreen')

    row = bottomRow + 2 # one blank row

    txt = "'*** OTDF Factors ***"
    otdfxls.set_cell((row,col),txt,fontStyle="Bold",fontSize=12, fontColor="red")
    row = row + 1

    tmplst=['<---------- Monitored Branch/Interface ------------->']
    for each in otdfobj.colabel:
        tmplst.append(each.strip())
    bottomRow,rightCol = otdfxls.set_range(row,col,tmplst)
    otdfxls.align((row,col,bottomRow,rightCol),'right')
    otdfxls.font_color((row,col,bottomRow,rightCol),'blue')

    row = bottomRow + 1

    tmplst=[]
    for i in range(otdfobj.size.nmline+otdfobj.size.ninter):
        tmplst.append([otdfobj.melement[i].strip()])
    bottomRow,rightCol = otdfxls.set_range(row,col,tmplst)
    otdfxls.align((row,col,bottomRow,col),'right')
    otdfxls.font_color((row,col,bottomRow,col),'dgreen')

    col = rightCol + 1
    bottomRow,rightCol = otdfxls.set_range(row,col,otdfobj.factor,transpose=True,numberFormat='0.0000')

    otdfxls.width((1,1),53)
    otdfxls.width((1,2,1,rightCol),12)

    # ------------------------------------------------------------------------------------------------
    # Save the workbook and close the Excel application
    xlfile = otdfxls.save(xlfile)

    if not show:
        otdfxls.close()
        txt = '\n OTDF Factors saved to file %s\n' % xlfile
        sys.stdout.write(txt)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':

    import psse35
    otdf_excel()
    # OR
    #otdf_excel(savfile, dfxfile, outpath, show)


# ====================================================================================================
