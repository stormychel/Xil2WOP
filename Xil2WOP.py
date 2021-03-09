# Xil2WOP: Converter Xilog3->WoodWOP door Michel Storms (stormychel@me.com)

# Versie 1.27.0 (Major, Minor, Patch)

#DEBUG
Debug=2 #0=stil, 1=info, 2=debug

#IMPORTS
from datetime import datetime
import glob
import math
import re
import sys

#CLASSES
class BohrVert: #EDIT
    """<102 \BohrVert\\""" #BohrVert: Drillings vertical
    XA="DX-34" #Drill coordinate in X
    YA="57" #Drill coordinate in Y
    BM="LS" #Drill mode
    TI="19" #Depth of drilling
    DU="15.0" #Diameter of drilling (alternative DU or TNO)
    TNO="0" #T-number (tool number) (alternative TNO or DU)
    LA="0" #Lenghts of hole row (alternative LA or AN)
    AN="1" #Number of drillings (alternative LA or AN)
    MI="0" #Hole row type: 0:start point- 1:center point.
    AB="0" #Raster distance of drillings
    WI="0" #Hole raster direction angle in X/Y-Level (optional additiv to WI or XR and YR).
    XR="0" #Hole row direction in X
    YR="0" #Hole row direction in Y
    F_="STANDARD" #Feedrate
    S_="2" #RPM
    KO="0" #Coordinate system
    ZA="0" #Z-Reference value for the depth
    QQ="1" #Condition, printed to file as ?? instead of QQ
    EN="1" #Enable 0=no 1=yes
    MNM="X2W: Boring D=??? / Z=???." #Info comment
    
class Contour: #EDIT, USE
    """Houdt informatie contour bij."""
    CurrentX = "00000000";
    CurrentY = "00000000";
    CurrentInfo = "00000000";
    PreviousX = CurrentX;
    PreviousY = CurrentY;

class Field: #EDIT, USE
    """Houdt informatie huidig werkveld (Xilog's 'F') bij."""
    Current = "1";
    Previous = Current;

#VARIABLES (velen nog in class steken zodat we geen globals nodig hebben)
Contour_Nummer=0 #nummering contour /// WORDT Contour.Nummer
Contour_Positie=0 #nummering positie /// WORDT Contour.Positie
errors=0 #teller errors
ruggroef_Breedte=7.80 #=dikte T184
ruggroefT184 = 0 #flag ruggroef gedetecteerd
ReleaseCode="%s-%s-%s" %(datetime.now().year, datetime.now().month, datetime.now().day)
wroteheader=0
command=""
ContourInfoList = []
current_C_S = {'': '0', 'S': '0'}
xbo = {'D': '50', 'y': '0', 'R': '1', 'x': '0', 'Y': '-10', 'F': '1', 'X': '-10', 'Z': '-5', 'T': '120'} # dictionary voorbereiden met alle mogelijke indexes
xlinesb = {}
sx = {'': '0', 'M': '0'} #voor SXSY()
sy = {'': '0', 'M': '0'}
g2g3 = {'X': '0', 'Y': '0', 'r': '0'}
xg0 = {'S': '9000', 'T': '000', 'V': '9000', 'Y': '-10', 'X': '-10', 'Z': '-5', 'F': '1'} # dictionary voorbereiden met alle mogelijke indexes
g1xl2p = {}
sx_switched=0
sy_switched=0
sxs = {}
Xilog3_line = 0 #houdt bij op welke lijn van de inputfile we zitten
ToolDiamTable = {'T64': '8', 'T65': '8', 'T66': '10', 'T67': '10', 'T1': '10', 'T2': '10', 'T3': '10', 'T4': '10', 'T5': '10', 'T6': '8', 'T7': '6', 'T8': '10', 'T9': '4', 'T10': '10', 'T11': '10', 'T12': '10', 'T13': '10', 'T14': '10', 'T15': '10', 'T16': '10', 'T17': '8', 'T18': '35', 'T19': '8', 'T20': '6', 'T21': '5', 'T22': '5', 'T23': '5', 'T24': '5', 'T25': '5', 'T26': '5', 'T27': '5', 'T28': '5', 'T29': '8', 'T30': '10', 'T119': '35', 'T120': '40'} # boortabel
X2W_OPT_NORMAAL=0
X2W_OPT_NCSTOP=31
X2W_OPT=X2W_OPT_NORMAAL
xea = {}
xpocket = {'A': '0', 'r': '0', 'C': '2', 'F': '1', 'I': 'DX/2', 'J': 'DY/2', 'T': '179', 'V': '5000', 'Y': '50', 'X': '100', 'Z': '5'}

#FUNC
def show_exception_and_exit(exc_type, exc_value, tb): #error handling
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    raw_input("Press key to exit.")
    sys.exit(-1)

def WriteHeader():
    if Debug==1 or Debug==2:
        print'WriteHeader():',header
    print >>woodWOPfile, '[H'
    print >>woodWOPfile, 'VERSION="4.0 Alpha"'
    print >>woodWOPfile, 'WW="6.0.18"'
    print >>woodWOPfile, 'HP="1"'
    print >>woodWOPfile, 'IN="0"'
    print >>woodWOPfile, 'GX="1"'
    print >>woodWOPfile, 'BFS="1"'
    print >>woodWOPfile, 'GY="0"'
    print >>woodWOPfile, 'GXY="0"'
    print >>woodWOPfile, 'UP="0"'
    print >>woodWOPfile, 'FM="1"'
    print >>woodWOPfile, 'FW="200"'
    print >>woodWOPfile, 'ZS="20"'
    print >>woodWOPfile, 'HS="0"'
    print >>woodWOPfile, 'OP="X2W_OPT"'
    print >>woodWOPfile, 'MAT="WEEKE"'
    print >>woodWOPfile, 'DN="STANDARD"'
    print >>woodWOPfile, 'INCH="0"'
    print >>woodWOPfile, 'VIEW="NOMIRROR"'
    print >>woodWOPfile, 'ANZ="1"'
    print >>woodWOPfile, 'BES="0"'
    print >>woodWOPfile, 'ENT="0"'
    print >>woodWOPfile, '_BSX=%s' %header['DX']
    print >>woodWOPfile, '_BSY=%s' %header['DY']
    print >>woodWOPfile, '_BSZ=%s' %header['DZ']
    print >>woodWOPfile, '_FNX=0.000000'
    print >>woodWOPfile, '_FNY=0.000000'
    print >>woodWOPfile, '_RNX=0.000000'
    print >>woodWOPfile, '_RNY=0.000000'
    print >>woodWOPfile, '_RNZ=0.000000'
    print >>woodWOPfile, '_RX=%s' %header['DX']
    print >>woodWOPfile, '_RY=%s' %header['DY']
    
