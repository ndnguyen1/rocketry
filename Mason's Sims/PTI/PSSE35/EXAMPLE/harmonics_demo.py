#[harmonics_demo.py]    Harmonics Analysis in PSSE
# =====================================================================================================
'''This is an example file showing how to run Harmonics Analysis.
   Plot frequency scan results.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example [where XX is psse version number]:
    import psseXX

- call function
    Run various functions from this file as desired.
    Refer test1(..) ... functions towards end of this file.
'''

"""
Use any of these keywords to run har_analysis.
Keyword     Default     Description
                      # INTGAR[]
anaoptn     = 0       # 1 analysis option:    =0 fscan and dstn; =1 only fscan; =2 only dstn
linmdl      = 0       # 2 line model option:  =0 nominal pi; =1 long line with skin effect;
                      #                       =2 long line but no skin effect
dstnbuop    = 0       # 3 bus option in dstn: =0 all buses; =1 only study subsystem buses
dstnrptop   = 0       # 4 bus option in dstn: =0 only THDs; =1 THDs + contributions
imachimpop  = 0       # 5 induction machine impedance option =0 from power flow data; =1 from sequene data
dcimpop     = 0       # 6 2TDC, VSCDC and MTDC equivalent impedance option in fscan =0 block; 1=consider
triplenop   = 0       # 7 Triplen Harmonics Option in distortion calculations =0 ignore; =1 consider
genimpop    = 0       # 8 generatir impedance option:  =0 Use ZSORCE impedance from power flow data
                      #                                =1 Use subtransient impedance from sequence data
                      #                                =2 Use transient impedance from sequence data
                      #                                =3 Use synchronous impedance from sequence data
                      #                                =4 Use negative sequence impedance from sequence data
                      # REALAR[]
hord_min    =  0.1    # 1 Minimum Harmonic Order
hord_max    = 50.0    # 2 Maximum Harmonic Order
hord_stp    =  0.1    # 3 Harmonic Order Step
                      # FILEAR[]
hrsfile     = ''      # 1 Binary Results File Name (.hrs)
dstnfile    = ''      # 2 Distortion Calculation Report File Name (.txt)
resnfile    = ''      # 3 Frequency Scan Resonance Report File Name (.txt)
"""

import sys, os, math, traceback

# ==============================================================================

# This data is from file CASE1TB.XLS of IEEE Task Force on Harmonics Modeling & Simulation
# Frequency Scan Thevenin Impedance
# Distributed Line Model: ZRdist, ZXdist, Zdist
# Pi Line Model: Zpi

#    HORD       , ZRdist        ,  ZXdist       , Zdist , Zpi
_ieee_tf_scan_results = [
    [1.00	, 0.0534	, 0.2197	, 0.226	, 0.226  ],
    [1.33	, 0.0793	, 0.3239	, 0.334	, 0.334  ],
    [1.67	, 0.1371	, 0.4711	, 0.491	, 0.492  ],
    [2.00	, 0.2075	, 0.5667	, 0.603	, 0.606  ],
    [2.33	, 0.5381	, 0.9926	, 1.129	, 1.136  ],
    [2.67	, 1.7230	, 1.1320	, 2.062	, 2.081  ],
    [3.00	, 2.0150	, -0.9333	, 2.221	, 2.217  ],
    [3.33	, 0.7628	, -1.0731	, 1.317	, 1.312  ],
    [3.67	, 0.3951	, -0.7590	, 0.856	, 0.855  ],
    [4.00	, 0.3626	, -0.5387	, 0.649	, 0.652  ],
    [4.33	, 0.3141	, -0.7507	, 0.814	, 0.806  ],
    [4.67	, 0.0891	, -0.5594	, 0.566	, 0.564  ],
    [5.00	, 0.0570	, -0.4405	, 0.444	, 0.443  ],
    [5.33	, 0.0460	, -0.3673	, 0.370	, 0.370  ],
    [5.67	, 0.0430	, -0.3170	, 0.320	, 0.320  ],
    [6.00	, 0.0378	, -0.2885	, 0.291	, 0.291  ],
    [6.33	, 0.0219	, -0.2551	, 0.256	, 0.256  ],
    [6.67	, 0.0166	, -0.2223	, 0.223	, 0.224  ],
    [7.00	, 0.0144	, -0.1957	, 0.196	, 0.197  ],
    [7.33	, 0.0131	, -0.1732	, 0.174	, 0.175  ],
    [7.67	, 0.0122	, -0.1537	, 0.154	, 0.155  ],
    [8.00	, 0.0116	, -0.1364	, 0.137	, 0.138  ],
    [8.33	, 0.0112	, -0.1211	, 0.122	, 0.123  ],
    [8.67	, 0.0105	, -0.1076	, 0.108	, 0.109  ],
    [9.00	, 0.0091	, -0.0949	, 0.095	, 0.096  ],
    [9.33	, 0.0077	, -0.0823	, 0.083	, 0.084  ],
    [9.67	, 0.0072	, -0.0702	, 0.071	, 0.071  ],
    [10.00	, 0.0071	, -0.0593	, 0.060	, 0.060  ],
    [10.33	, 0.0067	, -0.0498	, 0.050	, 0.050  ],
    [10.67	, 0.0051	, -0.0409	, 0.041	, 0.041  ],
    [11.00	, 0.0029	, -0.0311	, 0.031	, 0.031  ],
    [11.33	, 0.0014	, -0.0207	, 0.021	, 0.021  ],
    [11.67	, 0.0008	, -0.0105	, 0.011	, 0.010  ],
    [12.00	, 0.0007	, -0.0009	, 0.001	, 0.001  ],
    [12.33	, 0.0007	, 0.0081	, 0.008	, 0.008  ],
    [12.67	, 0.0008	, 0.0168	, 0.017	, 0.017  ],
    [13.00	, 0.0008	, 0.0251	, 0.025	, 0.025  ],
    [13.33	, 0.0009	, 0.0331	, 0.033	, 0.033  ],
    [13.67	, 0.0010	, 0.0410	, 0.041	, 0.041  ],
    [14.00	, 0.0010	, 0.0487	, 0.049	, 0.049  ],
    [14.33	, 0.0010	, 0.0562	, 0.056	, 0.057  ],
    [14.67	, 0.0010	, 0.0636	, 0.064	, 0.065  ],
    [15.00	, 0.0010	, 0.0709	, 0.071	, 0.072  ],
    [15.33	, 0.0010	, 0.0782	, 0.078	, 0.080  ],
    [15.67	, 0.0009	, 0.0855	, 0.085	, 0.087  ],
    [16.00	, 0.0009	, 0.0927	, 0.093	, 0.095  ],
    [16.33	, 0.0009	, 0.0998	, 0.100	, 0.102  ],
    [16.67	, 0.0009	, 0.1070	, 0.107	, 0.110  ],
    [17.00	, 0.0010	, 0.1141	, 0.114	, 0.117  ],
    [17.33	, 0.0010	, 0.1213	, 0.121	, 0.124  ],
    [17.66	, 0.0010	, 0.1285	, 0.129	, 0.132  ],
    [18.00	, 0.0010	, 0.1357	, 0.136	, 0.139  ],
    [18.33	, 0.0011	, 0.1430	, 0.143	, 0.147  ],
    [18.66	, 0.0011	, 0.1504	, 0.150	, 0.154  ],
    [19.00	, 0.0012	, 0.1579	, 0.158	, 0.162  ],
    [19.33	, 0.0012	, 0.1654	, 0.165	, 0.170  ],
    [19.66	, 0.0013	, 0.1732	, 0.173	, 0.178  ],
    [20.00	, 0.0014	, 0.1811	, 0.181	, 0.186  ],
    [20.33	, 0.0015	, 0.1892	, 0.189	, 0.194  ],
    [20.66	, 0.0016	, 0.1975	, 0.198	, 0.203  ],
    [21.00	, 0.0018	, 0.2062	, 0.206	, 0.211  ],
    [21.33	, 0.0019	, 0.2153	, 0.215	, 0.218  ],
    [21.66	, 0.0022	, 0.2247	, 0.225	, 0.224  ],
    [22.00	, 0.0025	, 0.2348	, 0.235	, 0.229  ],
    [22.33	, 0.0029	, 0.2456	, 0.246	, 0.236  ],
    [22.66	, 0.0034	, 0.2573	, 0.257	, 0.245  ],
    [23.00	, 0.0041	, 0.2703	, 0.270	, 0.254  ],
    [23.33	, 0.0052	, 0.2850	, 0.285	, 0.263  ],
    [23.66	, 0.0068	, 0.3023	, 0.302	, 0.273  ],
    [24.00	, 0.0094	, 0.3239	, 0.324	, 0.282  ],
    [24.33	, 0.0142	, 0.3530	, 0.353	, 0.292  ],
    [24.66	, 0.0258	, 0.3988	, 0.400	, 0.302  ],
    [25.00	, 0.0767	, 0.4914	, 0.497	, 0.313  ],
    [25.33	, 0.3804	, 0.4516	, 0.590	, 0.324  ],
    [25.66	, 0.2886	, 0.2076	, 0.355	, 0.336  ],
    [26.00	, 0.1861	, 0.1507	, 0.239	, 0.350  ],
    [26.33	, 0.0983	, 0.1640	, 0.191	, 0.366  ],
    [26.66	, 0.0543	, 0.2017	, 0.209	, 0.391  ],
    [27.00	, 0.0341	, 0.2359	, 0.238	, 0.384  ],
    [27.33	, 0.0239	, 0.2646	, 0.266	, 0.348  ],
    [27.66	, 0.0184	, 0.2898	, 0.290	, 0.374  ],
    [28.00	, 0.0152	, 0.3130	, 0.313	, 0.392  ],
    [28.33	, 0.0133	, 0.3355	, 0.336	, 0.407  ],
    [28.66	, 0.0122	, 0.3581	, 0.358	, 0.422  ],
    [29.00	, 0.0117	, 0.3815	, 0.382	, 0.437  ],
    [29.33	, 0.0118	, 0.4067	, 0.407	, 0.451  ],
    [29.66	, 0.0123	, 0.4343	, 0.434	, 0.466  ],
    [30.00	, 0.0133	, 0.4655	, 0.466	, 0.481  ],
    [30.33	, 0.0151	, 0.5019	, 0.502	, 0.497  ],
    [30.66	, 0.0179	, 0.5456	, 0.546	, 0.513  ],
    [31.00	, 0.0225	, 0.6004	, 0.601	, 0.530  ],
    [31.33	, 0.0301	, 0.6723	, 0.673	, 0.547  ],
    [31.66	, 0.0439	, 0.7735	, 0.775	, 0.565  ],
    [32.00	, 0.0731	, 0.9304	, 0.933	, 0.583  ],
    [32.33	, 0.1517	, 1.2148	, 1.224	, 0.603  ],
    [32.66	, 0.5070	, 1.8932	, 1.960	, 0.623  ],
    [33.00	, 4.5494	, 1.5400	, 4.803	, 0.645  ],
    [33.33	, 0.7725	, -1.1678	, 1.400	, 0.667  ],
    [33.66	, 0.2861	, -0.3206	, 0.430	, 0.691  ],
    [34.00	, 0.3196	, 0.1241	, 0.343	, 0.716  ],
    [34.33	, 0.9273	, 0.2502	, 0.960	, 0.743  ],
    [34.66	, 0.5444	, -0.5749	, 0.792	, 0.771  ],
    [35.00	, 0.1669	, -0.3331	, 0.373	, 0.801  ],
    [35.33	, 0.0812	, -0.1640	, 0.183	, 0.834  ],
    [35.66	, 0.0508	, -0.0578	, 0.077	, 0.870  ],
    [36.00	, 0.0367	, 0.0179	, 0.041	, 0.909  ],
    [36.33	, 0.0293	, 0.0777	, 0.083	, 0.952  ],
    [36.66	, 0.0255	, 0.1291	, 0.132	, 1.001  ],
    [37.00	, 0.0242	, 0.1773	, 0.179	, 1.058  ],
    [37.33	, 0.0257	, 0.2270	, 0.228	, 1.125  ],
    [37.66	, 0.0320	, 0.2852	, 0.287	, 1.201  ],
    [38.00	, 0.0506	, 0.3663	, 0.370	, 1.266  ],
    [38.33	, 0.1213	, 0.5124	, 0.527	, 1.224  ],
    [38.66	, 0.6464	, 0.7361	, 0.980	, 1.079  ],
    [39.00	, 0.4533	, -0.3164	, 0.553	, 1.047  ],
    [39.33	, 0.1071	, -0.0794	, 0.133	, 1.102  ],
    [39.66	, 0.0490	, 0.0401	, 0.063	, 1.178  ],
    [40.00	, 0.0302	, 0.1057	, 0.110	, 1.260  ],
    ]

