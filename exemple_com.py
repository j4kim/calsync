# -*- coding: latin-1 -*-

import os
import sys

import win32com.client  


... 

#########################################
#
# Ecriture dans les calendrier Outlook
#
#########################################

def WriteCalendrier() :
	
	# Constantes Outlook
	olAppointmentItem = 1
	olMeeting = 1    
	olRequired = 1
	olFolderCalendar = 9
	
	# Ouverture de outlook
	outlook = win32com.client.Dispatch("Outlook.Application")
	namespace = outlook.GetNamespace("MAPI")
	
	# Creation d'un rendez-vous
		
	recipient       = namespace.CreateRecipient(occupation[CSVPOSsalle])						<--- nom de la salle Salle-CA2-ING-019
	calendrier      = namespace.GetSharedDefaultFolder(recipient,olFolderCalendar)
	appt            = calendrier.Items.Add(1)
	appt.Start      = datedebut+' '+heuredebut  <--- date jj.mm.aaaa et heure hh:mm:ss   
	appt.End        = datefin  +' '+heurefin    <--- date jj.mm.aaaa et heure hh:mm:ss
	appt.Subject    = matiere										<--- texte libre
	appt.Location   = salle											<--- texte libre
	appt.Categories = categorie								  <--- catégorie Outlook (libre)
	appt.Save()

...