def WriteFixedVariables():
    if Debug==1 or Debug==2: print'WriteFixedVariables():'
    print >>woodWOPfile, ''
    print >>woodWOPfile, '[001'
    print >>woodWOPfile, 'DX="%s"' %header['DX']
    print >>woodWOPfile, 'KM="Lengte"'
    print >>woodWOPfile, 'DY="%s"' %header['DY']
    print >>woodWOPfile, 'KM="Breedte"'
    print >>woodWOPfile, 'DZ="%s"' %header['DZ']
    print >>woodWOPfile, 'KM="Dikte"'
    print >>woodWOPfile, 'X2W_CHK="1"'
    print >>woodWOPfile, 'KM="0=OK / 1=!!!ONGETEST!!! (%s Xil2WOP)"' %ReleaseCode
    
def WriteImportedVariables():
    if Debug==1 or Debug==2: print "WriteImportedVariables():",lpar
    print >>woodWOPfile, ''
    print >>woodWOPfile, '[001'
    print >>woodWOPfile, '%s="%s"' %(lpar["Name"], lpar["Value"])
    print >>woodWOPfile, 'KM="%s"' %lpar["Comment"]

def WriteOP():
    if Debug==1 or Debug==2: print "WriteOP():",X2W_OPT
    print >>woodWOPfile, ''
    print >>woodWOPfile, '[001'
    print >>woodWOPfile, 'X2W_OPT="%s"' %X2W_OPT
    print >>woodWOPfile, 'KM="%s=STD OPTIMALISATIE / %s=NC_STOP OPTIMALISATIE"' %(X2W_OPT_NORMAAL, X2W_OPT_NCSTOP)
    
def WriteContourVariables():
    if Debug==1 or Debug==2: print "WriteContourVariables():",ContourInfoList
    Contour_Nummer=0 #opgelet, niet de GLOBALE
    for key in ContourInfoList:
        Contour_Nummer=Contour_Nummer+1
        print >>woodWOPfile, '[001'
        print >>woodWOPfile, 'CONT_%s="00000000"' %str(Contour_Nummer)
        print >>woodWOPfile, 'KM="%s"' %str(key)
    
def WriteWorkpiece():
    if Debug==1 or Debug==2: print "WriteWorkpiece():"
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<100 \WerkStck\\'
    print >>woodWOPfile, 'LA="DX"'
    print >>woodWOPfile, 'BR="DY"'
    print >>woodWOPfile, 'DI="DZ"'
    print >>woodWOPfile, 'FNX="0"'
    print >>woodWOPfile, 'FNY="0"'
    print >>woodWOPfile, 'AX="0"'
    print >>woodWOPfile, 'AY="0"'
    print >>woodWOPfile, '' #X2W_CHK ingebouwde stop.
    print >>woodWOPfile, '<117 \NCStop\\'
    print >>woodWOPfile, 'KM="X2W: X2W_CHK -controleer programma- ==1!!!"'
    print >>woodWOPfile, 'KM=""'
    print >>woodWOPfile, 'KM="Nog niet gecontroleerd!!!"'
    print >>woodWOPfile, 'KM=""'
    print >>woodWOPfile, 'KM="Prog nakijken, dan 1 stuk bewerken."'
    print >>woodWOPfile, 'KM=""'
    print >>woodWOPfile, 'KM="Stuk nakijken."'
    print >>woodWOPfile, 'KM=""'
    print >>woodWOPfile, 'KM="Indien OK parameter X2W_CHK op -0- zetten!"'
    print >>woodWOPfile, 'KM=""'
    print >>woodWOPfile, 'KM="Daarna lijn NC_STOP -X2W: X2W_CHK controleer programma.- verwijderen!"'
    print >>woodWOPfile, 'VL="0"'
    print >>woodWOPfile, 'XA="0"'
    print >>woodWOPfile, 'F_="30"'
    print >>woodWOPfile, 'YA="0"'
    print >>woodWOPfile, '_Y="0"'
    print >>woodWOPfile, '_X="1"'
    print >>woodWOPfile, 'XV="0"'
    print >>woodWOPfile, 'YV="0"'
    print >>woodWOPfile, 'WT="0.0"'
    print >>woodWOPfile, 'ZR="1"'
    print >>woodWOPfile, 'KAT="NC-Stop"'
    print >>woodWOPfile, 'MNM="X2W: X2W_CHK controleer programma."'
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'KO="00"'
    print >>woodWOPfile, '??="X2W_CHK"'
   
def SwitchX(SwitchXinDict):
    if Debug==2: print "SwitchX():",SwitchXinDict
    SwitchXflag=0 #check if switch has been made to avoid double switching
    SwitchXin=str(SwitchXinDict)
    if SwitchXorY=="1" or SwitchXorY=="3": #SwitchX
       if SwitchXin[:3]=="DX-" and SwitchXflag==0: SwitchXout=SwitchXin[3:]; SwitchXflag=1
       if SwitchXin[:3]=="DX+" and SwitchXflag==0: SwitchXout="-"+SwitchXin[3:]; SwitchXflag=1
       if SwitchXin[:1]=="-" and SwitchXflag==0: SwitchXout="DX+"+SwitchXin[1:]; SwitchXflag=1
       if SwitchXflag==0: SwitchXout="DX-"+SwitchXin
    else:
        SwitchXout=SwitchXin
    return SwitchXout
    
def SwitchY(SwitchYinDict):
    if Debug==2: print "SwitchY():",SwitchYinDict
    SwitchYflag=0 #check if switch has been made to avoid double switching
    SwitchYin=str(SwitchYinDict)
    if SwitchXorY=="2" or SwitchXorY=="3": #SwitchY
       if SwitchYin[:3]=="DY-" and SwitchYflag==0: SwitchYout=SwitchYin[3:]; SwitchYflag=1
       if SwitchYin[:3]=="DY+" and SwitchYflag==0: SwitchYout="-"+SwitchYin[3:]; SwitchYflag=1
       if SwitchYin[:1]=="-" and SwitchYflag==0: SwitchYout="DY+"+SwitchYin[1:]; SwitchYflag=1
       if SwitchYflag==0: SwitchYout="DY-"+SwitchYin
    else:
        SwitchYout=SwitchYin
    return SwitchYout

def SX(): #alpha
    if Debug==2: print "SX():",sx
    global SwitchXorY
    SwitchXorY_prev=SwitchXorY
    sx_switched=0
    if SwitchXorY=="0" and sx_switched==0: SwitchXorY="1"; sx_switched=1
    if SwitchXorY=="1" and sx_switched==0: SwitchXorY="0"; sx_switched=1
    if SwitchXorY=="2" and sx_switched==0: SwitchXorY="3"; sx_switched=1
    if SwitchXorY=="3" and sx_switched==0: SwitchXorY="2"; sx_switched=1
    if Debug==1 or Debug==2: print "SX=%s: reversed SwitchXorY from %s to %s" %(sx[""],SwitchXorY_prev,SwitchXorY)

def SY(): #alpha
    if Debug==2: print "SY():",sy
    global SwitchXorY
    SwitchXorY_prev=SwitchXorY
    sy_switched=0
    if SwitchXorY=="0" and sy_switched==0: SwitchXorY="2"; sy_switched=1
    if SwitchXorY=="1" and sy_switched==0: SwitchXorY="3"; sy_switched=1
    if SwitchXorY=="2" and sy_switched==0: SwitchXorY="0"; sy_switched=1
    if SwitchXorY=="3" and sy_switched==0: SwitchXorY="1"; sy_switched=1
    if Debug==1 or Debug==2: print "SY=%s: reversed SwitchXorY from %s to %s" %(sy[""],SwitchXorY_prev,SwitchXorY)
 