# Reference:
# "Test Systems for Harmonics Modeling and Simulation",
# IEEE Transactions on Power Delivery, Vol. 11, No. 1, January 1996, Pages 466-474
#     Bus, Nominal kV,  LF Volts pu, LF Ang deg,  THD%
_ieee_tf_dstn_pf_thd_results = [
    [   1,      230.0,       1.0600,       0.00,  1.767 ],
    [   2,      230.0,       1.0450,      -5.68,  2.177 ],
    [   3,      230.0,       1.0427,     -15.30,  1.516 ],
    [   4,      230.0,       1.0282,     -11.41,  0.755 ],
    [   5,      230.0,       1.0337,      -9.82,  1.462 ],
    [   6,      115.0,       1.0700,     -15.87,  0.468 ],
    [   7,      230.0,       1.0193,     -14.47,  0.423 ],
    [   8,       13.8,       1.0209,     -14.49,  0.522 ],
    [   9,      115.0,       1.0147,     -16.09,  0.482 ],
    [  10,      115.0,       1.0168,     -16.33,  0.421 ],
    [  11,      115.0,       1.0394,     -16.21,  0.394 ],
    [  12,      115.0,       1.0528,     -16.72,  0.391 ],
    [  13,      115.0,       1.0458,     -16.73,  0.376 ],
    [  14,      115.0,       1.0154,     -17.39,  0.343 ],
    [ 301,       35.4,       1.0417,     -16.18,  9.169 ],
    [ 302,       35.4,       1.0417,     -16.18,  9.169 ],
    ]

#   Hord,   %mag,    deg
_ieee_tf_dstn_cursrc_hvdc = [
    [  1, 100.00, -49.56 ],
    [  5,  19.41, -67.77 ],
    [  7,  13.09,  11.9  ],
    [ 11,   7.58,  -7.13 ],
    [ 13,   5.86,  68.57 ],
    [ 17,   3.79,  46.53 ],
    [ 19,   3.29, 116.46 ],
    [ 23,   2.26,  87.47 ],
    [ 25,   2.41, 159.32 ],
    [ 29,   1.93, 126.79 ],
    ]

_ieee_tf_dstn_cursrc_tcr = [
    [  1, 100.00,   46.92 ],
    [  5,   7.02, -124.40 ],
    [  7,   2.50,  -29.87 ],
    [ 11,   1.36,  -23.75 ],
    [ 13,   0.75,   71.50 ],
    [ 17,   0.62,   77.12 ],
    [ 19,   0.32,  173.43 ],
    [ 23,   0.43,  178.02 ],
    [ 25,   0.13,  -83.45 ],
    [ 29,   0.40,  -80.45 ],
    ]

# ==============================================================================

def get_ieee_tf_scan_results():
    """Get IEEE Harmonics Task Force Test Case Frequency Scan Results.
    """
    hord_lst, zcal_lst, zdst_lst, zpi_lst = [], [], [], []
    for eachlist in _ieee_tf_scan_results:
        h, zr, zx, z1d, z1pi = eachlist
        zrx = complex(zr, zx)
        z = abs(zrx)
        hord_lst.append(h)
        zcal_lst.append(z)
        zdst_lst.append(z1d)
        zpi_lst.append(z1pi)

    return hord_lst, zcal_lst, zdst_lst, zpi_lst

# ==============================================================================

def get_ieee_tf_dstn_pf_thd_results():
    """Get IEEE Harmonics Task Force Test Case Distortion Calculation Results.
    """
    tf_keytup = ('bus', 'basekv', 'vmag', 'vang', 'thd')

    tfresults_pf_thd_dict = {}
    for row in _ieee_tf_dstn_pf_thd_results:
        for dk, val in zip(tf_keytup, row):
            if dk=='bus':
                bus = val
                tfresults_pf_thd_dict[bus] = {}
            else:
                tfresults_pf_thd_dict[bus][dk] = val

    return tfresults_pf_thd_dict

# ==============================================================================

def get_ieee_tf_dstn_cursrc():
    """Get IEEE Harmonics Task Force Test Case Harmonic Current Source Spectrum.
    """

    tfresults_cursrc_dict = {'hvdc':{}, 'tcr':{}}

    for eachrow in _ieee_tf_dstn_cursrc_hvdc:
        hord, imag, iang = eachrow
        tfresults_cursrc_dict['hvdc'][hord] = {'imag':imag, 'iang':iang}

    tfresults_cursrc_tcr_dict = {}
    for eachrow in _ieee_tf_dstn_cursrc_tcr:
        hord, imag, iang = eachrow
        tfresults_cursrc_dict['tcr'][hord] = {'imag':imag, 'iang':iang}

    return tfresults_cursrc_dict

# ==============================================================================

def get_resn_legends(peak_lst_h, peak_lst_rx, valley_lst_h=None, valley_lst_rx=None):
    """Get Frequency Scan Resonance legends.
    """
    txtlst = []
    txtlst.append("")
    txtlst.append("Parallel (peaks)")
    if peak_lst_rx:
        txtlst.append("Hord, Z")
        for h, pu in zip(peak_lst_h, peak_lst_rx):
            txt = "{:g}, {:g}".format(h, pu)
            txtlst.append(txt)
    else:
        txt = " None"
        txtlst.append(txt)

    if valley_lst_h:
        txtlst.append("")
        txtlst.append("Series (valleys)")
        if valley_lst_rx:
            txtlst.append("H,  Z")
            for h, pu in zip(valley_lst_h, valley_lst_rx):
                txt = "{:4.2f}, {:5.3f}".format(h, pu)
                txtlst.append(txt)
        else:
            txt = " None"
            txtlst.append(txt)

    return txtlst

# ==============================================================================
def _write_verbose_report(txt, report):
    if report is not None:
        report(txt)

class _SimpleObject(object):
    """Used for creating dummy object and set attributes as needed.
    """
    pass

def _set_rsn_object(**kwds):
    rsnobj = _SimpleObject()
    for k in ['x1', 'y1', 'x2', 'y2', 'inam', 'hidx', 'rflg']:
        setattr(rsnobj, k, kwds[k])
    return rsnobj

def _set_resn_pt_state(pctc, pctmx1, dpctpn1, pctmx2, dpctpn2, dltp=None, dltn=None):
    ok1, ok2 = False, False

    ok_pctc1 = pctc>=pctmx1
    ok_pctc2 = pctc>=pctmx2

    if dltp is not None:
        ok_dltp1 = dltp>=dpctpn1
        ok_dltp2 = dltp>=dpctpn2

    if dltn is not None:
        ok_dltn1 = dltn>=dpctpn1
        ok_dltn2 = dltn>=dpctpn2

    if dltp is None:
        ok1 = ok_pctc1 and ok_dltn1
        ok2 = ok_pctc2 and ok_dltn2
    elif dltn is None:
        ok1 = ok_pctc1 and ok_dltp1
        ok2 = ok_pctc2 and ok_dltp2
    else:
        ok1 = ok_pctc1 and (ok_dltp1 or ok_dltn1)
        ok2 = ok_pctc2 and (ok_dltp2 or ok_dltn2)

    found = ok1 or ok2

    return found

