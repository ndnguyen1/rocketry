#[gic_demo.py]    GIC Analysis in PSSE
# =====================================================================================================
'''This is an example file showing how to run different GIC Events with and without supplemental
event moving boxes.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example [where XX is psse version number]:
    import psseXX

- call function
    Run various functions from this file as desired.
    See notes in _run_one_test_api(..) (end of this file).
'''

"""
Use any of these keywords to run GIC_8.
Keyword               Default          Description
                                     # INTGOPTNS[]
tielevels           = 0              #  1  Number of levels of inter-tie buses to add to study subsystem
study_year          = 0              #  2  Year number to scale benchmark event GMD storm. These scaling factors account in the influence of geomagnetic latitude on the estimated geoelectric field magnitude and are provided in NERC TPL-007.
sid_supp            = 0              #  3  Subsystem sid for supplemental GMD event
thermal_ana_optn    = 0              #  4  Option for Transformer Thermal Analysis
degscan_pf_optn     = 0              #  5  Option to run power flow for each degree scan calculation
boundary_trn        = 0              #  6  Option to include buses of boundary transformers in study subsystem
worstcase_trn       = 0              #  7  Option for Transformers to include in worst case determination
supp_evt            = 0              #  8  Option for Supplemental event and moving box
supp_box_num        = 0              #  9  Option for number of Supplemental event moving boxes. It is not used when intgoptns(8)=0 and intgoptns(8)=4
brn_seg_efld        = 0              # 10  Option for treatment of the transmission line that intersect with Supplemental event moving box
                                     # REALOPTNS[]
efield_mag          = 8.0            #  1  electric field magnitude in units defined by charoptns(2), not used when charoptns(1)=nonuniform or supplemental
efield_deg          = 0              #  2  electric field direction in degrees, range 0 to 360 degrees, not used when charoptns(1)=nonuniform or supplemental
substation_r        = 0.1            #  3  substation grounding dc resistance in ohms
branch_xbyr         = 30             #  4  transmission line X/R ratio, must be > 0, used to calculate branch DC resistance if R=0.0 in network data
transformer_xbyr    = 30             #  5  transformer winding X/R ratio, must be > 0, used to calculate winding DC resistance if R=0.0 in network data
efield_mag_supp     = 12.0           #  6  supplemental event electric field magnitude in units defined by charoptns(2), not used when charoptns(1)=nonuniform
efield_deg_supp     = 0.0            #  7  local GMD hot spots electric field direction in degrees, range 0 to 360 degrees, not used when charoptns(1)=nonuniform
branch_rac2rdc      = 1.0            #  8  transmission line AC to DC resistance conversion factor, must be > 0
transformer_rac2rdc = 1.0            #  9  transformer winding AC to DC resistance conversion factor, must be > 0
degscan_step        = 10.0           # 10  Degree Scan step size, range 1.0 to 180 degrees
magscan_step        = 4.0            # 11   Magnitude Scan step size, must be > 1.0 V/km
pf_qpct_step        = 100.0          # 12   Percent GMD Mvar loss step size. Total GMD Mvar losses added incrementally to the base case to obtain power flow solution, must be > 1.0
magscan_max         = 20.0           # 13   Magnitude Scan maximum storm strength, must be > 1.0
supp_box_ns_km      = 100.0          # 14   Supplemental event moving box North-South length in km, must be > 1.0, used when intgoptns(8)>0
supp_box_ew_km      = 500.0          # 15   Supplemental event moving box East-West length in km, must be > 1.0, used when intgoptns(8)>0
supp_box_lon_c      = 0.0            # 16   Supplemental event moving box center point longitude in degrees, used only when intgoptns(8)=4
supp_box_lat_c      = 0.0            # 17   Supplemental event moving box center point latitude in degrees, used only when intgoptns(8)=4
                                     # CHAROPTNS[]
efield_type         = "uniform"      #  1  Electric Field Type
efield_unit         = "v/km"         #  2  Units of Electric Field Magnitude
addfile_optn        = "rdch"         #  3  Option to add GIC updates to base case
gic2mvar_optn       = "kfactors"     #  4  Option to select method for GIC to Mvar Calculation
earth_model_name    = ""             #  5  Earth Model Name. A Standard or User defined model name must be provided when Benchmark Event or Non-uniform electric field is to be modeled or Transformer Thermal Analysis is to be performed.
scan_storm_event    = ""             #  6  Option to scan storm event scenarios
power_flow_optn     = ""             #  7 Option to solve Power Flow with GIC losses added to the base case
                                     # EJETOPTNS[]
ejet_million_amps   = 1.0            #  1  eletrojet current in million amperes, must be > 0
ejet_halfwidth_km   = 200.0          #  2  Cauchy distribution half-width in km, must be > 0
ejet_period_min     = 5.0            #  3  period of variation in minutes, must be > 0
ejet_height_km      = 100.0          #  4  height of current in km, must be > 0
ejet_center_deg     = 54.0           #  5  latitude of center of electrojet in degrees
                                     # FILEOPTNS[]
addfile             = ""             #  2  GIC updates to Base Case file name (output).
purgfile            = ""             #  3  RDCH file to remove GIC updates from GIC updated case in working memory to set it back to Base Case network condition (output).
rnwkfile            = ""             #  4  GIC dc resistive network raw file. This represents the dc network used to calculate GIC flow (output).
pygicfile           = "nooutput"     #  5  GIC Results map data file for given Efield magnitude and degrees OR Efield magnitude and degrees scans which give maximum Var losses when scans are performed (output).  This is used by GICMAPS to plot GIC results on network map.
gictfile            = "nooutput"     #  6  Transformer Thermal Analysis GIC(t) CSV file (output).
                                     # REPTOPTNS[]
rptoptn             = -1             #  1  what to report
rptbrn_indv         = 1              #  2  report induced branch voltages
rptdc_busv          = 1              #  3  report DC bus voltages
rptbrn_gic          = 1              #  4  report branch GIC flows
rpttrn_gic          = 1              #  5  report transformer GIC flows
rptstn_gic          = 1              #  6  report substation GIC flows
rpttrn_q            = 1              #  7  report transformer losses
rpt_sid             = 0              #  8  Subsystem sid for report
"""

