#[sample_add_substations.py]    Create sample_zils case with various Node Breaker Substation Configurations
# =====================================================================================================
'''This file shows example of adding one or more substation configurations.
Uses sample.raw and sample.seq files.

This example uses substations data [latitude, longitude, RG] from sample_fv4.gic, but applies
different Substation Configurations.
'''
ss_config = {
    1: 'SB',        #'Single Bus',
    2: 'RB',        #'Ring Bus',
    3: 'DBDB',      #'Double Bus double breaker',
    4: 'BH',        #'Breaker and a half',
    5: 'DBSB',      #'Double Bus Single breaker',
    6: 'MBTB',      #'Main Bus Transfer Bus',
    }

sub_dict = {
     1: {'name': 'NILE',        'lat': 34.6135,  'long': -86.67371,  'rg':0.11, 'config':3, 'buses': [101, 102, 151, 201, 211      ]},
     2: {'name': 'YANGTZE',     'lat': 32.5104,  'long': -86.3658 ,  'rg':0.12, 'config':6, 'buses': [152, 153, 3006, 3021, 3022   ]},
     3: {'name': 'ARKANSAS',    'lat': 32.1551,  'long': -83.6794 ,  'rg':0.13, 'config':4, 'buses': [154, 9154                    ]},
     4: {'name': 'COLORADO',    'lat': 33.7051,  'long': -84.6634 ,  'rg':0.15, 'config':5, 'buses': [202, 203, 70202              ]},
     5: {'name': 'MISSISSIPPI', 'lat': 33.3773,  'long': -82.6188 ,  'rg':0.16, 'config':5, 'buses': [204, 205, 206, 208, 215, 9204]},
     6: {'name': 'VOLGA',       'lat': 34.2522,  'long': -82.8363 ,  'rg':0.17, 'config':1, 'buses': [209, 217, 218                ]},
     7: {'name': 'YUKON',       'lat': 33.5956,  'long': -88.798  ,  'rg':0.18, 'config':4, 'buses': [3001, 3002, 3011, 93002      ]},
     8: {'name': 'BRAHMAPUTRA', 'lat': 31.9123,  'long': -88.3123 ,  'rg':0.19, 'config':4, 'buses': [3004, 3005, 703005           ]},
     9: {'name': 'INDUS',       'lat': 31.0133,  'long': -82.0133 ,  'rg':0.2 , 'config':6, 'buses': [3008, 3010, 3012, 3018       ]},
    10: {'name': 'DANUBE',      'lat': 32.0143,  'long': -82.5143 ,  'rg':0.21, 'config':4, 'buses': [155                          ]},
    11: {'name': 'ALLEGHENY',   'lat': 35.2153,  'long': -86.0153 ,  'rg':0.22, 'config':2, 'buses': [207                          ]},
    12: {'name': 'GANGES',      'lat': 33.5163,  'long': -81.0163 ,  'rg':0.23, 'config':2, 'buses': [212                          ]},
    13: {'name': 'OXUS',        'lat': 35.0173,  'long': -82.0173 ,  'rg':0.24, 'config':1, 'buses': [214                          ]},
    14: {'name': 'SALWEEN',     'lat': 34.7183,  'long': -81.0183 ,  'rg':0.25, 'config':1, 'buses': [216                          ]},
    15: {'name': 'HEILONG',     'lat': 35.0193,  'long': -84.0193 ,  'rg':0.26, 'config':3, 'buses': [213                          ]},
    16: {'name': 'ZAIRE',       'lat': 35.003 ,  'long': -87.5203 ,  'rg':0.27, 'config':4, 'buses': [3003, 703003                 ]},
    17: {'name': 'ZAMBEZI',     'lat': 31.4213,  'long': -85.7213 ,  'rg':0.28, 'config':3, 'buses': [3007                         ]},
    18: {'name': 'PILCOMAYO',   'lat': 31.4223,  'long': -81.0223 ,  'rg':0.29, 'config':2, 'buses': [3009                         ]},
    }

rawfnam           = r"sample.raw"
seqfnam           = r"sample.seq"
rawoutfnam        = r"sample"
rawoutfnam_nb     = r"sample_nb"
rawoutfnam_nb_sec = r"sample_nb_sec"
prgfnam           = r"sample_nb_progress.txt"

import os