def _filter_rsn_pkvls(resn_pkvls, ymxpk, pctmx1, dpctpn1, pctmx2, dpctpn2, report):

    resn_pks_hord, resn_pks_zmag = [], []

    txtlst = []
    txtlst.append("")
    txtlst.append("Parallel (peaks)")

    if not resn_pkvls:
        txt = " None"
        txtlst.append(txt)

        txt = "\n".join(txtlst)
        _write_verbose_report(txt, report)

        return resn_pks_hord, resn_pks_zmag

    # ------------

    nnlst = len(resn_pkvls)

    txtlst.append("   X1,     Y1,     X2,     Y2,  %Ymax,  %dltY,  Found")

    for ii in range(nnlst):

        pt_crnt = resn_pkvls[ii]
        inam = pt_crnt.inam
        if inam!='peak': continue

        ipt_p = False
        ipt_n = False

        if ii==0:
            if nnlst>1:
                ipt_n = True
                pt_next = resn_pkvls[ii+1]
        elif ii==nnlst-1:
            ipt_p = True
            pt_prev = resn_pkvls[ii-1]
        else:
            ipt_p = True
            ipt_n = True
            pt_prev = resn_pkvls[ii-1]
            pt_next = resn_pkvls[ii+1]

        pctc = pt_crnt.y2*100/ymxpk                 # current value in percent of max

        found = False
        if ii==0:
            if ipt_n:
                dltn = abs(pt_crnt.y2 - pt_next.y2)*100/pt_crnt.y2
                found = _set_resn_pt_state(pctc, pctmx1, dpctpn1, pctmx2, dpctpn2, dltn=dltn)
        elif ii==nnlst-1:
            dltp = abs(pt_crnt.y2 - pt_prev.y2)*100/pt_crnt.y2
            found = _set_resn_pt_state(pctc, pctmx1, dpctpn1, pctmx2, dpctpn2, dltp=dltp)
        else:
            dltp = abs(pt_crnt.y2 - pt_prev.y2)*100/pt_crnt.y2
            dltn = abs(pt_crnt.y2 - pt_next.y2)*100/pt_crnt.y2
            found = _set_resn_pt_state(pctc, pctmx1, dpctpn1, pctmx2, dpctpn2, dltp=dltp, dltn=dltn)

        if found:
            resn_pkvls[ii].rflg = 1

        if ipt_p:
            txt = " {:4.1f}, {:6.3f}, {:6.3f}, {:6.3f}, {:6s}, {:6.2f}".format(pt_prev.x1, pt_prev.y1, pt_prev.x2, pt_prev.y2, '', dltp)
            txtlst.append(txt)

        txt = " {:4.1f}, {:6.3f}, {:6.3f}, {:6.3f}, {:6.2f}, {:6s},  {}".format(pt_crnt.x1, pt_crnt.y1, pt_crnt.x2, pt_crnt.y2, pctc, '', found)
        txtlst.append(txt)

        if ipt_n:
            txt = " {:4.1f}, {:6.3f}, {:6.3f}, {:6.3f}, {:6s}, {:6.2f}".format(pt_next.x1, pt_next.y1, pt_next.x2, pt_next.y2, '', dltn)
            txtlst.append(txt)

        txtlst.append("")

    txt = "\n".join(txtlst)
    _write_verbose_report(txt, report)

    # done filtering
    for rsnobj in resn_pkvls:
        inam = rsnobj.inam
        rflg = rsnobj.rflg
        if inam=='peak' and rflg==1:
            resn_pks_hord.append(rsnobj.x2)
            resn_pks_zmag.append(rsnobj.y2)

    return resn_pks_hord, resn_pks_zmag

def check_resonance(hlst, zlst, pctmx1, dpctpn1, pctmx2, dpctpn2, report=None):
    """Check and find Frequency Scan Resonances.
    """

    resn_pkvls = []
    nhord = len(hlst)
    for hh in range(nhord):
        hord = hlst[hh]
        zmag = zlst[hh]
        if hh==0:
            x1, y1 = hord, zmag
            xb, yb = hord, zmag    # beginning point
            ymxpk  = zmag
        else:
            x2, y2 = hord, zmag
            m2 = (y1-y2)/(x1-x2)
            if hh>1:
                if m1>0 and m2<0:           # found peak
                    inam = 'peak'
                    if y1>y2:
                        pt = 0
                    else:
                        pt = 1
                elif m1<0 and m2>0:         # found valley
                    inam = 'valy'
                    if y1<y2:
                        pt = 0
                    else:
                        pt = 1
                else:
                    inam = 'none'

                if inam!='none':
                    if pt==0:
                        xn = x1
                        yn = y1
                        hidx = hh-1
                    else:
                        xn = x2
                        yn = y2
                        hidx = hh

                    if inam=='peak' and yn>ymxpk:
                        ymxpk = yn

                    rsnobj = _set_rsn_object(x1=xb, y1=yb, x2=xn, y2=yn, inam=inam, hidx=hidx, rflg=0)
                    resn_pkvls.append(rsnobj)

                    # next segment begin point
                    xb, yb = xn, yn

            # update and go to next point
            m1, x1, y1 = m2, x2, y2

    # Filter Peak Resonance Points
    resn_pks_hord, resn_pks_zmag = _filter_rsn_pkvls(resn_pkvls, ymxpk, pctmx1, dpctpn1, pctmx2, dpctpn2, report)
    _write_verbose_report('\n', report)

    return resn_pks_hord, resn_pks_zmag

# ==============================================================================

def get_fscan_csvdata(csvfile):
    """Get frequency scan Thevenin Impedance data from PSSE results file.
    """
    import csv

    thevz_dict = {}
    with open(csvfile, newline='') as fobj:
        reader = csv.reader(fobj)
        for row in reader:
            bus   = row[0]
            sec   = row[1]
            nam   = row[2]
            basekv= row[3]
            desc  = row[4].strip()
            if desc=='HORD':
                thevz_dict['hord'] = [float(v) for v in row[5:]]
            else:
                iext = int(bus)
                try:
                    isec = int(sec)
                except:
                    isec = 0
                if isec>0:
                    dkey = (iext, isec)
                else:
                    dkey = iext
                if desc=='pu abs(thevz)':
                    bnam = nam.strip()
                    bkv  = float(basekv)
                    thevz_dict[dkey] = {'basekv': bkv, 'name': bnam}
                    thevz_dict[dkey]['mag'] = [float(v) for v in row[5:]]
                elif desc=='deg phase(thevz)':
                    thevz_dict[dkey]['phase'] = [float(v) for v in row[5:]]
                else:
                    txt = "Reading Harmonics FSCAN CSVFILE error, should not come here."
                    raise Exception(txt)

    return thevz_dict

# ==============================================================================

def get_hord_thevz_list(thevz_dict, busnum=None):
    """Get frequency scan Thevenin impedance harmonic orders.
    """
    found = False
    klst = list(thevz_dict.keys())
    for k in klst:
        if k=='hord': continue
        if busnum is None:
            busnum = k
            found = True
            break
        else:
            if k==busnum:
                found = True
                break

    if found:
        hord_lst = thevz_dict['hord'][:]
        thevz_mag_lst = thevz_dict[busnum]['mag'][:]
        thevz_phs_lst = thevz_dict[busnum]['phase'][:]
        ierr = False
    else:
        ierr = True
        hord_lst, thevz_mag_lst, thevz_phs_lst = [], [], []

    return ierr, hord_lst, thevz_mag_lst, thevz_phs_lst

# ==============================================================================

def get_dstn_csvdata_volt(csvfile):
    """Get Distortion Calculations Bus Voltage THD data from PSSE results file.
    """
    import csv

    dkeytup = ('hord', 'bus', 'sec', 'basekv', 'vrpu', 'vxpu', 'vmagpu', 'vangdeg', 'thd_indv')
    dtyptup = ('r'   , 'i'  , 'i'  , 'r'     , 'r'   , 'r'   , 'r'     , 'r'      , 'r'       )

    errmsg0 = " Error: Reading Harmonics Distortion Calculations Bus Voltage CSV file:\n    {}\n".format(csvfile)

    _NCLNS = len(dkeytup)

    volt_dict = {}
    with open(csvfile, newline='') as fobj:
        reader = csv.reader(fobj)
        nrow = 0
        for row in reader:
            nrow += 1
            if nrow==1: continue # skip column header line
            nclns = len(row)
            if nclns!=_NCLNS:
                txt = "    ROW {} has {} data items. It should have {} data items.".format(nrow, nclns, _NCLNS)
                errmsg = "{}{}".format(errmsg0, txt)
                raise Exception(errmsg)
            tempdct = {}
            for dk, dt, v0 in zip(dkeytup, dtyptup, row):
                if dt=='s':
                    val = v0
                elif dt=='i':
                    if dk=='sec':
                        try:
                            val = int(v0)
                        except:
                            val = 0
                    else:
                        val = int(v0)
                else:
                    val = float(v0)
                tempdct[dk] = val

            hord = tempdct['hord']
            ibus = tempdct['bus']
            isec = tempdct['sec']
            bus_sec = (ibus, isec)

            if bus_sec not in volt_dict:
                volt_dict[bus_sec] = {}

            if hord not in volt_dict[bus_sec]:
                volt_dict[bus_sec][hord] = {}
            else:
                txt = "    Duplicate harmonic order={} data found for '{}', at {}".format(hord, desc, srcktup)
                errmsg = "{}{}".format(errmsg0, txt)
                raise Exception(errmsg)

            volt_dict[bus_sec][hord]['basekv'] = tempdct['basekv']
            volt_dict[bus_sec][hord]['vmag']   = tempdct['vmagpu']
            volt_dict[bus_sec][hord]['vang']   = tempdct['vangdeg']
            if hord==1.0:
                volt_dict[bus_sec]['thd'] = tempdct['thd_indv']
            else:
                volt_dict[bus_sec][hord]['indv'] = tempdct['thd_indv']

    # add this test here
##    txt = "    Fundamental harmonic order data not found for bus={}, section={}".format(ibus, isec)
##    errmsg = "{}{}".format(errmsg0, txt)
##    raise Exception(errmsg)

    return volt_dict

# ==================================================================================================

