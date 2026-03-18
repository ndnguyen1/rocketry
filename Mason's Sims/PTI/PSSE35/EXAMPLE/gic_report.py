#[gic_report.py]    GIC Analysis in PSSE
# =====================================================================================================
'''This is an example file showing how to:
- Create GIC data file templates in Excel spreadsheets and create GIC data file from those
  Excel spredsheets
- Perform GIC analysis, post process GIC results, create customized GIC analysis reports
- Perform GIC analysis, post process GIC results, export GIC analysis results to Excel
- Map GIC results on network maps

Python module "gicdata" is used for creating GIC data files.
    See help(gicdata) for details.

Result retrival Python module "pssarrays" is converted to Python package "arrbox".
This is done to provide object access instead of function access.

Using Python package "arrbox" it is possible to create multiple objects and compare
PSSE results.

Now Python module 'pssarrays' provide aliases to modules in package "arrbox".

GIC related objects 'GIC' and 'GICMAPS' in module 'pssarrays' will work as is (that is
without any code changes in your script). However, better way to access them is from
package arrbox as shown in this script.

See detailed help on GIC related objects in arrbox as:
import arrbox.gic;help(arrbox.gic.GIC)
import arrbox.gicmaps;help(arrbox.gicmaps.GICMAPS)

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call funtion
    Run various functions from this file as desired. See notes in _run_one_test(..) (end of this file).

See function gic_results_on_network_map_custom(..) to know how you can decorate default plots with
data point annotations or any other custom settings.

---------------------------------------------------------------------------------
How to use PSSE and Python modules like numpy, matplotlib, Basemap together?
(a) In your python script, call following function before any of these modules are imported.
    psspy.set_fpcw_py()
(b) Call following function before exiting your python script.
    psspy.set_fpcw_psse()
To get details why this is needed, get help(..) on either of these functions.
Refer function gic_results_on_network_map(..) in this script for usage of these functions.
'''

# -----------------------------------------------------------------------------------------------------

import sys, os, time

# -----------------------------------------------------------------------------------------------------
# PSSE version Example folder
def get_example_folder():
    import psspy
    pn = os.path.dirname(psspy.__file__)
    p, jnk = os.path.split(pn)
    examdir = os.path.join(p, 'Example')
    return examdir

# -----------------------------------------------------------------------------------------------------

def get_output_dir(outpath):
    # if called from PSSE's Example Folder, create report in subfolder 'Output_Pyscript'

    if outpath:
        outdir = outpath
        if not os.path.exists(outdir): os.mkdir(outdir)
    else:
        outdir = os.getcwd()

    outdir = os.path.join(outdir, 'gic_report_output')
    if not os.path.exists(outdir): os.mkdir(outdir)

    return outdir

# -----------------------------------------------------------------------------------------------------

def get_output_filename(outpath, fname):

    outdir = get_output_dir(outpath)
    retvfile = os.path.join(outdir, fname)

    return retvfile

# -----------------------------------------------------------------------------------------------------

def _get_outfnam_event(pfx, efield_type, efield_mag, efield_deg, scan_storm_event):

    if efield_type=='nonuniform':
        outfnam = r"{}_{}".format(pfx, efield_type[0])
    else:
        if scan_storm_event:
            outfnam = r"{}_{}_{:g}(mag)_{:g}(deg)_{}".format(pfx, efield_type[0], efield_mag, efield_deg, scan_storm_event)
        else:
            outfnam = r"{}_{}_{:g}(mag)_{:g}(deg)".format(pfx, efield_type[0], efield_mag, efield_deg)

    return outfnam

# -----------------------------------------------------------------------------------------------------

def _get_formatted_real_value(vin):

    if vin<_BIGREL:
        rstr = "{:12.5f}".format(vin)
    else:
        rstr = "{:12s}".format(' ')

    return rstr

# -----------------------------------------------------------------------------------------------------
def _get_filenam_sfx(areas):

    if areas:
        s_lst = ["{}".format(e) for e in areas[:3]]
        s_sfx = "".join(s_lst)
    else:
        s_sfx = 'all'

    return s_sfx

# -----------------------------------------------------------------------------------------------------
def create_gicdata_template_sample(datapath=None, outpath=None, areas=[], showexcel=True):
    """ Create GIC data Excel template using sample.sav file from PSSE Example folder.
"""
    import psspy, gicdata

    f_sfx = _get_filenam_sfx(areas)

    savfile   = 'sample.sav'
    excelfile = 'gicdata_sample_template_{}'.format(f_sfx)

    if not datapath: datapath = get_example_folder()

    savfile = os.path.join(datapath, savfile)
    excelfile = get_output_filename(outpath, excelfile)

    basekv    = []
    areas     = areas
    buses     = []
    owners    = []
    zones     = []
    tielevels = 0

    psspy.psseinit()

    excelfile = gicdata.template_excel(savfile, excelfile, basekv=basekv, areas=areas, buses=buses, owners=owners, zones=zones,
                           tielevels=tielevels, showexcel=showexcel)
    return excelfile

# -----------------------------------------------------------------------------------------------------
def transfer_gicdata_sample(datapath=None, outpath=None, areas=[], showexcel=True):
    """ Transfer GIC data from .gic file into blank GIC data Excel template.
"""
    import psspy, gicdata

    f_sfx = _get_filenam_sfx(areas)

    gicfile_in   = 'sample_fv4.gic'
    tmplfile_in  = 'gicdata_sample_template_{}.xlsx'.format(f_sfx)
    excelfile_ou = 'gicdata_sample_{}.xlsx'.format(f_sfx)

    if not datapath: datapath = get_example_folder()

    gicfile_in   = os.path.join(datapath, gicfile_in)
    tmplfile_in  = get_output_filename(outpath, tmplfile_in)
    excelfile_ou = get_output_filename(outpath, excelfile_ou)

    showexcel = showexcel
    dbgout    = False
    prgfile   = None
    xlsfile = gicdata.transfer_data(gicfile_in, tmplfile_in, excelfile_ou,
                    showexcel=showexcel, prgfile=prgfile, dbgout=dbgout)

    return xlsfile

# -----------------------------------------------------------------------------------------------------
def gicdata_excel2gicfile(outpath=None, areas=[]):
    """ Create GIC data text file (.gic) from GIC data Excel file.
"""
    import gicdata

    f_sfx = _get_filenam_sfx(areas)
    excelfile = 'gicdata_sample_{}.xlsx'.format(f_sfx)
    gicfile = 'gicdata_sample_{}.gic'.format(f_sfx)

    excelfile = get_output_filename(outpath, excelfile)
    gicfile = get_output_filename(outpath, gicfile)

    gicdata.excel2gicfile(excelfile, gicfile)

    return gicfile

# -----------------------------------------------------------------------------------------------------
def gicdata_gicfile2excel(outpath=None, areas=[], showexcel=True):
    """ Create GIC data Excel file from GIC data text file (.gic).
"""
    import gicdata

    f_sfx = _get_filenam_sfx(areas)

    gicfile = 'gicdata_sample_{}.gic'.format(f_sfx)
    excelfile = 'gicdata_sample_{}(txt2xl).xlsx'.format(f_sfx)

    gicfile = get_output_filename(outpath, gicfile)
    excelfile = get_output_filename(outpath, excelfile)

    gicdata.gicfile2excel(gicfile, excelfile, showexcel=showexcel)

    return gicfile

# -----------------------------------------------------------------------------------------------------
def gicdata_merge(outpath=None, showexcel=True):
    """ Merge GIC data Excel files into one GIC data Excel file.
"""
    import gicdata

    flist = ['gicdata_sample_123.xlsx', 'gicdata_sample_456.xlsx']
    xl_list = []
    for fnam in flist:
        fou = get_output_filename(outpath, fnam)
        xl_list.append(fou)

    outxlnam   = "merged_sample.xlsx"
    prgfnam    = "merged_sample_progress.txt"

    outexcel = get_output_filename(outpath, outxlnam)
    prgfile  = get_output_filename(outpath, prgfnam)
    dbgout   = False

    #Allowed kwds: outexcel='', showexcel=False, prgfile=None, dbgout=False
    xlsfile = gicdata.merge_data_excel(*xl_list, outexcel=outexcel, showexcel=showexcel,
                                       prgfile=prgfile, dbgout=dbgout)

    return xlsfile