import sys, os, time, collections

# =========================================================================

def start_timer():
    '''start_time = start_timer()
    Start timer and return time in seconds since the Epoch.
    '''
    start_time = time.time()
    return start_time

# -------------------------------------------------------------------------

def finish_timer(start_time):
    '''timstr = finish_timer(start_time)
    Finish timer and return elapsed time as string.
    where start_time is value returned by start_timer().
    '''
    finish_time = time.time()
    elapsed_sec = finish_time - start_time
    hr,mn1 = divmod(elapsed_sec,3600)
    mn,sc  = divmod(mn1,60)
    timstr = " Elapsed time: Hours=%d , Minutes=%d, Seconds=%g\n" % (hr, mn, sc)
    return timstr

# =========================================================================

# PSSE version Example folder
def get_example_folder():
    import psspy
    pn = os.path.dirname(psspy.__file__)
    p, jnk = os.path.split(pn)
    examdir = os.path.join(p, 'Example')
    return examdir

# -------------------------------------------------------------------------

def get_output_dir(outpath=''):
    if outpath:
        outdir = outpath
        if not os.path.exists(outdir): os.mkdir(outdir)
    else:
        outdir = os.path.dirname(__file__)
        outdir = os.path.join(outdir, 'gic_demo_output')
        if not os.path.exists(outdir): os.mkdir(outdir)

    return outdir

# -------------------------------------------------------------------------

def get_output_filename(fname, outpath=''):

    outdir = get_output_dir(outpath)
    retvfile = os.path.join(outdir, fname)

    return retvfile

# =========================================================================

