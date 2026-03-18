#[excelpy_howto_qv_export.py]  Get QV solution and Export to Excel using excelpy Module
# ====================================================================================================
'''
This is an example file showing how to use excelpy Module to populate Excel Spreadsheets.
As an example, here PSSE QV solution is exported to Excel.

Get more info on as:
    help(arrbox.qv_pp.QV_PP)
    help(excelpy)

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psseXX
    where XX is PSSE version number like 34, 35, 3500, 3501.
    
- call funtion
    run_export(qvfile)
    or
    run_export(qvfile, overwritesheet=True, show=True, outpath=os.getcwd())

Excel file is saved to a file name derived from qvfile name.
'''

import os

shtlst = ['bus voltage', 'summary', 'generator dispatch', 'mismatch']

# ====================================================================================================
def qv_summary(xlsobj,sheet,smry):
    '''
    Use this to create ->
    QV worksheet: 'Summary'
    '''
    xlsobj.set_active_sheet(sheet)
    row, col = 1, 1
    xlsobj.set_cell((row,col),"QV SOLUTION RESULTS",fontStyle="bold",fontSize=14, fontColor="blue")

    tmplst=[
        smry.casetitle.line1,
        smry.casetitle.line2,
        'QV output file                             = %s' % smry.file.qv,
        'Saved Case file                            = %s' % smry.file.sav]

    if smry.file.thr:
        tmplst.append('Load throwover file                        = %s' % smry.file.thr)

    tlst = [
        'DFAX file                                  = %s' % smry.file.dfx,
        'Subsystem file                             = %s' % smry.file.sub,
        'Monitored Element file                     = %s' % smry.file.mon,
        'Contingency Description file               = %s' % smry.file.con]

    tmplst.extend(tlst)

    if smry.file.inl:
        tmplst.append('Inertia and Governor Response file         = %s' % smry.file.inl)
    if smry.file.zip:
        tmplst.append('Incremental Save Case Archive file         = %s' % smry.file.zip)

    tlst = [
        ' ',                                                                       # blank row
        'Number of Contingencies+Base Case          = %d' % smry.qvsize.ncase,
        'Number of Monitored Generators(Plants)     = %d' % smry.qvsize.nmgnbus,
        'Number of Voltage Monitored Buses          = %d' % smry.qvsize.nmvbus,
        'Number of Voltage Monitored Records        = %d' % smry.qvsize.nmvrec,
        'Number of maximum voltage setpoint changes = %d' % smry.qvsize.nmxvstp,
        ]

    tmplst.extend(tlst)

    row_optn_ttl = len(tmplst) + 2 + 2 # 2 for top title+blank row and 2 for blank row+opt ttl
    jnklst=[' ', 'QV Solution Options:']
    for i in range(len(smry.options)):
        j=smry.options[i]
        ti=str(i+1).rjust(2)
        tj=str(j)
        t1=arrbox.qv_pp._QV_INT_OPTIONS_NAMES[i]
        if (i+1)==arrbox.qv_pp._QV_INT_OPTIONS_STUDY_BUS_INDEX:
            jnklst.append("option(%(ti)s): %(t1)s =%(tj)s" % vars())
        else:
            t2=arrbox.qv_pp._QV_INT_OPTIONS_LIST[i][j]
            jnklst.append("option(%(ti)s): %(t1)s =%(tj)s =%(t2)s" % vars())

    tmplst.extend(jnklst)
    row_vals_ttl = len(tmplst) + 2 + 2 # 2 for top title+blank row and 2 for blank row+val ttl

    jnklst=[' ', 'QV Solution Values:']
    for i in range(len(smry.realvalues)):
        ti=str(i+1)
        tn=arrbox.qv_pp._QV_REAL_VALUES_NAMES[i]
        tv="%g" % smry.realvalues[i]
        jnklst.append("value(%(ti)s): %(tn)s =%(tv)s" % vars())

    tmplst.extend(jnklst)
    del jnklst

    row += 2
    bottomRow,rightCol = xlsobj.set_range(row,col,tmplst,transpose=True)
    xlsobj.font_color((row,col,row+1,col),'brown')
    xlsobj.font_color((row_optn_ttl,col),'red')
    xlsobj.font_color((row_vals_ttl,col),'red')

    if smry.qvsize.ncase:
        row = bottomRow+2
        xlsobj.set_cell((row,col),"QV Contingencies",fontStyle="Bold",fontSize=12, fontColor="red")

        conlst = [['CON#', 'LABEL', 'Min Vstp', 'Max Vstp', 'Min MVAR', 'Max MVAR',
                   'Max Mismatch', 'DESCRIPTION']]
        # determine rows for which QV is failed maxmsm>smry.realvalues[0]
        rfrm = row+1
        rto  = row+1
        failrows = []
        for i in range(smry.qvsize.ncase):
            rfrm += 1
            rto  += 1
            if i==0:
                srnum = ' '
            else:
                srnum = str(i)
            nam  = smry.colabel[i]
            minvstp = smry.minvstp[i]
            maxvstp = smry.maxvstp[i]
            minmvar = smry.minmvar[i]
            maxmvar = smry.maxmvar[i]
            maxmsm  = smry.maxmsm[i]
            for j in range(len(smry.codesc[i])):
                dsc = smry.codesc[i][j]
                if j==0:
                    conlst.append([srnum,nam,minvstp,maxvstp,minmvar,maxmvar,maxmsm,dsc])
                else:
                    conlst.append(['' ,'' ,'' ,'' ,'' ,'' ,'' ,dsc])
                    rto += 1
            if maxmsm>smry.realvalues[0]:
                failrows.append([rfrm, rto])
            else:
                failrows.append([0, 0])
            rfrm = rto

        row += 1
        bottomRow,rightCol = xlsobj.set_range(row,col,conlst)
        xlsobj.font_color((row,col,row,rightCol), "dgreen")
        xlsobj.font((row,col+2,bottomRow,col+3),numberFormat='0.00')  # Min Vstp and Max Vstp
        xlsobj.font((row,col+4,bottomRow,col+6),numberFormat='0.000') # Min MVAR, Max MVAR and Max MSM
        xlsobj.align((row,col),'right')
        xlsobj.font((row,col,row,rightCol),fontStyle=('Bold',))
        xlsobj.autofit_columns((row,col+1,row,rightCol))
        for each in failrows:
            r1 = each[0]
            r2 = each[1]
            if r1 and r2:
                xlsobj.font((r1,col,r2,rightCol),fontColor="cyan",fontStyle='bold')
    else:
        xlsobj.set_cell((row,col),"No Contingencies..",fontStyle="Bold",fontSize=12, fontColor="red")