# -----------------------------------------------------------------------------------------------------
def run_gic_ieee_test_case(efield_mag, efield_deg, efield_type, scan_storm_event, datapath=None, outpath=None):
    """ Use IEEE GIC Test Case provided in PSSE Example folder and run GIC calculations using arrbox.gic.GIC object.
Returns results in gicboj.
"""
    import psspy
    import arrbox.gic

    savfile = 'ieee_gic_test_case.sav'
    gicfile = 'ieee_gic_test_case.gic'

    if not datapath: datapath = get_example_folder()

    savfile = os.path.join(datapath, savfile)
    gicfile = os.path.join(datapath, gicfile)

    outdir = get_output_dir(outpath)

    if efield_type=='benchmark':
        efield_mag = 8.0
    else:
        efield_mag = 1.0

    efield_deg = 0.0

    outfnam   = _get_outfnam_event("ieee", efield_type, efield_mag, efield_deg, scan_storm_event)
    prgfile   = os.path.join(outdir, outfnam+'progress.txt')
    pygicfile = os.path.join(outdir, outfnam+'_map.pygic')
    gictfile  = os.path.join(outdir, outfnam+'_gict.csv')

    ejet_million_amps = 1.0
    ejet_halfwidth_km = 200.0
    ejet_period_min   = 5.0
    ejet_height_km    = 100.0
    ejet_center_deg   = 54.0

    earth_model_name = 'shield'

    efield_unit      = 'V/km'
    substation_r     = 0.1
    branch_xbyr      = 30.0
    transformer_xbyr = 30.0
    addfile          = ''
    addfile_optn     = 'rdch'
    purgfile         = ''
    rnwkfile         = ''

    basekv    = []  # specify subsystem options
    areas     = []
    buses     = []
    owners    = []
    zones     = []
    tielevels = 0

    power_flow_optn  = ''   # specify power flow solution options
    pf_itmxn   = 100
    pf_toln    = 0.1
    pf_tap     = 0
    pf_area    = 0
    pf_phshft  = 0
    pf_dctap   = 1
    pf_swsh    = 1
    pf_flat    = 0
    pf_varlmt  = 99
    pf_nondiv  = 0

    psspy.psseinit()

    psspy.lines_per_page_one_device(1,10000000)
    psspy.progress_output(2,prgfile,[0,0])
    psspy.alert_output(2,prgfile,[0,0])

    psspy.case(savfile)
    psspy.gic_read(gicfile)
    sid = 0
    busall = 1

    # run gic analysis
    gicobj = arrbox.gic.GIC(sid, busall, efield_mag=efield_mag, efield_deg=efield_deg,
        tielevels=tielevels, study_year=0, thermal_ana_optn=-1,
        substation_r=substation_r, branch_xbyr=branch_xbyr, transformer_xbyr=transformer_xbyr,
        efield_mag_local=0.0, efield_deg_local=0.0,
        branch_rac2rdc=1.0, transformer_rac2rdc=1.0,
        efield_type=efield_type, efield_unit=efield_unit, addfile_optn=addfile_optn,
        gic2mvar_optn='kfactors', earth_model_name=earth_model_name, scan_storm_event=scan_storm_event,
        power_flow_optn=power_flow_optn,
        ejet_million_amps=ejet_million_amps, ejet_halfwidth_km=ejet_halfwidth_km, ejet_period_min=ejet_period_min,
        ejet_height_km=ejet_height_km, ejet_center_deg=ejet_center_deg,
        addfile=addfile, purgfile=purgfile, rnwkfile=rnwkfile, pygicfile=pygicfile, gictfile=gictfile,
        basekv=basekv, areas=areas, buses=buses, owners=owners, zones=zones,
        basekv_local=[], areas_local=[], buses_local=[], owners_local=[], zones_local=[],
        pf_itmxn=pf_itmxn, pf_toln=pf_toln, pf_tap=pf_tap,
        pf_area=pf_area, pf_phshft=pf_phshft, pf_dctap=pf_dctap,
        pf_swsh=pf_swsh, pf_flat=pf_flat, pf_varlmt=pf_varlmt,
        pf_nondiv=pf_nondiv,
        )

    psspy.lines_per_page_one_device(2,10000000)
    psspy.progress_output(1,"",[0,0])
    psspy.alert_output(1,"",[0,0])

    return gicobj

# -----------------------------------------------------------------------------------------------------
def run_gic_sample_case(efield_mag, efield_deg, efield_type, scan_storm_event, power_flow_optn, datapath=None, outpath=None):
    """ Use sample Case provided in PSSE Example folder and run GIC calculations using arrbox.gic.GIC object.
Returns results in gicboj.
"""
    import psspy
    import arrbox.gic

    savfile = 'sample.sav'
    gicfile = 'sample_fv4.gic'

    outdir = get_output_dir(outpath)

    if not datapath: datapath = get_example_folder()

    savfile = os.path.join(datapath, savfile)
    gicfile = os.path.join(datapath, gicfile)

    if efield_type=='benchmark':
        efield_mag = 8.0
    else:
        efield_mag = 1.0

    efield_deg = 0.0

    outfnam   = _get_outfnam_event("sample", efield_type, efield_mag, efield_deg, scan_storm_event)
    prgfile   = os.path.join(outdir, outfnam+'progress.txt')
    pygicfile = os.path.join(outdir, outfnam+'_map.pygic')
    gictfile  = os.path.join(outdir, outfnam+'_gict.csv')

    ejet_million_amps = 1.0
    ejet_halfwidth_km = 200.0
    ejet_period_min   = 5.0
    ejet_height_km    = 100.0
    ejet_center_deg   = 54.0

    earth_model_name = 'shield'

    efield_unit      = 'V/km'
    substation_r     = 0.1
    branch_xbyr      = 30.0
    transformer_xbyr = 30.0
    addfile          = ''
    addfile_optn     = 'rdch'
    purgfile         = ''
    rnwkfile         = ''

    basekv    = []  # specify subsystem options
    areas     = []
    buses     = []
    owners    = []
    zones     = []
    tielevels = 0

    pf_itmxn   = 100    # specify power flow solution options
    pf_toln    = 0.1
    pf_tap     = 0
    pf_area    = 0
    pf_phshft  = 0
    pf_dctap   = 1
    pf_swsh    = 1
    pf_flat    = 0
    pf_varlmt  = 99
    pf_nondiv  = 0

    psspy.psseinit()

    psspy.lines_per_page_one_device(1,10000000)
    psspy.progress_output(2,prgfile,[0,0])

    print(savfile)
    print(gicfile)

    psspy.case(savfile)
    psspy.gic_read(gicfile)
    sid = 0
    busall = 1

    # run gic analysis
    gicobj = arrbox.gic.GIC(sid, busall, efield_mag=efield_mag, efield_deg=efield_deg,
        tielevels=tielevels, study_year=0, thermal_ana_optn=-1,
        substation_r=substation_r, branch_xbyr=branch_xbyr, transformer_xbyr=transformer_xbyr,
        efield_mag_local=0.0, efield_deg_local=0.0,
        branch_rac2rdc=1.0, transformer_rac2rdc=1.0,
        efield_type=efield_type, efield_unit=efield_unit, addfile_optn=addfile_optn,
        gic2mvar_optn='kfactors', earth_model_name=earth_model_name, scan_storm_event=scan_storm_event,
        power_flow_optn=power_flow_optn,
        ejet_million_amps=ejet_million_amps, ejet_halfwidth_km=ejet_halfwidth_km, ejet_period_min=ejet_period_min,
        ejet_height_km=ejet_height_km, ejet_center_deg=ejet_center_deg,
        addfile=addfile, purgfile=purgfile, rnwkfile=rnwkfile, pygicfile=pygicfile, gictfile=gictfile,
        basekv=basekv, areas=areas, buses=buses, owners=owners, zones=zones,
        basekv_local=[], areas_local=[], buses_local=[], owners_local=[], zones_local=[],
        pf_itmxn=pf_itmxn, pf_toln=pf_toln, pf_tap=pf_tap,
        pf_area=pf_area, pf_phshft=pf_phshft, pf_dctap=pf_dctap,
        pf_swsh=pf_swsh, pf_flat=pf_flat, pf_varlmt=pf_varlmt,
        pf_nondiv=pf_nondiv,
        )

    psspy.lines_per_page_one_device(2,10000000)
    psspy.progress_output(1,"",[0,0])

    return gicobj

# -----------------------------------------------------------------------------------------------------
def run_gic_ieee_text_report(efield_mag, efield_deg, efield_type, scan_storm_event, datapath=None, outpath=None):
    """ Use IEEE GIC Test Case provided in PSSE Example folder, run GIC calculations and create text report.
"""

    gicobj = run_gic_ieee_test_case(efield_mag, efield_deg, efield_type, scan_storm_event, datapath, outpath)

    if gicobj.ierr: return

    outdir = get_output_dir(outpath)
    rptnam = _get_outfnam_event("ieee", efield_type, efield_mag, efield_deg, scan_storm_event)

    rptfile  = os.path.join(outdir, rptnam+'.txt')
    qrptfile = os.path.join(outdir, rptnam+'_qloss.txt')

    gicobj.text_report(rptfile)
    gicobj.qtotal_report(qrptfile)

    msg = " Report created in file: {:s}".format(rptfile)
    print(msg)