def XBOVerticaal():
    if Debug==1 or Debug==2: print "XBOVerticaal():",xbo
    xbo_AB="0" #tussenafstand meervoudige boringen
    xbo_WI="0" #hoek meervoudige boringen
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<102 \BohrVert\\'
    try:
        test=xbo_prev["X"]
    except KeyError:
        xbo_prev["X"]="0"
    print >>woodWOPfile, 'XA="%s"' %SwitchX(xbo.setdefault('X', xbo_prev['X']))
    print >>woodWOPfile, 'YA="%s"' %SwitchY(xbo.setdefault('Y', xbo_prev['Y']))
    try:
        XBO_TI=xbo.setdefault('Z', xbo_prev['Z'])
    except KeyError:
        xbo_prev['Z']='0'
        XBO_TI=xbo.setdefault('Z', xbo_prev['Z'])
    if Debug==2: print"H_DZ=%s / XBO_TI=%s" %(H_DZ, XBO_TI)
    if float(XBO_TI)>float(H_DZ): #bepaal boormethode volgens diepte (gewoon of doorgaand)
        XBO_BM="LSL"
        if Debug==2: print"Boormodus LSL (doorgaand)."
    else:
        XBO_BM="LS"
        if Debug==2: print"Boormodus LS (normaal)."
    print >>woodWOPfile, 'BM="%s"' %XBO_BM
    print >>woodWOPfile, 'TI="%s"' %XBO_TI
    XBO_DU=float(xbo.setdefault('D', xbo_prev['D']))
    if XBO_DU==4 and XBO_BM=="LS": XBO_DU=5 #converteren niet-beschikbare naar wel-beschikbare diameters
    if XBO_DU==5 and XBO_BM=="LSL": XBO_DU=4 #converteren niet-beschikbare naar wel-beschikbare diameters
    if Debug==2: print'XBO_DU', XBO_DU
    print >>woodWOPfile, 'DU="%s"' %XBO_DU
    XBOMNM="D=%s / Z=%s." %(XBO_DU, xbo.setdefault('Z', xbo_prev['Z']))
    try:
        if xbo['R'].endswith("#"): #strip last character # if present
            xbo["R"] = xbo["R"][:-1]
    except KeyError:
        if xbo_prev['R'].endswith("#"): #strip last character # if present
            xbo_prev["R"] = xbo_prev["R"][:-1]
    if xbo.setdefault('R', xbo_prev['R'])=="0": xbo['R']="1" #woodWOP aanvaardt geen 0 herhalingen
    print >>woodWOPfile, 'AN="%s"' %xbo.setdefault('R', xbo_prev['R'])
    print >>woodWOPfile, 'MI="0"'
    print >>woodWOPfile, 'S_="2"'
    if xbo['R']<>"1":
        if Debug==2: print "MULTIPLE"
        try:
            test=xbo['x']
        except KeyError:
            xbo['x']=xbo_prev['x']
        try:
            test=xbo['y']
        except KeyError:
            xbo['y']=xbo_prev['y']
        if xbo['x']<>"0":
            xbo_AB=xbo['x']
            if SwitchXorY=="1" or SwitchXorY=="3": #Keer herhalingsafstand X om bij switchen over X.
                if xbo_AB.startswith("-"): #- naar +
                    if Debug==2: print "xbo_AB was NEGATIVE",xbo_AB
                    xbo_AB=(xbo_AB)[1:]
                    if Debug==2: print "new xbo_AB",xbo_AB
                else: #+ naar -
                    if Debug==2: print "xbo_AB was POSITIVE",xbo_AB
                    xbo_AB="-"+str(xbo_AB)
                    if Debug==2: print "new xbo_AB",xbo_AB
            xbo_WI="0"
        elif xbo['y']<>"0":
            xbo_AB=xbo['y']
            if SwitchXorY=="2" or SwitchXorY=="3": #Keer herhalingsafstand Y om bij switchen over Y.
                if xbo_AB.startswith("-"): #- naar +
                    if Debug==2: print "xbo_AB was NEGATIVE",xbo_AB
                    xbo_AB=(xbo_AB)[1:]
                    if Debug==2: print "new xbo_AB",xbo_AB
                else: #+ naar -
                    if Debug==2: print "xbo_AB was POSITIVE",xbo_AB
                    xbo_AB="-"+str(xbo_AB)
                    if Debug==2: print "new xbo_AB",xbo_AB
            xbo_WI="90"
    print >>woodWOPfile, 'AB="%s"' %xbo_AB
    print >>woodWOPfile, 'WI="%s"' %xbo_WI
    print >>woodWOPfile, 'ZT="0"'
    print >>woodWOPfile, 'RM="0"'
    print >>woodWOPfile, 'VW="0"'
    print >>woodWOPfile, 'HP="0"'
    print >>woodWOPfile, 'SP="0"'
    print >>woodWOPfile, 'YVE="0"'
    print >>woodWOPfile, 'WW="60,61,62"'
    print >>woodWOPfile, 'ASG="2"'
    print >>woodWOPfile, 'KAT="Bohren vertikal"'
    print >>woodWOPfile, 'MNM="X2W: Boring %s"' %XBOMNM
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'MX="0"'
    print >>woodWOPfile, 'MY="0"'
    print >>woodWOPfile, 'MZ="0"'
    print >>woodWOPfile, 'MXF="1"'
    print >>woodWOPfile, 'MYF="1"'
    print >>woodWOPfile, 'MZF="1"'
    print >>woodWOPfile, 'SYA="0"'
    print >>woodWOPfile, 'SYV="0"'
    print >>woodWOPfile, 'KO="00"'
    XBO_IF=xbo.setdefault('IF', "1") #waarde IF in XBO *OF* 1
    if Debug==2: print "IF statement:",XBO_IF
    print >>woodWOPfile, '??= "%s"' %XBO_IF

def XB():
    if Debug==1 or Debug==2: print "XB():",xbo
    try:
        xbo_fulltoolname="T"+xbo["T"]
    except KeyError:
        xbo["T"]=xbo_prev["T"]
        xbo_fulltoolname="T"+xbo["T"]
    if Debug==2: print"xbo_fulltoolname:",xbo_fulltoolname
    xbo["D"]=ToolDiamTable[xbo_fulltoolname] #zet diameter volgens boortabel
    