# ==================================================================================================
def solve_pf():
    import psspy
    pf_options = [1,0,0,1,1,0,99,0]
    psspy.fdns(pf_options)
    psspy.fdns(pf_options)
    ival = psspy.solved()
    return ival

def save_case(rawfile, seqfile, savfnam, outpath):
    import psspy
    psspy.read(0, rawfile)
    psspy.resq(seqfile)
    ival = solve_pf()
    if ival==0:
        savfile = "{}.sav".format(savfnam)
        savfile = os.path.join(outpath, savfile)
        psspy.save(savfile)

# ==================================================================================================

def run(datapath=None, outpath=None):
    import psspy

    if datapath is None:        # use Example folder
        psspy_dir = os.path.dirname(psspy.__file__)
        psse_dir, jnk = os.path.split(psspy_dir)
        datapath = os.path.join(psse_dir, 'Example')

    rawfile = os.path.join(datapath, rawfnam)
    seqfile = os.path.join(datapath, seqfnam)

    if not os.path.exists(rawfile):
        msg = "\n Error- RAW file not found, terminated:\n    {}".format(rawfile)
        print(msg)
        return

    if not os.path.exists(seqfile):
        msg = "\n Error- SEQ file not found, terminated:\n    {}".format(seqfile)
        print(msg)
        return

    if outpath is None:
        outpath = os.path.dirname(__file__)
        outpath = os.path.join(outpath, 'output_sample_nb')
    if not os.path.exists(outpath): os.makedirs(outpath)

    psspy.psseinit()

    prgfile = os.path.join(outpath, prgfnam)

    psspy.progress_output(2,prgfile,[0,0])

    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()
    _s = psspy.getdefaultchar()

    psspy.read(0, rawfile)
    psspy.resq(seqfile)

    ival_raw = solve_pf()
    if ival_raw>0:
        msg = "\n Error - Power flow non converged. RAW file:\n    {}".format(rawfile)
        print(msg)
        return

    sslst = list(sub_dict.keys())
    sslst.sort()

    for ss in sslst:
        vdict = sub_dict[ss]
        name  = sub_dict[ss]['name']
        lat   = sub_dict[ss]['lat']
        lon   = sub_dict[ss]['long']
        rg    = sub_dict[ss]['rg']
        config= sub_dict[ss]['config']
        buses = sub_dict[ss]['buses']

        s_ss = "{:{fill}2d}".format(ss, fill='0')
        s_config = ss_config[config]

        ss_name  = "SS{}_{}_TYP_{}_{}".format(s_ss, name, config, s_config)

        for b in buses:
            psspy.station_build_config(b,ss,_s,config)

        psspy.station_data(ss, [lat, lon, rg], ss_name)

    # Update/Change Node and Switching Device Names
    sid = -1
    flag = 1
    ierr, (ss_num_lst, node_lst) = psspy.anodeint(sid, flag, ['STATION', 'NODE'])
    ierr, (ss_nam_lst,) = psspy.anodechar(sid, flag, ['STATIONNAME'])

    for ss,node,nam in zip(ss_num_lst, node_lst, ss_nam_lst):
        nlst = nam.strip().split('_')
        newlst = ['SS', nlst[1], 'NODE', str(node)]
        newnam = '_'.join(newlst)
        psspy.station_node_chng(ss,node,[_i,_i],newnam)

    ierr, (swd_ss_lst, fromnode_lst, tonode_lst) = psspy.astaswdevint(sid, flag, ['STATION','FROMNODE', 'TONODE'])
    ierr, (swd_ss_nam_lst, swd_id_lst) = psspy.astaswdevchar(sid, flag, ['STATIONNAME','ID'])

    for ss,fm,to,nam,iid in zip(swd_ss_lst, fromnode_lst, tonode_lst, swd_ss_nam_lst, swd_id_lst):
        nlst = nam.strip().split('_')
        newlst = ['SS', nlst[1], 'SWD', str(fm), str(to), iid]
        newnam = '_'.join(newlst)
        psspy.station_swd_chng(ss,fm,to,iid,[_i,_i,_i],[_f,0.0,_f,0.0],newnam)

    # --------------------------------------------------
    # Save un-solved raw file
