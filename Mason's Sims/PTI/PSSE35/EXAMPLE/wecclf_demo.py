#[wecclf_demo.py]  Demo for running WECCLF Converter from Python Scripts
# ====================================================================================================
'''
WECCLF converter is used to convert PSLF Power Flow (.epc) and Sequence (.seq) Data
to PSSE Power Flow (.raw) and Sequence (.seq) Data.

Additionally it also compares PSSE and PSLF Power Flow Solutions.

WECCLF converter can be run from its own GUI:
>>> import wecclf_gui
>>> wecclf_gui.main()

This scripts shows different ways to run WECCLF Converter from Python Scripts.
'''

import os, sys

# ====================================================================================================

def run_wecclf(pslf_version, pslf_epcfile, psse_version, workdir=os.getcwd(), testnum=2):

    import ndppslf

    if not os.path.exists(pslf_epcfile):
        msgtxt = " EPC file does not exist, WECCLF converter not run.\n    {}".format(pslf_epcfile)
        print(msgtxt)
        return

    p, nx = os.path.split(pslf_epcfile)
    nam, ext  = os.path.splitext(nx)

    outdir = 'wecclf_demo_output_v{}'.format(psse_version)
    workdir = os.path.join(workdir, outdir)
    if not os.path.exists(workdir): os.makedirs(workdir)

    rawfnam  = "{}_v{}.raw".format(nam, psse_version)
    rawfile  = os.path.join(workdir, rawfnam)

    prgsplit = False
    prgfull  = True

    if testnum==1:
        #(1) Convert and compare power flow solutions using all default options
        ndppslf.pslf2psse(pslf_version, pslf_epcfile, psse_version,
            psse_rawfile=rawfile, ratea=1, rateb=2, ratec=3,
            workdir=workdir, prgsplit=prgsplit, prgfull=prgfull)

    elif testnum==2:
        #(2) Convert only
        ndppslf.pslf2psse(pslf_version, pslf_epcfile, psse_version,
            psse_rawfile=rawfile, do_psse_pfsoln=False,
            workdir=workdir, compare_pfsoln=False, prgfull=prgfull, prgsplit=prgsplit)

    elif testnum==3:
        #(3) Convert and compare power flow solutions using options from epcfile and options as specified
        ndppslf.pslf2psse(pslf_version, pslf_epcfile, psse_version,
            psse_rawfile=rawfile,
            workdir=workdir, prgsplit=prgsplit, prgfull=prgfull,
            pfmethod='RSOL', use_epcoptns=False, itmxn=100, flat=0, varlmt=99, nondiv=0,
            rsol_pfmethod='FDNS', rsol_solnfail=0, rsol_mismatch=500.0, rsol_varband=5.0,
            compare_pfsoln=True, show_ntop=-1, toler_vpu=-0.001,
            toler_pgen=-1.0, toler_qgen=-1.0, toler_bact=-0.01, toler_pitf=-1.0, toler_qitf=-1.0)

    elif testnum==4:
        #(4) Convert and compare power flow solutions using options as specified
        ndppslf.pslf2psse(pslf_version, pslf_epcfile, psse_version,
            psse_rawfile=rawfile, psse_autofile='',
            workdir=workdir, prgsplit=prgsplit, prgfull=prgfull,
            pfmethod='RSOL', use_epcoptns=False, itmxn=100, toln=0.1, thrshz=0.0001, tap=0,
            area=0, phshft=0, dctap=1, swsh=1,flat=0, varlmt=99, nondiv=0,
            rsol_pfmethod='FDNS', rsol_solnfail=0, rsol_mismatch=500.0, rsol_varband=5.0,
            compare_pfsoln=True, show_ntop=100, toler_vpu=0.02, toler_pgen=1.0,
            toler_qgen=-1.0, toler_bact=0.01, toler_pitf=1.0, toler_qitf=-1.0)

# ====================================================================================================

def _run_how():
    pass
##    # EPC file version=18
##    epcfile18 = r"sample18.epc"
##    run_wecclf(18, epcfile18, psse_version=34, workdir=os.getcwd(), testnum=3)
##
##    # EPC file version=19
##    epcfile19 = r"sample19.epc"
##    run_wecclf(19, epcfile19, psse_version=34, workdir=os.getcwd(), testnum=3)
##
##    # EPC file version=21
##    epcfile21 = r"sample21.epc"
##    run_wecclf(21, epcfile21, psse_version=34, workdir=os.getcwd(), testnum=3)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
if __name__ == '__main__':
    pass
    # Here "import psse34" or "import psse35" as appropriate.
    # Then run required test. See _run_how() above for reference.
