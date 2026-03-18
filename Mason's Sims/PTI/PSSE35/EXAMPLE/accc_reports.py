#[accc_reports.py]  GET ACCC SOLUTION IN ARRAYS and CREATE CUSTOM REPORTS
# ====================================================================================================
'''
This is an example file showing how to use ACCC Solution Array fetch APIs
from Python to generate custom accc solution reports.

Following ACCC solutions can be retrieved:
    - post-contingency solution,
    - post-tripping solution, or
    - post-corrective action solution

These ACCC solutions can be obtained in Python lists for:
    - single contingency,
    - multiple contingencies, or
    - all contingencies

The APIs used in this program are part of python "arrbox.accc_pp" module.
    accobj = arrbox.accc_pp.CONTINGENCY_PP(accfile)
    Following methods are defined for accobj.
    - accobj.summary and accobj.solution methods return ACCC solution
      in python object, which can be used to create custom reports, or
    - accobj.summary_report, accobj.solution_report or accobj.violations_report
      methods can be used to get pre-defined reports.

Get more info on as:
    help(arrbox.accc_pp.CONTINGENCY_PP)

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call funtion
    run_accc_reports()
    You may want to change input arguments when you call this function.
    run_accc_reports(accfile, rptfile)
    
---------------------------------------------------------------------------------
Alternatively, use either of the following menu items to export ACCC file output to Excel.
- from Windows Start>Programs>PSSExx>Export Results to Excel OR
- from PSSE GUI, Power Flow>Reports>Export Results to Excel
'''
# ----------------------------------------------------------------------------------------------------

import sys, os, random, time

# ----------------------------------------------------------------------------------------------------