def get_dstn_csvdata_cursrc(csvfile):
    """Get Distortion Calculations Harmonic Current Source Spectrum data from PSSE results file.
    """
    import csv

    dkeytup = ('hord', 'ibus', 'isec', 'jbus', 'jsec', 'kbus', 'ksec', 'ckt', 'irpu', 'ixpu', 'imagpu', 'iangdeg', 'thd_indv', 'desc')
    dtyptup = ('r'   , 'i'   , 'i'   , 'i'   , 'i'   , 'i'   , 'i'   , 's'  , 'r'   , 'r'   , 'r'     , 'r'      , 'r'       , 's'   )

    errmsg0 = " Error: Reading Harmonics Distortion Calculations Bus Voltage CSV file:\n    {}\n".format(csvfile)

    _NCLNS = len(dkeytup)

    cursrc_dict = {}
    with open(csvfile, newline='') as fobj:
        reader = csv.reader(fobj)
        nrow = 0
        for row in reader:
            nrow += 1
            if nrow==1: continue # skip column header line
            nclns = len(row)
            if nclns!=_NCLNS:
                txt = "    ROW {} has {} data items. It should have {} data items.".format(nrow, nclns, _NCLNS)
                errmsg = "{}{}".format(errmsg0, txt)
                raise Exception(errmsg)
            tempdct = {}
            srcklst = []
            for dk, dt, v0 in zip(dkeytup, dtyptup, row):
                if dt=='s':
                    val = v0.strip().lower()
                elif dt=='i':
                    if dk in ['isec', 'jbus', 'jsec', 'kbus', 'ksec']:
                        try:
                            val = int(v0)
                        except:
                            val = 0
                    else:
                        val = int(v0)
                else:
                    val = float(v0)

                if dk in ['ibus', 'isec', 'jbus', 'jsec', 'kbus', 'ksec']:
                    if val>0:
                        srcklst.append(val)
                elif dk in ['ckt']:
                    if val:
                        srcklst.append(val)
                else:
                    tempdct[dk] = val

            srcktup = tuple(srcklst)
            hord = tempdct['hord']
            desc = tempdct['desc']

            if desc not in cursrc_dict:
                cursrc_dict[desc] = {}

            if srcktup not in cursrc_dict[desc]:
                cursrc_dict[desc][srcktup] = {}

            if hord not in cursrc_dict[desc][srcktup]:
                cursrc_dict[desc][srcktup][hord] = {}
            else:
                txt = "    Duplicate harmonic order={} data found for '{}', at {}".format(hord, desc, srcktup)
                errmsg = "{}{}".format(errmsg0, txt)
                raise Exception(errmsg)

            cursrc_dict[desc][srcktup][hord]['imag'] = tempdct['imagpu']
            cursrc_dict[desc][srcktup][hord]['iang'] = tempdct['iangdeg']
            if hord==1.0:
                cursrc_dict[desc][srcktup]['thd'] = tempdct['thd_indv']
            else:
                cursrc_dict[desc][srcktup][hord]['indv'] = tempdct['thd_indv']

    # add this test here
##    txt = "    Fundamental harmonic order data not found for '{}', at {}".format(desc, srcktup)
##    errmsg = "{}{}".format(errmsg0, txt)
##    raise Exception(errmsg)

    return cursrc_dict

# ==================================================================================================

def compare_dstn_ieee_test_and_tf(outpath, csvfile_volt, csvfile_cursrc):
    # Compare PSSE Distortion Calculation Results and IEEE Task Force Results

    if not os.path.exists(csvfile_volt):
        msg0 = " Distortion Calculation comparison table for IEEE Test case not done."
        msg  = " File not found.{}\n    {}".format(msg0, csvfile_volt)
        print(msg)
        return

    # get task force results table in dictionary
    tfresults_pf_thd_dict = get_ieee_tf_dstn_pf_thd_results()
    tfresults_cursrc_dict = get_ieee_tf_dstn_cursrc()

    # get distotion bus volts CSV data in dictionary
    volt_dict   = get_dstn_csvdata_volt(csvfile_volt)
    cursrc_dict = get_dstn_csvdata_cursrc(csvfile_cursrc)

    # create comparison table
    errmsg0 = " Error: Processing Harmonics Distortion Calculations Bus Voltage CSV file:\n    {}\n".format(csvfile_volt)

    hdr1 = " IEEE Task Force (TF) Harmonics Test Case: TF and PSSE Results Comparison\n"
    hdr2 = " (1) Power Flow Solution Bus Voltages and Harmonics %THD\n"
    hdr3 = "    Bus |nominal| IEEE TF| IEEE TF|IEEE TF|  PSSE  |  PSSE  | PSSE  |   DIFF   |   DIFF   |   DIFF   |"
    hdr4 = " Number |  kV   |  V pu  |  V deg | THD % |  V pu  |  V deg | THD % |   V pu   |   V deg  |   THD %  |\n"

    oubflst = []
    oubflst.append(hdr1)
    oubflst.append(hdr2)
    oubflst.append(hdr3)
    oubflst.append(hdr4)

    buslist = list(tfresults_pf_thd_dict.keys())
    buslist.sort()
    for bus in buslist:
        tfdct = tfresults_pf_thd_dict[bus]
        tf_basekv = tfdct['basekv']
        tf_mag    = tfdct['vmag']
        tf_ang    = tfdct['vang']
        tf_thd    = tfdct['thd']

        sec = 0
        bus_sec = (bus, sec)
        dstndct = volt_dict[bus_sec]

        hord = 1.0

        p_basekv = dstndct[hord]['basekv']
        p_mag    = dstndct[hord]['vmag']
        p_ang    = dstndct[hord]['vang']
        p_thd    = dstndct['thd']

        if p_basekv!=tf_basekv:
            txt1 = "    Nominal bus voltage does not match for bus={}\n".format(bus)
            txt2 = "    Bus voltage (kV)  TF paper={}, PSSE case={}\n".format(tf_basekv, p_basekv)
            errmsg = "{}{}{}".format(errmsg0, txt1, txt2)
            raise Exception(errmsg)

        tf_txt = "{:6d} | {:5.1f} | {:6.4f} | {:6.2f} | {:5.3f} |".format(bus, tf_basekv, tf_mag, tf_ang, tf_thd)
        p_txt  = "{:6.4f} | {:6.2f} | {:5.3f} |".format(p_mag, p_ang, p_thd)

        df_mag = tf_mag - p_mag
        df_ang = tf_ang - p_ang
        df_thd = tf_thd - p_thd
        df_txt = "{:8.5f} | {:8.4f} | {:8.5f} |".format(df_mag, df_ang, df_thd)

        txt = " {} {} {}".format(tf_txt, p_txt, df_txt)
        oubflst.append(txt)

    hdr1 = "\n (2) Harmonic Current Source Spectrum applied for Distortion Calculations\n"
    hdr2 = " Hord |    Bus |  IEEE TF |  IEEE TF |   PSSE   |   PSSE   |   DIFF   |"
    hdr3 = "      | Number |   %I     |   I deg  |   %I     |   I deg  |   %I     |\n"

    oubflst.append(hdr1)
    oubflst.append(hdr2)
    oubflst.append(hdr3)

    p_keylist = list(cursrc_dict['load'].keys())
    buslist.sort()

    tf_hord_list = list(tfresults_cursrc_dict['hvdc'].keys())
    p_elmt = 'load'

    for hord in tf_hord_list:
        for srcktup in p_keylist:
            ibus = srcktup[0]
            if ibus==8:
                tfk = 'tcr'
            else:
                tfk = 'hvdc'

            p_imag  = cursrc_dict[p_elmt][srcktup][hord]['imag']
            p1_imag = cursrc_dict[p_elmt][srcktup][1.0]['imag']
            p_pct   = p_imag*100/p1_imag

            p_iang  = cursrc_dict[p_elmt][srcktup][hord]['iang']

            tf_imag = tfresults_cursrc_dict[tfk][hord]['imag']
            tf_iang = tfresults_cursrc_dict[tfk][hord]['iang']

            df_pct  = tf_imag - p_pct

            txt = " {:4.1f} | {:6d} | {:8.2f} | {:8.2f} | {:8.2f} | {:8.2f} | {:8.5f} |".format(hord, ibus, tf_imag, tf_iang, p_pct, p_iang, df_pct)
            oubflst.append(txt)

    #
    txt1 = "\n For multiple harmonic sources, the phase angles of harmonic current injections are"
    txt2 = " re-calculated considering power flow solution phase angle, spectrum phase angles and"
    txt3 = " harmonic order. Hence TF spectrum phase angles and PSSE phase angles are different."
    oubflst.extend([txt1, txt2, txt3])

    # write to output file
    pth, nx  = os.path.split(csvfile_volt)
    nam, xtn = os.path.splitext(nx)
    oufname = "{}_tf_THD_compare.txt".format(nam)
    outfile = os.path.join(outpath, oufname)
    outfobj = open(outfile, 'w')

    oubflst.append("")
    alltxt = "\n".join(oubflst)
    outfobj.write(alltxt)
    outfobj.close()

    msg = " IEEE Task Force Harmonics Test Case: TF and PSSE Results Comparison saved to file:\n    {}\n".format(outfile)
    print(msg)

# ==============================================================================

