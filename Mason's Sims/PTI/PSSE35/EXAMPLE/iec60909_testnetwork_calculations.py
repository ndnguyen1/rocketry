#[iec60909_testnetwork_calculations.py]    Calculation of IEC Test Network 3 Phase Fault Currents by Network Reduction
# =====================================================================================================
'''
This file calculates 3 Phase Fault Currents for IEC Test Network (IEC 60909-4, Figure 16) by network reduction.
Refer to Program Application Guide, Volume I, Chapter 10 for schematics and equations.
It uses network data from IEC 60909-4 Table 11.
This impedance data (corrected if necessary) of the electrical equipment
(see figure 16) is referred to the 110 kV side. Z(2) = Z(1) = Z
Results from these calculations are compared against results from PSS(R)E and those provided in
IEC 60909-4 Table 12.
'''

import os, math, time
sqrt3 = math.sqrt(3.0)
sbase = 100.0     # MVA

str_time = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
fnamout  = str_time + 'iec60909_testnetwork_calculations.txt'
fnamout  = os.path.join(os.getcwd(),fnamout)
foutobj  = open(fnamout,'w')

# =================================================================================
def format_complex(v):
    vre = v.real
    vim = abs(v.imag)
    if v.imag<0:
        sgn = '-'
    else:
        sgn = '+'
    retv = '%-10.6g %s j %-10.6g' % (vre, sgn, vim)
    return retv

def format_z_ratio(vlst,method=None):
    retvlst = []
    for v in vlst:
        vstr = format_complex(v)
        xbyr = v.imag/v.real
        if method=='C':
            xbyr = xbyr/0.4
        elif method=='DC':
            xbyr = xbyr/0.055
        retv = '%s, %-10.6g' % (vstr, xbyr)
        retvlst.append(retv)
    return retvlst

def print_complex(nam, v):
    vstr = format_complex(v)
    retv = '%-7s = %s\n' % (nam, vstr)
    #print retv.strip()
    return retv

def print_impedance_xr_ratio(nam, v, adj=1.0):
    vstr = format_complex(v)
    xbyr = adj*v.imag/v.real
    if adj!=1.0:
        retv = '%-6s = %s  X/R adj = %-10.6g\n' % (nam, vstr, xbyr)
    else:
        retv = '%-6s = %s  X/R     = %-10.6g\n' % (nam, vstr, xbyr)
    print(retv.strip())
    return retv

def print_fault_current(nam,v):
    vrect = format_complex(v)
    vmag = abs(v)
    vang = math.degrees(math.atan(v.imag/v.real))
    #retv = '%-6s = %s    OR %-10.6g / %-5.2g deg\n' % (nam, vrect, vmag, vang)
    retv = '%-6s = %-10.6g\n' % (nam, vmag)
    print(retv.strip())
    return retv

# =================================================================================

def print_z():
    dat_from_table11 = True
    txt = ''
    txt  += print_complex('zq1',    zq1)
    txt  += print_complex('zq1t',   zq1t)
    txt  += print_complex('zq2',    zq2)
    txt  += print_complex('zt3amv', zt3amv)
    txt  += print_complex('zt3bmv', zt3bmv)
    txt  += print_complex('zt3cmv', zt3cmv)
    txt  += print_complex('zt5mv',  zt5mv)
    if not dat_from_table11:
        txt  += print_complex('zt1mv',  zt1mv)
        txt  += print_complex('zg1',    zg1)
        txt  += print_complex('zg1t',   zg1t)
    txt  += print_complex('zs1',     zs1)
    if not dat_from_table11:
        txt  += print_complex('zt2mv',  zt2mv)
        txt  += print_complex('zg2',    zg2)
        txt  += print_complex('zg2t',   zg2t)
    txt  += print_complex('zs2',    zs2)
    txt  += print_complex('zg3',    zg3)
    txt  += print_complex('zg3t',   zg3t)
    txt  += print_complex('zm1',    zm1)
    txt  += print_complex('zm1t',   zm1t)
    txt  += print_complex('zm2',    zm2)
    txt  += print_complex('zm2t',   zm2t)
    txt  += print_complex('zl1',    zl1)
    txt  += print_complex('zl2',    zl2)
    txt  += print_complex('zl3',    zl3)
    txt  += print_complex('zl4',    zl4)
    txt  += print_complex('zl5',    zl5)
    txt  += print_complex('zl6',    zl6)
    txt  += print_complex('zl6t',   zl6t)
    return txt

