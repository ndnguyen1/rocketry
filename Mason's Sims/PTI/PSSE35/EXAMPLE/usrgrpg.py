# [pssgrpg.py]     04/23/20     Python Functions to emulate GRPG
#
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#  *                                                                     *
#  *  THIS PROGRAM AND ITS DOCUMENTATION ARE TRADE SECRETS OF POWER      *
#  *  TECHNOLOGIES, INC. (PTI).  THEY HAVE BEEN LEASED TO                *
#  *                   client full name (clabr)                          *
#  *  SUBJECT TO TERMS WHICH PROHIBIT clabr FROM DISCLOSING OR TRANS-    *
#  *  FERRING THE PROGRAM OR ITS DOCUMENTATION, WHETHER IN ITS ORIGINAL  *
#  *  OR MODIFIED FORM, TO A THIRD PARTY, OR FROM USING THE PROGRAM FOR  *
#  *  ANY PURPOSE OTHER THAN COMPUTATION RELATING TO clabr'S OWN SYSTEM. *
#  *  ANY SUCH TRANSFER OR USE BY clabr OR ITS EMPLOYEES WILL CONSTI-    *
#  *  TUTE A BREACH OF CONFIDENCE AND OF THE CONTRACT UNDER WHICH        *
#  *  RIGHTS OF USE HAVE BEEN GRANTED.                                   *
#  *                                                                     *
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
'''The functions in this Python module return:
    - formatted text which can be used to put annotation on slider diagrams.
    - values which are used to generate formatted text above.
Example: function 'area_summary' returns formatted text and
         function 'area_summary_v' returns values used by 'area_summary'
         i.e, functions with name ending with "_v" return values
'''

import psspy

#========================================================================================

def area_summary_v(arnum):
    '''Returns desired and net interchange, loads, generation and losses for
    area 'arnum'.
pdes,pint,qint,pload,qload,pgen,qgen,ploss,qloss = pssgrpg.area_summary_v(arnum)
'''
    sid  = 3
    flag = 2
    ierr = psspy.asys(sid, flag, [arnum])
    ierr, rdata = psspy.aareareal(sid,flag,
        ['PDES','PINT','QINT','PLOADLD','QLOADLD','PGEN','QGEN','PLOSS','QLOSS'])
    psspy.asysdef(sid, 0)
    if ierr==0:
        (pdes,pint,qint,ploadld,qloadld,pgen,qgen,ploss,qloss) = rdata
        if len(pdes)>0:
           return pdes[0],pint[0],qint[0],ploadld[0],qloadld[0],pgen[0],qgen[0],ploss[0],qloss[0]
    return None,None,None,None,None,None,None,None,None

def area_summary(arnum):
    '''Returns formatted text showing desired and net interchange, loads, generation
     and losses for area 'arnum'.
txt = pssgrpg.area_summary(arnum)
'''
    pdes,pint,qint,ploadld,qloadld,pgen,qgen,ploss,qloss = area_summary_v(arnum)
    if pdes:
        txt = '''Area %(arnum)d Summary:
  Desired Interchange: %(pdes)9.2f MW
  Net Interchange    : %(pint)9.2f MW, %(qint)9.2f MVAR
  Area loads         : %(ploadld)9.2f MW, %(qloadld)9.2f MVAR
  Area generation    : %(pgen)9.2f MW, %(qgen)9.2f MVAR
  Area losses        : %(ploss)9.2f MW, %(qloss)9.2f MVAR''' % vars()
    else:
        txt = '''Area %(arnum)d Summary:
  Desired Interchange: None
  Net Interchange    : None
  Area loads         : None
  Area generation    : None
  Area losses        : None''' % vars()
    return txt

def area_interchange_net_v(arnum):
    '''Returns desired and net interchange for area 'arnum'.
pdes,pint,qint = pssgrpg.area_interchange_net_v(arnum)
'''
    sid  = 3
    flag = 2
    ierr = psspy.asys(sid, flag, [arnum])
    ierr, rdata = psspy.aareareal(sid,flag,['PDES','PINT','QINT'])
    psspy.asysdef(sid, 0)
    if ierr==0:
        (pdes,pint,qint) = rdata
        if len(pdes)>0:
           return pdes[0],pint[0],qint[0]
    return None,None,None

def area_interchange_net(arnum):
    '''Returns formatted text showing desired and net interchange for area 'arnum'.
txt = pssgrpg.area_interchange_net(arnum)
'''
    pdes,pint,qint = area_interchange_net_v(arnum)
    if pdes:
        txt = '''Area %(arnum)d Interchange:
  Desired Interchange: %(pdes)9.2f MW
  Net Interchange    : %(pint)9.2f MW, %(qint)9.2f MVAR''' % vars()
    else:
        txt = '''Area %(arnum)d Interchange:
  Desired Interchange: None
  Net Interchange    : None''' % vars()
    return txt