##    rawfileout = "{}_pf_no.raw".format(rawoutfnam_nb)
##    rawfileout = os.path.join(outpath, rawfileout)
##    psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0,rawfileout)

    # --------------------------------------------------
    # Solve power flow and save raw file
    ival_raw_nb = solve_pf()
    psspy.case_title_data(r'PSS(R)E SAMPLE CASE - ALL RECORD GROUPS WITH SEQ DATA',
                          r'CONTAINS NODE BREAKERS BUT NO SUBSTN SECTIONS, NO ZILS')
    rawfileout_nb = "{}.raw".format(rawoutfnam_nb)
    rawfileout_nb = os.path.join(outpath, rawfileout_nb)
    psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0,rawfileout_nb)

    seqfileout_nb = "{}.seq".format(rawoutfnam_nb)
    seqfileout_nb = os.path.join(outpath, seqfileout_nb)
    psspy.rwsq_2(0,1,[1,1,1,0,0],0,seqfileout_nb)

    if ival_raw_nb>0:
        msg = "\n Error - Power flow non converged after adding substations, SAV file not created."
        print(msg)

    # --------------------------------------------------
    # Create substation sections
    psspy.station_swd_chng(3, 1, 4, '1', [0,_i,_i], [_f,_f,_f,_f], _s)
    psspy.station_swd_chng(3, 2,10, '1', [0,_i,_i], [_f,_f,_f,_f], _s)
    psspy.station_swd_chng(3, 1, 8, '1', [0,_i,_i], [_f,_f,_f,_f], _s)
    psspy.station_swd_chng(3, 2,14, '1', [0,_i,_i], [_f,_f,_f,_f], _s)
    psspy.station_swd_chng(8, 7, 9, '1', [0,_i,_i], [_f,_f,_f,_f], _s)
    psspy.station_swd_chng(8, 8,14, '1', [0,_i,_i], [_f,_f,_f,_f], _s)

    # --------------------------------------------------
    # Solve power flow and save raw file
    ival_raw_nb_sec = solve_pf()
    psspy.case_title_data(r'PSS(R)E SAMPLE CASE - ALL RECORD GROUPS WITH SEQ DATA',
                          r'CONTAINS NODE BREAKER AND SUBSTN SECTIONS, NO ZILS')
    rawfileout_nb_sec = "{}.raw".format(rawoutfnam_nb_sec)
    rawfileout_nb_sec = os.path.join(outpath, rawfileout_nb_sec)
    psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0,rawfileout_nb_sec)

    seqfileout_nb_sec = "{}.seq".format(rawoutfnam_nb_sec)
    seqfileout_nb_sec = os.path.join(outpath, seqfileout_nb_sec)
    psspy.rwsq_2(0,1,[1,1,1,0,0],0,seqfileout_nb_sec)

    if ival_raw_nb_sec>0:
        msg = "\n Error - Power flow non converged after adding substation sections, SAV file not created."
        print(msg)
        return

    # --------------------------------------------------
    # Create .sav files
    if not os.path.exists(seqfile):
        msg = "\n Error- SEQ sile not found:\n    {}".format(seqfile)
        print(msg)
        return

    # base case
    save_case(rawfile, seqfile, rawoutfnam, outpath)

    # base+NB case
    save_case(rawfileout_nb, seqfileout_nb, rawoutfnam_nb, outpath)

    # base+NB+sections case
    save_case(rawfileout_nb_sec, seqfileout_nb_sec, rawoutfnam_nb_sec, outpath)

    # --------------------------------------------------
    # all done

    psspy.progress_output(1,"",[0,0])

    msg = "\n Progress saved in file: {}".format(prgfile)
    print(msg)

# ==================================================================================================
def test1():
    # Run from outside of PSSE GUI.
    # Use input sample RAW/SEQ files from specified folder [datapath].
    # Create output RAW/SEQ files in specified folder [outpath].
    import psse35
    datapath = os.getcwd()
    outpath  = os.getcwd()
    run(datapath=datapath, outpath=outpath)

# --------------------------------------------------
def test2():
    # Run from inside of PSSE GUI.
    # Use input sample RAW/SEQ files from specified folder [datapath].
    # Create output RAW/SEQ files in specified folder [outpath].
    import psse35
    datapath = os.getcwd()
    outpath  = os.getcwd()
    run(datapath=datapath, outpath=outpath)

# --------------------------------------------------
def test3():
    # Run from inside of PSSE GUI.
    # Use input sample RAW/SEQ files from Example folder.
    # Create output RAW/SEQ files in folder Example/output_sample_nb.
    run()

# ==================================================================================================
if __name__=='__main__':
    pass