def print_network_reduction_z(txstr,zdct):
    for k,v in list(zdct.items()):
        txstr += print_complex(k,v)
    return txstr

# =================================================================================

def table11_data(xftr,peak=False):
    # peak = True, calculations are for Peak current, use Rgf for generators.
    
    global zq1, zq1t, zq2, zt3amv, zt3bmv, zt3cmv, zt5mv, zs1
    global zs2, zg3, zg3t, zm1, zm1t, zm2, zm2t
    global zl1, zl2, zl3, zl4, zl5, zl6, zl6t

    # TABLE 11 Data
    zq1    =  0.631933 +   6.319335j
    zq1t   =  0.056874 +   0.568740j
    zq2    =  0.434454 +   4.344543j

    zt3amv =  0.045714 +   8.096989j
    zt3bmv =  0.053563 -   0.079062j
    zt3cmv =  0.408568 +  20.292035j

    zt5mv  =  2.046454 +  49.072241j

    # power station unit 1 data
    #Ks       = 0.995975
    #zg1t     = (0.059977324263+12.3433333333j)
    #zg1t*Ks  = (0.0597359155329+12.2936514167j)
    #zt1mv*Ks = (0.439058979167+14.0430253611j)
    #zs1 = Ks*(zg1t + zt1mv) = (0.4987948947+26.3366767778j)

    Ks1    =  0.995975
    zg1    =  0.059977 +  12.343333j
    zg1c   =  0.059736 +  12.293651j
    zt1c   =  0.439059 +  14.043025j
    #zs1    =  0.498795 +  26.336676j
    zs1    =  zg1c + zt1c

    # power station unit 2 data
    #Ks       = 0.876832
    #zg2t     = (0.65306122449+23.04j)
    #zg2t*Ks  = (0.572624979592+20.20220928j)
    #zt2mv*Ks = (0.63131904+15.1384987665j)
    #zs2 = Ks*(zg2t + zt2mv) = (1.20394401959+35.3407080465j)

    Ks2    =  0.876832
    zg2    =  0.653061 +  23.04j
    zg2c   =  0.572625 +  20.202214j
    zt2c   =  0.631319 +  15.138499j
    #zs2    =  1.203944 +  35.340713j
    zs2    =  zg2c + zt2c

    zg3    =  0.017790 +   1.089623j
    zg3t   =  2.133964 + 130.705301j

    zm1    =  0.341497 +   3.414968j
    zm1t   = 40.964124 + 409.641243j
    zm2    =  0.412137 +   4.121368j
    zm2t   = 49.437719 + 494.377190j

    zl1    = 2.4   + 7.8j
    zl2    = 1.2   + 3.9j
    zl3    = 0.3   + 0.975j
    zl4    = 0.96  + 3.88j
    zl5    = 1.8   + 5.79j
    zl6    = 0.082 + 0.086j
    zl6t   = 9.836281 + 10.316100j

    # Fictitious resistances RGf may be used for the calculation of the peak short circuit current
    # RGf = 0.05 X''d for generators with UrG > 1 kV and SrG >= 100 MVA
    # RGf = 0.07 X''d for generators with UrG > 1 kV and SrG < 100 MVA
    # RGf = 0.15 X''d for generators with UrG <= 1 000 V
    if peak:
        # G1 -> 150 MVA, 21 kV
        # G2 -> 100 MVA, 10.5 kV
        # RGf = 0.05 X''d
        zg1  = complex(0.05*zg1.imag, zg1.imag)
        zg1c = zg1*Ks1
        zs1  = zg1c + zt1c

        zg2  = complex(0.05*zg2.imag, zg2.imag)
        zg2c = zg2*Ks2
        zs2  = zg2c + zt2c

        zg3  = complex(0.07*zg3.imag, zg3.imag)
        zg3t = complex(0.07*zg3t.imag, zg3t.imag)

    if xftr != 1.0:
        zq1    = complex(zq1.real,    zq1.imag*xftr)
        zq1t   = complex(zq1t.real,   zq1t.imag*xftr)
        zq2    = complex(zq2.real,    zq2.imag*xftr)
        zt3amv = complex(zt3amv.real, zt3amv.imag*xftr)
        zt3bmv = complex(zt3bmv.real, zt3bmv.imag*xftr)
        zt3cmv = complex(zt3cmv.real, zt3cmv.imag*xftr)
        zt5mv  = complex(zt5mv.real,  zt5mv.imag*xftr)
        zs1    = complex(zs1.real,    zs1.imag*xftr)
        zs2    = complex(zs2.real,    zs2.imag*xftr)
        zg3    = complex(zg3.real,    zg3.imag*xftr)
        zg3t   = complex(zg3t.real,   zg3t.imag*xftr)
        zm1    = complex(zm1.real,    zm1.imag*xftr)
        zm1t   = complex(zm1t.real,   zm1t.imag*xftr)
        zm2    = complex(zm2.real,    zm2.imag*xftr)
        zm2t   = complex(zm2t.real,   zm2t.imag*xftr)
        zl1    = complex(zl1.real,    zl1.imag*xftr)
        zl2    = complex(zl2.real,    zl2.imag*xftr)
        zl3    = complex(zl3.real,    zl3.imag*xftr)
        zl4    = complex(zl4.real,    zl4.imag*xftr)
        zl5    = complex(zl5.real,    zl5.imag*xftr)
        zl6    = complex(zl6.real,    zl6.imag*xftr)
        zl6t   = complex(zl6t.real,   zl6t.imag*xftr)