def XlinesB():
    if Debug==1 or Debug==2: print "XlinesB():",xlinesb
    if xlinesb['Q'].endswith("#"): #strip last character # if present
        xlinesb["Q"] = xlinesb["Q"][:-1]
    XlinesB_AN = (int(math.floor(((float(header["DX"])-float(xlinesb["X"]))-float(xlinesb["I"]))/float(xlinesb["Q"]))))+1
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<102 \BohrVert\\' #voorste rijboring xlinesb
    print >>woodWOPfile, 'XA="%s"' %SwitchX(xlinesb["X"])
    print >>woodWOPfile, 'YA="%s"' %SwitchY(xlinesb["Y"])
    print >>woodWOPfile, 'BM="LS"'
    print >>woodWOPfile, 'TI="%s"' %xlinesb["Z"]
    print >>woodWOPfile, 'DU="%s"' %xlinesb["D"]
    XBOMNM="Rijboring D=%s / Z=%s." %(xlinesb["D"], xlinesb["Z"])
    if xbo.setdefault('R', xbo_prev['R'])=="0": xbo['R']="1" #woodWOP aanvaardt geen 0 herhalingen
    print >>woodWOPfile, 'AN="%s"' %XlinesB_AN
    print >>woodWOPfile, 'MI="0"'
    print >>woodWOPfile, 'S_="2"'
    print >>woodWOPfile, 'AB="-%s"' %xlinesb["Q"]
    print >>woodWOPfile, 'WI="0"' #voorlopig enkel xlinesb in x-richting
    print >>woodWOPfile, 'ZT="0"'
    print >>woodWOPfile, 'RM="0"'
    print >>woodWOPfile, 'VW="0"'
    print >>woodWOPfile, 'HP="0"'
    print >>woodWOPfile, 'SP="0"'
    print >>woodWOPfile, 'YVE="0"'
    print >>woodWOPfile, 'WW="60,61,62"'
    print >>woodWOPfile, 'ASG="2"'
    print >>woodWOPfile, 'KAT="Bohren vertikal"'
    print >>woodWOPfile, 'MNM="X2W: %s"' %XBOMNM
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'MX="0"'
    print >>woodWOPfile, 'MY="0"'
    print >>woodWOPfile, 'MZ="0"'
    print >>woodWOPfile, 'MXF="1"'
    print >>woodWOPfile, 'MYF="1"'
    print >>woodWOPfile, 'MZF="1"'
    print >>woodWOPfile, 'SYA="0"'
    print >>woodWOPfile, 'SYV="0"'
    print >>woodWOPfile, 'KO="00"'
    XLINESB_IF=xlinesb.setdefault('IF', "1") #waarde IF in XLINESB *OF* 1
    if Debug==2: print "IF statement:",XLINESB_IF
    print >>woodWOPfile, '??= "%s"' %XLINESB_IF
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<102 \BohrVert\\' #achterste rijboring xlinesb
    print >>woodWOPfile, 'XA="%s"' %SwitchX(xlinesb["X"])
    print >>woodWOPfile, 'YA="DY-%s"' %SwitchY(xlinesb["J"])
    print >>woodWOPfile, 'BM="LS"'
    print >>woodWOPfile, 'TI="%s"' %xlinesb["Z"]
    print >>woodWOPfile, 'DU="%s"' %xlinesb["D"]
    XBOMNM="Rijboring D=%s / Z=%s." %(xlinesb["D"], xlinesb["Z"])
    if xbo.setdefault('R', xbo_prev['R'])=="0": xbo['R']="1" #woodWOP aanvaardt geen 0 herhalingen
    print >>woodWOPfile, 'AN="%s"' %XlinesB_AN
    print >>woodWOPfile, 'MI="0"'
    print >>woodWOPfile, 'S_="2"'
    print >>woodWOPfile, 'AB="-%s"' %xlinesb["Q"]
    print >>woodWOPfile, 'WI="0"' #voorlopig enkel xlinesb in x-richting
    print >>woodWOPfile, 'ZT="0"'
    print >>woodWOPfile, 'RM="0"'
    print >>woodWOPfile, 'VW="0"'
    print >>woodWOPfile, 'HP="0"'
    print >>woodWOPfile, 'SP="0"'
    print >>woodWOPfile, 'YVE="0"'
    print >>woodWOPfile, 'WW="60,61,62"'
    print >>woodWOPfile, 'ASG="2"'
    print >>woodWOPfile, 'KAT="Bohren vertikal"'
    print >>woodWOPfile, 'MNM="X2W: %s"' %XBOMNM
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'MX="0"'
    print >>woodWOPfile, 'MY="0"'
    print >>woodWOPfile, 'MZ="0"'
    print >>woodWOPfile, 'MXF="1"'
    print >>woodWOPfile, 'MYF="1"'
    print >>woodWOPfile, 'MZF="1"'
    print >>woodWOPfile, 'SYA="0"'
    print >>woodWOPfile, 'SYV="0"'
    print >>woodWOPfile, 'KO="00"'
    print >>woodWOPfile, '??= "%s"' %XLINESB_IF

def XG0():
    if Debug==1 or Debug==2: print "XG0():",xg0
    try: #strip last character '#' if present
        if xg0['S'].endswith("#"):
            xg0["S"] = xg0["S"][:-1]
    except KeyError:
        if Debug==2: print"KeyError: 'S'"        
    if xg0.setdefault('T', xg0_prev['T'])=="184": #mogelijke detectie ruggroef
        if Debug==1 or Debug==2: print "XG0(): RUGGROEF!"
        global ruggroefT184
        global ruggroef_StartX
        global ruggroef_StartY
        global ruggroef_Diepte
        global ruggroef_Comp
        global ruggroef_Offset
        ruggroefT184 = 1
        ruggroef_StartX=xg0["X"]
        ruggroef_StartY=xg0["Y"]
        ruggroef_Diepte=xg0["Z"]
        ruggroef_Comp=xg0.setdefault("C", current_C_S[""]) #NameError???
        ruggroef_Offset=current_C_S.setdefault("S", 0) #hopelijk hier geen problemen ivm vergeten offsets???
    else: #startpunt G0/XG0->kp freescontour
        global ContourInfoList
        global Contour_Nummer
        global Contour_Positie
        Contour_Nummer=Contour_Nummer+1 #volgend contournummer
        Contour_Positie=0 #positie contour resetten    
        if Debug==1 or Debug==2: print "XG0(): FREESCONTOUR! #",Contour_Nummer,"pos",Contour_Positie,"(startpunt)"
        if Debug==2: print "g1x12p",g1xl2p
        print >>woodWOPfile, ''
        print >>woodWOPfile, ']%s' %Contour_Nummer
        print >>woodWOPfile, '$E%s' %Contour_Positie
        print >>woodWOPfile, 'KP'
        Contour.PreviousX=Contour.CurrentX
        Contour.PreviousY=Contour.CurrentY
        try:
            Contour.CurrentX=xg0['X']
        except KeyError:
            pass
        try:
            Contour.CurrentY=xg0['Y']
        except KeyError:
            pass
        print >>woodWOPfile, 'X=%s' %SwitchX(Contour.CurrentX)
        print >>woodWOPfile, 'Y=%s' %SwitchY(Contour.CurrentY)
        print >>woodWOPfile, 'Z=0.0'
        print >>woodWOPfile, 'KO=00'
        print >>woodWOPfile, '.X=0.000000'
        print >>woodWOPfile, '.Y=0.000000'
        print >>woodWOPfile, '.Z=0.000000'
        print >>woodWOPfile, '.KO=00'
        ContourInfoList.append(Contour.CurrentInfo) #toevoegen aan infovariabelen