def create_accc_reports(accfile, rptfile):

    import psspy, arrbox.accc_pp

    if not os.path.exists(accfile):
        prgmsg = " Error: Input accfile '{0}' does not exist".format(accfile)
        print(prgmsg)
        return

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

        rptfpath, rptext = os.path.splitext(rptfile)

    # ----------------------------------------------------------------------------------------------------
    # common variables values (assumed)
    busmsm    = 0.5
    sysmsm    = 5.0
    rating    = 'a'
    flowlimit = 80.0
    stype_cnt = 'contingency'
    stype_trp = 'tripping'
    stype_cact= 'caction'

    # ----------------------------------------------------------------------------------------------------
    # (1) Create object
    accobj = arrbox.accc_pp.CONTINGENCY_PP(accfile)
    if accobj.ierr:
        prgmsg = " Error {0:d} creating 'accobj'.".format(accobj.ierr)
        print(prgmsg)
        return

    # ----------------------------------------------------------------------------------------------------
    # (2) ACCC summary report
    sumfile = None
    if rptfile:  sumfile = rptfpath + '_summary' + rptext
    accobj.summary_report(rptfile=sumfile)

    # ----------------------------------------------------------------------------------------------------
    # (3) ACCC post contingency solution report
    accobj.solution_options(stype=stype_cnt,busmsm=busmsm,sysmsm=sysmsm,rating=rating,flowlimit=flowlimit)
    cntsolnfile = None
    if rptfile:  cntsolnfile = rptfpath + '_solution_cnt' + rptext
    accobj.solution_report(colabels=None,rptfile=cntsolnfile)

    # ----------------------------------------------------------------------------------------------------
    # (4) ACCC post tripping solution report
    trpsolnfile = None
    if rptfile:  trpsolnfile = rptfpath + '_solution_trp' + rptext
    accobj.solution_options(stype=stype_trp)    # changed only solution type, other options remain same
    accobj.solution_report(colabels=None,rptfile=trpsolnfile)

    # ----------------------------------------------------------------------------------------------------
    # (5) ACCC post corrective action solution report
    cactsolnfile = None
    if rptfile:  cactsolnfile = rptfpath + '_solution_cact' + rptext
    accobj.solution_options(stype=stype_cact)    # changed only solution type, other options remain same
    accobj.solution_report(colabels=None,rptfile=cactsolnfile)

    # ----------------------------------------------------------------------------------------------------
    # (6) ACCC post contingency violations report
    cntviofile = None
    if rptfile:  cntviofile = rptfpath + '_violations_cnt' + rptext
    accobj.solution_options(stype=stype_cnt)
    accobj.violations_report(rptfile=cntviofile)

    # ----------------------------------------------------------------------------------------------------
    # (7) ACCC post tripping violations report
    trpviofile = None
    if rptfile:  trpviofile = rptfpath + '_violations_trp' + rptext
    accobj.solution_options(stype=stype_trp)
    accobj.violations_report(rptfile=trpviofile)

    # ----------------------------------------------------------------------------------------------------
    # (8) ACCC post corrective action violations report
    cactviofile = None
    if rptfile:  cactviofile = rptfpath + '_violations_cact' + rptext
    accobj.solution_options(stype=stype_cact)
    accobj.violations_report(rptfile=cactviofile)

    # ----------------------------------------------------------------------------------------------------
    # (9) Getting summary arrays and printing contingency lables in PSS(R)E progress window
    smryobj = accobj.summary()
        # note: returned "smryobj" is used in the following (10) to (16) examples of this program.
    psspy.progress('\n Contingency Labels:\n')
    for each in smryobj.colabel:
        psspy.progress('    '+each+'\n')

    # ----------------------------------------------------------------------------------------------------
    # (10) Getting solution arrays for one contingency and printing monitored element MVA and AMP flows
    #      in PSS(R)E progress window
    idx   = random.sample(list(range(len(smryobj.colabel))),1)   # select one contingency randomly
    colbl = smryobj.colabel[idx[0]]
    accobj.solution_options(stype=stype_cnt)
    solnobj  = accobj.solution(colabel=colbl)
    if solnobj!=None:        # contingency solution found/error, proceed
        rating = rating.strip().lower()
        try:
            rate = smryobj.rating.rating
        except:
            rate = smryobj.rating.a

        psspy.progress("\n Monitored Element Flows for contingency '%12s':\n" % colbl)
        psspy.progress("<-----------------MONITORED ELEMENT------------------> <RATING> <MVAFLOW> \
    <AMPFLOW> <PCTFLOW>\n")
        for i in range(len(solnobj.mvaflow)):
            elmt    = "%54s" % smryobj.melement[i]
            mvaflow = "%9.2f" % solnobj.mvaflow[i]
            if i < smryobj.acccsize.nmline:
                ampflow = "%9.2f" % solnobj.ampflow[i] # AMP flow exists for nmlines only.
                pctflow = abs(solnobj.ampflow[i])
            else:
                ampflow = 9*' '                 # for interfaces, no AMP flow
                pctflow = abs(solnobj.mvaflow[i])  # for interfaces, MVA rating to be considered

            if rate[i]:
                elmt_rate = "%8.2f" % rate[i]
                pctflow   = "%9.2f" % (pctflow*100.0/rate[i])
            else:   # if rating is not provided, don't calculate %flow
                elmt_rate = 8*' '
                pctflow   = 9*' '

            txtstr = "%(elmt)s %(elmt_rate)s %(mvaflow)s %(ampflow)s %(pctflow)s \n" %vars()
            psspy.progress(txtstr)

    # ----------------------------------------------------------------------------------------------------
    # (11) Getting solution arrays for three contingency and printing monitored element MVA and AMP flows
    #      in PSS(R)E progress window for converged contingencies

    # select upto maximum of 3 contingencies randomly
    idx    = random.sample(list(range(len(smryobj.colabel))),min(len(smryobj.colabel),3))
    colbls = [smryobj.colabel[x] for x in idx]

    rating = rating.strip().lower()
    try:
        rate = smryobj.rating.rating
    except:
        rate = smryobj.rating.a

    for lbl in colbls:
        solnobj  = accobj.solution(colabel=lbl)
        if solnobj==None: continue          # contingency solution not found, move to next
        if not solnobj.cnvflag: continue    # contingency solution not converged, move to next
        psspy.progress("\n Monitored Element Flows for contingency '%12s':\n" % lbl)
        psspy.progress("<-----------------MONITORED ELEMENT------------------> <RATING> <MVAFLOW> \
<AMPFLOW> <PCTFLOW>\n")
        for i in range(len(solnobj.mvaflow)):
            elmt    = "%54s" % smryobj.melement[i]
            mvaflow = "%9.2f" % solnobj.mvaflow[i]

            if i < smryobj.acccsize.nmline:
                ampflow = "%9.2f" % solnobj.ampflow[i] # AMP flow exists for nmlines only.
                pctflow = abs(solnobj.ampflow[i])
            else:
                ampflow = 9*' '                 # for interfaces, no AMP flow
                pctflow = abs(solnobj.mvaflow[i])  # for interfaces, MVA rating to be considered

            if rate[i]:
                elmt_rate = "%8.2f" % rate[i]
                pctflow   = "%9.2f" % (pctflow*100.0/rate[i])
            else:   # if rating is not provided, don't calculate %flow
                elmt_rate = 8*' '
                pctflow   = 9*' '

            txtstr = "%(elmt)s %(elmt_rate)s %(mvaflow)s %(ampflow)s %(pctflow)s \n" %vars()
            psspy.progress(txtstr)
        psspy.progress('\n')

    # ----------------------------------------------------------------------------------------------------
    # (12) Creating Overload report (similar to PSS(R)E ACCC Spreadsheet Overload Report) in
    #      PSS(R)E progress window

    rating = rating.strip().lower()
    try:
        rate = smryobj.rating.rating
    except:
        rate = smryobj.rating.a

    psspy.progress("\n OVERLOAD Report\n")
    for lbl in smryobj.colabel:
        solnobj  = accobj.solution(colabel=lbl)
        if solnobj==None: continue         # contingency solution not found, move to next
        if not solnobj.cnvflag: continue   # contingency solution not converged, move to next
        psspy.progress(" Monitored Element Flows above %g%% for contingency '%12s':\n" % (flowlimit,lbl))
        psspy.progress("<-----------------MONITORED ELEMENT------------------> <RATING> <MVAFLOW> \
<AMPFLOW> <PCTFLOW>\n")
        for i in range(len(solnobj.mvaflow)):
            elmt    = "%54s" % smryobj.melement[i]
            mvaflow = "%9.2f" % solnobj.mvaflow[i]

            if i < smryobj.acccsize.nmline:
                ampflow = "%9.2f" % solnobj.ampflow[i] # AMP flow exists for nmlines only.
                pctflow = abs(solnobj.ampflow[i])
            else:
                ampflow = 9*' '                 # for interfaces, no AMP flow
                pctflow = abs(solnobj.mvaflow[i])  # for interfaces, MVA rating to be considered

            if rate[i]:
                elmt_rate = "%8.2f" % rate[i]
                pctflow_v = pctflow*100.0/rate[i]
                pctflow   = "%9.2f" % (pctflow*100.0/rate[i])
            else:   # if rating is not provided, don't calculate %flow
                elmt_rate = 8*' '
                pctflow   = 9*' '
                pctflow_v = 0

            if pctflow_v >= flowlimit:
                psspy.progress("%(elmt)s %(elmt_rate)s %(mvaflow)s %(ampflow)s %(pctflow)s \n" %vars())
        psspy.progress('\n')

    # ----------------------------------------------------------------------------------------------------
    # (13) Creating Voltage Violations report in Text file, if provided

    if rptfile:  sumfile = rptfpath + '_summary' + rptext
    if rptfile:
        vviofpath, vviofext = os.path.splitext(rptfile)
        if not vviofext: vviofext = '.txt'
        vviofile   = vviofpath + '_vvio' + vviofext
        vviofile_h = open(vviofile,'w')
        report     = vviofile_h.write
    else:
        psspy.beginreport()
        report = psspy.report

    report("\n Post Contingency VOLTAGE VIOLATIONS Report\n")

    # get base case solution
    solnobj_basecase = accobj.solution(colabel="BASE CASE")

    if solnobj_basecase==None or not solnobj_basecase.cnvflag:
        report("    BASE CASE not converged\n")
    else:
        # remaining contingencies
        for lbl in smryobj.colabel[1:]:   # skipped "BASE CASE"
            solnobj  = accobj.solution(colabel=lbl)
            if solnobj==None: continue          # contingency solution not found, move to next
            if not solnobj.cnvflag: continue    # contingency solution not converged, move to next
            vvio_exists = False
            for r in range(len(solnobj.volts)):
                if solnobj.volts[r] == 0.0: continue # disconnected bus, move to next
                if smryobj.mvrectype[r]=='RANGE':
                    if smryobj.mvrecmin[r] and solnobj.volts[r] < smryobj.mvrecmin[r]:
                        vvio = solnobj.volts[r] - smryobj.mvrecmin[r]
                    elif smryobj.mvrecmax[r] and solnobj.volts[r] > smryobj.mvrecmax[r]:
                        vvio = solnobj.volts[r] - smryobj.mvrecmax[r]
                    else:
                        vvio = 0
                else: # DEVIATION
                    delta = solnobj.volts[r] - solnobj_basecase.volts[r]
                    if delta < 0:
                        if smryobj.mvrecmin[r] and abs(delta) > smryobj.mvrecmin[r]:
                            vvio =  delta + smryobj.mvrecmin[r]
                        else:
                            vvio = 0
                    else:
                        if smryobj.mvrecmax[r] and delta > smryobj.mvrecmax[r]:
                            vvio = delta - smryobj.mvrecmax[r]
                        else:
                            vvio = 0
                if vvio:
                    if not vvio_exists:
                        report(" Voltage Violations for contingency '%12s':\n" % (lbl))
                        report("<-----MONITORED BUS-----> <--MONITOR LABEL---> <--TYPE-> <-VMIN-> <-VMAX-> <-VINIT-> \
<-VOLT--> <-VVIO-->\n")
                        vvio_exists = True
                    mvbuslabel     = smryobj.mvbuslabel[r]
                    mvreclabel     = smryobj.mvreclabel[r]
                    mvrectype      = smryobj.mvrectype[r]
                    if smryobj.mvrecmin[r]:
                        mvrecmin   = "%8.5f" % smryobj.mvrecmin[r]
                    else:
                        mvrecmin   = '   --   '
                    if smryobj.mvrecmax[r]:
                        mvrecmax   = "%8.5f" % smryobj.mvrecmax[r]
                    else:
                        mvrecmax   = '   --   '
                    mvrecvolts_init= solnobj_basecase.volts[r]
                    mvrecvolts     = solnobj.volts[r]
                    report("%(mvbuslabel)25s %(mvreclabel)20s %(mvrectype)9s %(mvrecmin)s \
%(mvrecmax)s %(mvrecvolts_init)9.5f %(mvrecvolts)9.5f %(vvio)9.5f \n" %  vars())

            if vvio_exists: report('\n')

    if rptfile:
        vviofile_h.close()
        print('\n Voltage Violations Report saved to file %s' % vviofile)
    else:
        print('\n Voltage Violations Report created in Report window.')

    # ----------------------------------------------------------------------------------------------------
    # (14) Creating Post-Contingency Solution Load Shedding report in progress

    report = psspy.progress
    load_curtailment_exists = False
    report('\n Post-Contingency LOAD CURTAILMENTS Report\n')
    stype = stype_cnt
    for lbl in smryobj.colabel:
        solnobj  = accobj.solution(colabel=lbl)
        if solnobj==None: continue              # contingency solution not found, move to next
        if not solnobj.cnvflag: continue        # contingency solution not converged, move to next
        if not len(solnobj.lshedbus): continue  # no load shedding, move to next
        report("\n Load Curtailments for contingency '%12s':\n" % (lbl))
        if not load_curtailment_exists:
            if stype=='contingency' or stype=='tripping':
                report("<----------BUS----------> <LDSHED(MW)> <CONTINGENCY>\n")
            else:
                report("<----------BUS----------> <INITLD(MW)>  <LDSHED(MW)> <CONTINGENCY>\n")
            load_curtailment_exists = True

        for c in range(len(solnobj.lshedbus)):
            if stype=='contingency' or stype=='tripping':
                report("%25s %12.2f %-12s\n" % (solnobj.lshedbus[c],solnobj.loadshed[c],lbl))
            else:
                report("%25s %12.2f %12.2f %-12s\n" % (solnobj.lshedbus[c],solnobj.loadshed[0][c],
                                                       solnobj.loadshed[1][c],lbl))
    if not load_curtailment_exists:
        report('    None\n')

    # ----------------------------------------------------------------------------------------------------
    # (15) Creating Corrective Action Solution Generation Dispatch report in progress

    accobj.solution_options(stype=stype_cact)

    report = psspy.progress
    gen_disp_exists = False
    report('\n Corrective Action GENERATION DISPATCH  Report\n')

    for lbl in smryobj.colabel:
        solnobj  = accobj.solution(colabel=lbl)
        if solnobj==None: continue              # contingency solution not found, move to next
        if not solnobj.cnvflag: continue        # contingency solution not converged, move to next
        if not len(solnobj.gdispbus): continue  # no generation dispatch, move to next
        if not gen_disp_exists:
            report("<----------BUS----------> <INITGEN(MW)>  <GENDISP(MW)> <CONTINGENCY>\n")
            gen_disp_exists = True
        for c in range(len(solnobj.gdispbus)):
            report("%25s %9.2f %s %9.2f %s %-12s\n" % (solnobj.gdispbus[c],solnobj.gendisp[0][c],4*' ',
                                                      solnobj.gendisp[1][c],3*' ',lbl))

    if not gen_disp_exists:
        report('    None\n')

    # ----------------------------------------------------------------------------------------------------
    # (16) Creating Corrective Action Solution Phase Shifter Angle report in progress

    accobj.solution_options(stype=stype_cact)

    report = psspy.progress
    phsftr_exists = False
    report('\n Corrective Action PHASE SHIFTER ANGLE Report\n')

    for lbl in smryobj.colabel:
        solnobj  = accobj.solution(colabel=lbl)
        if solnobj==None: continue              # contingency solution not found, move to next
        if not solnobj.cnvflag: continue        # contingency solution not converged, move to next
        if not len(solnobj.phsftr): continue    # no generation dispatch, move to next
        if not phsftr_exists:
            report("<-------FROM BUS------------------TO BUS-----------ID> <INITANG(deg)> <NEWANG(deg)> \
<CONTINGENCY>\n")
            phsftr_exists = True
        for c in range(len(solnobj.phsftr)):
            report("%54s %9.2f %s %9.2f %s %-12s\n" % (solnobj.phsftr[c],solnobj.phsftrang[0][c],5*' ',
                                                       solnobj.phsftrang[1][c],3*' ',lbl))
    if not phsftr_exists:
        report('    None\n')

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

def run_accc_reports(accfile='savnw.acc', rptfile='accc_reports_savnw.txt'):

    rptfile  = check_psse_example_folder(rptfile)
    
    create_accc_reports(accfile, rptfile)

# ====================================================================================================
# ====================================================================================================

if __name__ == '__main__':
    import psse35
    run_accc_reports()

# ====================================================================================================