# =================================================================================

def parallel(zp,zq):
    return (zp*zq)/(zp+zq)

def calculate_3ph_fault_zthev():
    # Reduction at Bus 5
    z7g  = parallel(zm1t, zm2t)
    z6g1 = zl6t + z7g
    z6g2 = parallel(zg3t, z6g1)
    z56  = zt5mv/2.0
    z5g1 = z56 + z6g2
    z5g2 = parallel(zq2, z5g1)

    rdzstr = ''
    rdzstr = print_network_reduction_z(rdzstr,{'z7g':z7g, 'z6g1':z6g1, 'z6g2':z6g2, 'z56':z56, 'z5g1':z5g1, 'z5g2':z5g2})

    # Reduction at Bus 2
    z12t3   = zt3amv + zt3bmv
    z12t3t4 = z12t3/2.0
    z2g1    = zq1t + z12t3t4
    
    rdzstr = print_network_reduction_z(rdzstr,{'z12t3':z12t3, 'z12t3t4':z12t3t4, 'z2g1':z2g1})

    # delta to star of buses 2, 3, 5, star point=N1
    zden1 = zl1 + zl3 + zl4
    za    = (zl1*zl3) / zden1
    zb    = (zl1*zl4) / zden1
    zc    = (zl3*zl4) / zden1

    rdzstr = print_network_reduction_z(rdzstr,{'za':za, 'zb':zb, 'zc':zc})

    # star to delta of buses N1, 3, 4, and ground
    znum1 = zb*zs2 + zb*zl2 + zs2*zl2
    zd = znum1/zs2
    ze = znum1/zl2
    zf = znum1/zb

    rdzstr = print_network_reduction_z(rdzstr,{'zd':zd, 'ze':ze, 'zf':zf})

    # delta to star of buses N1, 4, 5, star point=N2
    zden2 = zc + zd + zl5
    zg    = (zc*zd)  / zden2
    zh    = (zd*zl5) / zden2
    zi    = (zc*zl5) / zden2

    rdzstr = print_network_reduction_z(rdzstr,{'zg':zg, 'zh':zh, 'zi':zi})

    # Zthev at Bus 4
    z1    = z2g1 + za
    z2    = parallel(z1, ze)
    z3    = z2 + zg
    z4    = zi + z5g2
    z5    = parallel(z3, z4)
    z6    = z5 + zh
    z7    = parallel(z6,zf)
    zthv4 = parallel(z7, zs1)

    rdzstr = print_network_reduction_z(rdzstr,{'z1':z1, 'z2':z2, 'z3':z3, 'z4':z4, 'z5':z5, 'z6':z6, 'z7':z7})

    # Zthev at Bus 5
    z8    = parallel(zs1,zf)
    z9    = z8 + zh
    z10   = parallel(z3,z9)
    z11   = zi + z10
    zthv5 = parallel(z11, z5g2)

    rdzstr = print_network_reduction_z(rdzstr,{'z8':z8, 'z9':z9, 'z10':z10, 'z11':z11})

    # Zthev at Bus 2
    z12   = parallel(z4,z9)
    z13   = z12 + zg
    z14   = parallel(z13,ze)
    z15   = za + z14
    zthv2 = parallel(z15, z2g1)

    rdzstr = print_network_reduction_z(rdzstr,{'z12':z12, 'z13':z13, 'z14':z14, 'z15':z15})

    # Zthev at Bus 1
    z16   = z15 + z12t3t4
    z17   = z16*(400.*400.)/(120.*120.)
    zthv1 = parallel(z17, zq1)

    rdzstr = print_network_reduction_z(rdzstr,{'z16':z16, 'z17':z17})

    # Zthev at Bus 6
    zt5lv = zt5mv*(10.5*10.5)/(115.0*115.0)
    z21   = parallel(z11, zq2)
    z21lv = z21*(10.5*10.5)/(115.0*115.0)
    z22   = z21lv + zt5lv*0.5
    z24   = parallel(zm1, zm2)
    z25   = zl6 + z24
    z26   = parallel(zg3, z25)
    zthv6 = parallel(z22, z26)

    rdzstr = print_network_reduction_z(rdzstr,{'zt5lv':zt5lv, 'z21':z21, 'z21lv':z21lv, 'z22':z22, 'z24':z24, 'z25':z25, 'z26':z26})

    # Zthev at Bus 7
    z27   = parallel(z22, zg3)
    z28   = z27 + zl6
    zthv7 = parallel(z28, z24)

    rdzstr = print_network_reduction_z(rdzstr,{'z27':z27, 'z28':z28})

    zthev = [zthv1, zthv2, zthv4, zthv5, zthv6, zthv7]
    
    return zthev, rdzstr