def plot_main_fscan_ieee_test_and_tf(outpath, **kwds):
    """Plot IEEE Test Case frequency scan impedance.
    Results from PSSE and IEEE Task Force are plotted.
    """

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    filetyp = kwds.get('filetyp', 'png')
    verbose = kwds.get('verbose', False)
    pctmx1  = kwds.get('pctmx1',  60.0)
    dpctpn1 = kwds.get('dpctpn1', 75.0)
    pctmx2  = kwds.get('pctmx2',  20.0)
    dpctpn2 = kwds.get('dpctpn2', 85.0)

    casnam = "ieee_tf_psse"
    busnum = 3

    hmajor = []
    for ii in range(0, 41, 5):
        hmajor.append(ii)

    ymajor = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]

    csv_dict = {
        1: {'nam': "ieee_testcase_linmdl=0_fscan.csv", 'ttl': "nominal PI"},
        2: {'nam': "ieee_testcase_linmdl=1_fscan.csv", 'ttl': "long line distibuted with skin effect"},
        3: {'nam': "ieee_testcase_linmdl=2_fscan.csv", 'ttl': "long line distibuted but no skin effect"},
        }

    csv_exists_dict = {}
    for k, vdict in csv_dict.items():
        nam = vdict['nam']
        csvfile = os.path.join(outpath, nam)
        if os.path.exists(csvfile):
            csv_exists_dict[k] = vdict

    if not csv_exists_dict:
        msg = "\n Error- IEEE Test Harmonics Frequency Scan result files not found, not ploted, terminated:\n    {}".format(outpath)
        print(msg)
        return

    # PSSE results
    ierr_pi, ierr_dst_skin, ierr_dst = True, True, True
    ii = 0
    for k, vdict in csv_exists_dict.items():
        nam = vdict['nam']
        ttl = vdict['ttl']
        csvfile = os.path.join(outpath, nam)
        thevz_dict = get_fscan_csvdata(csvfile)
        ierr, hlst, zlst, phlst = get_hord_thevz_list(thevz_dict, busnum)
        if not ierr:
            if ii==0:
                hlst_pi = hlst[:]
                zlst_pi = zlst[:]
                ttl_pi = ttl
                ierr_pi = False
            elif ii==1:
                hlst_dst_skin = hlst[:]
                zlst_dst_skin = zlst[:]
                ttl_dst_skin = ttl
                ierr_dst_skin = False
            elif ii==2:
                hlst_dst = hlst[:]
                zlst_dst = zlst[:]
                ttl_dst  = ttl
                ierr_dst = False
        ii += 1

    if ierr_pi or ierr_dst:
        print(" Error -- PSSE getting results data")
        return

    tf_hlst, tf_zlst_cal, tf_zlst_dst, tf_zlst_pi = get_ieee_tf_scan_results()

    peak_lst_h, peak_lst_rx = check_resonance(hlst_dst, zlst_dst, pctmx1, dpctpn1, pctmx2, dpctpn2)
    resn_lgd_lst = get_resn_legends(peak_lst_h, peak_lst_rx)
    resn_lgd_lst.insert(0, "Resonance: distibuted but no skin")
    resn_lgd = "\n".join(resn_lgd_lst)

    clr_lst = ['red', 'blue', 'black', 'green', 'magenta']
    sty_lst = ['-', ':', '--', '-.', '-']
    wdt_lst = [2, 2, 1, 1, 1]

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(8.0, 9.0)

    ii=0
    ax.plot(hlst_dst, zlst_dst, label=ttl_dst+' - PSSE', color=clr_lst[ii], linestyle=sty_lst[ii], linewidth=wdt_lst[ii])

    ii=1
    ax.plot(tf_hlst, tf_zlst_dst, label=ttl_dst+' - IEEE Task Force', color=clr_lst[ii], linestyle=sty_lst[ii], linewidth=wdt_lst[ii])

    ii=2
    ax.plot(hlst_pi, zlst_pi, label=ttl_pi+' - PSSE', color=clr_lst[ii], linestyle=sty_lst[ii], linewidth=wdt_lst[ii])

    ii=3
    ax.plot(tf_hlst, tf_zlst_pi, label=ttl_pi+' - IEEE Task Force', color=clr_lst[ii], linestyle=sty_lst[ii], linewidth=wdt_lst[ii])

    ax.set_xticks(hmajor)
    ax.set_yticks(ymajor)
    #ax.set_yscale('log')
    ax.set_xlabel("Harmonic Order")
    ax.set_ylabel("Harmonic Impedance (pu)")
    ax.set_title("IEEE 14 Bus Harmonics Test System")
    ax.grid(True, which='both')
    ax.legend()
    ax.annotate(resn_lgd, (10, 1.75), fontfamily='monospace')

    if filetyp=='pdf':
        pdffile = os.path.join(outpath, "{}.pdf".format(casnam))
        pdfobj  = PdfPages(pdffile)
    else:
        figfile = os.path.join(outpath, "{}.png".format(casnam))

    if filetyp=='pdf':
        pdfobj.savefig(fig, bbox_inches='tight')
        pdfobj.close()
        print(" Plots saved: {}".format(pdffile))
    else:
        fig.savefig(figfile, bbox_inches='tight')
        print(" Plots saved: {}".format(figfile))

    plt.show()

# ==============================================================================

def plot_main_fscan_ieee_test(outpath, **kwds):
    """Plot IEEE Test Case frequency scan Thevenin impedance.
    """
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    filetyp = kwds.get('filetyp', 'png')
    verbose = kwds.get('verbose', False)
    pctmx1  = kwds.get('pctmx1',  60.0)
    dpctpn1 = kwds.get('dpctpn1', 75.0)
    pctmx2  = kwds.get('pctmx2',  20.0)
    dpctpn2 = kwds.get('dpctpn2', 85.0)

    if verbose:
        report = sys.stdout.write
    else:
        report = None

    csv_dict = {
        1: {'nam': "ieee_testcase_linmdl=0_fscan.csv", 'ttl': "nominal PI"},
        2: {'nam': "ieee_testcase_linmdl=1_fscan.csv", 'ttl': "long line distibuted with skin effect"},
        3: {'nam': "ieee_testcase_linmdl=2_fscan.csv", 'ttl': "long line distibuted but no skin effect"},
        }

    csv_exists_dict = {}
    for k, vdict in csv_dict.items():
        nam = vdict['nam']
        csvfile = os.path.join(outpath, nam)
        if os.path.exists(csvfile):
            csv_exists_dict[k] = vdict

    if not csv_exists_dict:
        msg = "\n Error- IEEE Test Harmonics Frequency Scan result files not found, not ploted, terminated:\n    {}".format(outpath)
        print(msg)
        return

    hmajor = []
    for ii in range(0, 41, 5):
        hmajor.append(ii)

    ymajor = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]

    busnum = 3

    clr_lst = ['black', 'green', 'red']
    sty_lst = ['--', ':', '-']
    wdt_lst = [2, 3, 1]

    resn_lgd = ''
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(8.0, 9.0)
    ii = 0
    for k, vdict in csv_exists_dict.items():
        nam = vdict['nam']
        ttl = vdict['ttl']
        csvfile = os.path.join(outpath, nam)
        thevz_dict = get_fscan_csvdata(csvfile)
        ierr, hlst, zlst, phlst = get_hord_thevz_list(thevz_dict, busnum)
        if not ierr:
            ax.plot(hlst, zlst, label=ttl, color=clr_lst[ii], linestyle=sty_lst[ii], linewidth=wdt_lst[ii])
            if k==3:
                peak_lst_h, peak_lst_rx = check_resonance(hlst, zlst, pctmx1, dpctpn1, pctmx2, dpctpn2, report=report)
                resn_lgd_lst = get_resn_legends(peak_lst_h, peak_lst_rx)
                resn_lgd_lst.insert(0, "Resonance: linmdl-distibuted but no skin")
                resn_lgd = "\n".join(resn_lgd_lst)

        ii += 1

    ax.set_xticks(hmajor)
    ax.set_yticks(ymajor)
    #ax.set_yscale('log')
    ax.set_xlabel("Harmonic Order")
    ax.set_ylabel("Harmonic Impedance (pu)")
    ax.set_title("IEEE 14 Bus Harmonics Test System")
    ax.grid(True, which='both')
    ax.legend()
    if resn_lgd: ax.annotate(resn_lgd, (10, 1.75), fontfamily='monospace')

    casnam = 'ieee_test'
    if filetyp=='pdf':
        pdffile = os.path.join(outpath, "{}_fscan.pdf".format(casnam))
        pdfobj  = PdfPages(pdffile)
    else:
        figfile = os.path.join(outpath, "{}_fscan.png".format(casnam))

    if filetyp=='pdf':
        pdfobj.savefig(fig, bbox_inches='tight')
        pdfobj.close()
        print(" Plots saved: {}".format(pdffile))
    else:
        fig.savefig(figfile, bbox_inches='tight')
        print(" Plots saved: {}".format(figfile))

    plt.show()

# =========================================================================

def _har_ana_ieee_test(**kwds):
    """Run PSSE Harmonic Analysis using IEEE Test Case.
    Allowed kwds:

    outpath  = os.getcwd(), Folder name to save outfile files
    rpt2file = False, Save Report to file

    Thresholds to filter Thevenin Impedance
        dft_thresholds = True, Use defualt thresholds

        pctmx1  = kwds.get('pctmx1' , 60.0)
        dpctpn1 = kwds.get('dpctpn1', 75.0)
        pctmx2  = kwds.get('pctmx2' , 20.0)
        dpctpn2 = kwds.get('dpctpn2', 85.0)
    """
    import psspy

    name,major,minor,modlvl,date,stat = psspy.psseversion()

    kwds_api = {}
    kwds_api['anaoptn'   ] = 0
    kwds_api['dstnbuop'  ] = 0
    kwds_api['dstnrptop' ] = 1
    kwds_api['imachimpop'] = 0
    kwds_api['dcimpop'   ] = 0
    kwds_api['triplenop' ] = 0
    kwds_api['genimpop'  ] = 0

    kwds_api['hord_min' ] = 0.0
    kwds_api['hord_max' ] = 40.0
    kwds_api['hord_stp' ] = 0.33

    kwds_api['hrsfile'  ] = ''

    fscan_buslist = [3]
    sid = 3
    busall = 0
    psspy.bsys(sid, numbus=len(fscan_buslist), buses=fscan_buslist)

    outpath = kwds.get('outpath', os.getcwd())
    rpt2file = kwds.get('rpt2file', False)
    dft_thresholds = kwds.get('dft_thresholds', True)

    if not dft_thresholds:
        pctmx1  = kwds.get('pctmx1' , 60.0)
        dpctpn1 = kwds.get('dpctpn1', 75.0)
        pctmx2  = kwds.get('pctmx2' , 20.0)
        dpctpn2 = kwds.get('dpctpn2', 85.0)

        s_pctmx1  = "{:g}".format(pctmx1)
        s_dpctpn1 = "{:g}".format(dpctpn1)
        s_pctmx2  = "{:g}".format(pctmx2)
        s_dpctpn2 = "{:g}".format(dpctpn2)
        usr_thresholds = "thresholds_usr_{}_{}_{}_{}".format(s_pctmx1, dpctpn1, s_pctmx2, dpctpn2)

    for linmdl in [0, 1, 2]:
        outnam = "ieee_testcase_linmdl={}".format(linmdl)
        if dft_thresholds:
            outpath1 = os.path.join(outpath,"dft_thresholds")
        else:
            outpath1 = os.path.join(outpath,usr_thresholds)

        if not os.path.exists(outpath1): os.makedirs(outpath1)

        if rpt2file:
            dstnfile = os.path.join(outpath1, "{}_dstn.txt".format(outnam))
            resnfile = os.path.join(outpath1, "{}_resn.txt".format(outnam))
        else:
            dstnfile = ''
            resnfile = ''

        kwds_api['linmdl']   = linmdl
        kwds_api['dstnfile'] = dstnfile
        kwds_api['resnfile'] = resnfile

        if dft_thresholds:
            psspy.har_set_resn_thresholds_default()
        else:
            psspy.har_set_resn_thresholds(pctmx1=pctmx1, dpctpn1=dpctpn1, pctmx2=pctmx2, dpctpn2=dpctpn2)

        ierr = psspy.har_analysis(sid, busall, **kwds_api)

        if not ierr:
            if kwds_api['anaoptn'] in [0, 1]:
                fscan_csvfile = os.path.join(outpath1, "{}_fscan.csv".format(outnam))
                psspy.har_export_fscan(fscan_csvfile)

                msg = "\n Frequency Scan Thevenin impedance exported to file:\n    {}".format(fscan_csvfile)
                print(msg)

            if major>=35 and minor>=4 and modlvl>=2:
                if kwds_api['anaoptn'] in [0, 2]:
                    dstn_csvfile = os.path.join(outpath1, "{}_dstn.csv".format(outnam))
                    voltoptn, flowoptn,cursrcoptn = 2, 2, 2
                    psspy.har_export_dstn(dstn_csvfile, voltoptn=voltoptn, flowoptn=flowoptn, cursrcoptn=cursrcoptn )

                    pn, xtn = os.path.splitext(dstn_csvfile)
                    msg  = "\n Distortion calculation results exported to files:\n"
                    msg += "    {}_volt{}\n".format(pn, xtn)
                    msg += "    {}_flow{}\n".format(pn, xtn)
                    msg += "    {}_cursrc{}\n".format(pn, xtn)
                    print(msg)