# -----------------------------------------------------------------------------------------------------
def run_gic_ieee_text_report_DIY(datapath=None, outpath=None):
    """ Run GIC Analysis on IEEE GIC Test Case provided in PSSE Example folder and create customized report.
"""
    global _BIGREL

    import psspy
    _BIGREL = psspy.getdefaultreal()     # Largest real value

    efield_mag = 1.0
    efield_deg = 0.0
    efield_type = 'uniform'
    scan_storm_event = ''

    gicobj = run_gic_ieee_test_case(efield_mag, efield_deg, efield_type, scan_storm_event, datapath, outpath)

    if gicobj.ierr: return

    outdir = get_output_dir(outpath)
    rptnam = _get_outfnam_event("DIY_ieee", efield_type, efield_mag, efield_deg, scan_storm_event)
    rptfile = os.path.join(outdir, rptnam+'.txt')

    rptfobj = open(rptfile, 'w')
    report  = rptfobj.write

    elecfld_mag = "{:10.2f}".format(gicobj.misc.efield_mag)
    elecfld_mag = elecfld_mag.strip()

    elecfld_unt = gicobj.misc.efield_unit

    elecfld_deg = "{:10.2f}".format(gicobj.misc.efield_deg)
    elecfld_deg = elecfld_deg.strip()

    txt  = "\n GMD Event: Uniform Electric Field, {} {}, {} deg\n".format(elecfld_mag, elecfld_unt, elecfld_deg)

    txt += "\n GIC data file: {}\n".format(gicobj.gicfile)
    txt += " Power flow data file: {}\n".format(gicobj.savfile)

    if gicobj.basekv or gicobj.areas or gicobj.buses or gicobj.owners or gicobj.zones:
        txt += "\n Subsystem used for GIC studiies is defined as:\n"
        if gicobj.basekv: txt += "     Voltage = {}\n".format(str(gicobj.basekv))
        if gicobj.areas:  txt += "     Areas   = {}\n".format(str(gicobj.areas))
        if gicobj.buses:  txt += "     Buses   = {}\n".format(str(gicobj.buses))
        if gicobj.owners: txt += "     Owners  = {}\n".format(str(gicobj.owners))
        if gicobj.zones:  txt += "     Zones   = {}\n".format(str(gicobj.zones))
        txt += "     Subsystem Inter tie Levels = {}\n".format(gicobj.tielevels)
    else:
        txt += "\n Subsystem used for GIC studiies comprises entire network.\n"

    txt += "\n Number of buses in study subsystem        = {}\n".format(gicobj.misc.nbus_study)
    txt += " Number of substations in study subsystem  = {}\n".format(gicobj.misc.nsubstation_study)
    txt += " Number of branches in study subsystem     = {}\n".format(gicobj.misc.nbranch_study)
    txt += " Number of transformers in study subsystem = {}\n".format(gicobj.misc.ntransformer_study)
    report(txt)

    txt  = '\n Bus DC Voltages\n'
    txt += "    Bus Substation DC Voltage(V)\n"
    report(txt)

    buslist = list(gicobj.bus.keys())
    buslist.sort()
    for eachbus in buslist:
        # all of these work, shows how to use them
        #print "attr lower-->", eachbus, gicobj.bus[eachbus].substation, gicobj.bus[eachbus].dcvolts
        #print "dict lower-->", eachbus, gicobj.bus[eachbus]['substation'], gicobj.bus[eachbus]['dcvolts']
        #print "attr mixed-->", eachbus, gicobj.bus[eachbus].suBSTation, gicobj.bus[eachbus].dcVolts
        #print "dict mixed-->", eachbus, gicobj.bus[eachbus]['subStation'], gicobj.bus[eachbus]['DCvolts']
        txt = " {:6d}     {:6d}  {:12.5f}\n".format(eachbus, gicobj.bus[eachbus].substation, gicobj.bus[eachbus].dcvolts)
        report(txt)

    txt  = '\n Substations DC Voltages and GIC Flows, flowing from Bus to Substation Ground\n'
    txt += " Substation Name         Latitude(deg) Longitude(deg) DC Voltage(V)    GIC(Amps)\n"
    report(txt)

    sslist = list(gicobj.substation.keys())
    sslist.sort()
    for ss in sslist:
        txt = "     {:6d} {:12s}  {:12.6f}   {:12.6f}  {:12.5f} {:12.5f}\n".format(ss, gicobj.substation[ss].name,
                            gicobj.substation[ss].latitude, gicobj.substation[ss].longitude,
                            gicobj.substation[ss].dcvolts, gicobj.substation[ss].gic)
        report(txt)

    # Non-Transformer Branches
    txt  = '\n GIC flow in Non-Transformer Branches, flowing from From Bus to To Bus\n'
    txt += " FromBus  ToBus Ckt  Distance(km) per-Phase(A)   3-Phase(A)\n"
    report(txt)

    brnlist = list(gicobj.branch.keys())
    brnlist.sort()
    for brn in brnlist:
        txt = "  {:6d} {:6d}  {:2s}  {:12.5f} {:12.5f} {:12.5f}\n".format(brn[0], brn[1], brn[2],
                            gicobj.branch[brn].distance, gicobj.branch[brn].gic,
                            3*gicobj.branch[brn].gic)
        report(txt)

    # Transformers
    trnlist = list(gicobj.transformer.keys())
    trnlist.sort()

    no_2wdg_nrml = "\n     No two winding transformers in GIC studied network.\n"
    no_2wdg_auto = "\n     No two winding auto transformers in GIC studied network.\n"
    no_3wdg_nrml = "\n     No three winding transformers in GIC studied network.\n"
    no_3wdg_auto = "\n     No three winding auto transformers in GIC studied network.\n"

    # Two Winding Transformers - normal
    txt  = '\n Two Winding Transformers: Per Phase GIC flow in windings, flowing from winding Bus to Neutral\n'
    txt += " Reactive power loss, represented as constant current load on highest voltage bus in power flow\n"
    txt += "   Ibus   Jbus Ckt       Igic(A)      Jgic(A)    Effgic(A) Kfactor KftrTyp  Qloss(Mvar)\n"
    report(txt)

    for trn in trnlist:
        kbus  = trn[2]
        if kbus: continue

        autoi = gicobj.transformer[trn].wdg1_auto
        autoj = gicobj.transformer[trn].wdg2_auto
        if (autoi or autoj): continue

        igic    = _get_formatted_real_value(gicobj.transformer[trn].wdg1_gic)
        jgic    = _get_formatted_real_value(gicobj.transformer[trn].wdg2_gic)
        effgic  = _get_formatted_real_value(gicobj.transformer[trn].eff_gic)
        qloss   = _get_formatted_real_value(gicobj.transformer[trn].qloss)

        kftrtyp = gicobj._get_kfactor_type(gicobj.transformer[trn].kfactor_type)

        txt = " {:6d} {:6d}  {:2s}  {:s} {:s} {:s} {:7.3f} {:s} {:s}\n".format(trn[0], trn[1], trn[3], igic, jgic, effgic,
                            gicobj.transformer[trn].kfactor, kftrtyp, qloss)
        report(txt)
        if no_2wdg_nrml: no_2wdg_nrml=''

    if no_2wdg_nrml: report(no_2wdg_nrml)

    # Two Winding Transformers - auto
    txt  = '\n Two Winding Auto Transformers: Per Phase GIC flow in windings, flowing from winding Bus to Neutral\n'
    txt += " Reactive power loss, represented as constant current load on Series Winding bus in power flow\n"
    txt += " Common Series Ckt Common gic(A) Series gic(A)    Effgic(A) Kfactor KftrTyp  Qloss(Mvar)\n"
    report(txt)
    for trn in trnlist:
        kbus  = trn[2]
        if kbus: continue

        autoi = gicobj.transformer[trn].wdg1_auto
        autoj = gicobj.transformer[trn].wdg2_auto
        if ( (not autoi) or (not autoj) ): continue
        if autoi==1:
            ibus = trn[0]
            jbus = trn[1]
        else:
            ibus = trn[1]
            jbus = trn[0]

        igic    = _get_formatted_real_value(gicobj.transformer[trn].wdg1_gic)
        jgic    = _get_formatted_real_value(gicobj.transformer[trn].wdg2_gic)
        effgic  = _get_formatted_real_value(gicobj.transformer[trn].eff_gic)
        qloss   = _get_formatted_real_value(gicobj.transformer[trn].qloss)

        kftrtyp = gicobj._get_kfactor_type(gicobj.transformer[trn].kfactor_type)

        txt = " {:6d} {:6d}  {:2s}  {:s}  {:s} {:s} {:7.3f} {:s} {:s}\n".format(ibus, jbus, trn[3], igic, jgic, effgic,
                            gicobj.transformer[trn].kfactor, kftrtyp, qloss)
        report(txt)
        if no_2wdg_auto: no_2wdg_auto=''

    if no_2wdg_auto: report(no_2wdg_auto)

    # Three Winding Transformers - normal
    txt  = '\n Three Winding Transformers: Per Phase GIC flow in windings, flowing from winding Bus to Neutral\n'
    txt += " Reactive power loss, represented as constant current load on highest voltage bus in power flow\n"
    txt += "   Ibus   Jbus   Kbus Ckt       Igic(A)      Jgic(A)      Kgic(A)    Effgic(A) Kfactor KftrTyp  Qloss(Mvar)\n"
    report(txt)

    for trn in trnlist:
        kbus  = trn[2]
        if not kbus: continue

        autoi = gicobj.transformer[trn].wdg1_auto
        autoj = gicobj.transformer[trn].wdg2_auto
        autok = gicobj.transformer[trn].wdg3_auto
        if (autoi or autoj or autok): continue

        igic    = _get_formatted_real_value(gicobj.transformer[trn].wdg1_gic)
        jgic    = _get_formatted_real_value(gicobj.transformer[trn].wdg2_gic)
        kgic    = _get_formatted_real_value(gicobj.transformer[trn].wdg3_gic)
        effgic  = _get_formatted_real_value(gicobj.transformer[trn].eff_gic)
        qloss   = _get_formatted_real_value(gicobj.transformer[trn].qloss)

        kftrtyp = gicobj._get_kfactor_type(gicobj.transformer[trn].kfactor_type)

        txt = " {:6d} {:6d} {:6d}  {:2s}  {:s} {:s} {:s} {:s} {:7.3f} {:s} {:s}\n".format(trn[0], trn[1], trn[2], trn[3], igic, jgic, kgic, effgic,
                            gicobj.transformer[trn].kfactor, kftrtyp, qloss)
        report(txt)
        if no_3wdg_nrml: no_3wdg_nrml=''

    if no_3wdg_nrml: report(no_3wdg_nrml)

    # Three Winding Transformers - auto
    txt  = '\n Three Winding Auto Transformers: Per Phase GIC flow in windings, flowing from winding Bus to Neutral\n'
    txt += " Reactive power loss, represented as constant current load on highest voltage bus in power flow\n"
    txt += " Common Series   Kbus Ckt Common gic(A) Series gic(A)      Kgic(A)    Effgic(A) Kfactor KftrTyp  Qloss(Mvar)\n"
    report(txt)
    for trn in trnlist:
        kbus  = trn[2]
        if not kbus: continue

        autoi = gicobj.transformer[trn].wdg1_auto
        autoj = gicobj.transformer[trn].wdg2_auto
        if ( (not autoi) or (not autoj) ): continue
        if autoi==1:
            ibus = trn[0]
            jbus = trn[1]
        else:
            ibus = trn[1]
            jbus = trn[0]

        igic    = _get_formatted_real_value(gicobj.transformer[trn].wdg1_gic)
        jgic    = _get_formatted_real_value(gicobj.transformer[trn].wdg2_gic)
        kgic    = _get_formatted_real_value(gicobj.transformer[trn].wdg3_gic)
        effgic  = _get_formatted_real_value(gicobj.transformer[trn].eff_gic)
        qloss   = _get_formatted_real_value(gicobj.transformer[trn].qloss)

        kftrtyp = gicobj._get_kfactor_type(gicobj.transformer[trn].kfactor_type)

        txt = " {:6d} {:6d} {:6d}  {:2s}  {:s}  {:s} {:s} {:s} {:7.3f} {:s} {:s}\n".format(ibus, jbus, kbus, trn[3], igic, jgic, kgic, effgic,
                            gicobj.transformer[trn].kfactor, kftrtyp, qloss)
        report(txt)
        if no_3wdg_auto: no_3wdg_auto=''

    if no_3wdg_auto: report(no_3wdg_auto)

    # Total Qloss
    if no_2wdg_nrml:
        qwdg2_nrml = '        None'
    else:
        qwdg2_nrml = "{:12.5f} Mvar".format(gicobj.qtotal.wdg2_normal)
    if no_2wdg_auto:
        qwdg2_auto = '        None'
    else:
        qwdg2_auto = "{:12.5f} Mvar".format(gicobj.qtotal.wdg2_auto)
    if no_3wdg_nrml:
        qwdg3_nrml = '        None'
    else:
        qwdg3_nrml = "{:12.5f} Mvar".format(gicobj.qtotal.wdg3_normal)
    if no_3wdg_auto:
        qwdg3_auto = '        None'
    else:
        qwdg3_auto = "{:12.5f} Mvar".format(gicobj.qtotal.wdg3_auto)
    txt  = '\n Transformer Reactive Power Loss Summary\n'
    txt += ' Two Winding Transformers        = {:s}\n'.format(qwdg2_nrml)
    txt += ' Two Winding Auto Transformers   = {:s}\n'.format(qwdg2_auto)
    txt += ' Three Winding Transformers      = {:s}\n'.format(qwdg3_nrml)
    txt += ' Three Winding Auto Transformers = {:s}\n'.format(qwdg3_auto)
    txt += '                           Total = {:12.5f} Mvar\n'.format(gicobj.qtotal.total)
    report(txt)

    # done - close report file
    if rptfile:
        rptfobj.close()
        txt = "\n GIC analysis output report saved to file: {:s}\n".format(rptfile)
        sys.stdout.write(txt)