# =================================================================================

def calculate_3ph_fault_ik(zthev):

    zthv1 = zthev[0]
    zthv2 = zthev[1]
    zthv4 = zthev[2]
    zthv5 = zthev[3]
    zthv6 = zthev[4]
    zthv7 = zthev[5]

    vflt = 1.1*110.0/sqrt3
    if2   = vflt/zthv2
    if4   = vflt/zthv4
    if5   = vflt/zthv5

    vflt1 = 1.1*380.0/sqrt3
    if1   = vflt1/zthv1

    vfl67 = 1.1*10.0/sqrt3
    if6   = vfl67/zthv6
    if7   = vfl67/zthv7

    ik = [if1, if2, if4, if5, if6, if7]
    return ik

# =================================================================================

def calculate_k_factor_method_B(bus,zc):
    r = zc.real
    x = zc.imag
    rx = r/x
    rbyx = -3.0*rx
    k = 1.02 + 0.98*math.exp(rbyx)
    if bus==7: k = k*1.15   # add safety factor for bus 7 faults
    if k>2.0: k=2.0
    return k    
    
def calculate_k_factor_method_C(zc):
    r = zc.real
    x = zc.imag
    rx = r/x
    rbyx = 0.4*rx
    rbyx = -3.0*rbyx
    k = 1.02 + 0.98*math.exp(rbyx)
    #print 'K factor for r/x=%f, is k=%f' % (rbyx,k)
    return k

def calculate_ip(buslst,iklst,zclst,method):
    klst  = []
    iplst = []
    for bus,ik,zc in zip(buslst,iklst,zclst):
        ik = abs(ik)
        if method=='B':
            k  = calculate_k_factor_method_B(bus,zc)
        if method=='C':
            k  = calculate_k_factor_method_C(zc)
        ip = k*math.sqrt(2.0)*ik
        klst.append(k)
        iplst.append(ip)

    return klst, iplst

def back_calculate_k(iklst,iplst):
    klst = []
    for ik,ip in zip(iklst,iplst):
        # ip=k*sprt(2)*ik
        k = ip/(math.sqrt(2)*ik)
        klst.append(k)
    return klst

def calculate_idc(iklst,zlst):
    # idc = sprt(2)*ik*e^(-2piftR/X)
    idclst = []
    for ik,z in zip(iklst,zlst):
        r = z.real
        x = z.imag
        rx = r/x
        rx = 0.055*rx
        rbyx = -2.0*math.pi*50.0*0.1*rx
        k = math.exp(rbyx)
        idc = math.sqrt(2)*abs(ik)*k
        #print 'dc component: z, k, abs(ik), idc = ',z,k,abs(ik),idc
        idclst.append(idc)
    return idclst
    