def G1XL2P():
    if Debug==1 or Debug==2: print "G1XL2P():",g1xl2p
    global Contour_Nummer
    global Contour_Positie
    Contour_Positie=Contour_Positie+1 #volgend positienummer
    if Debug==1 or Debug==2: print "G1XL2P(): FREESCONTOUR! #",Contour_Nummer,"pos",Contour_Positie
    print >>woodWOPfile, ''
    print >>woodWOPfile, '$E%s' %Contour_Positie
    print >>woodWOPfile, 'KL'
    if Debug==2: print "g1x12p",g1xl2p; print "g1x12p_prev",g1xl2p_prev
    Contour.PreviousX=Contour.CurrentX #nieuw systeem met classes
    Contour.PreviousY=Contour.CurrentY
    try:
        Contour.CurrentX=g1xl2p['X']
    except KeyError:
        pass
    try:
        Contour.CurrentY=g1xl2p['Y']
    except KeyError:
        pass
    print >>woodWOPfile, 'X=%s' %SwitchX(Contour.CurrentX)
    print >>woodWOPfile, 'Y=%s' %SwitchY(Contour.CurrentY)
    print >>woodWOPfile, '.X=0.000000'
    print >>woodWOPfile, '.Y=0.000000'
    print >>woodWOPfile, '.Z=0.000000'
    print >>woodWOPfile, '.WI=0.000000'
    print >>woodWOPfile, '.WZ=0.000000'

def XEA():
    if Debug==1 or Debug==2: print "XEA():",xea
    print "Deze functie is nog niet volledig ondersteund."
    
def XPOCKET():
    if Debug==1 or Debug==2: print "XPOCKET():",xpocket
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<112 \Tasche\\'
    print >>woodWOPfile, 'XA="%s"' %SwitchX(xpocket.setdefault('I', xpocket_prev['I']))
    print >>woodWOPfile, 'YA="%s"' %SwitchY(xpocket.setdefault('J', xpocket_prev['J']))
    print >>woodWOPfile, 'LA="%s"' %xpocket.setdefault('X', xpocket_prev['X'])
    print >>woodWOPfile, 'BR="%s"' %xpocket.setdefault('Y', xpocket_prev['Y'])
    print >>woodWOPfile, 'RD="%s"' %xpocket.setdefault('r', xpocket_prev['r'])
    print >>woodWOPfile, 'WI="%s"' %xpocket.setdefault('A', xpocket_prev['A'])
    print >>woodWOPfile, 'TI="%s"' %xpocket.setdefault('Z', xpocket_prev['Z'])
    print >>woodWOPfile, 'ZT="0"'
    print >>woodWOPfile, 'XY="80"'
    print >>woodWOPfile, 'T_="%s"' %xpocket.setdefault('T', xpocket_prev['T'])
    print >>woodWOPfile, 'F_="%s"' %xpocket.setdefault('V', xpocket_prev['V'])
    print >>woodWOPfile, 'DS="1"'
    print >>woodWOPfile, 'OSZI="0"'
    print >>woodWOPfile, 'BL="0"'
    print >>woodWOPfile, 'OSZVS="0"'
    print >>woodWOPfile, 'HP="0"'
    print >>woodWOPfile, 'SP="0"'
    print >>woodWOPfile, 'YVE="0"'
    print >>woodWOPfile, 'WW="1,2,3"'
    print >>woodWOPfile, 'ASG="2"'
    print >>woodWOPfile, 'KG="0"'
    print >>woodWOPfile, 'RP="STANDARD"'
    print >>woodWOPfile, 'KAT="Tasche"'
    print >>woodWOPfile, 'MNM="X2W: Pocket X=%s / Y=%s / Z=%s / T=%s."' %(xpocket["X"], xpocket["Y"], xpocket["Z"], xpocket["T"])
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'MX="0"'
    print >>woodWOPfile, 'MY="0"'
    print >>woodWOPfile, 'MZ="0"'
    print >>woodWOPfile, 'MXF="1"'
    print >>woodWOPfile, 'MYF="1"'
    print >>woodWOPfile, 'MZF="1"'
    print >>woodWOPfile, 'SYA="0"'
    print >>woodWOPfile, 'SYV="0"'
    print >>woodWOPfile, 'KO="00"'
    XPOCKET_IF=xpocket.setdefault('IF', "1") #waarde IF in XPOCKET *OF* 1
    if Debug==2: print "IF statement:",XPOCKET_IF
    print >>woodWOPfile, '??= "%s"' %XPOCKET_IF
   
def RUGGROEFT184():
    if Debug==1 or Debug==2: print "RUGGROEFT184():",g1xl2p
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<109 \Nuten\\'
    print >>woodWOPfile, 'XA="%s"' %SwitchX(ruggroef_StartX)
    print >>woodWOPfile, 'YA="%s"' %SwitchY(ruggroef_StartY)
    print >>woodWOPfile, 'WI="0"'
    print >>woodWOPfile, 'XE="%s"' %SwitchX(g1xl2p["X"])
    print >>woodWOPfile, 'YE="%s"' %SwitchY(g1xl2p.setdefault("Y", ruggroef_StartY))
    print >>woodWOPfile, 'NB="%s"' %ruggroef_Breedte
    if ruggroef_Comp.startswith("0") or ruggroef_Comp.startswith("3"): #compensaties, nog verbeteren ivm C03,13,23
        ruggroef_RK="NOWRK"
    elif ruggroef_Comp.startswith("1"):
        ruggroef_RK="WRKR"
    elif ruggroef_Comp.startswith("2"):
        ruggroef_RK="WRKL"
    print >>woodWOPfile, 'RK="%s"' %ruggroef_RK
    if ruggroef_Comp.endswith("3"): #compensatie start en stop
        ruggroef_EM="MOD1" #=C0/1/2+3
    else:
        ruggroef_EM="MOD0" #=C0/1/2
    print >>woodWOPfile, 'EM="%s"' %ruggroef_EM
    print >>woodWOPfile, 'AD="0"'
    print >>woodWOPfile, 'TI="%s"' %ruggroef_Diepte
    print >>woodWOPfile, 'TV="0"'
    print >>woodWOPfile, 'MV="GL"'
    print >>woodWOPfile, 'XY="90"'
    print >>woodWOPfile, 'MN="GL"'
    print >>woodWOPfile, 'BL="0"'
    print >>woodWOPfile, 'OP="0"'
    print >>woodWOPfile, 'AN="0"'
    print >>woodWOPfile, 'T_="40"'
    print >>woodWOPfile, 'MT="0"'
    print >>woodWOPfile, 'HU="0"'
    print >>woodWOPfile, 'ZU="3"'
    print >>woodWOPfile, 'HP="0"'
    print >>woodWOPfile, 'SP="0"'
    print >>woodWOPfile, 'YVE="0"'
    print >>woodWOPfile, 'WW="40,41,42,45,141,142"'
    print >>woodWOPfile, 'ASG="2"'
    print >>woodWOPfile, 'KAT="Nuten"'
    ruggroef_MNM="X2W: Ruggroef D=%s / Z=%s." %(ruggroef_Breedte, ruggroef_Diepte)
    print >>woodWOPfile, 'MNM="%s"' %ruggroef_MNM
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'MX="0"'
    print >>woodWOPfile, 'MY="0"'
    print >>woodWOPfile, 'MZ="0"'
    print >>woodWOPfile, 'MXF="1"'
    print >>woodWOPfile, 'MYF="1"'
    print >>woodWOPfile, 'MZF="1"'
    print >>woodWOPfile, 'SYA="0"'
    print >>woodWOPfile, 'SYV="0"'
    print >>woodWOPfile, 'KO="00"'
    global ruggroefT184; ruggroefT184=0 #reset flag

