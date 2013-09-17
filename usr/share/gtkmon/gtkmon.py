#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import gtk, sys, os, gobject, pango, gst, re, vte

class princ:
	def __init__(self):
		self.win = gtk.Window()
		self.vb = gtk.VBox()
		self.hb1 = gtk.HBox()
		self.hb2 = gtk.HBox()
		self.vb1 = gtk.VBox()
		self.vb2 = gtk.VBox()
		self.vb3 = gtk.VBox()
		self.vb4 = gtk.VBox()
		self.labstatus = gtk.Label('Estado')
		self.labmodel = gtk.Label()
		self.labsignal = gtk.Label('Señal:')
		self.labsignalnum = gtk.Label('---.-%')
		self.labsnr = gtk.Label('Relación señal/ruido:')
		self.labsnrnum = gtk.Label('---')
		self.labber = gtk.Label('Error de Bitrate:')
		self.labbernum = gtk.Label('--')
		self.labunc = gtk.Label('Paquetes erroneos:')
		self.labuncnum = gtk.Label('--')
		self.seph1 = gtk.HSeparator()
		self.seph2 = gtk.HSeparator()
		self.seph3 = gtk.HSeparator()
		self.seph4 = gtk.HSeparator()
		self.sepv1 = gtk.VSeparator()
		self.sepv2 = gtk.VSeparator()
		self.botaudio = gtk.ToggleButton('Medidor de señal por audio')
		self.terminal = vte.Terminal()
		self.contador = 0 #para arreglar un bug en la nueva esctuctura de lecturamodel()
		
		self.win.add(self.vb)
		self.vb.pack_end(self.botaudio, 0, 0, 0)
		self.vb.pack_end(self.seph4, 0, 0, 0)
		self.vb.pack_end(self.hb1, 1, 1, 0)
		self.vb.pack_end(self.seph1, 0, 0, 0)
		self.vb.pack_end(self.hb2, 1, 1, 0)
		self.vb.pack_end(self.seph2, 0, 0, 0)
		self.vb.pack_end(self.labstatus, 0, 0, 0)
		self.vb.pack_end(self.seph3, 0, 0, 0)
		self.vb.pack_end(self.labmodel, 0, 0, 0)
		self.hb1.pack_start(self.vb1, 1, 1, 0)
		self.hb1.pack_start(self.sepv1, 0, 0, 0)
		self.hb1.pack_start(self.vb2, 1, 1, 0)
		self.hb2.pack_start(self.vb3, 1, 1, 0)
		self.hb2.pack_start(self.sepv2, 0, 0, 0)
		self.hb2.pack_start(self.vb4, 1, 1, 0)
		self.vb1.pack_start(self.labunc, 0, 0, 0)
		self.vb1.pack_start(self.labuncnum, 1, 0, 0)
		self.vb2.pack_start(self.labber, 0, 0, 0)
		self.vb2.pack_start(self.labbernum, 1, 0, 0)
		self.vb3.pack_start(self.labsignal, 0, 0, 0)
		self.vb3.pack_start(self.labsignalnum, 1, 0, 0)
		self.vb4.pack_start(self.labsnr, 0, 0, 0)
		self.vb4.pack_start(self.labsnrnum, 1, 0, 0)
		
		self.terminal.fork_command('femon')
		self.terminal.set_size(90, 5)

		self.win.set_title('Gtkmon')
		self.win.set_size_request(300, 300)

		font1 = pango.FontDescription('Ubuntu Bold 13')
		font2 = pango.FontDescription('Ubuntu Bold 10')
		font3 = pango.FontDescription('Ubuntu 16')
		self.labmodel.modify_font(font1)
		self.labsignal.modify_font(font2)
		self.labber.modify_font(font2)
		self.labunc.modify_font(font2)
		self.labsnr.modify_font(font2)
		self.labsignalnum.modify_font(font3)
		self.labbernum.modify_font(font3)
		self.labuncnum.modify_font(font3)
		self.labsnrnum.modify_font(font3)

		self.vb1.set_size_request(200, 128)
		self.vb2.set_size_request(200, 128)
		self.vb3.set_size_request(200, 128)
		self.vb4.set_size_request(200, 128)

		self.labstatus.set_tooltip_text('''S: señal detectada
C: señal digital comprensible (portadora completa)
V: detección y corrección de errores estable
Y: bits de sincronización encontrados
L: señal usable''')

		self.win.show_all()
		self.win.set_resizable(0)

		self.win.connect('destroy', self.quit)
		self.botaudio.connect('toggled', self.activaudio)
		self.terminal.connect('cursor-moved', self.lectura)
		self.terminal.connect('child-exited', self.errorf)
		self.audio()