# =================================================================================

foutobj.write('IEC 60909-4:2000 Figure 16 (Page 121) 3-phase Fault Calculations with Network reduction')
foutobj.write(' '+time.asctime())
foutobj.write('\n')

buses = [1,2,4,5,6,7]

# Base frequency calculations
xftr = 1.0
table11_data(xftr)
base_z = print_z()

zthev_bas, rdzstr_bas = calculate_3ph_fault_zthev()

ik_bas = calculate_3ph_fault_ik(zthev_bas)

# Method B
# Method B peak currents are worse (compared to results in standard) when Rgf is used.
#xftr = 1.0
#table11_data(xftr,peak=True)
#mthdB_z = print_z()
#zthev_b, rdzstr_b = calculate_3ph_fault_zthev()
#k_b, ip_b = calculate_ip(buses,ik_bas,zthev_b,method='B')
k_b, ip_b = calculate_ip(buses,ik_bas,zthev_bas,method='B')

# Method C
xftr = 20.0/50.0
table11_data(xftr,peak=True)
mthdC_z = print_z()

zthev_c, rdzstr_c = calculate_3ph_fault_zthev()
k_c, ip_c = calculate_ip(buses,ik_bas,zthev_c,method='C')

# DC Component
# tmin=0.1 s, f*t = 50*0.1 = 5, fc/f=0.055
xftr = 0.055
table11_data(xftr,peak=False)
dc_z = print_z()

zthev_dc, rdzstr_dc = calculate_3ph_fault_zthev()
idc_cal = calculate_idc(ik_bas,zthev_dc)

# Table 12 from Standard
ik1_tbl12   = 40.6447
ip1_b_tbl12 = 100.5766
ip1_c_tbl12 = 100.5677
ib1_tbl12   = 40.645

ik2_tbl12   = 31.7831
ip2_b_tbl12 = 80.8249
ip2_c_tbl12 = 80.6079
ib2_tbl12   = 31.570

ik4_tbl12   = 16.2277
ip4_b_tbl12 = 36.8041
ip4_c_tbl12 = 36.8427
ib4_tbl12   = 16.017

ik5_tbl12   = 33.1894
ip5_b_tbl12 = 83.6266
ip5_c_tbl12 = 83.4033
ib5_tbl12   = 32.795

ik6_tbl12   = 37.5629
ip6_b_tbl12 = 99.1910
ip6_c_tbl12 = 98.1434
ib6_tbl12   = 34.028

ik7_tbl12   = 25.5895
ip7_b_tbl12 = 51.3864*1.15
ip7_c_tbl12 = 51.6899
ib7_tbl12   = 23.212

ik_tbl12   = [ik1_tbl12,   ik2_tbl12,   ik4_tbl12,   ik5_tbl12,   ik6_tbl12,   ik7_tbl12  ] 
ip_b_tbl12 = [ip1_b_tbl12, ip2_b_tbl12, ip4_b_tbl12, ip5_b_tbl12, ip6_b_tbl12, ip7_b_tbl12] 
ip_c_tbl12 = [ip1_c_tbl12, ip2_c_tbl12, ip4_c_tbl12, ip5_c_tbl12, ip6_c_tbl12, ip7_c_tbl12] 
ib_tbl12   = [ib1_tbl12,   ib2_tbl12,   ib4_tbl12,   ib5_tbl12,   ib6_tbl12,   ib7_tbl12  ] 

k_b_tbl12  = back_calculate_k(ik_tbl12,ip_b_tbl12)
k_c_tbl12  = back_calculate_k(ik_tbl12,ip_c_tbl12)

# PSS(R)E Results
# Bus Nums      1        2        4        5        6       7
ik_psse  = [ 40.6447, 31.7830, 16.2277, 33.1894, 37.5628, 25.5894]
ipb_psse = [100.5766, 80.5119, 36.8041, 83.6265, 99.1908, 59.0943]
ipc_psse = [100.5676, 80.6079, 36.8427, 83.4033, 98.1432, 51.6898]
idc_psse = [  2.7396, 12.7917,  2.6296,  3.9796, 15.1072,  0.0671]
ibs_psse = [ 40.6426, 31.5777, 16.0211, 32.8065, 34.0131, 23.1936]
iba_psse = [ 40.7348, 34.0702, 16.2354, 33.0470, 37.2171, 23.1937]

