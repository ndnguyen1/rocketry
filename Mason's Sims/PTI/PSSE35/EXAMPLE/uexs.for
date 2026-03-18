C[UEXS]         05/12/20      SIMPLE EXCITATION SYSTEM MODEL
C  
C  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
C  *                                                                         *
C  *  THIS PROGRAM AND ITS DOCUMENTATION ARE TRADE SECRETS OF POWER TECHNO-  *
C  *  LOGIES, A DIVISION OF S&W CONSULTANTS, INC.  THEY HAVE BEEN LEASED TO  *
C  *                   YOU, OUR CLIENT,                                      *
C  *  SUBJECT TO TERMS WHICH PROHIBIT YOU FROM DISCLOSING OR TRANSFERRING    *
C  *  THE PROGRAM OR ITS DOCUMENTATION, WHETHER IN ITS ORIGINAL OR MODIFIED  *
C  *  FORM, TO A THIRD PARTY, OR FROM USING THE PROGRAM FOR ANY PURPOSE      *
C  *  OTHER THAN COMPUTATION  RELATING TO YOUR OWN SYSTEM.  ANY SUCH         *
C  *  TRANSFER OR USE BY YOU OR YOUR EMPLOYEES WILL CONSTITUTE A BREACH OF   *
C  *  CONFIDENCE AND OF THE CONTRACT UNDER WHICH RIGHTS OF USE HAVE BEEN     *
C  *  GRANTED.                                                               *
C  *                                                                         *
C  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
C++
C     This model is similar to PSSE library model SEXS with the following
C     simplification:
C     a) the SEXS lead-lag block (shown in SEXS as TA and TB) is removed
C     b) the max. and min. limits (shown in SEXS block diagram as EMAX & EMIN
C        is also not modeld).
C--
      SUBROUTINE UEXS(MC,SLOT)
C++
C     define the local variables and global variables that are going to be used
C     in the model
C--  
      INCLUDE 'COMON4.INS'   ! this is the global declaration
C
      IMPLICIT NONE
C++
C     Now add all the local variable declarations that will be used in this 
C     model
C--     
      INTEGER IB    ! bus index
      INTEGER IERR  ! error code
      INTEGER J     ! starting CON index
      INTEGER K     ! starting state index
      INTEGER L     ! starting VAR index
      INTEGER M     ! starting ICON index
      INTEGER MC    ! this is the machine index
      INTEGER SLOT  ! used to get starting indices J, K, L & M
C
      REAL Verr   ! error signal   
      REAL VINP   ! block input
      REAL VOUT   ! block output
C
      LOGICAL ERRFLG ! used in docu,check functionality
C
      IF (MODE == 8) THEN
C++
C     Add the logic here for wahtever the model is expected to do when MODE is
C     8.
C--
         J=1
         CON_DSCRPT(J)   = 'TA (s), lead time constant'
         CON_DSCRPT(J+1) = 'TB (s), lag time constant'
         CON_DSCRPT(J+2) = 'K (pu), exciter gain'
         CON_DSCRPT(J+3) = 'Te (s), exciter time constant' 
         CON_DSCRPT(J+4) = 'EMIN (pu), exciter minimum'
         CON_DSCRPT(J+5) = 'EMAX (pu), exciter maximum'    
C
         RETURN
      ENDIF
C++
C     At this point in the code, MODE is any value 1 through 7
C--
      J = STRTIN(1,SLOT)    ! starting CON index
      K = STRTIN(2,SLOT)    ! starting state index
      L = STRTIN(3,SLOT)    ! since this model does not use VAR, L will be 0
      M = STRTIN(4,SLOT)    ! since this model does not use ICON, M will be 0
C++
C     Get the value of IB which is the bus index. IB is the index of the bus
C     at which the machie is connected
C--
      IB = NUMTRM(MC)   ! bus sequence number
C++
C     If NUMTRM(MC) is negative (which means that IB has a negative value)
C     it means machine is not in-service
C--
      IF (MODE > 4) GO TO 1000   ! MODE 5 through 7, we jump to statement 1000
C++
C    At this point in the code, MODE is any value 1 through 4
C--
      IF (MODE == 2) THEN
C++
C     Add the logic here for whatever the model is expected to do when MODE is
C     2.
C--
         IF (MIDTRM) RETURN  ! means model is not ready for Mid-term simulation
C++
C     At this point we know that we are running the normal stat-space 
C     simulation
C--
         VINP = VREF(MC) - ETERM(MC) + VOTHSG(MC) + VUEL(MC) + VOEL(MC)
         VOUT = LDLG_MODE2(1.0,      ! lead-lag block gain
     &                     CON(J),   ! TA
     &                     CON(J+1), ! TB
     &                     VINP,     ! block input
     &                     K)        ! state index of this block
     &                     
C
         VINP = VOUT
C
         VOUT = NWLAG_MODE2(CON(J+2), ! exciter gain
     &                      CON(J+3), ! exciter time constant
     &                      CON(J+4), ! Emax
     &                      CON(J+5), ! Emin
     &                      VINP,     ! block input
     &                      K+1)      ! state index of this block
C
         RETURN
      ENDIF
C
      IF (MODE == 3) THEN
C++
C     Add the logic here for whatever the model is expected to do when MODE is
C     3.
C--
         IF (MIDTRM) RETURN  ! means model is not ready for Mid-term simulation
C++
C     At this point we know that we are running the normal stat-space 
C     simulation
C--
         VOUT = LDLG_MODE3(1.0,      ! lead-lag block gain
     &                     CON(J),   ! TA
     &                     CON(J+1), ! TB
     &                     VINP,     ! block input
     &                     K)        ! state index of this block
     &                     
