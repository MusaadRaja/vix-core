# for localized messages
from . import _
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Components.config import config
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.Language import language
from Components.Button import Button
from Components.MenuList import MenuList
from Components.Sources.List import List
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
from os import listdir, remove, path
import datetime, time

class VIXIPKInstaller(Screen):
	skin = """<screen name="VIXIPKInstaller" position="center,center" size="560,400" title="IPK Installer" flags="wfBorder" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="lab1" position="0,50" size="560,50" font="Regular; 20" zPosition="2" transparent="0" halign="center"/>
		<widget name="list" position="10,105" size="540,300" scrollbarMode="showOnDemand" />
		<applet type="onLayoutFinish">
			self["list"].instance.setItemHeight(25)
		</applet>
	</screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("IPK Installer"))
		self['lab1'] = Label()
		self.defaultDir = '/tmp'
		self.onChangedEntry = [ ]
		self.list = []
		self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions', "MenuActions"],
			{
				'cancel': self.close,
				'red': self.close,
				'green': self.keyInstall,
				'yellow': self.changelocation,
				'ok': self.keyInstall,
				"menu": self.close,
			}, -1)

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Install"))
		self["key_yellow"] = Button()

		self.list = []
		self['list'] = MenuList(self.list)
		self.populate_List()

		if not self.selectionChanged in self["list"].onSelectionChanged:
			self["list"].onSelectionChanged.append(self.selectionChanged)

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["list"].getCurrent()
		if item:
			name = item
			desc = ""
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def changelocation(self):
		if self.defaultDir == '/tmp':
			self["key_yellow"].setText(_("Extra IPK's"))
			self.defaultDir = config.backupmanager.xtraplugindir.getValue()
			if not path.exists(self.defaultDir):
				message = _("Sorry but location does exist or not setup, please setup in Backup Manager ?")
				ybox = self.session.openWithCallback(self.Install, MessageBox, message, MessageBox.TYPE_INFO)
				ybox.setTitle(_("Change Location"))
			else:
				self.populate_List()
		else:
			self["key_yellow"].setText(_("Temp Folder"))
			self.defaultDir = '/tmp'
			self.populate_List()

	def populate_List(self):
		if self.defaultDir == '/tmp':
			self["key_yellow"].setText(_("Extra IPK's"))
		else:
			self["key_yellow"].setText(_("Temp Folder"))

		self['lab1'].setText(_("Select a package to install:"))
		del self.list[:]
		f = listdir(self.defaultDir)
		for line in f:
			if line.find('.ipk') != -1:
				self.list.append(line)
		self.list.sort()
		self['list'].l.setList(self.list)

	def keyInstall(self):
		message = _("Are you ready to install ?")
		ybox = self.session.openWithCallback(self.Install, MessageBox, message, MessageBox.TYPE_YESNO)
		ybox.setTitle(_("Install Confirmation"))

	def Install(self,answer):
		if answer is True:
			sel = self['list'].getCurrent()
			if sel:
				self.defaultDir = self.defaultDir.replace(' ', '%20')
				cmd1 = "/usr/bin/opkg install " + path.join(self.defaultDir, sel)
				self.session.openWithCallback(self.installFinished(sel), Console, title=_("Installing..."), cmdlist = [cmd1], closeOnSuccess = True)

	def installFinished(self,sel):
		message = ("Do you want to restart GUI now ?")
		ybox = self.session.openWithCallback(self.restBox, MessageBox, message, MessageBox.TYPE_YESNO)
		ybox.setTitle(_("Restart Enigma2."))

	def restBox(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.populate_List()
			self.close()

	def myclose(self):
		self.close()