# ====================================================================================================
def qv_mismath(xlsobj,sheet,lbl,ttl,row,rowttl,mwtransfer,mvaworst,mvatotal,cnvflag,cnvcond):
    '''
    Use this to create ->
    QV worksheet: 'Mismatch'
    '''
    
    # assemble data in columns: 1st=MW Transfer, 2nd=MVAWORST and 3rd=MVATOTAL
    contitle = 'CONTINGENCY: ' + lbl.strip() + 5*' ' + ttl # Contingency Label
    cnvyesno = []
    noclns   = []
    i = 1
    for each in cnvflag:
        i += 1
        if each:
            cnvyesno.append('YES')
            noclns.append(0)
        else:
            cnvyesno.append('NO')
            noclns.append(i)

    tmplst = [ rowttl ]
    for i in range(len(mwtransfer)):
        tmplst.append([mwtransfer[i],mvaworst[i],mvatotal[i],cnvyesno[i],cnvcond[i]])

    xlsobj.set_active_sheet(sheet)
    col = 1
    # added 1 to row in violation check for 'contitle' row
    xlsobj.set_cell((row,col+1),contitle,fontStyle='bold',fontSize=12,fontColor="dgreen")
    row += 1
    bottomRow,rightCol = xlsobj.set_range(row,col,tmplst,transpose=True,numberFormat="0.00000")
    xlsobj.font((row,col,row,rightCol),fontColor="red",fontStyle='bold',numberFormat="0.000")
    xlsobj.align((row,col,row,rightCol),'h_center')
    xlsobj.align((row+3,col,row+3,rightCol),'h_center')
    xlsobj.align((row,col,bottomRow,col),'right')
    xlsobj.font((row+1,col,bottomRow,col),fontColor="blue",fontStyle='bold')
    for each in noclns:
        if each:
            xlsobj.font((row+3,each,bottomRow,each),fontColor="cyan",fontStyle='bold')

    row = bottomRow + 2 # one blank row

    return row

# ====================================================================================================
def qv_one(xlsobj,sheet,lbl,ttl,row,rowttl,mwtransfer,solnvalue,options,cnvflag=[]):
    '''
    Use this to create ->
    QV worksheets: 'Bus Voltage', 'Generator Dispatch'
    '''

    contitle = 'CONTINGENCY: ' + lbl.strip() + 5*' ' + ttl # Contingency Label
    namesplit = options[0]
    nttlclns  = options[1]
    transpose = options[2]

    # determine non-converged solution columns
    noclns = []
    i = nttlclns
    for each in cnvflag:
        i += 1
        if each:
            noclns.append(0)
        else:
            noclns.append(i)

    # assemble data in columns: 1st=MW Transfer, rest=solution values
    t = []
    for i in range(len(mwtransfer)):
        t1 = list(solnvalue[i])
        t1.insert(0,mwtransfer[i])
        t.append(t1)
        
    tmplst = t
    tmplst.insert(0,rowttl)
    xlsobj.set_active_sheet(sheet)
    col = 1
    xlsobj.set_cell((row,col+nttlclns),contitle,fontStyle='bold',fontSize=12,fontColor="dgreen")
    row += 1
    bottomRow,rightCol = xlsobj.set_range(row,col,tmplst,transpose=transpose)
    xlsobj.font((row,col+nttlclns-1,row,rightCol),fontColor="red",fontStyle='bold')
    xlsobj.font((row,col+nttlclns,bottomRow,rightCol),numberFormat="0.000")
    xlsobj.align((row,col,row,rightCol),'h_center')
    if namesplit: xlsobj.merge((row,col,row,nttlclns))
    xlsobj.align((row,col),'right')
    xlsobj.font((row+1,col,bottomRow,nttlclns),fontColor="blue",fontStyle='bold')
    for each in noclns:
        if each:
            xlsobj.font((row+1,each,bottomRow,each),fontColor="cyan")
    row = bottomRow + 2 # one blank row

    return row