# =========================================================================

def _ieee_test_get_names(datapath, outpath):

    if datapath is None:        # use Example folder
        exampath = os.path.dirname(__file__)
        datapath = exampath

    savfile = os.path.join(datapath, 'ieee_harmonics_test_case.sav')
    harfile = os.path.join(datapath, 'ieee_harmonics_test_case_har.rawx')

    if not os.path.exists(savfile):
        msg = "\n Error- File not found, terminated:\n    {}".format(savfile)
        print(msg)

    if not os.path.exists(harfile):
        msg = "\n Error- File not found, terminated:\n    {}".format(harfile)
        print(msg)

    if outpath is None:
        exampath = os.path.dirname(__file__)
        outpath  = os.path.join(exampath, r'output_harmonics_demo\ieee')
        if not os.path.exists(outpath): os.makedirs(outpath)

    return savfile, harfile, outpath

# =========================================================================

def run_ieee_test(datapath=None, outpath=None):
    """Run PSSE Harmonic Analysis using IEEE Test Case.
    """
    import psspy

    psspy.psseinit()

    savfile, harfile, outpath = _ieee_test_get_names(datapath=datapath, outpath=outpath)
    psspy.case(savfile)
    psspy.readrawx(harfile, 'harmonics', 'new')

    _har_ana_ieee_test(outpath=outpath, rpt2file=True)

# =========================================================================

def run_ieee_test_thevz_thresholds(datapath=None, outpath=None):
    """Run PSSE Harmonic Analysis using IEEE Test Case.
    """
    import psspy

    psspy.psseinit()

    savfile, harfile, outpath = _ieee_test_get_names(datapath=datapath, outpath=outpath)
    psspy.case(savfile)
    psspy.readrawx(harfile, 'harmonics', 'new')

    kwds = {}
    kwds['outpath' ] = outpath
    kwds['rpt2file' ] = True
    kwds['dft_thresholds' ] = False

    kwds['pctmx1' ] = 60.0
    kwds['dpctpn1'] = 75.0
    kwds['pctmx2' ] = 20.0
    kwds['dpctpn2'] = 65.0

    _har_ana_ieee_test(**kwds)

# =========================================================================
def plot_fscan_ieee_test(outpath=None, **kwds):
    """Plot PSSE Harmonic Analysis Frequency Scan results of IEEE Test Case.
    """
    if outpath is None:
        exampath = os.path.dirname(__file__)
        outpath  = os.path.join(exampath, r'output_harmonics_demo\ieee\dft_thresholds')
    if not os.path.exists(outpath):
        msg = "\n Error- IEEE Harmonics Frequency Scan results folder not found, terminated:\n    {}".format(outpath)
        print(msg)
        return

##    kwds = {}
##    kwds['filetyp'] = 'png'
##    kwds['verbose'] = verbose
##    kwds['pctmx1' ] = pctmx1
##    kwds['dpctpn1'] = dpctpn1
##    kwds['pctmx2' ] = pctmx2
##    kwds['dpctpn2'] = dpctpn2

    plot_main_fscan_ieee_test(outpath, **kwds)

# =========================================================================
def plot_fscan_ieee_test_tf_psse(outpath=None, **kwds):
    """Plot Frequency Scan results of PSSE Harmonic Analysis and IEEE Task Force for IEEE Test Case.
    """
    if outpath is None:
        exampath = os.path.dirname(__file__)
        outpath  = os.path.join(exampath, r'output_harmonics_demo\ieee\dft_thresholds')
    if not os.path.exists(outpath):
        msg = "\n Error- IEEE Harmonics Frequency Scan results folder not found, terminated:\n    {}".format(outpath)
        print(msg)
        return

##    kwds = {}
##    kwds['filetyp'] = 'png'
##    kwds['verbose'] = verbose
##    kwds['pctmx1' ] = pctmx1
##    kwds['dpctpn1'] = dpctpn1
##    kwds['pctmx2' ] = pctmx2
##    kwds['dpctpn2'] = dpctpn2

    plot_main_fscan_ieee_test_and_tf(outpath, **kwds)

# =========================================================================
def compare_dstn_ieee_test(outpath=None):

    if outpath is None:
        exampath = os.path.dirname(__file__)
        outpath  = os.path.join(exampath, r'output_harmonics_demo\ieee\dft_thresholds')

    if not os.path.exists(outpath):
        msg = "\n Error- IEEE Harmonics Distortion Calculations results folder not found, terminated:\n    {}".format(outpath)
        print(msg)
        return

    csvnam_volt   = "ieee_testcase_linmdl=2_dstn_volt.csv"
    csvnam_flow   = "ieee_testcase_linmdl=2_dstn_flow.csv"
    csvnam_cursrc = "ieee_testcase_linmdl=2_dstn_cursrc.csv"

    csvfile_volt   = os.path.join(outpath, csvnam_volt)
    csvfile_cursrc = os.path.join(outpath, csvnam_cursrc)
    compare_dstn_ieee_test_and_tf(outpath, csvfile_volt, csvfile_cursrc)

# =========================================================================

def _run_har_ana_main(*fscanbuses, **kwds):
    # Run Harmonic Analysis using working case
    import psspy

    # No need to process these API keywords here

    ##    _i = psspy.getdefaultint()
    ##    _f = psspy.getdefaultreal()
    ##    _s = psspy.getdefaultchar()
    ##
    ##    anaoptn   = kwds.get('anaoptn'   , _i)
    ##    linmdl    = kwds.get('linmdl'    , _i)
    ##    dstnbuop  = kwds.get('dstnbuop'  , _i)
    ##    dstnrptop = kwds.get('dstnrptop' , _i)
    ##    imachimpop= kwds.get('imachimpop', _i)
    ##    dcimpop   = kwds.get('dcimpop'   , _i)
    ##    triplenop = kwds.get('triplenop' , _i)
    ##    genimpop  = kwds.get('genimpop'  , _i)
    ##
    ##    hord_min = kwds.get('hord_min'  , _f)
    ##    hord_max = kwds.get('hord_max'  , _f)
    ##    hord_stp = kwds.get('hord_stp'  , _f)

    # subsystem
    onezerobus = False
    if fscanbuses:
        if len(fscanbuses)==1:
            if fscanbuses[0]==0:
                onezerobus = True

    if fscanbuses:
        if not onezerobus:
            sid = 3
            busall = 0
            psspy.bsys(sid, numbus=len(fscanbuses), buses=fscanbuses)
        else:
            # no scan, just run distortion calculations
            sid = 0
            busall = 0
    else:
        totbus = psspy.totbus()
        # if case has <100 buses, run scan on all buses
        if totbus<100:
            sid = 0
            busall = 1
        else:
            # no scan, just run distortion calculations
            sid = 0
            busall = 0

    ierr = True
    outfdict = {}
    outfdict['dstn'] = ''
    outfdict['resn'] = ''
    outfdict['scan'] = ''

    anaoptn = kwds.get('anaoptn', 0)
    if sid==0 and busall==0:
        if anaoptn==0:
            kwds['anaoptn'] = 2  # only distortion anlysis
        elif anaoptn==2:
            pass
        else:
            msg = "\n Error- Specify frequency scan buses, terminated"
            print(msg)
            return ierr, outfdict

    outfnam  = kwds.get('outfnam' , '')
    outpath  = kwds.get('outpath' , '')

    if not outfnam:
        savfile, snpfile = psspy.sfiles()
        if not savfile:
            outfnam = "tmpout"
        else:
            p, nx = os.path.split(savfile)
            outfnam, xtn = os.path.splitext(nx)

    if outpath:
        if not os.path.exists(outpath): os.makedirs(outpath)
        dstnfile = os.path.join(outpath, "{}_dstn.txt".format(outfnam))
        resnfile = os.path.join(outpath, "{}_resn.txt".format(outfnam))
    else:
        dstnfile = ''
        resnfile = ''

    kwds['hrsfile']  = ''
    kwds['dstnfile'] = dstnfile
    kwds['resnfile'] = resnfile

    if 'outpath' in kwds: del kwds['outpath']
    if 'outfnam' in kwds: del kwds['outfnam']

    ierr = psspy.har_analysis(sid, busall, **kwds)

    fscan_csvfile = ''

    if anaoptn in [0,1]:
        if not ierr and outpath:
            fscan_csvfile = os.path.join(outpath, "{}_fscan.csv".format(outfnam))
            psspy.har_export_fscan(fscan_csvfile)
            msg = "\n Frequency Scan Thevenin impedance saved to file:\n    {}".format(fscan_csvfile)
            print(msg)

    outfdict['dstn'] = dstnfile
    outfdict['resn'] = resnfile
    outfdict['scan'] = fscan_csvfile

    return ierr, outfdict