# -----------------------------------------------------------------------------------------------------
def run_gic_ieee_excel_export_DIY(datapath=None, outpath=None, show=True):
    """ Use IEEE GIC Test Case provided in PSSE Example folder, run GIC calculations and export results to spreadsheet.
"""
    import psspy
    import excelpy

    _BIGREL = psspy.getdefaultreal()     # Largest real value

    efield_mag = 1.0
    efield_deg = 0.0
    efield_type = 'uniform'
    scan_storm_event = ''

    gicobj = run_gic_ieee_test_case(efield_mag, efield_deg, efield_type, scan_storm_event, datapath, outpath)

    if gicobj.ierr: return

    outdir = get_output_dir(outpath)
    rptnam = _get_outfnam_event("DIY_ieee", efield_type, efield_mag, efield_deg, scan_storm_event)
    xlsfile = os.path.join(outdir, rptnam)

    # What to export?
    overwritesheet = True
    do_sheets = ['optn', 'bus', 'sub', 'brn', 'trn']

    _EXPORT_QTY_GIC   = {
    'optn': 'options'     ,
    'bus' : 'bus'         ,
    'sub' : 'substation'  ,
    'brn' : 'branch'      ,
    'trn' : 'transformer' ,
    }

    _WORKSHT_SEQ_GIC = ['optn','bus','sub','brn','trn']

    _WORKSHT_COLUMN_LABELS_GIC = {
        'bus': ['Bus', 'Substation', 'DC Voltage(V)'],
        'sub': ['Substation', 'Name', 'Latitude(deg)', 'Longitude(deg)', 'DC Voltage(V)', 'GIC(Amps)'],
        'brn': ['FromBus', 'ToBus', 'Ckt', 'Distance(km)', 'per-Phase(A)', '3-Phase(A)'],
        'trn_nrml': ['Ibus', 'Jbus', 'Kbus', 'Ckt', 'Igic(A)', 'Jgic(A)', 'Kgic(A)', 'Effgic(A)', 'Kfactor', 'KftrTyp', 'Qloss(Mvar)'],
        'trn_auto': ['Common', 'Series', 'Kbus', 'Ckt', 'Common gic(A)', 'Series gic(A)', 'Kgic(A)', 'Effgic(A)', 'Kfactor', 'KftrTyp', 'Qloss(Mvar)'],
        }

    _WORKSHT_INFO_TXT_GIC = {
        'bus': ['Bus DC Voltages'],
        'sub': ['Substations DC Voltages and GIC Flows, flowing from Bus to Substation Ground'],
        'brn': ['GIC flow in Non-Transformer Branches, flowing from From Bus to To Bus'],
        'trn_nrml': ['Transformers: Per Phase GIC flow in windings, flowing from winding Bus to Neutral',
                     'Reactive power loss, represented as constant current load on highest voltage bus in power flow'],
        'trn_auto': ['Auto Transformers: Per Phase GIC flow in windings, flowing from winding Bus to Neutral',
                     'Reactive power loss, represented as constant current load on Series Winding bus in power flow'],
        }

    gicshts = []
    for each in _WORKSHT_SEQ_GIC:
        if each in do_sheets:
            if each=='trn':
                gicshts.extend( [ _EXPORT_QTY_GIC[each], 'auto '+_EXPORT_QTY_GIC[each] ] )
            else:
                gicshts.append(_EXPORT_QTY_GIC[each])

    for i, shtnam in enumerate(gicshts):
        if i==0:
            xlsobj = excelpy.workbook(xlsfile, shtnam, overwritesheet=overwritesheet)
            if show:
                xlsobj.show()
            else:
                xlsobj.hide()

            xlsobj.show_alerts(0) # do not show pop-up alerts
            xlsfnam = xlsobj.XLSFNAM
        else:
            xlsobj.worksheet_add_end(shtnam, overwritesheet=overwritesheet)
        xlsobj.page_format(orientation="landscape",left=1.0,right=1.0,
                           top=0.5,bottom=0.5,header=0.25,footer=0.25)
        xlsobj.page_footer(left='page number of page total', right='date, time')
        xlsobj.page_header(center='file name:sheet name')
        xlsobj.font_sheet()

    if not xlsobj:
        print("Excel file and worksheets not created.\n")

    # Options
    do_key = 'optn'
    if do_key in do_sheets:

        elecfld_mag = "{:10.2f}".format(gicobj.misc.efield_mag)
        elecfld_mag = elecfld_mag.strip()

        elecfld_unt = gicobj.misc.efield_unit

        elecfld_deg = "{:10.2f}".format(gicobj.misc.efield_deg)
        elecfld_deg = elecfld_deg.strip()

        txt  = "\n GMD Event: Uniform Electric Field, {:s} {:s}, {:s} deg\n".format(elecfld_mag, elecfld_unt, elecfld_deg)

        txt += "\n GIC data file: {:s}\n".format(gicobj.gicfile)
        txt += " Power flow data file: {:s}\n".format(gicobj.savfile)

        if gicobj.basekv or gicobj.areas or gicobj.buses or gicobj.owners or gicobj.zones:
            txt += "\n Subsystem used for GIC studies is defined as:\n"
            if gicobj.basekv: txt += "     Voltage = {:s}\n".format(str(gicobj.basekv))
            if gicobj.areas:  txt += "     Areas   = {:s}\n".format(str(gicobj.areas))
            if gicobj.buses:  txt += "     Buses   = {:s}\n".format(str(gicobj.buses))
            if gicobj.owners: txt += "     Owners  = {:s}\n".format(str(gicobj.owners))
            if gicobj.zones:  txt += "     Zones   = {:s}\n".format(str(gicobj.zones))
            txt += "     Subsystem Inter tie Levels = {:d}\n".format(gicobj.tielevels)
        else:
            txt += "\n Subsystem used for GIC studies comprises entire network.\n"

        txt += "\n Number of buses in study subsystem        = {:d}\n".format(gicobj.misc.nbus_study)
        txt += " Number of substations in study subsystem  = {:d}\n".format(gicobj.misc.nsubstation_study)
        txt += " Number of branches in study subsystem     = {:d}\n".format(gicobj.misc.nbranch_study)
        txt += " Number of transformers in study subsystem = {:d}\n".format(gicobj.misc.ntransformer_study)

        optnlist = txt.split("\n")

        xlsobj.set_active_sheet(_EXPORT_QTY_GIC[do_key])
        br, rc = 1, 1
        br, rc = xlsobj.set_range(br, rc, optnlist, transpose=True)

    # DC Bus voltages
    do_key = 'bus'
    if do_key in do_sheets:
        buslist = list(gicobj.bus.keys())
        buslist.sort()
        rowdata = [_WORKSHT_COLUMN_LABELS_GIC[do_key]]
        for eachbus in buslist:
            tlst = [eachbus, gicobj.bus[eachbus].substation, gicobj.bus[eachbus].dcvolts]
            rowdata.append(tlst)

        xlsobj.set_active_sheet(_EXPORT_QTY_GIC[do_key])
        br0, rc0 = 3, 1
        br, rc = xlsobj.set_range(br0, rc0, rowdata)
        del rowdata
        xlsobj.autofit_columns((br0,rc0,br0,rc))
        xlsobj.font_color((br0,rc0,br0,rc),"red")
        xlsobj.align_rows((br0, rc0),alignv='right')    #label row
        xlsobj.set_cell((1,1),_WORKSHT_INFO_TXT_GIC[do_key][0],fontStyle="bold",fontSize=12, fontColor="blue")

    # Substation
    do_key = 'sub'
    if do_key in do_sheets:
        sslist = list(gicobj.substation.keys())
        sslist.sort()
        rowdata = [_WORKSHT_COLUMN_LABELS_GIC[do_key]]
        for ss in sslist:
            tlst = [ss, gicobj.substation[ss].name, gicobj.substation[ss].latitude, gicobj.substation[ss].longitude,
                    gicobj.substation[ss].dcvolts, gicobj.substation[ss].gic]
            rowdata.append(tlst)

        xlsobj.set_active_sheet(_EXPORT_QTY_GIC[do_key])
        br0, rc0 = 3, 1
        br, rc = xlsobj.set_range(br0, rc0, rowdata)
        del rowdata
        xlsobj.autofit_columns((br0,rc0,br0,rc))
        xlsobj.font_color((br0,rc0,br0,rc),"red")
        xlsobj.align_rows((br0, rc0),alignv='right')    #label row
        xlsobj.set_cell((1,1),_WORKSHT_INFO_TXT_GIC[do_key][0],fontStyle="bold",fontSize=12, fontColor="blue")


    # Non-Transformer Branches
    do_key = 'brn'
    if do_key in do_sheets:
        brnlist = list(gicobj.branch.keys())
        brnlist.sort()
        rowdata = [_WORKSHT_COLUMN_LABELS_GIC[do_key]]
        for brn in brnlist:
            tlst = [brn[0], brn[1], brn[2], gicobj.branch[brn].distance, gicobj.branch[brn].gic,3*gicobj.branch[brn].gic]
            rowdata.append(tlst)

        xlsobj.set_active_sheet(_EXPORT_QTY_GIC[do_key])
        br0, rc0 = 3, 1
        br, rc = xlsobj.set_range(br0, rc0, rowdata)
        del rowdata
        xlsobj.autofit_columns((br0,rc0,br0,rc))
        xlsobj.font_color((br0,rc0,br0,rc),"red")
        xlsobj.align_rows((br0, rc0),alignv='right')    #label row
        xlsobj.set_cell((1,1),_WORKSHT_INFO_TXT_GIC[do_key][0],fontStyle="bold",fontSize=12, fontColor="blue")

    # Transformers
    do_key = 'trn'
    if do_key in do_sheets:
        do_key_nrml = 'trn_nrml'
        do_key_auto = 'trn_auto'

        trnlist = list(gicobj.transformer.keys())
        trnlist.sort()

        rowdata_nrml = [_WORKSHT_COLUMN_LABELS_GIC[do_key_nrml]]
        rowdata_auto = [_WORKSHT_COLUMN_LABELS_GIC[do_key_auto]]

        for trn in trnlist:
            kbus  = trn[2]
            igic  = gicobj.transformer[trn].wdg1_gic
            jgic  = gicobj.transformer[trn].wdg2_gic
            if kbus:
                kgic = gicobj.transformer[trn].wdg3_gic
            else:
                kgic = None

            effgic  = gicobj.transformer[trn].eff_gic
            qloss   = gicobj.transformer[trn].qloss
            kftr    = gicobj.transformer[trn].kfactor
            kftrtyp = gicobj._get_kfactor_type(gicobj.transformer[trn].kfactor_type)

            autoi = gicobj.transformer[trn].wdg1_auto
            autoj = gicobj.transformer[trn].wdg2_auto
            if autoi or autoj:
                if autoi==1:
                    ibus = trn[0]
                    jbus = trn[1]
                else:
                    ibus = trn[1]
                    jbus = trn[0]
            else:
                ibus = trn[0]
                jbus = trn[1]

            if igic:
                if igic>=_BIGREL: igic = ''
            else:
                igic = ''

            if jgic:
                if jgic>=_BIGREL: jgic = ''
            else:
                jgic = ''

            if kgic:
                if kgic>=_BIGREL: kgic = ''
            else:
                kgic = ''

            if effgic:
                if effgic>=_BIGREL: effgic = ''
            else:
                effgic = ''

            if qloss:
                if qloss>=_BIGREL: qloss = ''
            else:
                qloss = ''

            tlst = [ibus, jbus, kbus, trn[3], igic, jgic, kgic, effgic, kftr, kftrtyp, qloss]
            if autoi or autoj:
                rowdata_auto.append(tlst)
            else:
                rowdata_nrml.append(tlst)

        # Total Qloss
        txt  = ' Transformer Reactive Power Loss Summary\n'
        txt += ' Two Winding Transformers        = {:g} Mvar\n' .format(gicobj.qtotal.wdg2_normal)
        txt += ' Two Winding Auto Transformers   = {:g} Mvar\n' .format(gicobj.qtotal.wdg2_auto)
        txt += ' Three Winding Transformers      = {:g} Mvar\n' .format(gicobj.qtotal.wdg3_normal)
        txt += ' Three Winding Auto Transformers = {:g} Mvar\n' .format(gicobj.qtotal.wdg3_auto)
        txt += '                           Total = {:g} Mvar'   .format(gicobj.qtotal.total)
        qlosslist = txt.split("\n")

        # normal transformers
        xlsobj.set_active_sheet(_EXPORT_QTY_GIC[do_key])
        br0, rc0 = 4, 1
        br, rc = xlsobj.set_range(br0, rc0, rowdata_nrml)
        del rowdata_nrml
        xlsobj.autofit_columns((br0,rc0,br0,rc))
        xlsobj.font_color((br0,rc0,br0,rc),"red")
        xlsobj.align_rows((br0, rc0),alignv='right')    #label row
        xlsobj.set_cell((1,1),_WORKSHT_INFO_TXT_GIC[do_key_nrml][0],fontStyle="bold",fontSize=12, fontColor="blue")
        xlsobj.set_cell((2,1),_WORKSHT_INFO_TXT_GIC[do_key_nrml][1],fontStyle="bold",fontSize=12, fontColor="blue")

        br, rc = br+2, 1
        br, rc = xlsobj.set_range(br, rc, qlosslist, transpose=True)

        # auto transformers
        xlsobj.set_active_sheet('auto '+_EXPORT_QTY_GIC[do_key])
        br0, rc0 = 4, 1
        br, rc = xlsobj.set_range(br0, rc0, rowdata_auto)
        del rowdata_auto
        xlsobj.autofit_columns((br0,rc0,br0,rc))
        xlsobj.font_color((br0,rc0,br0,rc),"red")
        xlsobj.align_rows((br0, rc0),alignv='right')    #label row
        xlsobj.set_cell((1,1),_WORKSHT_INFO_TXT_GIC[do_key_auto][0],fontStyle="bold",fontSize=12, fontColor="blue")
        xlsobj.set_cell((2,1),_WORKSHT_INFO_TXT_GIC[do_key_auto][1],fontStyle="bold",fontSize=12, fontColor="blue")

        br, rc = br+2, 1
        br, rc = xlsobj.set_range(br, rc, qlosslist, transpose=True)

    # done exporting
    xlsobj.save(xlsfile)

    if not show:
        txt = "\n GIC analysis output report saved to file: \n    {0}\n".format(xlsobj.XLSFNAM)
        xlsobj.close()
        sys.stdout.write(txt)

