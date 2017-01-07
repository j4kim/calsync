# -*- coding: latin-1 -*-
import os
import sys
import win32com.client

#########################################
#
# Ecriture dans les calendrier Outlook
#
#########################################

def WriteCalendrier():
    # Constantes Outlook
    olAppointmentItem = 1
    olMeeting = 1
    olRequired = 1
    olFolderCalendar = 9

    # Ouverture de outlook
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")

    datedebut = "12.01.2017"
    heuredebut = "12:12:12"
    heurefin = "13:13:13"
    # Creation d'un rendez-vous
    recipient = namespace.CreateRecipient("Salle-CA2-ING-019")
    print(help(namespace.GetSharedDefaultFolder))
    calendrier = namespace.GetSharedDefaultFolder(recipient, olFolderCalendar)
    appt = calendrier.Items.Add(1)
    appt.Start = datedebut + ' ' + heuredebut
    appt.End = datedebut + ' ' + heurefin
    appt.Subject = "sujet"
    appt.Save()

if __name__ == "__main__":
    WriteCalendrier()