# Print Base frequency and Method C impedances
base_z_lst  = base_z.split('\n')
mthdC_z_lst = mthdC_z.split('\n')
dc_z_lst = dc_z.split('\n')

rdzstr_bas_lst = rdzstr_bas.split('\n')
rdzstr_c_lst   = rdzstr_c.split('\n')
rdzstr_dc_lst  = rdzstr_dc.split('\n')

hdr = r"""NETWORK ELEMENT IMPEDANCES in OHMS (COMPARE this to TABLE 11, PP 127)
|---------- BASE FREQUENCY ------|   |  |---- METHOD C FREQ (fc/f=0.4)---|   |  |--- DC COMPONENT (fc/f=0.055)---|"""
foutobj.write(hdr)
foutobj.write('\n')

for v1,v2,v3 in zip(base_z_lst, mthdC_z_lst,dc_z_lst):
    if not v1: continue
    txt = v1 + '  |  ' + v2 + '  |  ' + v3 + '\n'
    foutobj.write(txt)
    

hdr = r"""
NETWORK REDUCTION  CALCULATION IMPEDANCES in OHMS 
|---------- BASE FREQUENCY ------|   |  |---- METHOD C FREQ (fc/f=0.4)---|   |  |--- DC COMPONENT (fc/f=0.055)---|"""
foutobj.write(hdr)
foutobj.write('\n')

for v1,v2,v3 in zip(rdzstr_bas_lst, rdzstr_c_lst, rdzstr_dc_lst):
    if not v1: continue
    txt = v1 + '  |  ' + v2 + '  |  ' + v3 + '\n'
    foutobj.write(txt)

hdr = r"""
Thevenin Impedance in OHMS calculated with NETWORK REDUCTION (R+jX, X/R ratio)
|BUS| |---------- BASE FREQUENCY --------|    |   |----- METHOD C FREQ (fc/f=0.4)----|    |   |---- DC COMPONENT (fc/f=0.055)----|"""
foutobj.write(hdr)
foutobj.write('\n')

zstrlst_bas = format_z_ratio(zthev_bas)
zstrlst_c   = format_z_ratio(zthev_c,method='C')
zstrlst_dc  = format_z_ratio(zthev_dc,method='DC')
for b,zstr, zstr_c, zstr_dc in zip(buses,zstrlst_bas,zstrlst_c,zstrlst_dc):
    foutobj.write('  %d    %s       %s       %s' % (b, zstr, zstr_c, zstr_dc))
    foutobj.write('\n')


hdr ="""
 METHOD        BUS    I"k       K ip(50)     ip(50)     K ip(20)     ip(20)      Ib dc"""
foutobj.write(hdr)
foutobj.write('\n')

for b1,ik,kb,ipb,kc,ipc,idc,ik_t,kb_t,ipb_t,kc_t,ipc_t,ik_e,ipb_e,ipc_e,idc_e in zip(buses, ik_bas, k_b, ip_b, k_c, ip_c, idc_cal,
                                                            ik_tbl12, k_b_tbl12, ip_b_tbl12, k_c_tbl12, ip_c_tbl12,
                                                            ik_psse, ipb_psse, ipc_psse, idc_psse):
    ikabs = abs(ik)
    s1    = ' '
    lin1 = " CALCULATED   %(b1)3d   %(ikabs)-10.4f   %(kb)-10.4f %(ipb)-10.4f   %(kc)-10.4f %(ipc)-10.4f   %(idc)-10.4f" % vars()
    lin2 = " PSS(R)E      %(s1)3s   %(ik_e)-10.4f   %(s1)10s %(ipb_e)-10.4f   %(s1)10s %(ipc_e)-10.4f   %(idc_e)-10.4f" % vars()
    lin3 = " STANDARD     %(s1)3s   %(ik_t)-10.4f   %(kb_t)-10.4f %(ipb_t)-10.4f   %(kc_t)-10.4f %(ipc_t)-10.4f" % vars()
    foutobj.write(lin1)
    foutobj.write('\n')

    foutobj.write(lin2)
    foutobj.write('\n')

    foutobj.write(lin3)
    foutobj.write('\n\n')

foutobj.close()    

msg = " Results saved in file: %s" % fnamout
print(msg)
# =================================================================================