# =========================================================================
def run_har_analysis(savfile, *fscanbuses, **kwds):
    """Run PSSE Harmonic Analysis using savfile and harfile provided.

    Arguments:
        savfile (str): PSSE Saved Case file name

        fscanbuses (int): One or bus numbers at which frequency scan done

        kwds (dict):  All PSSE har_analysis() API keywords plus followng
            are allowed key words.

            harfile (str) : PSSE harmonics data (.har) file
            outpath (str) : Output Results File Folder name
            outfnam (str) : Output Results File Name prefix
    """

    import psspy

    if not os.path.exists(savfile):
        msg = "\n Error- File not found, terminated:\n    {}".format(savfile)
        print(msg)
        return True, {}

    harfile = kwds.get('harfile', '')
    if harfile:
        if not os.path.exists(harfile):
            msg = "\n Error- File not found, ignored:\n    {}".format(harfile)
            print(msg)
            harfile = ''

    psspy.psseinit()

    ierr = psspy.case(savfile)
    if ierr:
        msg = "\n Error- reading SAV file, terminated:\n    {}".format(savfile)
        print(msg)
        return True, {}

    if harfile:
        ierr = psspy.readrawx(harfile, 'harmonics', 'new')
        if ierr:
            msg = "\n Error- reading Harmonics data file, terminated:\n    {}".format(harfile)
            print(msg)
            return True, {}

    if 'harfile' in kwds: del kwds['harfile']
    ierr, outfdict = _run_har_ana_main(*fscanbuses, **kwds)

    return ierr, outfdict

# ==============================================================================

def _plot_fscan_one(ax, hlst, zlst, **kwds):
    #  main plot function
    basemva  = kwds.get('basemva' , 100.0)
    basekv   = kwds.get('basekv'  , None)
    hmajor   = kwds.get('hmajor'  , [])
    ymajor   = kwds.get('ymajor'  , [])
    plotzpu  = kwds.get('plotzpu' , False)
    title    = kwds.get('title'   , '')
    add_xlbl = kwds.get('add_xlbl', None)
    add_lgnd = kwds.get('add_lgnd', False)
    annot_xy = kwds.get('annot_xy', (0.5, 0.5))

    pctmx1  = kwds.get('pctmx1' , 60.0)
    dpctpn1 = kwds.get('dpctpn1', 75.0)
    pctmx2  = kwds.get('pctmx1' , 20.0)
    dpctpn2 = kwds.get('dpctpn1', 85.0)
    report  = kwds.get('report' , None)

    if add_lgnd:
        peak_lst_h, peak_lst_rx = check_resonance(hlst, zlst, pctmx1, dpctpn1, pctmx2, dpctpn2, report)

    ylbl = "Thevenin Impedance (pu)"
    if not plotzpu:
        if basemva and basekv:
            zbase = basekv*basekv/basemva
            zlst_ohm = [zbase*each for each in zlst]
            zlst = zlst_ohm[:]
            del zlst_ohm
            ylbl = "Thevenin Impedance (ohm)"

            if add_lgnd:
                peak_lst_rx_ohm = [zbase*each for each in peak_lst_rx]
                peak_lst_rx = peak_lst_rx_ohm[:]
                del peak_lst_rx_ohm

    if add_lgnd:
        resn_lgd_lst = get_resn_legends(peak_lst_h, peak_lst_rx)
        resn_lgd = "\n".join(resn_lgd_lst)

    if add_lgnd:
        ax.plot(hlst, zlst, label=resn_lgd)
    else:
        ax.plot(hlst, zlst)
    #ax.set_yscale('log')
    if hmajor: ax.set_xticks(hmajor)
    if ymajor: ax.set_yticks(ymajor)
    if (add_xlbl): ax.set_xlabel("Harmonic Order")
    ax.set_ylabel(ylbl)

    ax.grid(True, which='both')

    if add_lgnd:
        ax.legend(loc='best')

    if title: ax.set_title(title)

# ==============================================================================

def plot_frequency_scan(busnum, *csvfiles, **kwds):
    """Plot Harmonics Frequency Scan Thevenin Impedance.
    for one bus from multiple Frequency Scan Result Files

    Arguments:
        busnum (int): Bus Number. The 'csvfiles' provided must have Thevenin Impedance
            for this bus.

        csvfiles (str): One or more CSV files that contain Frequency Scan results.
            These files are created by api psspy.har_export_fscan(..).

        kwds (dict):  Followng are allowed key words.

            (A) These keywords are for plot figure options.

            figfiletyp (str): File type to which plots are saved.
                              ='pdfobj' -- files are saved to already created pdfobj
                              [Create pdfobj = PdfPages(pdffile). This is done so
                              as to save many plots to one pdffile.]
                              ='pdf', 'png', 'jpg' etc. [all allowed file types].
                              (default: '')
            figfile (str)   : Name of the file or pdfobj to save plots
                              When file name is not provided plot is not saved.
                              (default: '')
            basemva (float) : Base MVA (used to calculate Thev Z in ohms)
                              (default: 100.0)
            basekv  (float) : Base kV of the bus (used to calculate Thev Z in ohms)
                              (default: No default allowed)
            hmajor  (float) : List of Harmonics Orders (used to draw X axis grid)
                              (default: [])
            ymajor  (float) : List of Thev Z (used to draw X axis grid)
                              (default: [])
            ttl_lst (str)   : Title list (one for each csvfile provided)
                              When one title is provided, same title is used for all.
                              (default: [])
            plotzpu (bool)  : True for Plot PU Thev Z
                              (default: False)
            add_lgnd (bool) : True to add resonance rrequeny legend
                              (default: False)
            annot_xy (tuple): Resonance Frequency legend location
                              Specify normalized (0 through 1) XY co-ordinates of a point
                              (default: (0.5, 0.5))
            subplts (bool)  : True, plot as subplots for more than one csvfiles.
                              (default: True) Subplots are drawn with 3 rows and 1 column.
            fwidth  (float) : Figure Width in inches
                              (default: matplotlib rcParms default figure width)
            fheight (float) : Figure Height in inches
                              (default: matplotlib rcParms default figure height)

            (B) These keywords are for filtering and reporting Thevenin Impedance Peaks.

            - Criterion 1 to select Thevenin Impedance Peak - slow rising peak point
            pctmx1 (float)     : current point in percent of maximum peak value
                                 (default:60.0)
            dpctpn1 (float)    : delta previous and delta next points in percent of current point
                                 (default:75.0)

            - Criterion 2 to select Thevenin Impedance Peak - fast rising peak point
            pctmx2 (float)     : current point in percent of maximum peak value
                                 (default:20.0)
            dpctpn2 (float)    : delta previous and delta next points in percent of current point
                                 (default:85.0)

            verbose (bool)     : Show verbose (detailed) output of Thevenin Impedance filtering
                                 (default: False)
            verbose_file (str) : File name to write verbose output.
                                 (default: '')
    """
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    # Use outfigfile to save output figure file and
    # also use its path to find csvfile when csvfile path is not provided.
    csvpath = ''

    figfiletyp = kwds.get('figfiletyp', '')
    figfiletyp = figfiletyp.lower()

    outfigfile = kwds.get('figfile', '')

    if outfigfile:
        if figfiletyp=='pdfobj':
            pass
        else:
            csvpath, nx = os.path.split(outfigfile)
            n, x = os.path.splitext(nx)
            xlw = x.lower().strip()
            if xlw=='.pdf': figfiletyp = 'pdf'
    else:
        figfiletyp = ''

    title = ''
    has_ttl4each = False
    ttl_lst = kwds.get('ttl_lst', [])
    nttl = len(ttl_lst)
    ncsv = len(csvfiles)
    if nttl==ncsv:
        has_ttl4each = True
    elif nttl==1 and ncsv>1:
        title = ttl_lst[0]

    exists_csvfiles = []
    exists_titles   = []
    for ii, csvnam in enumerate(csvfiles):
        if has_ttl4each:
            ttl = ttl_lst[ii]
        else:
            ttl = title
        if os.path.exists(csvnam):
            exists_csvfiles.append(csvnam)
            exists_titles.append(ttl)
        else:
            p, nx = os.path.split(csvnam)
            if not p and csvpath:
                csvnam2 = os.path.join(csvpath, nx)
                if os.path.exists(csvnam2):
                    exists_csvfiles.append(csvnam2)
                    exists_titles.append(ttl)
            else:
                msg = " File not found: {}".format(csvnam)
                print(msg)

    if not exists_csvfiles:
        return

    fwidth  = kwds.get('fwidth',  None)
    fheight = kwds.get('fheight', None)
    subplts = kwds.get('subplts', True)

    verbose  = kwds.get('verbose', False)
    verbose_file = kwds.get('verbose_file', '')
    report = None
    if verbose:
        if verbose_file:
            verbose_fobj = open(verbose_file, 'w')
            report = verbose_fobj.write
        else:
            report = sys.stdout.write

    if subplts:
        if fwidth is None or fheight is None:
            fwidth, fheight = 8.0, 9.0

    nfigs = len(exists_csvfiles)
    if not subplts:
        npages = nfigs
        nrows = 1
    else:
        if nfigs>3:
            npages = int(math.ceil(nfigs/3.0))   # three subplots per page
            nrows = 3
        else:
            npages = 1
            nrows = nfigs

    if outfigfile and figfiletyp=='pdf':
        pdffile = outfigfile
        pdfobj = PdfPages(pdffile)
    elif outfigfile and figfiletyp=='pdfobj':
        pdfobj = outfigfile

    nn = 0
    for pp in range(npages):
        fig, axlst = plt.subplots(nrows,1)
        if nrows==1: axlst = [axlst]
        fig.subplots_adjust(hspace=0.25)
        if fwidth is not None or fheight is not None:
            fig.set_size_inches(fwidth, fheight)

        for nr in range(nrows):
            ii = pp*nrows + nr
            if ii<nfigs:
                csvfile = exists_csvfiles[ii]
                ttl = exists_titles[ii]
                ax = axlst[nr]
                if (nr+1==nrows):
                    add_xlbl = True
                else:
                    add_xlbl = False

                kwds['title'] = ttl
                kwds['add_xlbl'] = add_xlbl
                kwds['report'] = report

                thevz_dict = get_fscan_csvdata(csvfile)
                ierr, hlst, zlst, phlst = get_hord_thevz_list(thevz_dict, busnum)
                if not ierr:
                    _plot_fscan_one(ax, hlst, zlst, **kwds)
            else:
                axlst[nr].set_visible(False)

        if outfigfile:
            if figfiletyp=='pdf':
                pdfobj.savefig(fig, bbox_inches='tight')
            elif figfiletyp=='pdfobj':
                try:
                    pdfobj.savefig(fig, bbox_inches='tight')
                except:
                    traceback.print_last()
            else:
                if npages>1:
                    pn, x = os.path.splitext(outfigfile)
                    zn = "{}".format(pp).zfill(2)
                    tmpfnam = "{}_{}{}".format(pn,zn,x)
                else:
                    tmpfnam = outfigfile
                fig.savefig(tmpfnam, bbox_inches='tight')

    if outfigfile:
        if figfiletyp=='pdf':
            pdfobj.close()

        if figfiletyp=='pdfobj':
            plt.close(fig=fig)
        else:
            print(" Plots saved: {}".format(outfigfile))

    if verbose:
        if verbose_file:
            verbose_fobj.close()

    if figfiletyp!='pdfobj':
        plt.show()