# -----------------------------------------------------------------------------------------------------
def run_gic_sample_text_report(efield_mag, efield_deg, efield_type, scan_storm_event, power_flow_optn, datapath=None, outpath=None):
    """ Use sample Case provided in PSSE Example folder, run GIC calculations and create text report.
"""

    gicobj = run_gic_sample_case(efield_mag, efield_deg, efield_type, scan_storm_event, power_flow_optn, datapath, outpath)

    if gicobj.ierr: return

    outdir = get_output_dir(outpath)
    rptnam = _get_outfnam_event("sample", efield_type, efield_mag, efield_deg, scan_storm_event)
    if power_flow_optn:  rptnam += '_pf'

    rptfile  = os.path.join(outdir, rptnam+'.txt')
    qrptfile = os.path.join(outdir, rptnam+'_qloss.txt')

    gicobj.text_report(rptfile)
    gicobj.qtotal_report(qrptfile)

    msg = "\n Report created in file: {:s}".format(rptfile)
    print(msg)

# -----------------------------------------------------------------------------------------------------
def run_gic_sample_excel_export(efield_mag, efield_deg, efield_type, scan_storm_event, power_flow_optn, show=True,
                                datapath=None, outpath=None):
    """ Use sample Case provided in PSSE Example folder, run GIC calculations and export results to spreadsheet.
"""
    gicobj = run_gic_sample_case(efield_mag, efield_deg, efield_type, scan_storm_event, power_flow_optn, datapath, outpath)

    if gicobj.ierr: return

    outdir = get_output_dir(outpath)
    rptnam = _get_outfnam_event("sample", efield_type, efield_mag, efield_deg, scan_storm_event)
    if power_flow_optn:  rptnam += '_pf'

    xlfile = os.path.join(outdir, rptnam)
    string = ''
    overwritesheet = True
    xlfile = gicobj.excel_export(string, xlfile, show, overwritesheet)

    msg = "\n Spreadsheet created in file:\n    {0}".format(xlfile)
    print(msg)