def area_interchange_ij_v(iar,jar):
    '''Returns interchange from area 'iar' to area 'jar'.
p,q = pssgrpg.area_interchange_ij_v(iar,jar)
'''
    ierr, cmpval = psspy.aritoj(iar,jar)
    if ierr==0:
        return cmpval.real, cmpval.imag
    return None,None

def area_interchange_ij(iar,jar):
    '''Returns formatted text showing interchange from area 'iar' to area 'jar'.
txt = pssgrpg.area_interchange_ij(iar,jar)
'''
    pint,qint = area_interchange_ij_v(iar,jar)
    if pint:
        txt = '''Interchange from Area %(iar)d to Area %(jar)d: %(pint)9.2f MW, %(qint)9.2f MVAR''' % vars()
    else:
        txt = '''Interchange from Area %(iar)d to Area %(jar)d: None''' % vars()
    return txt

#========================================================================================

def zone_summary_v(znnum):
    '''Returns net interchange, loads, generation and losses for zone 'znnum'.
pint,qint,pload,qload,pgen,qgen,ploss,qloss = pssgrpg.zone_summary_v(znnum)
'''
    sid  = 3
    flag = 2
    ierr = psspy.zsys(sid, flag, [znnum])
    ierr, rdata = psspy.azonereal(sid,flag,
        ['PINT','QINT','PLOADLD','QLOADLD','PGEN','QGEN','PLOSS','QLOSS'])
    psspy.zsysdef(sid, 0)
    if ierr==0:
        (pint,qint,ploadld,qloadld,pgen,qgen,ploss,qloss) = rdata
        if len(pint)>0:
           return pint[0],qint[0],ploadld[0],qloadld[0],pgen[0],qgen[0],ploss[0],qloss[0]
    return None,None,None,None,None,None,None,None,None

def zone_summary(znnum):
    '''Returns formatted text showing net interchange, loads, generation and losses
    for zone 'znnum'.
txt = pssgrpg.zone_summary(znnum)
'''
    pint,qint,ploadld,qloadld,pgen,qgen,ploss,qloss = zone_summary_v(znnum)
    if pint:
        txt = '''Zone %(znnum)d Summary:
  Net Interchange : %(pint)9.2f MW, %(qint)9.2f MVAR
  Zone loads      : %(ploadld)9.2f MW, %(qloadld)9.2f MVAR
  Zone generation : %(pgen)9.2f MW, %(qgen)9.2f MVAR
  Zone losses     : %(ploss)9.2f MW, %(qloss)9.2f MVAR''' % vars()
    else:
        txt = '''Zone %(znnum)d Summary:
  Net Interchange : None
  Zone loads      : None
  Zone generation : None
  Zone losses     : None''' % vars()
    return txt

def zone_interchange_ij_v(izn,jzn):
    '''Returns interchange from zone 'izn' to zone 'jzn'.
p,q = pssgrpg.zone_interchange_ij_v(izn,jzn)
'''
    ierr, cmpval = psspy.znitoj(izn,jzn)
    if ierr==0:
        return cmpval.real, cmpval.imag
    return None,None

def zone_interchange_ij(izn,jzn):
    '''Returns formatted text showing interchange from zone 'izn' to zone 'jzn'.
txt = pssgrpg.zone_interchange_ij(izn,jzn)
'''
    pint,qint = zone_interchange_ij_v(izn,jzn)
    if pint:
        txt = '''Interchange from Zone %(izn)d to Area %(jzn)d: %(pint)9.2f MW, %(qint)9.2f MVAR''' % vars()
    else:
        txt = '''Interchange from Zone %(izn)d to Zone %(jzn)d: None''' % vars()
    return txt

#========================================================================================

def system_summary_v():
    '''Returns working case loads, generation and losses.
pload,qload,pgen,qgen,ploss,qloss = pssgrpg.system_summary_v()
'''
    ierr, syslod = psspy.systot('LOAD')
    ierr, sysgen = psspy.systot('GEN')
    ierr, syslos = psspy.systot('LOSS')
    return syslod.real, syslod.imag, sysgen.real, sysgen.imag, syslos.real, syslos.imag

def system_summary():
    '''Returns formatted text showing working case loads, generation and losses.
txt = pssgrpg.system_summary()
'''
    pload,qload,pgen,qgen,ploss,qloss = system_summary_v()
    txt = '''Case Summary:
  Total loads      : %(pload)9.2f MW, %(qload)9.2f MVAR
  Total generation : %(pgen)9.2f MW, %(qgen)9.2f MVAR
  Total losses     : %(ploss)9.2f MW, %(qloss)9.2f MVAR''' % vars()
    return txt

#========================================================================================