def SXS(): #Weergave aanroep Xilog subprogramma via een commentaarlijn.
    if Debug==1 or Debug==2: print "SXS():",sxs
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<101 \Kommentar\\'
    for key in sxs:
        print >>woodWOPfile, 'KM="%s=%s"' %(str(key), str(sxs[key]))
    print >>woodWOPfile, 'KAT="Comment"'
    print >>woodWOPfile, 'MNM="X2W: Xilog subprog (S/XS) %s."' %sxs['N'] 
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, '??="0"'

        
def SETSTANDBY():
    if Debug==1 or Debug==2: print "SETSTANDBY():"
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<117 \NCStop\\'
    print >>woodWOPfile, 'KM="X2W: Stuk draaien over Y-as!"'
    print >>woodWOPfile, 'VL="1"'
    print >>woodWOPfile, 'XA="0"'
    print >>woodWOPfile, 'F_="30"'
    print >>woodWOPfile, 'YA="0"'
    print >>woodWOPfile, '_Y="0"'
    print >>woodWOPfile, '_X="1"'
    print >>woodWOPfile, 'XV="0"'
    print >>woodWOPfile, 'YV="0"'
    print >>woodWOPfile, 'WT="0.0"'
    print >>woodWOPfile, 'ZR="1"'
    print >>woodWOPfile, 'KAT="NC-Stop"'
    print >>woodWOPfile, 'MNM="X2W: Stuk draaien over Y-as!"'
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'KO="00"'

def XBOHorizontaal():
    if Debug==1 or Debug==2: print "XBOHorizontaal():",xbo
    xbo_AB="0" #tussenafstand meervoudige boringen
    xbo_WI="0" #hoek meervoudige boringen
    xbo_H_ZA="%s" %xbo.setdefault('X', xbo_prev['X']) #hoogte Z center boring (positie indien 0 komt overeen met Xilog dus 0=op rand onderkant plaat)
    xbo_H_XA="0"
    xbo_H_BM="XP"
    XBO_DU=float(xbo.setdefault('D', xbo_prev['D']))
    if XBO_DU==4: XBO_DU=5 #converteren niet-beschikbare naar wel-beschikbare diameters
    try:
        xbo_H_TI=xbo.setdefault('Z', xbo_prev['Z'])
    except KeyError:
        xbo_prev['Z']='0'
        xbo_H_TI=xbo.setdefault('Z', xbo_prev['Z'])
    if XBO_DU==10.0: #detecteer deuvel 10mm, blokkeer diepte op BorHor_Z (globale variabele)
        xbo_H_TI="BorHor_Z" #Globale variabele WoodWOP: Standaard boordiepte horizontale boring voor deuvels. (ook voor X2W)
    if SwitchXorY=="2": #boorparameters bij Y-spiegel
        if Field.Current=="3": #Xilog veld.
            xbo_H_XA="0"
            xbo_H_BM="XP"
        if Field.Current=="2": #Xilog veld.
            xbo_H_XA="DX"
            xbo_H_BM="XM"
    elif SwitchXorY=="1": #boorparameters bij X-spiegel (standaard)
        if Field.Current=="2": #Xilog veld.
            xbo_H_XA="0"
            xbo_H_BM="XP"
        if Field.Current=="3": #Xilog veld.
            xbo_H_XA="DX"
            xbo_H_BM="XM"
    elif SwitchXorY=="3": #boorparameters bij X&Y-spiegel
        if Field.Current=="2": #Xilog veld.
            xbo_H_XA="0"
            xbo_H_BM="XP"
        if Field.Current=="3": #Xilog veld.
            xbo_H_XA="DX"
            xbo_H_BM="XM"
    print >>woodWOPfile, ''
    print >>woodWOPfile, '<103 \BohrHoriz\\'
    try:
        test=xbo_prev["X"]
    except KeyError:
        xbo_prev["X"]="-10"
    print >>woodWOPfile, 'XA="%s"' %xbo_H_XA #x-afstand '0' (begin gat)
    print >>woodWOPfile, 'YA="%s"' %SwitchY(xbo.setdefault('Y', xbo_prev['Y']))
    print >>woodWOPfile, 'BM="%s"' %xbo_H_BM #boormodus (richting)
    print >>woodWOPfile, 'TI="%s"' %xbo_H_TI
    print >>woodWOPfile, 'DU="%s"' %XBO_DU
    XBOMNM="D=%s / Z=%s." %(XBO_DU, xbo_H_TI)
    try:
        if xbo['R'].endswith("#"): #strip last character # if present
            xbo["R"] = xbo["R"][:-1]
    except KeyError:
        if xbo_prev['R'].endswith("#"): #strip last character # if present
            xbo_prev["R"] = xbo_prev["R"][:-1]
    if xbo.setdefault('R', xbo_prev['R'])=="0": xbo['R']="1" #woodWOP aanvaardt geen 0 herhalingen
    print >>woodWOPfile, 'AN="%s"' %xbo.setdefault('R', xbo_prev['R'])
    print >>woodWOPfile, 'MI="0"'
    print >>woodWOPfile, 'S_="2"'
    if xbo['R']<>"1":
        if Debug==2: print "MULTIPLE"
        try:
            test=xbo['x']
        except KeyError:
            xbo['x']=xbo_prev['x']
        try:
            test=xbo['y']
        except KeyError:
            xbo['y']=xbo_prev['y']
        if xbo['x']<>"0":
            xbo_AB=xbo['x']
            xbo_WI="0"
        elif xbo['y']<>"0":
            xbo_AB=xbo['y']
            xbo_WI="90"
    print >>woodWOPfile, 'ZA="%s"' %xbo_H_ZA
    print >>woodWOPfile, 'AB="%s"' %xbo_AB
    print >>woodWOPfile, 'WI="%s"' %xbo_WI
    print >>woodWOPfile, 'ZT="0"'
    print >>woodWOPfile, 'RM="0"'
    print >>woodWOPfile, 'VW="0"'
    print >>woodWOPfile, 'HP="0"'
    print >>woodWOPfile, 'SP="0"'
    print >>woodWOPfile, 'YVE="0"'
    print >>woodWOPfile, 'WW="60,61,62"'
    print >>woodWOPfile, 'ASG="2"'
    print >>woodWOPfile, 'KAT="Horizontalbohren"'
    print >>woodWOPfile, 'MNM="X2W: Boring %s"' %XBOMNM
    print >>woodWOPfile, 'ORI=""'
    print >>woodWOPfile, 'MX="0"'
    print >>woodWOPfile, 'MY="0"'
    print >>woodWOPfile, 'MZ="0"'
    print >>woodWOPfile, 'MXF="1"'
    print >>woodWOPfile, 'MYF="1"'
    print >>woodWOPfile, 'MZF="1"'
    print >>woodWOPfile, 'SYA="0"'
    print >>woodWOPfile, 'SYV="0"'
    print >>woodWOPfile, 'KO="00"'
    print >>woodWOPfile, 'ANA="15"'
    print >>woodWOPfile, 'F_="STANDARD"' #feedrate
    XBO_IF=xbo.setdefault('IF', "1") #waarde IF in XBO *OF* 1
    if Debug==2: print "IF statement:",XBO_IF
    print >>woodWOPfile, '??= "%s"' %XBO_IF