# -----------------------------------------------------------------------------------------------------
def gic_results_on_network_map(pygicfile, outpath=None, outfext='.pdf', show=True):
    """ Plot GIC results on map.
"""
    import collections
    import psspy

    psspy.set_fpcw_py()     # To use PSSE, numpy and matplotlib, this is needed.
    import arrbox.gicmaps

    outdir = get_output_dir(outpath)

    p, nx = os.path.split(pygicfile)
    pyfnam, x = os.path.splitext(nx)

    if not p:
        if not os.path.exists(pygicfile):
            pygicfile = os.path.join(outdir, pygicfile)

    pltfiles = collections.OrderedDict()
    for k in ['busvpu_base','busvpu_gic', 'ssgic1', 'ssgic2', 'brngic',
              'qtline', 'qtline', 'qtbar', 'effgic', 'effgicmax']:
        if outfext=='.pdf':
            pltfiles[k] = None
        else:
            fnam = "{}_{}{}".format(pyfnam, k, outfext)
            pltfiles[k] = os.path.join(outdir, fnam)

    gicmapsobj  = arrbox.gicmaps.GICMAPS(pygicfile)

    if gicmapsobj.ierr: return

    if outfext=='.pdf':
        fnam = "{}_allplots{}".format(pyfnam, outfext)
        pdffile = os.path.join(outdir, fnam)
        gicmapsobj.pdf_open(pdffile)

    gicmapsobj.plot_bus_voltages(figfile=pltfiles['busvpu_base'], case='base', limit='min', markersize=100)

    gicmapsobj.plot_bus_voltages(figfile=pltfiles['busvpu_gic'], case='gic', limit='min', markersize=100)

    # combine substations GICs flowing in and out on one legend
    gicmapsobj.plot_substation_gicflows(figfile=pltfiles['ssgic1'], markersize=20)

    # separate substations GICs flowing in and out on two legends
    gicmapsobj.set_legend_options_ss_gic_values(loc=None)
    gicmapsobj.plot_substation_gicflows(figfile=pltfiles['ssgic2'], markersize=20)

    gicmapsobj.plot_branch_gicflows(figfile=pltfiles['brngic'])

    gicmapsobj.plot_qtotal(figfile=pltfiles['qtline'])

    gicmapsobj.plot_qtotal_barchart(figfile=pltfiles['qtbar'])

    gicmapsobj.plot_effgic(figfile=pltfiles['effgic'], gicmax=False)

    gicmapsobj.plot_effgic(figfile=pltfiles['effgicmax'], gicmax=True)

    if show:
        gicmapsobj.plots_show()
    else:
        gicmapsobj.plots_close()

    if outfext=='.pdf':
        gicmapsobj.pdf_close()

    if outfext=='.pdf':
        msg  = "\n GIC analysis custom plots saved in file:\n    {}\n".format(pdffile)
    else:
        msg  = "\n GIC analysis custom plot [{}] files saved in folder:\n    {}\n".format(outfext, outdir)

    print(msg)
    psspy.set_fpcw_psse()   # To use PSSE, numpy and matplotlib, this is needed.

