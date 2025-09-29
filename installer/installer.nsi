; BACnet Scanner Installer Script
!define APPNAME "BACnet Scanner v4"
!define COMPANYNAME "Siemens"
!define DESCRIPTION "BACnet Network Scanner and Device Discovery Tool"
!define VERSIONMAJOR 4
!define VERSIONMINOR 0
!define VERSIONBUILD 0

; Pfade relativ zum installer/ Verzeichnis
!define EXEPATH "output\dist\BACnet_Scanner_v4.exe"
!define ICONPATH "assets\installer_icon.ico"
!define LICENSEPATH "assets\license.txt"

!define HELPURL "https://siemens.com/support"
!define UPDATEURL "https://siemens.com/updates"
!define ABOUTURL "https://siemens.com/bacnet-scanner"
!define INSTALLSIZE 50000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"

Name "${APPNAME}"
Icon "${ICONPATH}"
OutFile "BACnet_Scanner_v4_Installer.exe"

!include LogicLib.nsh
!include MUI2.nsh

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${ICONPATH}"
!define MUI_UNICON "${ICONPATH}"

; Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSEPATH}"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "English"

; Admin-Rechte prüfen
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator-Rechte erforderlich!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

Function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
FunctionEnd

; Hauptkomponente
Section "BACnet Scanner (erforderlich)" SecMain
    SectionIn RO  ; Read-only, kann nicht abgewählt werden
    
    SetOutPath $INSTDIR
    
    ; Hauptprogramm kopieren
    File "${EXEPATH}"
    
    ; Konfigurationsdateien (falls vorhanden)
    SetOutPath $INSTDIR\config
    File /nonfatal /r "..\config\*.*"
    
    ; UI-Dateien (falls als separate Dateien benötigt)
    SetOutPath $INSTDIR\ui
    File /nonfatal /r "..\ui\*.*"
    
    ; Assets (falls als separate Dateien benötigt)
    SetOutPath $INSTDIR\assets
    File /nonfatal /r "..\assets\*.*"
    
    ; Uninstaller erstellen
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Registry-Einträge
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\BACnet_Scanner_v4.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
SectionEnd

; Verknüpfungen
Section "Verknüpfungen" SecShortcuts
    ; Startmenü
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\BACnet_Scanner_v4.exe" "" "$INSTDIR\BACnet_Scanner_v4.exe"
    CreateShortCut "$SMPROGRAMS\${COMPANYNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\uninstall.exe"
    
    ; Desktop-Verknüpfung
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\BACnet_Scanner_v4.exe" "" "$INSTDIR\BACnet_Scanner_v4.exe"
SectionEnd

; Beschreibungen
LangString DESC_SecMain ${LANG_GERMAN} "Hauptprogramm BACnet Scanner"
LangString DESC_SecMain ${LANG_ENGLISH} "Main BACnet Scanner application"
LangString DESC_SecShortcuts ${LANG_GERMAN} "Verknüpfungen im Startmenü und auf dem Desktop"
LangString DESC_SecShortcuts ${LANG_ENGLISH} "Shortcuts in Start Menu and on Desktop"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
!insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} $(DESC_SecShortcuts)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller
Section "Uninstall"
    ; Dateien entfernen
    Delete "$INSTDIR\BACnet_Scanner_v4.exe"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Verzeichnisse entfernen (falls vorhanden)
    RMDir /r "$INSTDIR\config"
    RMDir /r "$INSTDIR\ui"
    RMDir /r "$INSTDIR\assets"
    RMDir "$INSTDIR"
    
    ; Verknüpfungen entfernen
    Delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${COMPANYNAME}\Uninstall ${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${COMPANYNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Registry-Einträge entfernen
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
SectionEnd