def run_gic(sid, allbus, outnam, outdir, prg2file, rpt2file, **kwds):

    import psspy

    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()

    name,major,minor,modlvl,date,stat = psspy.psseversion()
    vrsn = "v{}{}{}".format(major,minor,modlvl)

    if 'efield_type' not in kwds: kwds['efield_type'] = "benchmark"

    # add suffix to prg/rpt names (to make them unique, so they are not overwritten.)
    optn_nam_dict = collections.OrderedDict([
        ('efield_deg'      , 'deg' ),
        ('scan_storm_event', ''    ),
        ('power_flow_optn' , ''    ),
        ('boundary_trn'    , 'btrn'),
        ('worstcase_trn'   , 'wtrn'),
        ('supp_evt'        , 'optnbx' ),
        ('brn_seg_efld'    , 'brnseg'),
        ])

    sid_supp, supp_evt, brn_seg = 0, 0, 0
    if 'sid_supp' in kwds: sid_supp = kwds['sid_supp']
    if 'supp_evt' in kwds: supp_evt = kwds['supp_evt']
    if 'supp_box_num' in kwds: supp_box_num = kwds['supp_box_num']
    if 'supp_box_lon_c' in kwds: supp_box_lon_c = kwds['supp_box_lon_c']
    if 'supp_box_lat_c' in kwds: supp_box_lat_c = kwds['supp_box_lat_c']
    if 'brn_seg_efld' in kwds:brn_seg = kwds['brn_seg_efld']

    s_brnseg = ''
    subdir = ''
    outfsfx = kwds['efield_type'][0]
    if (supp_evt==1 and sid_supp>0)             or \
       (supp_evt in [2,3,4] and supp_box_num>0) or \
       (supp_evt==5 and abs(supp_box_lon_c)>0 and abs(supp_box_lat_c)>0):
        outfsfx += "+s"
        s_brnseg = "bseg{}".format(brn_seg)
        if supp_evt in [2,3] and supp_box_num>0:
            subdir = "supp_opbx{}_numbx{}_brnseg{}".format(supp_evt, supp_box_num, brn_seg)

    for k, s_nam in optn_nam_dict.items():
        if k in kwds:
            vin = kwds[k]
            if vin:
                if s_nam:
                    if supp_evt==1:
                        outfsfx += "_sid"
                    else:
                        outfsfx += "_{}{}".format(s_nam, vin)
                else:
                    outfsfx += "_{}".format(vin)

    if s_brnseg:
        outfsfx += "_{}".format(s_brnseg)

    outdir = get_output_dir(outdir)
    if subdir:
        outdir = os.path.join(outdir, subdir)
        if not os.path.exists(outdir): os.mkdir(outdir)

    if prg2file:
        nam = "{}_{}_progress.txt".format(outnam, outfsfx)
        prgfile = os.path.join(outdir, nam)

    if rpt2file:
        nam = "{}_{}_report.txt".format(outnam, outfsfx)
        rptfile = os.path.join(outdir, nam)

    # Create output file names when they are not provided
    for sfx in ['add', 'purg', 'rnwk', 'pygic', 'gict']:
        k = "{}file".format(sfx)
        if k not in kwds:
            s0 = sfx
            if sfx=='pygic': s0 = 'map'
            fnam = "{}_{}_{}".format(outnam, outfsfx, s0)
            kwds[k] = os.path.join(outdir, fnam)

    # run activity gic_8
    if prg2file: psspy.progress_output(2,prgfile,[0,0])
    if rpt2file: psspy.report_output(2,rptfile,[0,0])

    start_time = start_timer()
    psspy.gic_8(sid, allbus, **kwds)
    timstr = finish_timer(start_time)

    if prg2file: psspy.progress_output(1,"",[0,0])
    if rpt2file: psspy.report_output(1,"",[0,0])

    print(timstr)

    if rpt2file:
        print("  --------- Report saved to: {} ".format(rptfile))

# =========================================================================