C
         VINP = VOUT
C
         VOUT = NWLAG_MODE3(CON(J+2), ! exciter gain
     &                      CON(J+3), ! exciter time constant
     &                      CON(J+4), ! Emax
     &                      CON(J+5), ! Emin
     &                      VINP,     ! block input
     &                      K+1)      ! state index of this block
C++
C     Set the model output
C--
         EFD(MC) = VOUT
C
         RETURN
      ENDIF
C
      IF (MODE == 4) THEN
C++
C     Add the logic here for whatever the model is expected to do when MODE is
C     4.
C--
         IF (MIDTRM) THEN
C++
C     MIDTRM is a logical global variable which is accessible via the include
C     of COMON4.INS. This variable will be TRUE if the user attempts to run
C     a mid-term type simulation.
C
C     Put out a message that the model is not ready or not coded to be run in
C     mid-term type simulation
C--      
            CALL NOTMID  ! this function will put out the necessary message    
            RETURN
C++
C     Set the number of integrators or the number of state variables
C--
         ELSE     ! means MIDTRM is false
C++
C     Check if the highest state number is greater than NINTEG, if it is then
C     set NINTEG equal to the highest state number of that model
C--
           IF (K+1 > NINTEG) NINTEG = K+1
        ENDIF
C
         RETURN
      ENDIF
C
      IF (MODE == 1) THEN
C++
C     Add the logic here for whatever the model is expected to do when MODE is
C     1.
C--
         IF (MIDTRM) RETURN  ! means model is not ready for Mid-term simulation
C
         VOUT = EFD(MC)
         VINP = NWLAG_MODE1(CON(J+2), ! exciter gain
     &                      CON(J+3), ! exciter time constant
     &                      CON(J+4), ! Emax
     &                      CON(J+5), ! Emin
     &                      VOUT,     ! block input
     &                      K+1,      ! state index of this block
     &                      IERR)     ! erro code
C
         VOUT = VINP
C
         VINP = LDLG_MODE1(1.0,      ! lead-lag block gain
     &                     CON(J),   ! TA
     &                     CON(J+1), ! TB
     &                     VINP,     ! block input
     &                     K,        ! state index of this block
     &                     IERR)     ! erro code
C
         VREF(MC) = VINP + ETERM(MC) - VOTHSG(MC) - VUEL(MC) - VOEL(MC)
C
         RETURN
      ENDIF
C++
C     At this point, MODE can be any value 5 through 7
C--
 1000 IB = ABS(IB)
      IF (MODE == 6) THEN
C++
C     Add the logic here for whatever the model is expected to do when MODE is
C     6.
C--
         WRITE(DBUF01,507) NUMBUS(IB), MACHID(MC), CON(J:J+5)
         CALL REPORTS(IPRT,DBUF01,2)
C
         RETURN
      ENDIF
C
      IF ((MODE==5) .OR. (MODE==7)) THEN
C++
C     Here MODE can be either 5 or 7
C--      
         IF (MODE == 5) THEN
C
            CALL docuHeading    ! this prints out the heading for DOCU
C
         ELSE   ! else here means MODE can only be 7
C++
C     Here MODE has a value of 7. Do the data checking for the model
C--
           CALL DOCUCHK(3,'K',conMsgWARN,
     &                  docuChkErr_LessOrEq,100.0,0.0,ERRFLG)
           CALL DOCUCHK(4,'Te',conMsgWarn,
     &                  docuChkErr_Equal,0.0,0.0,ERRFLG)
           IF (.NOT. ERRFLG) THEN    ! means is Te is not zero
              CALL DOCUCHK(4,'Te',conMsgWarn,
     &                  docuChkErr_InclusiveRange,0.1,0.5,ERRFLG)
           ENDIF
C++
C     After doing data checking:
C     a) if there are no errors, RETURN back to PSSE.
C     b) if there is one or more data error, proceed further down, 
C--
           IF (.NOT. ErrorsFound()) RETURN
C
         ENDIF
C++
C     When code comes in here it means either of the following:
C     a) MODE is 5
C     b) MODE is 7 and there is at least one data error
C     We do the following here:
C     a) list the model CON, ICON indices
C     b) list out the CON data
C--
         CALL SHOW_MODEL_INDICIES(0,   ! starting ICON (0 means no ICONs)
     &                            0,   ! last ICON of the model
     &                            J,   ! starting CON of the model
     &                            J+5, ! last CON of the model
     &                            K,   ! starting state index of the model
     &                            K+1, ! last state index of the model
     &                            0,   ! starting VAR index (0 means no VARs)
     &                            0,   ! 1 VAR and hence specify this as 0
     &                            0,   ! starting reserved ICON
     &                            0)   ! ending reserved ICON
C++
C     Now write out the CON value
C--
         WRITE(DBUF01,7) CON(J:J+5)
         CALL REPORTS(IPRT,DBUF01,6) 
C
         RETURN
      ENDIF  
C++
C     All Format statements are placed in one place for ease of readig 
C--
 7    FORMAT(/'        TA             TB            K'/5X,3(G11.4,3X)//
     &         '        Te            Emax         Emin'/5X,3(G11.4,3X)) 
 507  FORMAT(I7,' ''USRMDL''   ',A,'  ''UEXS''    4   0   0   6    2   0'/
     &       7X,6(G11.4,3X),'    /')
C -----------------------------------------------------------------------------
      END SUBROUTINE UEXS
   