#este es el 'motor' encargado de la utilización de femon (reestructurado) ###
	def lectura(self, z):

		if self.contador == 0:
			self.lecturamodel()

		a = self.terminal.get_cursor_position()
		b = int(a[1])
		c = self.terminal.get_text_range(b - 1, 0, b - 1, 81, self.gbtrue)
		d = c.split('\n')
		f = str(d[0])
		g = f.split(' | ')


		statussep = str(g[0])
		self.status = str(statussep[7:])

		signalsep = str(g[1])
		signalhex = str(signalsep[7:])
		self.signal = round((float((int(signalhex, 16) / 1000.000) + 22)), 1)

		snrsep = str(g[2])
		snrhex = str(snrsep[4:])
		self.snr = int((int(snrhex, 16))/10)
		
		bersep = str(g[3])
		berhex = str(bersep[4:])
		self.ber = int(berhex, 16)
		
		uncsep = str(g[4])
		unchex = str(uncsep[4:])
		self.unc = int(unchex, 16)
		
		self.actualizar()
		
	#leer modelo de hardware (reestructurado) ##
	def lecturamodel(self):
		a = self.terminal.get_text_range(0, 0, 0, 80, self.gbtrue)
		b = a.split('\n')
		self.model = str(b[0])
		self.labmodel.set_text(self.model[3:])
		self.contador = 1
	##########################

##############################################################


#actualizador de datos en la interfaz##################################
	def actualizar(self):
		#signalf1 = round(self.signal, 1)
		self.labsignalnum.set_text(str(self.signal)+' %')
		self.labuncnum.set_text(str(self.unc))
		self.labbernum.set_text(str(self.ber))
		self.labsnrnum.set_text(str(self.snr)+' dB')

		#colores para los múmeros###
		if self.signal >= 65:
			self.labsignalnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#009000'))
		
		if self.signal < 65 and self.signal >= 40:
			self.labsignalnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#DC8A00'))
		if self.signal < 40:
			self.labsignalnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#B60000'))

		if self.unc != 0:
			self.labuncnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#B60000'))
		
		if self.unc == 0:
			self.labuncnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))

		if self.ber != 0:
			self.labbernum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('blue'))
		
		if self.ber == 0:
			self.labbernum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))
		
		if self.snr >= 17:
			self.labsnrnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#009000'))

		if self.snr < 17 and self.snr > 5:
			self.labsnrnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#B60000'))

		if self.snr <= 5:
			self.labsnrnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))

		############################

		#mas colores y uso de status##
		if not self.status == 'SCVYL':

			self.labstatus.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#FF2121'))
			self.labstatus.set_text('Señal incompleta (' + self.status + ')')

			if self.status == 'S V L':
				self.labstatus.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))
				self.labstatus.set_text('Dispositivo apagado')
				self.labsignalnum.set_text('---.-%')
				self.labuncnum.set_text('--')
				self.labbernum.set_text('--')
				self.labsnrnum.set_text('---')
				self.labsignalnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))
				self.labsnrnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))
				self.labbernum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))
				self.labuncnum.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('black'))
				
			if self.status == 'SC   ':
				self.labstatus.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('blue'))
				self.labstatus.set_text('Sintonizando')

			if self.status == '     ':
				self.labstatus.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#B60000'))
				self.labstatus.set_text('Sin señal comprensible')
		
		else:
			self.labstatus.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#009000'))
			self.labstatus.set_text('Señal completa')
		##############################

		# actualizar audio ##
		if self.labstatus.get_text() == 'Sintonizando' or self.labstatus.get_text() == 'Señal completa':
			self.audiofuente.set_property("freq", self.signal * 10)

		elif re.search('Señal incompleta (.....)', self.labstatus.get_text()) and self.unc != 0:
			self.audiofuente.set_property("freq", self.signal * 10)
		else:
        		self.audiofuente.set_property("freq", 0)
		
		if not self.unc == 0:
			if self.unc >= 1 and self.unc <= 10:
				gobject.timeout_add(450, self.audiounc)
			else:
				gobject.timeout_add(250, self.audiounc)

	def audiounc(self):
			self.audiofuente.set_property("freq", 0)
		###################################

		
###############################################################################

#motor de audio (gst) + swith para activar/desactivar #######################
	def audio(self):
		self.audiotuberia = gst.Pipeline("gtkmon audio")
        	self.audiofuente = gst.element_factory_make("audiotestsrc", "audio")
		self.audiofuente.set_property("freq", 0)
        	self.audiotuberia.add(self.audiofuente)
		self.alsa = gst.element_factory_make("alsasink", "sink")
        	self.audiotuberia.add(self.alsa)
        	self.audiofuente.link(self.alsa)
		
	def activaudio(self, b):
		if self.botaudio.get_active():
			self.audiotuberia.set_state(gst.STATE_PLAYING)
		else:
			self.audiotuberia.set_state(gst.STATE_NULL)

###########################################################################

#controla si desde fomen sale algo (reestructurado) ##
	def errorf(self, b):
			self.labmodel.set_text('ERROR: no hay dispositivo!!')
			self.labmodel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#B60000'))
			self.labmodel.set_tooltip_text('''femon, el programa cual Gtkmon recoje los datos,
se ha cerrado inesperadamente.
Comunmente esto significa que no se encuentra ningun dispositivo en el sistema. 

Cierre el programa''')

########################

	def gbtrue(self, a, b, c, d):
		return True

	def quit(self, b):
		gtk.main_quit()
princ()
gtk.main()