# -----------------------------------------------------------------------------------------------------
def gic_results_on_network_map_custom(pygicfile, outpath=None, outfext='.pdf', show=True):
    """ Plot GIC results on map with custom legends, annotations.
"""
    import collections
    import psspy

    psspy.set_fpcw_py()
    import arrbox.gicmaps

    outdir = get_output_dir(outpath)

    p, nx = os.path.split(pygicfile)
    pyfnam, x = os.path.splitext(nx)

    if not p:
        if not os.path.exists(pygicfile):
            pygicfile = os.path.join(outdir, pygicfile)

    outnam  = '{}_custom'.format(pyfnam)

    pltfiles = collections.OrderedDict()
    for k in ['busvpu_base','busvpu_gic', 'ssgic1', 'ssgic2', 'brngic',
              'qtline', 'qtline', 'qtbar', 'effgic', 'effgicmax']:
        if outfext!='.pdf':
            fnam = "{}_{}{}".format(outnam, k, outfext)
            pltfiles[k] = os.path.join(outdir, fnam)

    gicmapsobj = arrbox.gicmaps.GICMAPS(pygicfile)

    if gicmapsobj.ierr: return

    if outfext=='.pdf':
        fnam = "{}_allplots{}".format(outnam, outfext)
        pdffile = os.path.join(outdir, fnam)
        pdf2fobj = gicmapsobj.pdf2_open(pdffile)  # open pdf2 object to save custom plots to pdf file

    gicmapsobj.set_figure_size(6,4.8)

    gicmapsobj.set_state_boundary_options(show=True, color='#CCCCCC', linewidth=1.0)
    gicmapsobj.set_latitude_options(show=True, color='#CCFFFF', linewidth=2.0, dashes=[1, 1], fontsize=10)
    gicmapsobj.set_longitude_options(show=True, color='#CCFFFF', linewidth=2.0, dashes=[1, 3], fontsize=10)

    gicmapsobj.annotate_substations([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18], color='blue', fontsize=10)

    # Plot1 - GIC case bus voltage
    pf_flag = gicmapsobj.pygicobj.power_flow_solution_flag
    if pf_flag==0:
        case = 'gic'
        if outfext!='.pdf': figfile = pltfiles['busvpu_gic']
        ttl = 'Bus Voltages - GIC Case'
    else:
        case = 'base'
        if outfext!='.pdf': figfile = pltfiles['busvpu_base']
        ttl = 'Bus Voltages - Base Case'
    ax, fig, basemap, anptobj = gicmapsobj.plot_bus_voltages(figfile=None, case=case, limit='min', markersize=100,
                                 title=ttl)
    if ax is None:
        if outfext=='.pdf':
            gicmapsobj.pdf_close()
        return

    # data point annotation
    anptobj.set_options(xytext=(-15,-40), textcoords='offset points')
    anptobj.set_annote_from_key(5)                          # use SS number as key
    #anptobj.set_annote_from_key('ss05_mississippi')        # use SS name as key
    anptobj.set_options(xytext=(-40,-100), textcoords='offset points')
    anptobj.set_annote_from_key(7)                          # use SS number as key
    #anptobj.set_annote_from_key('ss07_yukon')
    anptobj.set_options(xytext=(-20,25), textcoords='offset points')
    anptobj.set_annote_from_key(13)                         # use SS number as key
    #anptobj.set_annote_from_key('ss13_oxus')               # use SS number as key
    anptobj.set_options(xytext=(-40,25), textcoords='offset points')
    #anptobj.set_annote_from_key(15)                        # use SS number as key
    anptobj.set_annote_from_key('ss15_heilong')             # use SS number as key

    # custom annotation
    gicmapsobj.annotate_text('LabelLeft', -89, 30.2, ax, basemap, xycoords='long_lat', color='cyan', fontsize=15)
    x, y = gicmapsobj.datapoint_xy_from_longitude_latiude(basemap, -84, 30.2)
    gicmapsobj.annotate_text('LabelRight', x, y, ax, basemap, xycoords='data', color='magenta', fontsize=15)

    if outfext=='.pdf':
        gicmapsobj.pdf2_add_figure(pdf2fobj, fig)               # add custom plot to pdf file
    else:
        fig.savefig(figfile, dpi=300, bbox_inches='tight')   # save custom plot to file

    # Plot2 - Base case bus voltage
    if pf_flag==0:
        ax, fig, basemap, anptobj = gicmapsobj.plot_bus_voltages(figfile=None,  case='base', limit='min', markersize=100,
                                     title='Bus Voltages - Base Case')
        anptobj.set_options(xytext=(-50,-50), textcoords='offset points')
        anptobj.set_annote_from_key(15)

        if outfext=='.pdf':
            gicmapsobj.pdf2_add_figure(pdf2fobj, fig)
        else:
            fig.savefig(pltfiles['busvpu_base'], dpi=300, bbox_inches='tight')

    # Plot3 - substations GICs (combine GICs flowing in and out on one legend)
    ax, fig, basemap, anptobj = gicmapsobj.plot_substation_gicflows(figfile=None, markersize=20)

    anptobj.set_options(xytext=(-65,40), textcoords='offset points')
    anptobj.set_annote_from_key('ss01_nile')
    anptobj.set_options(xytext=(-60,-70), textcoords='offset points')
    anptobj.set_annote_from_key('ss02_yangtze')
    anptobj.set_options(xytext=(-60,-70), textcoords='offset points')
    anptobj.set_annote_from_key('ss03_arkansas')
    anptobj.set_options(xytext=(-20,-35), textcoords='offset points')
    anptobj.set_annote_from_key('ss09_indus')

    if outfext=='.pdf':
        gicmapsobj.pdf2_add_figure(pdf2fobj, fig)
    else:
        fig.savefig(pltfiles['ssgic1'], dpi=300, bbox_inches='tight')

    # Plot4 - substations GICs (separate GICs flowing in and out on two legends)
    gicmapsobj.set_legend_options_ss_gic_values(loc=None)
    ax, fig, basemap, anptobj = gicmapsobj.plot_substation_gicflows(figfile=None, markersize=20)
    anptobj.set_options(xytext=(-50,-50), textcoords='offset points')
    anptobj.set_annote_from_key(1)
    anptobj.set_annote_from_key(3)
    anptobj.set_annote_from_key(8)

    if outfext=='.pdf':
        gicmapsobj.pdf2_add_figure(pdf2fobj, fig)
    else:
        fig.savefig(pltfiles['ssgic2'], dpi=300, bbox_inches='tight')

    # Plot5 - Effective GIC
    ax, fig, anptobj = gicmapsobj.plot_effgic(figfile=None, gicmax=False)
    anptobj.set_options(xytext=(-30,-30), textcoords='offset points')
    anptobj.set_annote_from_key('catdog_xmer')          # use transformer name as key
    anptobj.set_annote_from_key((3018, 3008, '11'))     # use transformer id tuple: (wdg1bus, wdg2bus, 'ckt')
                                                        # or (wdg1bus, wdg2bus, wdg3bus, 'ckt')
    anptobj.set_options(xytext=(-65,30), textcoords='offset points')
    anptobj.set_annote_from_key((203, 202, 't7'))

    if outfext=='.pdf':
        gicmapsobj.pdf2_add_figure(pdf2fobj, fig)
    else:
        fig.savefig(pltfiles['effgic'], dpi=300, bbox_inches='tight')

    # Plot6 - Maximum Effective GIC
    ax, fig, anptobj = gicmapsobj.plot_effgic(figfile=None, gicmax=True)
    anptobj.set_options(xytext=(-30,-40), textcoords='offset points')
    anptobj.set_annote_from_key('catdog_xmer')
    anptobj.set_options(xytext=(-30,-60), textcoords='offset points')
    anptobj.set_annote_from_key(('urb tx'))
    anptobj.set_options(xytext=(-10,20), textcoords='offset points')
    anptobj.set_annote_from_key(('mid ltc'))

    if outfext=='.pdf':
        gicmapsobj.pdf2_add_figure(pdf2fobj, fig)
    else:
        fig.savefig(pltfiles['effgicmax'], dpi=300, bbox_inches='tight')

    if show:
        gicmapsobj.plots_show()
    else:
        gicmapsobj.plots_close()

    if outfext=='.pdf':
        gicmapsobj.pdf2_close(pdf2fobj)

    if outfext=='.pdf':
        msg  = "\n GIC analysis custom plots saved in file:\n    {}\n".format(pdffile)
    else:
        msg  = "\n GIC analysis custom plot [{}] files saved in folder:\n    {}\n".format(outfext, outdir)

    print(msg)
    psspy.set_fpcw_psse()

# -----------------------------------------------------------------------------------------------------
def gict_result_plots(gictfile, outpath=None, top_trn=10, nrows=2, ncols=2, outfext='.pdf', show=True):
    """ Plot GIC Thermal results.
top_trn - plot so many transformers with maximum GICs
nrows   - numbers of rows in plot figure
ncols   - numbers of columns in plot figure
nrows X ncols subplots are drawn on one figure.
"""
    import collections
    import psspy

    psspy.set_fpcw_py()
    import arrbox.gicthermal

    outdir = get_output_dir(outpath)

    p, nx = os.path.split(gictfile)
    pyfnam, x = os.path.splitext(nx)

    if not p:
        if not os.path.exists(gictfile):
            gictfile = os.path.join(outdir, gictfile)

    outnam  = '{}'.format(pyfnam)

    pltfiles = collections.OrderedDict()
    for k in ['evt','trn']:
        if outfext=='.pdf':
            pltfiles[k] = None
        else:
            fnam = "{}_{}{}".format(outnam, k, outfext)
            pltfiles[k] = os.path.join(outdir, fnam)

    thermalobj = arrbox.gicthermal.GICTHERMAL(gictfile)

    if thermalobj.ierr: return

    if outfext=='.pdf':
        fnam = "{}_allplots{}".format(outnam, outfext)
        pdffile = os.path.join(outdir, fnam)
        thermalobj.pdf_open(pdffile)

    evtnamlst, figdict, axdict = thermalobj.plot_events(figfile=pltfiles['evt'], show=show)

    figlst, axdict = thermalobj.plot_transformer_gict(figfile=pltfiles['trn'], top=top_trn, nrows=nrows, ncols=ncols, show=show)

    if show:
        thermalobj.plots_show()
    else:
        thermalobj.plots_close()

    if outfext=='.pdf':
        thermalobj.pdf_close()

    if outfext=='.pdf':
        msg  = "\n GIC Transformer Thermal GICT(t) profile plots saved in file:\n    {}\n".format(pdffile)
    else:
        msg  = "\n GIC Transformer Thermal GICT(t) profile plot [{}] files saved in folder:\n    {}\n".format(outfext, outdir)

    print(msg)
    psspy.set_fpcw_psse()

# =============================================================================================================