def G2G3(): #Voorlopig simpele implementatie, werkt nog niet goed met i,j. Radius 'r' al getest met Castle!
    if Debug==1 or Debug==2: print "G2G3():",g2g3 
    global Contour_Nummer
    global Contour_Positie
    Contour_Positie=Contour_Positie+1 #volgend positienummer
    if Debug==1 or Debug==2: print "G2G3(): FREESCONTOUR! #",Contour_Nummer,"pos",Contour_Positie
    print >>woodWOPfile, ''
    print >>woodWOPfile, '$E%s' %Contour_Positie
    print >>woodWOPfile, 'KA'
    if Debug==2: print "g2g3",g2g3; print "g2g3_prev",g2g3_prev
    Contour.PreviousX=Contour.CurrentX
    Contour.PreviousY=Contour.CurrentY
    try:
        Contour.CurrentX=g2g3['X']
    except KeyError:
        pass
    try:
        Contour.CurrentY=g2g3['Y']
    except KeyError:
        pass
    print >>woodWOPfile, 'X=%s' %SwitchX(Contour.CurrentX)
    print >>woodWOPfile, 'Y=%s' %SwitchY(Contour.CurrentY)
    if command=="G2" and SwitchXorY=="0": g2g3_DS=1 #bepaal type boog cw, ccw, ...
    if command=="G2" and SwitchXorY=="1": g2g3_DS=0
    if command=="G2" and SwitchXorY=="2": g2g3_DS=1
    if command=="G2" and SwitchXorY=="3": g2g3_DS=1
    if command=="G3" and SwitchXorY=="0": g2g3_DS=0
    if command=="G3" and SwitchXorY=="1": g2g3_DS=1
    if command=="G3" and SwitchXorY=="2": g2g3_DS=0
    if command=="G3" and SwitchXorY=="3": g2g3_DS=0
    print >>woodWOPfile, 'DS=%s' %g2g3_DS
    try: #boog met radius 'r'
        print >>woodWOPfile, 'R=%s' %g2g3['r']
        g2g3_rji_ok=1
    except KeyError:
        pass
    try: #boog met middelpunt 'I','J'
        print >>woodWOPfile, '.I=%s' %SwitchX(g2g3['I'])
        print >>woodWOPfile, '.J=%s' %SwitchY(g2g3['J'])
        g2g3_rji_ok=1
    except KeyError:
        pass
    if g2g3_rji_ok<>1: print"Error in G2G3(): geen radiusinfo r of I,J gevonden! Boog mogelijk onjuist."; errors=errors+1
def WriteFooter():
    if Debug==1 or Debug==2: print "WriteFooter():"
    print >>woodWOPfile, '!'
    woodWOPfile.close()
    f.close()

#MAIN
sys.excepthook = show_exception_and_exit #error handling
xxlfilelist = glob.glob('*.xxl') #maak lijst van files
currentfilename=xxlfilelist[0] #kies eerste file in lijst voor openen
print "\n" * 100 #clear Python Shell
print ">>> Xil2WOP - converter van Xilog3 naar WoodWOP -",ReleaseCode,"<<<"
print ""
print ">>> Bestandsnaam:",currentfilename,"<<<"
print ""
print ">>> Keuze Switchmodus, rekening mee houden dat we RECHTSE zijden nodig hebben!!!"
inputvalid=0 #keuze switch X/Y modus
while inputvalid==0:
    SwitchXorY = str(raw_input('>>> Switchmodus? (.bmp): 0=/ 1=X (std vr progs m. ASY=voorkant), 2=Y, 3=X&Y ?'))
    if SwitchXorY=="0" or SwitchXorY=="1" or SwitchXorY=="2" or SwitchXorY=="3": inputvalid=1