# ====================================================================================================

def run_export(qvfile, overwritesheet=True, show=True, outpath=os.getcwd()):
    import arrbox.qv_pp
    import excelpy
    
    if not os.path.exists(qvfile):
        msgstr = " Error - QV file does not exist, no export.\n     {}." .format(qvfile)
        print(msgstr)
        return
        
    p, nx = os.path.split(qvfile)
    xlnam, x = os.path.splitext(nx)
    xlnam = "{}_qv".format(xlnam)
    xlsfile = os.path.join(outpath, xlnam)

    # -----------------------------------------------------------
    xlsobj = excelpy.workbook(xlsfile, shtlst[0], overwritesheet=overwritesheet)
    if show:
        xlsobj.show()
    else:
        xlsobj.hide()

    xlsobj.show_alerts(0) # do not show pop-up alerts
    xlsfnam = xlsobj.XLSFNAM

    for shtnam in shtlst[1:]:
        xlsobj.worksheet_add_end(shtnam, overwritesheet=overwritesheet)
    
    xlsobj.page_format(orientation="landscape",left=1.0,right=1.0,
                       top=0.5,bottom=0.5,header=0.25,footer=0.25)
    xlsobj.page_footer(left='page number of page total', right='date, time')
    xlsobj.page_header(center='file name:sheet name')
    xlsobj.font_sheet()

    # -----------------------------------------------------------
    # Retrive QV data
    qvobj = arrbox.qv_pp.QV_PP(qvfile)
    smry = qvobj.summary()

    qv_summary(xlsobj, 'summary', smry)

    row_msm = 1
    msmlabel = ['VOLTAGE SETPOINT->', 'LARGEST MVA MISMATCH', 'TOTAL MVA MISMATCH', 'CONVERGED', 'CONVERGE CONDITION']

    row_vlt = 1
    options_vlt = [False,1,True]
    mvbuslabel = list(smry.mvbuslabel)
    mvbuslabel.insert(0,'VOLTAGE SETPOINT->')

    row_gen = 1
    options_gen = [False,1,True]
    mgenbuslabel = list(smry.mgenbus)
    mgenbuslabel.insert(0,'VOLTAGE SETPOINT->')
    
    ret_ierr = 0
    for lbl in smry.colabel:
        soln = qvobj.solution(lbl)
        if soln==None: continue                 # contingency solution not found, move to next
        if soln.ierr !=0: ret_ierr = soln.ierr  # return any non-zero ierr

        row_msm = qv_mismath(xlsobj, 'mismatch',lbl,'Mismatch (MVA)',
                             row_msm,msmlabel,soln.vsetpoint,soln.mvaworst,soln.mvatotal,
                             soln.cnvflag, soln.cnvcond)
        
        row_vlt = qv_one(xlsobj,'bus voltage',lbl,'Voltage (pu)',
                         row_vlt,mvbuslabel,soln.vsetpoint,soln.volts,options_vlt,soln.cnvflag)

        row_gen = qv_one(xlsobj,'generator dispatch',lbl,'Plant (MVAR)',
                         row_gen,mgenbuslabel,soln.vsetpoint,soln.mgenmvar,options_gen,soln.cnvflag)

    # --------------------------------------
    # Format worksheets
    xlsobj.autofit_columns((1,1),'mismatch')
    xlsobj.autofit_columns((1,1),'bus voltage')
    xlsobj.autofit_columns((1,1),'generator dispatch')

    if show: xlsobj.set_active_sheet('bus voltage')
    
    # -----------------------------------------------------------
    # Save the workbook and close the Excel application
    xlsfile = xlsobj.save()

    if not show:
        xlsobj.close()
        msgstr = "\n Done ...QV Export saved to file:\n     {}." .format(xlsfnam)
        print(msgstr)

# ====================================================================================================
if (__name__ == "__main__"):
    pass
    # Change appropriately 'psseXX' and 'qvfile' values below.
    import psseXX
    qvfile = "savnw.qv"
    run_export(qvfile, overwritesheet=True, show=True)
    