def run_all_tests(datapath=None, outpath=None, efields='ubn', scan='d', pf='fdns', outfext='.pdf'):

    outdir = get_output_dir(outpath)

    efield_type_lst = []
    scan_lst = []
    pf_lst = []

    if efields:
        s_efld = efields.lower()
        if 'u' in s_efld: efield_type_lst.append('uniform')
        if 'b' in s_efld: efield_type_lst.append('benchmark')
        if 'n' in s_efld: efield_type_lst.append('nonuniform')

    if scan:
        s_scan = scan.lower()
        if 'd' in s_scan: scan_lst.append('scan_deg')
        if 'm' in s_scan: scan_lst.append('scan_mag')
        if 'd_m' in s_scan: scan_lst.append('scan_d_m')

    if pf:
        pf_lst.append(pf)

    if not efield_type_lst: efield_type_lst = ['uniform']
    if not scan_lst: scan_lst = ['']
    if not pf_lst: pf_lst = ['']

    # -----------------------------------------

    print ("\n >>>>>>>>>>>>> Running create_gicdata_template_sample")
    excelfile = create_gicdata_template_sample(datapath, outpath, showexcel=False)

    print ("\n >>>>>>>>>>>>> Running excel2gicfile")
    gicdata_excel2gicfile(outpath)

    efield_mag = 1.0
    efield_deg = 0.0

    print ("\n >>>>>>>>>>>>> Running run_gic_ieee_text_report")
    for efield_type in efield_type_lst:
        for scan_storm_event in scan_lst:
            run_gic_ieee_text_report(efield_mag, efield_deg, efield_type, scan_storm_event,datapath, outpath)
            break

    print ("\n >>>>>>>>>>>>> Running run_gic_sample_text_report")
    for efield_type in efield_type_lst:
        for scan_storm_event in scan_lst:
            for power_flow_optn in pf_lst:
                run_gic_sample_text_report(efield_mag, efield_deg, efield_type,
                                           scan_storm_event, power_flow_optn, datapath, outpath)
                break

    print ("\n >>>>>>>>>>>>> Running run_gic_ieee_text_report_DIY")
    run_gic_ieee_text_report_DIY(datapath, outpath)

    print ("\n >>>>>>>>>>>>> Running run_gic_ieee_excel_export_DIY")
    run_gic_ieee_excel_export_DIY(datapath, outpath, show=False)


    print ("\n >>>>>>>>>>>>> Running run_gic_sample_excel_export, uniform, no scan, no powerflow")
    run_gic_sample_excel_export(efield_mag=1.0, efield_deg=0.0, efield_type='uniform', scan_storm_event='',
                                power_flow_optn='',     show=False, datapath=datapath, outpath=outpath)

    print ("\n >>>>>>>>>>>>> Running run_gic_sample_excel_export, uniform, scan_deg, fdns")
    run_gic_sample_excel_export(efield_mag=1.0, efield_deg=0.0, efield_type='uniform', scan_storm_event='scan_deg',
                                power_flow_optn='fdns', show=False, datapath=datapath, outpath=outpath)


    pygicfile = ''
    for fnam in os.listdir(outdir):
        n, x = os.path.splitext(fnam)
        if x=='.pygic':
            i = n.find('sample')
            if i>=0:
                pygicfile = os.path.join(outdir, fnam)
                break

    print ("\n >>>>>>>>>>>>> Running gic_results_on_network_map")
    if pygicfile:
        gic_results_on_network_map(pygicfile, outpath, outfext=outfext, show=False)
    else:
        print ("    mapdata file does not exist.\n    {}\n".format(pygicfile))

    print ("\n >>>>>>>>>>>>> Running gic_results_on_network_map_custom")
    if pygicfile:
        gic_results_on_network_map_custom(pygicfile, outpath, outfext=outfext, show=False)
    else:
        print ("    mapdata file does not exist.\n    {}\n".format(pygicfile))

    gictfile = ''
    for fnam in os.listdir(outdir):
        n, x = os.path.splitext(fnam)
        if x=='.csv':
            i = n.find('sample')
            if i>=0:
                gictfile = os.path.join(outdir, fnam)
                break

    print ("\n >>>>>>>>>>>>> Running gicthermal")
    if gictfile:
        gict_result_plots(gictfile, outpath, outfext=outfext, show=False)
    else:
        print ("    GIC results gict CSV file does not exist.\n")

# =============================================================================================================

def run_gicdata_templates(outpath=None):
    excelfile = create_gicdata_template_sample(outpath=outpath, areas=[], showexcel=True)
    excelfile = create_gicdata_template_sample(outpath=outpath, areas=[1,2,3], showexcel=False)
    excelfile = create_gicdata_template_sample(outpath=outpath, areas=[4,5,6], showexcel=False)

# =============================================================================================================

def run_gicdata_transfer(outpath=None):
    excelfile = transfer_gicdata_sample(outpath=outpath, areas=[], showexcel=False)
    excelfile = transfer_gicdata_sample(outpath=outpath, areas=[1,2,3], showexcel=False)
    excelfile = transfer_gicdata_sample(outpath=outpath, areas=[4,5,6], showexcel=False)

# =============================================================================================================

def run_gicdata_excel2gicfile(outpath=None):
    gicfile = gicdata_excel2gicfile(outpath=outpath, areas=[])
    gicfile = gicdata_excel2gicfile(outpath=outpath, areas=[1,2,3])
    gicfile = gicdata_excel2gicfile(outpath=outpath, areas=[4,5,6])

# =============================================================================================================

def run_gicdata_gicfile2excel(outpath=None):
    excelfile = gicdata_gicfile2excel(outpath=outpath, areas=[], showexcel=False)
    excelfile = gicdata_gicfile2excel(outpath=outpath, areas=[1,2,3], showexcel=False)
    excelfile = gicdata_gicfile2excel(outpath=outpath, areas=[4,5,6], showexcel=False)

# =============================================================================================================

def run_gicdata_merge(outpath=None):
    excelfile = gicdata_merge(outpath=outpath, showexcel=False)

# =============================================================================================================

def run_gicdata_all(outpath=None):
    """ Run all gicdata tests.
"""
    run_gicdata_templates(outpath)
    run_gicdata_transfer(outpath)
    run_gicdata_excel2gicfile(outpath)
    run_gicdata_gicfile2excel(outpath)
    run_gicdata_merge(outpath)

# =============================================================================================================
def _run_one_test():

    # Run these one by one in __main__ (just copy each line in __main__ and run).
    #
    # - Function create_gicdata_template_sample() must be run before running gicdata_excel2gicfile().
    # - Functions run_gic_ieee_text_report(..) and run_gic_sample_text_report(..) return pygicfile name.
    #   Use that as input to gic_results_on_network_map(..) and gic_results_on_network_map_custom(..).

    # GIC data tests
    run_gicdata_templates()
    run_gicdata_transfer()
    run_gicdata_excel2gicfile()
    run_gicdata_gicfile2excel()
    run_gicdata_merge()

    # GIC calculation tests
    run_gic_ieee_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='uniform',    scan_storm_event='')
    run_gic_ieee_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='uniform',    scan_storm_event='scan_deg')
    run_gic_ieee_text_report(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark',  scan_storm_event='')
    run_gic_ieee_text_report(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark',  scan_storm_event='scan_deg')
    run_gic_ieee_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='nonuniform', scan_storm_event='')
    run_gic_ieee_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='nonuniform', scan_storm_event='scan_deg')    # scan not allowed, so does not scan

    run_gic_sample_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='uniform',    scan_storm_event='',         power_flow_optn='')
    run_gic_sample_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='uniform',    scan_storm_event='scan_deg', power_flow_optn='fdns')
    run_gic_sample_text_report(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark',  scan_storm_event='',         power_flow_optn='')
    run_gic_sample_text_report(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark',  scan_storm_event='scan_deg', power_flow_optn='fdns')
    run_gic_sample_text_report(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark',  scan_storm_event='scan_mag', power_flow_optn='fdns')
    run_gic_sample_text_report(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark',  scan_storm_event='scan_d_m', power_flow_optn='fdns')
    run_gic_sample_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='nonuniform', scan_storm_event='',         power_flow_optn='')
    run_gic_sample_text_report(efield_mag=1.0, efield_deg=0.0, efield_type='nonuniform', scan_storm_event='scan_deg', power_flow_optn='fdns') # scan not allowed, so does not scan

    run_gic_ieee_text_report_DIY()
    run_gic_ieee_excel_export_DIY(show=True)

    run_gic_sample_excel_export(efield_mag=1.0, efield_deg=0.0, efield_type='uniform',   scan_storm_event='',         power_flow_optn='',     show=True)
    run_gic_sample_excel_export(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark', scan_storm_event='scan_deg', power_flow_optn='fdns', show=True)
    run_gic_sample_excel_export(efield_mag=8.0, efield_deg=0.0, efield_type='benchmark', scan_storm_event='scan_d_m', power_flow_optn='fdns', show=True)

    pygicfile = r"sample_b_8(mag)_0(deg)_scan_d_m_map(deg).pygic"
    gic_results_on_network_map(pygicfile, show=False)

    pygicfile = r"sample_b_8(mag)_0(deg)_scan_d_m_map(deg).pygic"
    gic_results_on_network_map_custom(pygicfile, show=False)

    # ---------------------------------
    run_all_tests(datapath=datapath, outpath=outpath, efields='ubn', scan='d_m', pf='fdns')
    run_all_tests(datapath=None, outpath=None, efields='b', scan='', pf='', outfext='.png')

# =============================================================================================================
if __name__ == '__main__':
    pass
    import psse35