print ""; print ">>> Keuze OK! Druk <ENTER> voor conversie. <<<"; raw_input()
f = open(currentfilename) # open input file
woodWOPfile = open(currentfilename[:-4]+".mpr", 'w') # open output file
for raw_line in f:
    Xilog3_line=Xilog3_line+1
    if Debug==1 or Debug==2: print ">>> Xilog3_line: %s" %Xilog3_line
    line = raw_line.split()
    if not line:
        continue
    if Debug==2: print line

    if line[0] == 'H': #*****HEADER*****
        header = {}
        for entry in line[1:4]:
            name, value = entry.split('=')
            header[name] = str(value)
        H_DZ=header["DZ"]
        if Debug==1: print"H_DZ",H_DZ
        
    elif line[0] == 'C': #*****COMPENSATIE/OFFSET*****
        current_C_S = {}
        for entry in line[1:4]:
            try:
                name, value = entry.split('=')
                current_C_S[name] = str(value)
            except ValueError:
                if Debug==2: print "(Intercepted ValueError)"
                pass

    elif line[0] == 'SET': #*****SET(NC)*****
        if line[1] == 'STANDBY' and line[2] == '=1':
            command="SETSTANDBY"

    elif line[0] == 'L' or line[0] == 'PAR': # Variabele L of PAR
        command="LPAR"
        lpar = {} #clear next version
        lpar["Name"]=line[1]
        if line[2].startswith("="): #strip '=' if present
            line[2]=line[2][1:]
        lpar["Value"]=line[2]
        lpar["Comment"]=(re.sub('"''', '', raw_line)).rstrip('\n') #verwijder ', " met re.sub en <ENTER> met .rstrip

    elif line[0].startswith('F'): #Verandering Field F(=)1<>5
        Field.Previous=Field.Current
        Field.Current=line[0][-1:] #strip 'F'
        if str(Field.Current).startswith('='):
            Field.Current=Field.Current[-1:] #strip '='         
                            
    elif line[0] == 'XBO': #*****XBO*****
        command="XBO"
        xbo_prev = xbo #preserve previous version
        xbo = {} #clear next version
        for entry in line[1:12]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                xbo[name] = str(value)
            except ValueError:
                xbo[name] = value[1:-1] #stripping of the ""

    elif line[0] == 'SX': #*****SX*****
        command="SX"
        sx_prev = sx #preserve previous version
        sx = {} #clear next version
        for entry in line[1:3]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                sx[name] = str(value)
            except ValueError:
                sx[name] = value[1:-1] #stripping of the ""
        if Debug==2: print"Found SX: ",sx

    elif line[0] == 'SY': #*****SY*****
        command="SY"
        sy_prev = sy #preserve previous version
        sy = {} #clear next version
        for entry in line[1:3]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                sy[name] = str(value)
            except ValueError:
                sy[name] = value[1:-1] #stripping of the ""
        if Debug==2: print"Found SY: ",sy

    elif line[0] == 'XB' or line[0] == 'B': #*****XB(of B???)***** zelfde als XBO maar zoekt eerst tooldiameter op
        command="XB"
        xbo_prev = xbo #preserve previous version
        xbo = {} #clear next version
        for entry in line[1:11]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                xbo[name] = str(value)
            except ValueError:
                xbo[name] = value[1:-1] #stripping of the ""

    elif line[0] == 'XLINESB': #*****XLINESB*****
        command="XLINESB"
        xlinesb_prev = xlinesb #preserve previous version
        xlinesb = {} #clear next version
        for entry in line[1:11]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                xlinesb[name] = str(value)
            except ValueError:
                xlinesb[name] = value[1:-1] #stripping of the ""

    elif line[0] == 'G0' or line[0] == 'XG0': #start freesprofiel
        command="XG0"
        xg0_prev = xg0 #preserve previous version
        xg0 = {} #clear next version
        for entry in line[1:11]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                xg0[name] = str(value)
            except ValueError:
                xg0[name] = value[1:-1] #stripping of the ""
        Contour.CurrentInfo=(re.sub('"''', '', raw_line)).rstrip('\n') #verwijder ', " met re.sub en <ENTER> met .rstrip

    elif line[0] == 'G1' or line[0] == 'XL2P': #vervolg freesprofiel
        command="G1XL2P"
        g1xl2p_prev = g1xl2p #preserve previous version
        g1xl2p = {} #clear next version
        for entry in line[1:11]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                g1xl2p[name] = str(value)
            except ValueError:
                g1xl2p[name] = value[1:-1] #stripping of the ""
        if Debug==2: print "g1x12p",g1xl2p; print "g1x12p_prev",g1xl2p_prev

    elif line[0] == 'XEA': #Cirkel/ellips XEA
        command="XEA"
        xea_prev = xea #preserve previous version
        xea = {} #clear next version
        for entry in line[1:14]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                xea[name] = str(value)
            except ValueError:
                xea[name] = value[1:-1] #stripping of the ""
        if Debug==2: print "xea",xea; print "xea_prev",xea_prev

    elif line[0] == 'XPOCKET': #XPOCKET.
        command="XPOCKET"
        xpocket_prev = xpocket #preserve previous version
        xpocket = {} #clear next version
        for entry in line[1:15]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                xpocket[name] = str(value)
            except ValueError:
                xpocket[name] = value[1:-1] #stripping of the ""
        if Debug==2: print "xpocket",xpocket; print "xpocket_prev",xpocket_prev

    elif line[0] == 'G2' or line[0] == 'G3': #vervolg freesprofiel met G2 (G3 nog toevoegen)
        if line[0] == 'G2': command="G2"
        elif line[0] == 'G3': command="G3"
        g2g3_prev = g2g3 #preserve previous version
        g2g3 = {} #clear next version
        for entry in line[1:11]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                g2g3[name] = str(value)
            except ValueError:
                g2g3[name] = value[1:-1] #stripping of the ""
        if Debug==2: print "g2g3",g2g3; print "g2g3_prev",g2g3_prev 

    elif line[0]=='S' or line[0]=='XS': #Xilog subprogramma.
        command="SXS"
        sxs_prev = sxs #preserve previous version
        sxs = {} #clear next version
        for entry in line[1:10]:
            try:
                name, value = entry.split('=')
            except ValueError: #negeer commentaren voorlopig
                if Debug==2: print "(Intercepted ValueError)"
                pass
            try:
                sxs[name] = str(value)
            except ValueError:
                sxs[name] = value[1:-1] #stripping of the ""

    if wroteheader==0 and header['DX']>0: #write header and fixed variables
        WriteHeader() #write header of output file
        WriteFixedVariables()
        WriteWorkpiece()
        wroteheader=1 #prevent writing 2 headers :-)

    if command == "XBO" or command == "XB": #boring B, XB of XBO
        if command=="XB": XB() #zoek toolinfo op
        Field.Previous=Field.Current
        Field.Current=xbo.setdefault('F', Field.Previous)
        if Field.Current=="1": #XBOVerticaal
            XBOVerticaal()
        else: #XBOHorizontaal
            XBOHorizontaal()
        command=""
    if command == "XLINESB": #rijboring
        Field.Previous=Field.Current
        Field.Current=xlinesb.setdefault('F', Field.Previous)
        XlinesB()
        command=""
    if command == "XG0": #start freesprofiel (indien T184/T295 voorstel ruggroef)
        Field.Previous=Field.Current
        Field.Current=xg0.setdefault('F', Field.Previous)
        XG0()
        command=""
    if command == "G1XL2P": #vervolg freesprofiel (of eindpunt ruggroef)
        if ruggroefT184==1:
            RUGGROEFT184()
        else:
            G1XL2P()
        command=""
    if command == "G2" or command == "G3": #vervolg freesprofiel G2/G3
        G2G3()
        command=""
    if command == "XEA": #XEA - boog van een ellips.
        XEA()
        command=""
    if command == "XPOCKET": #XPOCKET.
        XPOCKET()
        command=""
    if command == "SXS": #Xilog subprogramma S/XS.
        SXS() 
        command=""
    if command == "SETSTANDBY": #SET STANDBY (NC STOP)
        X2W_OPT=X2W_OPT_NCSTOP #verander optimalisatietype
        SETSTANDBY() 
        command=""
    if command == "LPAR": #Variabelen L of PAR
        WriteImportedVariables()
        command=""
    if command == "SX": #Functie SX (spiegeling X)
        SwitchXorY_prev=SwitchXorY
        SX()
        command=""
    if command == "SY": #Functie SX (spiegeling X)
        SwitchXorY_prev=SwitchXorY
        SY()
        command=""
    if Debug==1 or Debug==2: print "Field.Current:",Field.Current
    if Debug==1 or Debug==2: print "<<< Xilog3_line: %s" %Xilog3_line
    if Debug==1 or Debug==2: print ""

WriteOP() # Schrijf parameter met optimalisatietype weg
WriteContourVariables() # write variables gathered from contour lines
WriteFooter() # close output file
print'' #just a new line
if Debug==0 or Debug==1 or Debug==2:
    print '>>> Export OK! Controleer',(currentfilename[:-4]+".mpr"),'in WoodWOP. Indien OK, verwijder',currentfilename,'. Indien niet OK, herhaal conversie met andere switchmodus, aangepast .xxl bestand, of los de problemen op in WoodWOP. <<<'
    print ''
    print '>>> !!!NIET VERGETEN UITEINDELIJK HET .XXL BESTAND TE VERWIJDEREN!!! <<<'
    print''
if errors>0: print errors,"error(s). Dit .xxl prog naar map z:/Xil2WOP/Error kopieren ter controle!!!"; print ""
print '>>> Druk <ENTER> om dit venster te sluiten. <<<',raw_input()
#