def run_test_sample(**optns):
    import psspy
    psspy.psseinit()

    gicfilevrsn = optns.get('gicfilevrsn', 4)

    if gicfilevrsn>4:
        savfnam = r'sample_nb.sav'      # SAV file with Node Breaker Modeling
        gicfnam = r'sample_fv5.gic'     # GIC file version 5
    else:
        savfnam = r'sample.sav'         # SAV file with NO Node Breaker Modeling
        gicfnam = r'sample_fv4.gic'     # GIC file version 4

    examdir = get_example_folder()

    savfile = os.path.join(examdir, savfnam)
    gicfile = os.path.join(examdir, gicfnam)

    sid      = 0
    allbus   = 1

    outnam, jnk = os.path.splitext(savfnam)

    outdir   = get_output_dir()
    prg2file = True
    rpt2file = True

    study_year = 2019
    earth_model_name = 'SHIELD'

    kwds = {}
    kwds['study_year'] = study_year
    kwds['earth_model_name'] = earth_model_name
    kwds['addfile']  = ''
    kwds['purgfile'] = ''

    for k, v in optns.items():
        if k=='gicfilevrsn': continue
        kwds[k] = v

    if 'thermal_ana_optn' not in kwds:
        kwds['thermal_ana_optn'] = -1

    psspy.case(savfile)
    psspy.gic_read(gicfile)

    if 'sid_supp' in kwds:
        kwds['sid_supp'] = 4
        areas = [5]
        ierr = psspy.bsys(kwds['sid_supp'], numarea=len(areas), areas=areas)

    run_gic(sid, allbus, outnam, outdir, prg2file, rpt2file, **kwds)

# =========================================================================

def run_gicmaps(pygicfile):
    import arrbox.gicmaps

    outdir   = get_output_dir()
    fpth, nx = os.path.split(pygicfile)
    outnam, fxtn = os.path.splitext(nx)
    if not fpth: pygicfile = os.path.join(outdir, pygicfile)

    outdir_maps = os.path.join(outdir, 'maps')
    if not os.path.exists(outdir_maps): os.mkdir(outdir_maps)

    gicmapsobj = arrbox.gicmaps.GICMAPS(pygicfile)

    if gicmapsobj.ierr: return

    gicmapsobj.enable_draw_supp_box()

    pngfile = get_output_filename("{}_ssflow.png".format(outnam), outdir_maps)

    sublst = list(gicmapsobj.pygicobj.substation.keys())
    gicmapsobj.annotate_substations(sublst, color='blue', fontsize=10)

    ax, fig, basemap, anptobj = gicmapsobj.plot_substation_gicflows(pngfile, markersize=20)

    oufile_seg = get_output_filename("{}_brnsegments.txt".format(outnam), outdir_maps)
    gicmapsobj.report_supp_box_line_segments(rptfile=oufile_seg)

    oufile_evt = get_output_filename("{}_element_events.txt".format(outnam), outdir_maps)
    gicmapsobj.report_network_element_events(rptfile=oufile_evt)

    gicmapsobj.plots_show()

# =========================================================================

def _template_sample():
    # 1) Benchmark event
    #    No storm scan, No supplemental event, No power flow solution
    run_test_sample(efield_type='benchmark', gicfilevrsn=5)

    # 2) Supplemental event
    #    No storm scan, No power flow solution
    run_test_sample(efield_type='supplemental', gicfilevrsn=5)

    # 3) Benchmark + Supplemental event
    #    Supplemental event defined by subsystem
    #    No storm scan, No power flow solution
    run_test_sample(efield_type='benchmark', supp_evt=1, sid_supp=4, gicfilevrsn=5)

    # 4) Benchmark + Supplemental event
    #    Supplemental event defined by Moving Box,
    #    Rank substations with maximum GIC flows as center of the moving box
    #    No storm scan, No power flow solution
    run_test_sample(efield_type='benchmark', supp_evt=2, supp_box_num=2, gicfilevrsn=5)

    # 5) Benchmark + Supplemental event
    #    Supplemental event defined by Moving Box,
    #    Rank transformers with maximum GIC flows as center of the moving box
    #    No storm scan, No power flow solution
    run_test_sample(efield_type='benchmark', supp_evt=3, supp_box_num=2, gicfilevrsn=5)

    # 6) Benchmark + Supplemental event
    #    Supplemental event defined by Moving Box,
    #    Use substation number provided as center of the moving box
    #    No storm scan, No power flow solution
    run_test_sample(efield_type='benchmark', supp_evt=4, supp_box_num=10, gicfilevrsn=5)

    # 7) Benchmark + Supplemental event
    #    Supplemental event defined by Moving Box,
    #    Use location provided as center of the moving box
    #    No storm scan, No power flow solution
    run_test_sample(efield_type='benchmark', supp_evt=5, supp_box_lon_c=-82.0, supp_box_lat_c=32.0, gicfilevrsn=5)

    # 8) Benchmark + Supplemental event
    #    Supplemental event defined by Moving Box,
    #    Rank substations with maximum GIC flows as center of the moving box

    #    Degree Scan with specified settings [step=1 deg, add Qloss in steps of 100%]
    #    FDNS - run PowerFlow for each scan step
    #       Number of degree scans = 1+ 180/degscan_step = 181
    #       Number PF due % Qstep = 100/pf_qpct_step = 5
    #       Number PF due to moving boxes = supp_box_num = 20
    #    Number of GIC calculations = 181 (for ranking) + 181*20 (one each supp box) = 3801
    #    Number of PF solved = 181*20*5 = 18100