# =========================================================================

def test1():
    """Run Harmonics Analysis using IEEE Harmonics Test case.
    Uses Example folder files.
    """
    run_ieee_test()

def test1A():
    """Run Harmonics Analysis using IEEE Harmonics Test case.
    Also specify thresholds to filter thevenin resonance frequencies.
    Uses Example folder files.
    """
    run_ieee_test_thevz_thresholds()

def test2():
    """Plot Harmonics Test PSSE Results.
    Uses Example folder files.
    """
    plot_fscan_ieee_test()

def test2A():
    """Plot Harmonics Test PSSE Results.
    Also specify thresholds to filter thevenin resonance frequencies.
    Uses Example folder files.
    """
    plot_fscan_ieee_test(verbose=True, pctmx1=60.0, dpctpn1=75.0, pctmx2=20.0, dpctpn2=65.0)

def test3():
    """Plot Harmonics Test PSSE and harmonics Task Force Results.
    Compare PSSE and TF distortion calculation results.
    Uses Example folder files.
    """
    compare_dstn_ieee_test()
    plot_fscan_ieee_test_tf_psse()

def test3A():
    """Plot Harmonics Test PSSE and harmonics Task Force Results.
    Also specify thresholds to filter thevenin resonance frequencies.
    Uses Example folder files.
    """
    plot_fscan_ieee_test_tf_psse(verbose=True, pctmx1=60.0, dpctpn1=75.0, pctmx2=20.0, dpctpn2=65.0)

def test4():
    """Run Harmonics Analysis on Example folder 'sample' case.
    Output Reports created in Report Window
    """
    workdir  = os.path.dirname(__file__)
    datapath = workdir
    savfile  = os.path.join(datapath, "sample.sav")
    harfile  = os.path.join(datapath, "sample_har.rawx")
    run_har_analysis(savfile, harfile=harfile)

def test5():
    """Run Harmonics Analysis on Example folder 'sample_zils' case.
    Output Reports created in 'outpath' folder with savfile name used for file name prefix.
    """
    workdir  = os.path.dirname(__file__)
    datapath = workdir
    savfile  = os.path.join(datapath, "sample_zils.sav")
    harfile  = os.path.join(datapath, "sample_zils_har.rawx")
    outpath  = os.path.join(workdir,  "output_harmonics_demo", "sample_zils")
    run_har_analysis(savfile, harfile=harfile, outpath=outpath)

def test6():
    """Run Harmonics Analysis on Example folder 'sample_nb' case.
    Output Reports created in 'outpath' folder with 'outfnam' used for file name prefix.
    """
    workdir  = os.path.dirname(__file__)
    datapath = workdir
    savfile  = os.path.join(datapath, "sample_nb.sav")
    harfile  = os.path.join(datapath, "sample_har.rawx")
    outfnam  = "sample_nbXX"
    outpath  = os.path.join(workdir, "output_harmonics_demo", outfnam)
    run_har_analysis(savfile, harfile=harfile, outpath=outpath, outfnam=outfnam)

def test7():
    """Run Harmonics Analysis on Example folder 'sample_zils_nb_sec' case.
    Output Reports created in 'outpath' folder with 'outfnam' used for file name prefix.
    Also specified values to some API arguments.
    """
    workdir  = os.path.dirname(__file__)
    datapath = workdir
    savfile  = os.path.join(datapath, "sample_zils_nb_sec.sav")
    harfile  = os.path.join(datapath, "sample_zils_har.rawx")
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils_nb_sec")
    run_har_analysis(savfile, harfile=harfile, outpath=outpath, linmdl=1,
                     dstnrptop=1, imachimpop=1, dcimpop=1, triplenop=1)

def test8():
    """Run Harmonics Analysis on Example folder 'sample_zils_nb_sec' case.
    Output Reports created in 'outpath' folder with 'outfnam' used for file name prefix.
    Also specified values to some API arguments.
    Do frequency scan on few buses.
    """
    workdir  = os.path.dirname(__file__)
    datapath = workdir
    savfile  = os.path.join(datapath, "sample_zils_nb_sec.sav")
    harfile  = os.path.join(datapath, "sample_zils_har.rawx")
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils_nb_sec_few")
    run_har_analysis(savfile, 101, 212, 154, harfile=harfile, outpath=outpath, linmdl=1,
                     dstnrptop=1, imachimpop=1, dcimpop=1, triplenop=1)

def test9():
    """Plot Frequency Scan, one file
    """
    kwds = {}
    kwds['basemva'] = 100.0
    kwds['basekv']  = 21.6
    kwds['basehz']  = 60.0
    kwds['hmajor']  = []
    kwds['ymajor']  = []
    kwds['ttl_lst'] = ['bus101_ohms (sample_zils_nb_sec_few)']
    kwds['add_lgnd']= True
    kwds['plotzpu'] = False
    workdir  = os.path.dirname(__file__)
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils_nb_sec_few")
    csvfile1 = os.path.join(outpath, "sample_zils_nb_sec_fscan.csv")
    kwds['figfile'] = os.path.join(outpath, "fscan_bus101_ohms.png")
    plot_frequency_scan(101, csvfile1, **kwds)

def test10():
    """Plot Frequency Scan, two files
    """
    kwds = {}
    kwds['basemva'] = 100.0
    kwds['basekv']  = 21.6
    kwds['basehz']  = 60.0
    kwds['hmajor']  = []
    kwds['ymajor']  = []
    kwds['ttl_lst'] = ['bus101_ohms (sample_zils_nb_sec_few)', 'bus101_ohms (sample_zils)']
    kwds['add_lgnd']= True
    kwds['plotzpu'] = False
    workdir  = os.path.dirname(__file__)
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils_nb_sec_few")
    csvfile1 = os.path.join(outpath, "sample_zils_nb_sec_fscan.csv")
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils")
    csvfile2 = os.path.join(outpath, "sample_zils_fscan.csv")
    kwds['figfile'] = os.path.join(outpath, "fscan_bus101_ohms.pdf")
    plot_frequency_scan(101, csvfile1, csvfile2, **kwds)

def test11():
    """Plot Frequency Scan, two files, figfiletype=pdfobj
    """
    from matplotlib.backends.backend_pdf import PdfPages

    kwds = {}
    kwds['basemva'] = 100.0
    kwds['basekv']  = 21.6
    kwds['basehz']  = 60.0
    kwds['hmajor']  = []
    kwds['ymajor']  = []
    kwds['ttl_lst'] = ['bus101_ohms (sample_zils_nb_sec_few)', 'bus101_ohms (sample_zils)']
    kwds['add_lgnd']= True
    kwds['plotzpu'] = False
    workdir  = os.path.dirname(__file__)
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils_nb_sec_few")
    csvfile1 = os.path.join(outpath, "sample_zils_nb_sec_fscan.csv")
    outpath  = os.path.join(workdir, "output_harmonics_demo", "sample_zils")
    csvfile2 = os.path.join(outpath, "sample_zils_fscan.csv")

    pdffile = os.path.join(outpath, "fscan_bus101_ohms_2.pdf")
    pdfobj = PdfPages(pdffile)

    kwds['figfiletyp'] = 'pdfobj'
    kwds['figfile'] = pdfobj

    plot_frequency_scan(101, csvfile1, **kwds)
    plot_frequency_scan(101, csvfile2, **kwds)

    pdfobj.close()
    print(" Plots saved: {}".format(pdffile))

# ----------------------------
def _temp():
    pass
    # Available tests
    # Note 1: Run tests 2, 2A, 3, 3A, 9, 10, 11 from outside of PSSE GUI.
    # Note 2: Other tests can be run from inside as well as outside of PSSE GUI.
    # Note 3: Copy and Modify test4() and later tests to use on any SAV and HAR files.
    #
    test1()    # Run Harmonics Analysis using IEEE Test case
    test1A()   # Run Harmonics Analysis using IEEE Test case and specify thresholds to filter thevenin resonance frequencies
    test2()    # IEEE Test case: Plot Frequency scan PSSE Results.
    test2A()   # Plot Harmonics Test PSSE Results and specify thresholds to filter thevenin resonance frequencies
    test3()    # Plot Harmonics Test PSSE and harmonics Task Force Results and compare PSSE and TF distortion calculation results
    test3A()   # Plot Harmonics Test PSSE and harmonics Task Force Results and specify thresholds to filter thevenin resonance frequencies
    test4()    # Run Harmonics Analysis on Example folder 'sample' case, Output Reports created in Report Window
    test5()    # Run Harmonics Analysis on Example folder 'sample_zils' case, Output Reports created in files
    test6()    # Run Harmonics Analysis on Example folder 'sample_nb' case
    test7()    # Run Harmonics Analysis on Example folder 'sample_zils_nb_sec' case
    test8()    # Run Harmonics Analysis on Example folder 'sample_zils_nb_sec' case and frequency scan on few buses
    test9()    # Plot Frequency Scan, one file [sample_zils_nb_sec_few]
    test10()   # Plot Frequency Scan, two files [sample_zils_nb_sec_fscan, sample_zils_fscan]
    test11()   # Plot Frequency Scan, two files, figfiletype=pdfobj

# ==============================================================================
if __name__=="__main__":
    pass
    # Modify following two lines as desired and run.
    # import psse3504
    # test1()
