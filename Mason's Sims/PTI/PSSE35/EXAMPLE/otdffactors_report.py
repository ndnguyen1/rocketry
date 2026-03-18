#[otdffactors_report.py]  OTDF FACTORS REPORT
# ====================================================================================================
'''
This is an example file showing how to use DFAX_PP object's method "otdf_factors" from
PSSARRAYS module to generate OTDF factors report.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call funtion
    otdf_report(savfile, dfxfile, outpath, show)
    or
    otdf_report()  <-- savnw.sav and savnw.dfx must exist in working folder.
'''

# ----------------------------------------------------------------------------------------------------

import sys, os, time

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

def otdf_report(savfile='savnw.sav', dfxfile='savnw.dfx', outpath=None):

    import psspy, arrbox.dfax_pp

    if not os.path.exists(savfile):
        print("\n SAV file '%s' not found." % savfile)
        return

    if not os.path.exists(dfxfile):
        print("\n DFAX file '%s' not found." % dfxfile)
        return

    p, nx = os.path.split(dfxfile)
    n, x  = os.path.splitext(nx)
    rptfile = get_output_filename(outpath, 'otdffactors_'+n+'.txt')

    psspy.psseinit()

    psspy.case(savfile)

    dfxobj = arrbox.dfax_pp.DFAX_PP(dfxfile)
    otdfobj = dfxobj.otdf_factors()
    if otdfobj.ierr != 0: return

    rptfile_h = open(rptfile,'w')
    report    = rptfile_h.write

    # (0) Report title
    ttl_hline = '*' + 46* ' *' + '\n\n'
    ttl       = 30*' ' + "OTDF Factors Report" + "\n"
    ttl_file  = 30*' ' + otdfobj.file.dfx + "\n"
    ttl_time  = 30*' ' + time.ctime() + "\n\n"
    report(ttl_hline)
    report(ttl)
    report(ttl_file)
    report(ttl_time)
    report(ttl_hline)

    report('%s\n' % otdfobj.casetitle.line1)
    report('%s\n' % otdfobj.casetitle.line2)
    report('\n')

    report('Saved Case file              = %s\n' % otdfobj.file.sav)
    report('DFAX file                    = %s\n' % otdfobj.file.dfx)
    report('Subsystem file               = %s\n' % otdfobj.file.sub)
    report('Monitored Element file       = %s\n' % otdfobj.file.mon)
    report('Contingency Description file = %s\n' % otdfobj.file.con)
    report('\n')

    report('*** OTDF Contingency Description ***\n')
    for i in range(otdfobj.size.ncase):
        lbl  = otdfobj.colabel[i]
        desc = otdfobj.codesc[i]
        report("  %(lbl)12s  %(desc)s\n" %vars())

    report("\n")
    report('*** OTDF Factors ***\n')
    report('  <---------- Monitored Branch/Interface ------------->  ')
    for each in otdfobj.colabel:
        report("%12s  " %each.strip())
    report("\n")
    for i in range(otdfobj.size.nmline+otdfobj.size.ninter):
        report("  %52s  " % otdfobj.melement[i].strip())
        for j in range(otdfobj.size.ncase):
            report("%12.6f  " % otdfobj.factor[j][i])
        report("\n")

    # ------------------------------------------------------------------------------------------------
    rptfile_h.close()
    txt = '\n OTDF Factors saved to file %s\n' % rptfile
    sys.stdout.write(txt)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':

    import psse35
    otdf_report()
    # OR
    #otdf_report(savfile, dfxfile, outpath)

# ====================================================================================================