##    run_test_sample(efield_type='benchmark', supp_evt=2, supp_box_num=20,
##                    scan_storm_event="scan_deg", power_flow_optn='fdns',
##                    degscan_pf_optn=1, degscan_step=1, pf_qpct_step=20,
##                    gicfilevrsn=5)

    print(" all done - _template_sample")

# =========================================================================
def _run_one_test_api():
    # Just run one of these calls as desired.

    run_test_sample(efield_type='benchmark')
    run_test_sample(efield_type='benchmark', gicfilevrsn=5)
    run_test_sample(efield_type='benchmark', gicfilevrsn=4)
    run_test_sample(efield_type='supplemental')
    run_test_sample(efield_type='benchmark', supp_evt=1, sid_supp=4)
    run_test_sample(efield_type='benchmark', supp_evt=2, supp_box_num=2)
    run_test_sample(efield_type='benchmark', supp_evt=3, supp_box_num=2)
    run_test_sample(efield_type='benchmark', supp_evt=4, supp_box_num=10)
    run_test_sample(efield_type='benchmark', supp_evt=5, supp_box_lon_c=-82.0, supp_box_lat_c=32.0)
    run_test_sample(efield_type='benchmark', supp_evt=2, supp_box_num=20,
                    scan_storm_event="scan_deg", power_flow_optn='fdns',
                    degscan_pf_optn=1, degscan_step=1, pf_qpct_step=20)

    # Creat a function similar to "run_test_sample(..)"
    # - to use any power flow study cases
    # - define common arguments
    # - output directory etc
    # Then use that function to run the GIC study of interest.

# =========================================================================
def _run_one_test_maps():
    # Just run one of these calls as desired.
    # The 'pygic' files created by tests in "_run_one_test_api" serve as input
    # for these tests.

    run_gicmaps(r"sample_b+s_sid_bseg0_map(deg)-oldVrsn.pygic")
    run_gicmaps(r"sample_b_map(deg).pygic")
    run_gicmaps(r"sample_s_map(deg).pygic")
    run_gicmaps(r"sample_b+s_sid_bseg0_map(deg).pygic")
    run_gicmaps(r"sample_b+s_optnbx4_bseg0_map(deg).pygic")
    run_gicmaps(r"sample_b+s_optnbx5_bseg0_map(deg).pygic")
    run_gicmaps(r".\gic_demo_output\supp_opbx2_numbx2_brnseg0\sample_b+s_optnbx2_bseg0_map(deg)_supp_box1.pygic")
    run_gicmaps(r".\gic_demo_output\supp_opbx2_numbx2_brnseg0\sample_b+s_optnbx2_bseg0_map(deg)_supp_box2.pygic")
    run_gicmaps(r".\gic_demo_output\supp_opbx3_numbx2_brnseg0\sample_b+s_optnbx3_bseg0_map(deg)_supp_box1.pygic")
    run_gicmaps(r".\gic_demo_output\supp_opbx3_numbx2_brnseg0\sample_b+s_optnbx3_bseg0_map(deg)_supp_box2.pygic")

# =========================================================================
if __name__=="__main__":
    pass
    #import psse35
