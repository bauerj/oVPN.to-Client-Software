# encoding=utf8
from Tkinter import *
import Tkinter,tkMessageBox,Tkconstants,types,os,platform,sys,hashlib,random,base64,urllib,urllib2,time,datetime
import _winreg,zipfile
from waiting import wait, TimeoutExpired, ANY, ALL
import subprocess
import threading
#import logging
import win32com.client
import socket
from Crypto.Cipher import AES

BUILT="0.0.8"
STATE="alpha"

DEBUG = True

DOMAIN = "vcp.ovpn.to"
PORT="443"
API="xxxapi.php"
#SSL="CE:4F:88:43:F8:6B:B6:60:C6:02:C7:AB:9C:A9:2F:15:3A:9F:F4:65:A3:20:D0:11:A1:27:74:B4:07:B9:54:6A"

class AppUI(Frame):

	def __init__(self, root):
		Frame.__init__(self, root, relief=SUNKEN, bd=2)
		self.root = root
		self.root.protocol("WM_DELETE_WINDOW", lambda root=root: self.on_closing(root))
		self.self_vars()		
		self.frame = Frame(self,bg="#1a1a1a", width=self.screen_width, height=self.screen_height)
		self.frame.pack_propagate(0)		
		self.frame.pack()
		self.make_mini_menubar()
		self.check_preboot()		
		try:
			pass
			#debuglog = "%APPDATA%\ovpn\bin\client\dist\debug.log"
			#debuglog = 'ovpn_client_debug.log'
			#logging.basicConfig(filename=debuglog,level=logging.DEBUG)
			#logging.debug('This message should go to the log file')
		except:
			pass
					
	def self_vars(self):
		self.SMALL_WINDOW = False
		self.SWITCH_SMALL_WINDOW = False
		self.isLOGGEDin = False
		self.menubar = False
		self.UPDATE_MENUBAR = False
		self.statusbar = False
		self.timer_statusbar_running = False
		self.timer_ovpn_ping_running = False
		self.timer_ovpn_reconnect_running = False
		self.timer_check_certdl_running = False
		self.statustext_from_before = False
		self.statusbar_text = StringVar()
		self.SYSTRAYon = False
		self.screen_width = 320
		self.screen_height = 240
		self.USERID = False
		self.input_PH = False
		self.extract = False
		self.isLoggedIn = False
		self.STATE_OVPN = False
		self.GATEWAY_LOCAL = False
		self.GATEWAY_DNS = False
		self.WIN_TAP_DEVICE = False
		self.WIN_EXT_DEVICE = False
		self.OVPN_SERVER = list()
		self.OVPN_FAV_SERVER = False
		self.OVPN_AUTO_RECONNECT = True
		self.OVPN_CONNECTEDto = False
		self.OVPN_CONNECTEDtoIP = False
		self.OVPN_CONNECTEDtoIPbefore = False
		self.OVPN_THREADID = False
		self.OVPN_THREAD_STARTED = False
		self.OVPN_RECONNECT_NOW = False
		self.OVPN_PING = list()
		self.OVPN_isTESTING = False
		self.OVPN_PING_LAST = -1
		self.OVPN_PING_STAT = -1
		self.INTERFACES = False
		
		
	def errorquit(self,text):
		self.debug(text)
		tkMessageBox.showinfo("Error","%s" % (text))
		sys.exit()
		
	def msgwarn(self,text):
		self.debug(text)
		tkMessageBox.showinfo("Warning","%s" % (text))	
	
	def debug(self,text):
		self.localtime = time.asctime (time.localtime(time.time()))
		if DEBUG: 
			#self.localtime = "x"
			debugstring = "%s: "%(self.localtime)+text
			print(debugstring)
			#logging.debug(debugstring)

	def check_preboot(self):
		if self.pre0_detect_os():
			if self.win_pre1_check_app_dir():
				if self.win_pre2_check_profiles_win():
					if self.win_pre3_load_profile_dir_vars():
						if self.check_config_folders():
							self.debug(text="def check_preboot: if self.check_config_folders :True")
							self.preboot = False
							self.timer_preboot()
							self.make_statusbar()
							self.check_inet_connection()						
							self.receive_passphrase()
							self.update_idletasks()
							self.debug(text="We start looping!")
							return True
						else:
							self.form_enter_new_encryption_password()
							self.debug(text="We start looping too!")
							return True
	def removethis(self):
		self.frame.destroy()
		self.frame = Frame(self, width=self.screen_width, height=self.screen_height)
		self.frame.pack_propagate(0)
		self.frame.pack()		
		self.frame.update_idletasks()
							
	def timer_preboot(self):
		if self.preboot == True:
			self.removethis()
			self.make_menubar()
			if self.gui_check_remotelogin():
				self.debug(text="def timer_preboot remotelogin OK")
				if self.timer_check_certdl_running == False: self.isLOGGEDin = True				
				if self.extract:
					self.make_menubar()
					text = "Extraction well done!"
					self.statusbar_text.set(text)
					self.make_label(text=text) 
					return True
				return True
		else:
			#self.debug(text="def timer_preboot: looping!")
			self.root.after(1000,self.timer_preboot)
							
	def ask_passphrase(self):
		self.debug(text="def ask_passphrase")
		self.removethis()
		self.make_label(text="oVPN.to Client Authentication\n\n\nEnter your Passphrase")
		self.input_PH = Entry(self.frame,show="*")
		self.input_PH.pack()		
		button = Button(self.frame, text="OK", command=self.receive_passphrase).pack()
	

	def receive_passphrase(self):
		self.debug(text="def receive_passphrase")
		
		if not self.input_PH == False: 
			self.PH = self.input_PH.get().rstrip()
			
		if not self.USERID == False and not self.input_PH == False:
			if self.read_config():
				self.debug(text="def receive_passphrase :self.read_config")
				if self.compare_confighash():
					self.input_PH = False
					self.preboot = True
					self.debug(text="def receive_passphrase :True")
					self.statusbar_text.set("Passphrase Ok!")
					self.removethis()
					self.make_label(text="\n\n\nPlease wait!")
					return True
				else:
					os.remove(self.api_cfg)
					self.quit_text = "READ_CONFIG HASH ERROR"
					self.errorquit()
			else:
				self.ask_passphrase()					
		else:
			self.ask_passphrase()							
	
	def pre0_detect_os(self):
		self.self_vars()
		self.OS = sys.platform
		if self.OS == "win32":
			w32Reg = _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)
			w32Key1 = _winreg.OpenKey(w32Reg, "HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0", _winreg.KEY_READ)
			key1_value, type = _winreg.QueryValueEx(w32Key1,"Identifier")
			key1_value = key1_value.split()
			w32Key1.Close()
			if key1_value[0] == "Intel64": 
				self.OSARCH = "x86_64"
				self.OSBITS = "64"			
			elif key1_value[0] == "AMD64": 
				self.OSARCH = "x86_64"
				self.OSBITS = "64"
			elif key1_value[0] == "x86" or key1_value[0] == "i686" or key1_value[0] == "i586":
				self.OSARCH = "x86"
				self.OSBITS = "32"
			else:
				self.errorquit(text = "Operating System not supported: %s %s" % (self.OS,key1_value[0]))				
			if DEBUG: print("def pre0_detect_os: arch=%s bits=%s key=%s OS=%s" % (self.OSARCH,self.OSBITS,key1_value[0],self.OS))
			self.win_get_interfaces()
			return True
		elif OS == "linux2" :
			self.errorquit(text = "Operating System not supported: %s" % (self.OS))	
		elif OS == "darwin":
			self.errorquit(text = "Operating System not supported: %s" % (self.OS))
		else: 
			self.errorquit(text = "Operating System not supported: %s" % (self.OS))
	
	def win_pre1_check_app_dir(self):
		os_appdata = os.getenv('APPDATA')
		self.app_dir = "%s\ovpn" % (os_appdata)
		if not os.path.exists(self.app_dir):
			if DEBUG: print("win_pre1_check_app_dir %s not found, creating." % (self.app_dir))
			os.mkdir(self.app_dir)
		if os.path.exists(self.app_dir):
			self.debug(text="win_pre1_check_app_dir self.app_dir=%s :True" % (self.app_dir))
			return True
		else:
			self.errorquit(text = "def check_winapp_dir could not create app_dir: %s" % (self.app_dir))

	def win_pre2_check_profiles_win(self):
		self.debug(text="def win_pre2_check_profiles_win: %s" % (self.app_dir))
		self.profiles_unclean = os.listdir(self.app_dir)
		self.profiles = list()
		for profile in self.profiles_unclean:
			if profile.isdigit():
				self.profiles.append(profile)
				
		self.profiles_count = len(self.profiles)
		if DEBUG: print("_check_profiles_win profiles_count %s" % (self.profiles_count))
		
		if self.profiles_count == 0:
			if DEBUG: print("No profiles found")
			if self.USERID == False:
				self.debug(text="spawn popup userid = %s" % (self.USERID))
				self.form_ask_userid()				
				
		elif self.profiles_count == 1 and self.profiles[0] > 1:
			self.profile = self.profiles[0]
			self.USERID = self.profile
			return True
		elif self.profiles_count > 1:
			self.errorquit(text = "Multiple profiles not yet implemented.\nPlease empty\n %s" % (self.app_dir))
		#elif self.check_userid_format:
		#	return True
		
		for profile in self.profiles:
			print("Profile: %s" % (profile))
			
		if DEBUG: print("def check_profiles_win end")
		#return True
			
	def win_pre3_load_profile_dir_vars(self):
		self.api_dir = "%s\%s" % (self.app_dir,self.profile)
		
		self.debuglog = "%s\cient_debug.log" % (self.api_dir)
		
		self.api_cfg = "%s\ovpnapi.conf" % (self.api_dir)
		self.vpn_dir = "%s\openvpn" % (self.api_dir)
		self.prx_dir = "%s\proxy" % (self.api_dir)
		self.stu_dir = "%s\stunnel" % (self.api_dir)
		self.pfw_dir = "%s\pfw" % (self.api_dir)
		
		self.vpn_cfg = "%s\config" % (self.vpn_dir)
		self.zip_cfg = "%s\confs.zip" % (self.vpn_dir)
		self.zip_crt = "%s\certs.zip" % (self.vpn_dir)
		self.api_upd = "%s\lastupdate.txt" % (self.vpn_dir)
		

		if DEBUG: print("win_pre3_load_profile_dir_vars loaded")
		return True	

	def check_config_folders(self):
		self.debug(text="def check_config_folders userid = %s" % (self.USERID))
		if not os.path.exists(self.api_dir):
			if DEBUG: print("api_dir %s not found, creating." % (self.api_dir))
			os.mkdir(self.api_dir)

		if not os.path.exists(self.vpn_dir):
			if DEBUG: print("vpn_dir %s not found, creating." % (self.vpn_dir))
			os.mkdir(self.vpn_dir)

		if not os.path.exists(self.vpn_cfg):
			if DEBUG: print("vpn_cfg %s not found, creating." % (self.vpn_cfg))
			os.mkdir(self.vpn_cfg)			

		if not os.path.exists(self.prx_dir):
			if DEBUG: print("prx_dir %s not found, creating." % (self.prx_dir))
			os.mkdir(self.prx_dir)
			
		if not os.path.exists(self.stu_dir):
			if DEBUG: print("stu_dir %s not found, creating." % (self.stu_dir))
			os.mkdir(self.stu_dir)
			
		if not os.path.exists(self.pfw_dir):
			if DEBUG: print("pfw_dir %s not found, creating." % (self.pfw_dir))
			os.mkdir(self.pfw_dir)			
			
		if os.path.exists(self.api_dir) and os.path.exists(self.vpn_dir) and os.path.exists(self.vpn_cfg) \
		and os.path.exists(self.prx_dir) and os.path.exists(self.stu_dir) and os.path.exists(self.pfw_dir):
			if not os.path.isfile(self.api_upd):
				if DEBUG: print("writing lastupdate to %s" % (self.api_upd))
				cfg = open(self.api_upd,'w')
				cfg.write("0")
				cfg.close()
				
			if not os.path.isfile(self.api_upd):
				self.errorquit(text = "Creating FILE\n%s\nfailed!" % (self.api_upd))
				
			if os.path.isfile(self.api_cfg):
				self.debug(text="def check_config_folders :True")
				return True
			else:
				return False
		else:
			self.errorquit(text = "Creating API-DIRS\n%s \n%s \n%s \n%s \n%s failed!" % (self.api_dir,self.vpn_dir,self.prx_dir,self.stu_dir,self.pfw_dir))

			
	def form_ask_userid(self):
		if DEBUG: print("def form_ask_userid")
		self.removethis()
		self.make_label(text = "oVPN.to Client\n\n\nPlease enter your oVPN.to User-ID Number:")
		self.input_userid = Entry(self.frame)
		self.input_userid.pack()
		Button(self.frame, text="OK", command=self.receive_userid).pack()
		
	def receive_userid(self):
		self.USERID = self.input_userid.get().rstrip()
		if self.check_userid_format():
			if DEBUG: print("def receive_userid userid = %s" % (self.USERID))
			if self.OS == "win32": 
				self.profile = self.USERID				
				self.win_pre3_load_profile_dir_vars()
				if self.check_config_folders() == False:
					self.form_enter_new_encryption_password()
					return True
		else: self.USERID = False	

	def form_enter_new_encryption_password(self):
		self.removethis()
		self.make_label(text="oVPN.to Client Setup\n\n\nPassphrase to encrypt and decrypt your API Configuration.\n\nEnter New Passphrase!\nRepeat New Passphrase!")
				
		self.input_PH1 = Entry(self.frame,show="*")
		self.input_PH1.pack()
		self.input_PH2 = Entry(self.frame,show="*")
		self.input_PH2.pack()

		Button(self.frame, text="Save Encryption Passphrase!", command=self.receive_new_passphrase).pack()
		
		
	def receive_new_passphrase(self):
		self.PH1 = self.input_PH1.get().rstrip()
		self.PH2 = self.input_PH2.get().rstrip()
		if self.PH1 == self.PH2 and len(self.PH1) > 0:
			if DEBUG: print("passphrase accepted")
			self.form_enter_api_login()
		else:
			if DEBUG: print("passphrase mismatch")	
			self.form_enter_new_encryption_password()
			
			
	def form_enter_api_login(self):
		self.removethis()
		self.make_label(text="oVPN.to Client Setup\n\n\nEnter your oVPN.to API-Key:")
		self.input_apikey = Entry(self.frame,show="*")
		self.input_apikey.pack()
		
		Button(self.frame, text="Save API-Key!", command=self.write_new_config).pack()		

		
	def gui_check_remotelogin(self):
		self.removethis()
		#if DEBUG: print("check_remotelogin: userid=%s apikey=%s") % (self.USERID,self.APIKEY)
		
		Label(self.frame,text="oVPN.to Client %s\n\n\n" % (self.USERID)).pack()
		
		if self.curl_api_request(API_ACTION = "lastupdate"):
			if DEBUG: print("self.curldata: %s") % (self.curldata)
			self.remote_lastupdate = self.curldata
			if self.check_last_server_update():
				text = "Updating oVPN Configurations..."
				self.statusbar_text.set(text)
				self.make_label(text = text)
				if self.curl_api_request(API_ACTION = "getconfigs"):
					text = "Updating oVPN Certificates..."
					self.statusbar_text.set(text)
					self.make_label(text = text)
					if self.curl_api_request(API_ACTION = "requestcerts"):
						self.make_label(text = "Please wait up to 5 minutes.")
						self.timer_check_certdl()
						return True
			else:
				self.make_label(text="Checking for oVPN Updates: Complete!")
				self.make_label(text="\n\nAlpha is not Beta!\nThanks for testing!")
				return True	
		else:
			#os.remove(self.api_cfg)
			self.errorquit(text="Invalid User-ID/API-Key or Connection failed to https://vcp.ovpn.to!")	

	def check_last_server_update(self):
		cfg = open(self.api_upd,'r')
		read_data = cfg.read()
		cfg.close()
		if read_data < self.remote_lastupdate:
			if DEBUG: print("our last update: %s") % (read_data)
			return True	
	
	
	def write_last_update(self):
		cfg = open(self.api_upd,'wb')
		now = int(time.time())
		cfg.write("%s" % (now))
		cfg.close()
		return True

		
	def extract_ovpn(self):
		z1file = zipfile.ZipFile(self.zip_cfg)
		z2file = zipfile.ZipFile(self.zip_crt)		
		z1file.extractall(self.vpn_cfg) 
		z2file.extractall(self.vpn_cfg)
		if self.write_last_update():
			self.statusbar_text.set("Certificates and Configs extracted.")
			return True
		
		
	
	def timer_check_certdl(self):
		self.timer_check_certdl_running = True
		self.curl_api_request(API_ACTION = "requestcerts")
		if not self.body == "ready":
			self.root.after(15000,self.timer_check_certdl)
			#self.root.update_idletasks()
		if self.body == "ready":
			if self.curl_api_request(API_ACTION = "getcerts"):	
				#self.removethis()
				self.body = False
				if self.extract_ovpn():
					self.removethis()
					#self.make_label(text = "oVPN.to Client %s\n\n\noVPN Server Update Complete!\nFiles saved to:\n%s\n%s\nFiles extracted to:\n%s" % (self.USERID,self.zip_cfg,self.zip_crt,self.vpn_cfg))
					self.extract = True
					self.make_menubar()
					self.isLOGGEDin = True
					self.timer_check_certdl_running = False
					return True
				else:
					self.make_label(text = "\noVPN Server Update Failed!")
					return False
					
	def check_inet_connection(self):
		s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host = "vcp.ovpn.to"
		port = 443
				
		if not self.try_socket(host,port):
			text="1) Could not connect to vcp.ovpn.to\nTry setting firewall rule to access VCP!"
			#self.msgwarn(text=text)
			self.debug(text=text)
			self.win_firewall_add_rule_to_vcp(option="add")
			time.sleep(2)
			if not self.try_socket(host,port):
				text="2) Could not connect to vcp.ovpn.to\nRetry"
				#self.msgwarn(text=text)
				self.debug(text=text)
				time.sleep(2)
				if not self.try_socket(host,port):
					#text="3) Could not connect to vcp.ovpn.to\nTry setting firewall rule to allowing outbound connections to world!"
					#self.win_firewall_allow_outbound()
					text="3) Could not connect to vcp.ovpn.to\n"
					self.debug(text=text)
					self.msgwarn(text=text)			
					#time.sleep(8)
					
				

	def try_socket(self,host,port):
		
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = s.connect_ex((host, port))
			s.close()			
		except:
			result = False
		
		print "def try_socket: result = %s" % (result)
		if result == 0:
			return True
		return False
			
		
		
						
	def curl_api_request(self,API_ACTION):
		self.APIURL = "https://%s:%s/%s" % (DOMAIN,PORT,API)
		self.API_ACTION = API_ACTION
		url = self.APIURL
		
		if self.API_ACTION == "lastupdate": 
			self.TO_CURL = "uid=%s&apikey=%s&action=%s" % (self.USERID,self.APIKEY,self.API_ACTION)
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : self.API_ACTION }		
			
		if self.API_ACTION == "getconfigs": 
			if os.path.isfile(self.zip_cfg): os.remove(self.zip_cfg)
			fp = open(self.zip_cfg, "wb")
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : self.API_ACTION, 'version' : '23x', 'type' : 'win' }	
			
		if self.API_ACTION == "requestcerts":			
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : self.API_ACTION }	
			
		if self.API_ACTION == "getcerts":
			if os.path.isfile(self.zip_crt): os.remove(self.zip_crt)
			fp = open(self.zip_crt, "wb")
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : self.API_ACTION }	
			
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		
		self.body = False
		try: 
			response = urllib2.urlopen(req)
			self.body = response.read()
			#self.debug("self.body = %s"%(self.body))
		except:
			self.debug("URL TIMEOUT: self.API_ACTION = %s" % (self.API_ACTION))
			self.errorquit(text="Connection to https://vcp.ovpn.to failed!")
			return False
			
		if self.API_ACTION == "getconfigs" or self.API_ACTION == "getcerts": 
			fp.write(self.body)
			fp.close()
			return True

		if self.API_ACTION == "requestcerts": 
			if self.body == "ready" or self.body == "wait" or self.body == "submitted":
				if DEBUG: print("self.body: %s") % (self.body)
				return True		
		
		if not self.body == "AUTHERROR":
			self.curldata = self.body.split(":")
			if self.curldata[0] == "AUTHOK":
				self.curldata = self.curldata[1]
				return True				
			
	def check_userid_format(self):
		if self.USERID.isdigit() and self.USERID > 1 and len(self.USERID) > 1:
			return True		
			
	def check_login_format(self):
		if self.check_userid_format():
			self.APIKEY = self.input_apikey.get().rstrip()
			if self.USERID.isdigit() and self.USERID > 1 and len(self.USERID) > 1:
				if self.APIKEY.isalnum() and len(self.APIKEY) == 128:
					return True				
			
	def load_decryption(self):
		self.debug(text="def load_decryption")
		if len(self.input_PH.get()) > 0: 
			self.aeskey = hashlib.sha256(self.input_PH.get().rstrip()).digest()
			return True

			
	def read_config(self):
		self.debug(text="def read_config")
		if not self.input_PH == False and self.load_decryption():
			cfg = open(self.api_cfg,'r')
			read_data = cfg.read()
			cfg.close()
			b64decode = base64.b64decode(read_data)
			configdata = b64decode.split(",")
			aesiv = base64.b64decode(configdata[0])
			b64config = base64.b64decode(configdata[1])
			crypt = AES.new(self.aeskey, AES.MODE_CBC, aesiv)
			self.apidata = crypt.decrypt(b64config).split(",")
			aesiv = False
			self.aeskey = False						
			if len(self.apidata) > 3:
				USERID = self.apidata[0].split("=")
				APIKEY = self.apidata[1].split("=")
				CFGSHA = self.apidata[2].split("=")
				if len(USERID) == 2 and USERID[1] > 1 and USERID[1].isdigit():					
					self.debug(text="def read_config USERID = %s :True" % (USERID))
					if len(APIKEY) == 2 and len(APIKEY[1]) == 128 and APIKEY[1].isalnum():						
						self.debug(text="def read_config APIKEY len = %s :True" % (len(APIKEY)))
						if len(CFGSHA) == 2 and len(CFGSHA[1]) == 64 and CFGSHA[1].isalnum():
							if not self.USERID == False and self.USERID == USERID[1]:
								self.APIKEY = APIKEY[1]
								self.USERID = int(USERID[1])
								self.CFGSHA = CFGSHA[1]
								#self.debug(text="def read_config CFGSHA = %s" % (self.CFGSHA))
								#self.debug(text="def read_config print self.apidata: %s" % (self.apidata))
								return True
							#else:
							#	self.debug(text="def read_config self.USERID = %s " % (self.USERID))
							#	self.debug(text="def read_config passphrase :True") 
			self.statusbar_text.set("Invalid Passphrase!")
			self.debug(text="def read_config passphrase :False")
			return False

	def write_new_config(self):
		if self.check_login_format():
			self.aeskeyhash = hashlib.sha256(self.PH1).digest()
			self.aesiv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
			self.make_confighash()			
			self.randint = random.randint(0,9)
			self.text2aes = "%s,CFGSHA=%s,AESPAD=%s" % (self.text2hash1,self.hash2aes,self.randint)
			self.text2aeslen = len(self.text2aes)
			self.targetpad = 64*64
			self.addpad = self.targetpad - self.text2aeslen
			self.padfill = 2
			self.paddata = self.randint
			while self.padfill <= self.addpad:
				self.randadd = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
				self.paddata = '%s%s' % (self.paddata,self.randadd)
				#if DEBUG: print("padfill=%s\npaddata=%s" % (self.padfill,self.paddata))
				self.padfill += 1
			self.text2aes = "%s%s" % (self.text2aes,self.paddata)
			self.text2aeslen = len(self.text2aes)
			#if DEBUG: print("text2aeslen=%s\n" % (self.text2aeslen))
			#if DEBUG: print("\n##############debug:text2aes=%s\ndebug:aesiv=%s\ndebug:len(self.text2aeslen)=%s\nself.addpad=%s" % (self.text2aes,self.aesiv,self.text2aeslen,self.addpad))
			self.crypt = AES.new(self.aeskeyhash, AES.MODE_CBC, self.aesiv)
			cipherd_data = base64.b64encode(self.crypt.encrypt(self.text2aes))
			data2file = "%s,%s" % (base64.b64encode(self.aesiv),cipherd_data)
			cfg = open(self.api_cfg,'wb')
			cipherd_data_b64 = base64.b64encode(data2file)
			cfg.write(cipherd_data_b64)
			cfg.close()
			self.aesiv = False
			self.aeskeyhash = False
			self.hash2aes = False
			self.text2aes = False
			self.paddata = False
			self.check_preboot()			
			
	def make_confighash(self):
		self.text2hash1 = "USERID=%s,APIKEY=%s" % (self.USERID,self.APIKEY)
		self.hash2aes = hashlib.sha256(self.text2hash1).hexdigest()
			
	def compare_confighash(self):
		self.make_confighash()
		if self.hash2aes == self.CFGSHA:
			self.debug(text="def compare_confighash :True")
			return True	

	def make_label(self,text):
		Label(self.frame,text=text).pack()
		self.update_idletasks()
			
		
	def dologout(self):
		self.removethis()
		#self.canvas.destroy()
		self.menubar.destroy()
		self.isLOGGEDin = False
		self.USERID = False
		self.debug(text="Logout")
		self.make_mini_menubar()
		self.check_preboot()
		

	def make_mini_menubar(self):
		self.mini_menubar = Menu(self)

		#menu = Menu(self.mini_menubar, tearoff=0)
		#self.mini_menubar.add_cascade(label="Menu", menu=menu)
		#self.mini_menubar.add_separator()
		#menu.add_command(label="Anything")
		
		menu = Menu(self.mini_menubar, tearoff=0)
		self.mini_menubar.add_cascade(label="?", menu=menu)
		menu.add_command(label="Info")	

		try:
			self.master.config(menu=self.mini_menubar)
		except AttributeError:
			# master is a toplevel window (Python 1.4/Tkinter 1.63)
			self.master.tk.call(master, "config", "-menu", self.mini_menubar)

		#self.boot_canvas = Canvas(self, bg="#1a1a1a", width=self.screen_width, height=self.screen_height,bd=0, highlightthickness=0)
		#self.boot_canvas.pack()
		
	def load_ovpn_server(self):
		self.removethis()
		content = os.listdir(self.vpn_cfg)
		#self.debug(text="def load_ovpn_server: content = %s " % (content))
		self.OVPN_SERVER = list()
		for trash in content:
			if trash.endswith('.ovpn.to.ovpn'):
				trash = trash[:-5]
				self.OVPN_SERVER.append(trash)
				#self.debug(text="def: trash = %s " % (trash))
		self.OVPN_SERVER.sort()
			
		
	def openvpn(self,server):
		if self.STATE_OVPN == False:
			self.OVPN_AUTO_RECONNECT = True
			self.ovpn_server_UPPER = server
			self.ovpn_server_LOWER = server.lower()

			self.ovpn_server_config_file = "%s\%s.ovpn" % (self.vpn_cfg,self.ovpn_server_UPPER)
			for line in open(self.ovpn_server_config_file):
				if "remote " in line:
					print(line)
					try:
						self.OVPN_CONNECTEDtoIP = line.split()[1]
						self.OVPN_CONNECTEDtoPort = line.split()[2]
						#break
					except:
						self.errorquit(text="Could not read Servers Remote-IP:Port from config: %s" % (self.ovpn_server_config_file) )
				if "proto " in line:
					try:
						self.OVPN_CONNECTEDtoProtocol = line.split()[1]
					except:
						self.errorquit(text="Could not read Servers Protocol from config: %s" % (self.ovpn_server_config_file) )
			
			
			self.ovpn_sessionlog = "%s\ovpn.log" % (self.vpn_dir)
			self.ovpn_server_dir = "%s\%s" % (self.vpn_cfg,self.ovpn_server_LOWER)
			self.ovpn_cert_ca = "%s\%s.crt" % (self.ovpn_server_dir,self.ovpn_server_LOWER)
			self.ovpn_tls_key = "%s\%s.key" % (self.ovpn_server_dir,self.ovpn_server_LOWER)
			self.ovpn_cli_crt = "%s\client%s.crt" % (self.ovpn_server_dir,self.USERID)
			self.ovpn_cli_key = "%s\client%s.key" % (self.ovpn_server_dir,self.USERID)
			self.ovpn_string = "openvpn.exe --config \"%s\" --ca \"%s\" --cert \"%s\" --key \"%s\" --tls-auth \"%s\" --log \"%s\" " % (self.ovpn_server_config_file,self.ovpn_cert_ca,self.ovpn_cli_crt,self.ovpn_cli_key,self.ovpn_tls_key,self.ovpn_sessionlog)
			
			try:
				self.call_ovpn_srv = server
				threading.Thread(target=self.inThread_spawn_openvpn_process).start()
				self.OVPN_THREADID = threading.currentThread()
				self.debug(text="Started: oVPN %s on Thread: %s" %(server,self.OVPN_THREADID))
				#self.statusbar_text.set("oVPN connecting to %s ..." %(server))
				self.OVPN_THREAD_STARTED = True
			except:
				self.statusbar_text.set("Unable to start Thread: oVPN (%s) "%(server))
				tkMessageBox.showwarning("Error", "Unable to start thread: oVPN %s "%(server))
				self.debug(text="Error: unable to start thread: oVPN")
				
			if self.OVPN_AUTO_RECONNECT == True:
				self.debug("def openvpn: self.OVPN_AUTO_RECONNECT == True")
				self.OVPN_RECONNECT_NOW = False
				threading.Thread(target=self.inThread_timer_openvpn_reconnect).start()
			else:
				self.debug("def openvpn: self.OVPN_AUTO_RECONNECT == False")
				
		else:
			self.debug(text="def openvpn: self.OVPN_THREADID = %s" % (self.OVPN_THREADID))
			#if tkMessageBox.askokcancel("Change oVPN Server?", "oVPN is connected to: %s\n\nSwitch to oVPN Server: %s?"%(self.OVPN_CONNECTEDto,server)):
			self.debug(text="Change oVPN to %s" %(server))
			self.kill_openvpn()
			self.openvpn(server)
		self.UPDATE_MENUBAR = True
		

	def inThread_timer_ovpn_ping(self):
		if self.timer_ovpn_ping_running == False:
			self.debug(text="def inThread_timer_ovpn_ping")
			self.timer_ovpn_ping_running = True
		if self.STATE_OVPN == True:
			
			if self.OS == "win32": 
				ovpn_ping_cmd = "ping.exe -n 1 172.16.32.1"
				PING_PROC = False
				#PING_PROC = subprocess.Popen("%s" % (ovpn_ping_cmd),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				try: PING_PROC = subprocess.check_output("%s" % (ovpn_ping_cmd),shell=True)
				except:	pass
					
				try: OVPN_PING_out = PING_PROC.split('\r\n')[2].split()[4].split('=')[1][:-2] 
				except: OVPN_PING_out = -2
				
				pingsum = 0
				if OVPN_PING_out > 0:
					self.OVPN_PING.append(OVPN_PING_out)
					self.OVPN_PING_LAST = OVPN_PING_out
				if len(self.OVPN_PING) > 90:
					self.OVPN_PING.pop(0)
				if len(self.OVPN_PING) > 0:
					for ping in self.OVPN_PING:
						pingsum += int(ping)
					self.OVPN_PING_STAT = pingsum/len(self.OVPN_PING)
				#self.debug(text="ping = %s\n#############\nList len=%s\n%s\npingstat=%s"%(OVPN_PING_out,len(self.OVPN_PING),self.OVPN_PING,self.OVPN_PING_STAT))
				#self.debug("timer ovpn ping running threads: %s" % (threading.active_count()))
				time.sleep(6)
				threading.Thread(target=self.inThread_timer_ovpn_ping).start()
				return True
		elif self.STATE_OVPN == False:
			self.debug("leaving timer_ovpn_ping")
			self.OVPN_PING_STAT = -1
			self.OVPN_PING = list()
			self.timer_ovpn_ping_running = False

		
	def inThread_spawn_openvpn_process(self):
		self.debug(text="def inThread_spawn_openvpn_process")
		self.ovpn_proc_retcode = False
		self.STATE_OVPN = True
		self.OVPN_CONNECTEDto = self.call_ovpn_srv
		self.win_firewall_start()
		self.win_netsh_set_dns_ovpn()
		self.win_firewall_modify_rule(option="add")	
		self.OVPN_PING_STAT = -2
		self.OVPN_PING_LAST = -1
		self.debug(text="def call_openvpn self.OVPN_CONNECTEDto = %s" %(self.OVPN_CONNECTEDto))
		self.ovpn_proc_retcode = subprocess.call("%s" % (self.ovpn_string),shell=True)
		self.OVPN_CONNECTEDtoIPbefore = self.OVPN_CONNECTEDtoIP
		self.win_firewall_modify_rule(option="delete")
		self.STATE_OVPN = False
		self.OVPN_CONNECTEDto = False
		self.OVPN_CONNECTEDtoIP = False
		self.OVPN_THREADID = False
		self.OVPN_PING_STAT = -1
		self.debug(text="def call_openvpn self.ovpn_proc_retcode = %s" %(self.ovpn_proc_retcode))
		if self.OVPN_AUTO_RECONNECT == True:
			self.debug(text="def inThread_spawn_openvpn_process: auto-reconnect %s" %(self.call_ovpn_srv))
			self.OVPN_RECONNECT_NOW = True

	def add_ovpn_routes(self):
		pass
		
	def read_gateway_from_routes(self):
		self.debug(text="def read_ovpn_routes:")
		string = "route.exe print"
		self.OVPN_READ_ROUTES = subprocess.check_output("%s" % (string),shell=True)
		#self.debug(text="self.OVPN_READ_ROUTES = %s"%(self.OVPN_READ_ROUTES))
		split = self.OVPN_READ_ROUTES.split('\r\n')
		#self.debug(text="split=%s"%(split))
		for line in split:
			#self.debug(text="%s"%(line))
			if "%s"%(self.OVPN_CONNECTEDtoIPbefore) in line:
				#self.debug(text="def read_ovpn_routes: %s"%(line))
				self.GATEWAY_LOCAL = line.split()[2]
				self.debug(text="self.GATEWAY_LOCAL: %s"%(self.GATEWAY_LOCAL))
					
	def del_ovpn_routes(self):
		if not self.OVPN_CONNECTEDtoIPbefore == False:
			self.read_gateway_from_routes()
			if not self.GATEWAY_LOCAL == False:
				self.debug(text="def del_ovpn_routes")
				string1 = "route.exe DELETE %s MASK 255.255.255.255 %s" % (self.OVPN_CONNECTEDtoIPbefore,self.GATEWAY_LOCAL)
				string2 = "route.exe DELETE 0.0.0.0 MASK 128.0.0.0 172.16.32.1"
				string3 = "route.exe DELETE 128.0.0.0 MASK 128.0.0.0 172.16.32.1"
				try: 
					self.OVPN_DEL_ROUTES1 = subprocess.check_output("%s" % (string1),shell=True)
					self.OVPN_DEL_ROUTES2 = subprocess.check_output("%s" % (string2),shell=True)
					self.OVPN_DEL_ROUTES3 = subprocess.check_output("%s" % (string3),shell=True)
					#self.debug(text="self.OVPN_DEL_ROUTES: %s, %s, %s"%(self.OVPN_DEL_ROUTES1,self.OVPN_DEL_ROUTES2,self.OVPN_DEL_ROUTES3))
				except:
					self.debug(text="def del_ovpn_routes: failed")
					pass
			self.OVPN_CONNECTEDtoIPbefore = False
			self.GATEWAY_LOCAL = False
			

		
	def inThread_timer_openvpn_reconnect(self):
		#self.debug("def inThread_timer_openvpn_reconnect")
		time.sleep(3)		
		if self.OVPN_RECONNECT_NOW == True and self.OVPN_AUTO_RECONNECT == True and self.STATE_OVPN == False:
			self.openvpn(self.call_ovpn_srv)
			text = "oVPN process crashed and restarted."
			self.debug(text=text)
			return False
		elif self.STATE_OVPN == True:
			#self.debug(text="Watchdog: oVPN is running to %s %s" %(self.OVPN_CONNECTEDto,self.OVPN_CONNECTEDtoIP))
			if self.timer_ovpn_ping_running == False: 
				self.debug("def inThread_timer_openvpn_reconnect starting ping timer")
				threading.Thread(target=self.inThread_timer_ovpn_ping).start()
			else:
				#self.debug("def inThread_timer_openvpn_reconnect: timer_ovpn_ping is running")
				pass
			threading.Thread(target=self.inThread_timer_openvpn_reconnect).start()
			time.sleep(3)
			return True
			
	def kill_openvpn(self):		
		self.OVPN_AUTO_RECONNECT = False
		#self.OVPN_RECONNECT_NOW = False
		self.debug(text="def kill_openvpn")	
		string1 = "taskkill /im openvpn.exe"
		string2 = "taskkill /im openvpn.exe /f"
		try: 
			self.OVPN_KILL1 = subprocess.check_output("%s" % (string1),shell=True)
		except:
			try:
				self.OVPN_KILL2 = subprocess.check_output("%s" % (string2),shell=True)
			except:
				pass
		self.UPDATE_MENUBAR = True
		self.del_ovpn_routes()

	def win_netsh_set_dns_down(self):
		d0wns_dns = "178.32.122.65 37.187.0.40 128.199.248.105 95.85.9.86 31.220.27.46 108.61.210.58 178.17.170.67 46.151.208.154 91.214.71.181 217.12.210.54 217.12.203.133"
		for dns in d0wns_dns.split():
			pass
		
		
		
	def win_netsh_set_dns_ovpn(self):
		self.debug(text="def win_netsh_set_dns_ovpn:")
		string1 = "netsh interface ip set dnsservers \"%s\" static 172.16.32.1 primary" % (self.WIN_EXT_DEVICE)
		try: 
			read1 = subprocess.check_output("%s" % (string1),shell=True)
			#read2 = subprocess.check_output("%s" % (string2),shell=True)
			self.debug(text="read1:\n%s"%(read1))
		except:
			self.debug(text="def win_netsh_set_dns_ovpn: setting dns failed: string =\n%s"%(string1))
			
		
	def win_netsh_restore_dns_dhcp(self):
		os.system('netsh interface ip set dnsservers "%" dhcp'%(self.WIN_EXT_DEVICE))
		
	def win_netsh_restore_dns_from_backup(self):
		string = 'netsh interface ip set dnsservers "%s" static %s primary no'%(self.WIN_EXT_DEVICE,self.GATEWAY_DNS)
		read = False
		try: 
			read = subprocess.check_output("%s" % (string),shell=True)
		except:
			pass
		if not read == False:
			self.msgwarn(text="Primary DNS Server restored to: %s"%(self.GATEWAY_DNS))
		else:
			self.msgwarn(text="Error: Restoring your DNS Server to %s failed."%(self.GATEWAY_DNS))
		self.debug(text="def win_netsh_restore_dns_from_backup: %s"%(read))

	def win_netsh_read_dns_to_backup(self):
		string = "netsh interface ipv4 show dns"
		read = subprocess.check_output("%s" % (string),shell=True)
		read = read.strip().decode('utf-8','ignore')
		search = '"%s"' % (self.WIN_EXT_DEVICE)
		list = read.strip(' ').split('\r\n')
		i=0
		m=0
		t=0
		for line in list:
			#self.debug(text=line)
			if search in line:
				self.debug(text=line)
				self.debug(text="%s"%(i))
				m=i+1
			if i == m:
				if "DNS" in line:
					dns = line.strip().split(":")[1].lstrip()
					self.debug(text=line)
					self.debug(text=dns)
					check = dns.split(".")
					for n in check:
						x = int(n)
						if x >= 0 and x <= 255 and t <= 4:
							t+=1
						else: 
							t = 0
							break
			i+=1
		if t == 4: self.GATEWAY_DNS = dns
		else: self.GATEWAY_DNS = self.GATEWAY_LOCAL
		self.debug(text="self.GATEWAY_DNS = %s"%(self.GATEWAY_DNS))
			

	def win_netsh_show_interfaces(self):
		os.system('netsh interface ip show interfaces')

	def win_netsh_show_dnsservers(self):
		os.system('netsh interface ip show dnsservers')	
		
	def win_detect_openvpn(self):
		pass

	def win_install_tap_adapter(self):
		#C:\Program Files\TAP-Windows\bin\tapinstall.exe find *TAP
		pass
		
	def win_get_interfaces(self):
		
		self.debug(text="def win_get_interfaces")
		wmi=win32com.client.GetObject('winmgmts:')
		adapters=wmi.InstancesOf('win32_networkadapter')
		self.INTERFACES = list()
		for adapter in adapters:
			for p in adapter.Properties_:
				if p.Name == "NetConnectionID" and not p.Value == None:
					INTERFACE=p.Value
					string = "%s"%(INTERFACE)
					#self.debug(text=string)
					self.INTERFACES.append(string)
		#self.debug(text="%s"%(self.INTERFACES))			
		if len(self.INTERFACES)	< 2:
			self.errorquit(text="Could not read your Network Interfaces!")
		
		#try: 
		string = "openvpn.exe --show-adapters"
		ADAPTERS = subprocess.check_output("%s" % (string),shell=True)
		ADAPTERS = ADAPTERS.split('\r\n')
		self.debug(text="TAP ADAPTER = %s"%(ADAPTERS))
		for line in ADAPTERS:
			#self.debug(text="checking line = %s"%(line))
			for INTERFACE in self.INTERFACES:
				#self.debug(text="is IF %s listed as TAP?"%(INTERFACE))
				if line.startswith("'%s'"%(INTERFACE)):
					self.debug(text=INTERFACE+" is TAP ADAPTER")
					self.WIN_TAP_DEVICE = INTERFACE
					break
				elif line.startswith("Available TAP-WIN32 adapters"):
					#self.debug(text="ignoring tap line")
					pass
				elif len(line) < 16:
					#self.debug(text="ignoring line < 16")
					pass
				else:
					#self.debug(text="ignoring else")
					pass
					
		if self.WIN_TAP_DEVICE == False:
			self.errorquit(text="No openVPN TAP-Adapter found!")
		else:
			self.INTERFACES.remove(self.WIN_TAP_DEVICE)
			self.debug(text="remaining INTERFACES = %s"%(self.INTERFACES))
			if len(self.INTERFACES) > 1:
				self.msgwarn(text="Multiple Network Adapters found! Please select your External/Internet Network Adapter!")
				for INTERFACE in self.INTERFACES:					
					if tkMessageBox.askyesno("Choose your Externel/Internet Network Adapter", "Is '%s' your External/Internet Network Adapter?"%(INTERFACE)):
						self.WIN_EXT_DEVICE = INTERFACE
						break
					else:
						pass
			elif len(self.INTERFACES) < 1:
				self.errorquit(text="No Network Adapter found!")
			else:
				self.WIN_EXT_DEVICE = self.INTERFACES[0]
				text = "External Interface = %s"%(self.WIN_EXT_DEVICE)
				#self.msgwarn(text=text)
				self.debug(text=text)
				
		self.win_netsh_read_dns_to_backup()

		
	def win_firewall_start(self):
		self.pfw_bak = "%s\pfw.%s.bak.wfw" % (self.pfw_dir,int(time.time()))
		self.pfw_log = "%s\pfw.%s.log" % (self.pfw_dir,int(time.time()))
		self.pfw_cmdlist = list()
		self.pfw_cmdlist.append("advfirewall export %s" % (self.pfw_bak))
		self.pfw_cmdlist.append("advfirewall reset")
		self.pfw_cmdlist.append("advfirewall set allprofiles state on")
		self.pfw_cmdlist.append("advfirewall set currentprofile logging filename \"%s\"" % (self.pfw_log))
		self.pfw_cmdlist.append("advfirewall set privateprofile firewallpolicy blockinbound,blockoutbound")
		self.pfw_cmdlist.append("advfirewall set publicprofile firewallpolicy blockinbound,allowoutbound")
		self.pfw_cmdlist.append("advfirewall set domainprofile firewallpolicy blockinbound,blockoutbound")
		self.win_join_netsh_cmd()
	
	def win_firewall_add_rule_to_vcp(self,option):
		self.debug(text="def win_firewall_add_rule_to_vcp:")
		self.pfw_cmdlist = list()
		url = "https://vcp.ovpn.to"
		ips = list()
		ips.append("178.17.170.116")
		ips.append("172.16.32.1")	
		port = 443
		protocol = "tcp"
		for ip in ips:
			rule_name = "Allow OUT to %s at %s to Port %s Protocol %s" % (url,ip,port,protocol)
			rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=private dir=out action=allow" % \
					(option,rule_name,ip,port,protocol)
			self.pfw_cmdlist.append(rule_string)
			
		self.win_join_netsh_cmd()	
		
	def win_firewall_allow_outbound(self):
		self.debug(text="def win_firewall_allow_outbound:")
		self.pfw_cmdlist = list()
		self.pfw_cmdlist.append("advfirewall set privateprofile firewallpolicy blockinbound,allowoutbound")
		#self.pfw_cmdlist.append('interface set interface "%s" DISABLED'%(self.WIN_EXT_DEVICE))	
		#self.pfw_cmdlist.append('interface set interface "%s" ENABLED'%(self.WIN_EXT_DEVICE))
		self.win_join_netsh_cmd()
		
	def win_firewall_modify_rule(self,option):
		self.pfw_cmdlist = list()
		if option == "add" or option == "delete":
			rule_name = "Allow OUT oVPN-IP %s to Port %s Protocol %s" % (self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol)
			rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=private dir=out action=allow" % (option,rule_name,self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol)
			self.debug(text="def pfw: %s"%(rule_string))
			self.pfw_cmdlist.append(rule_string)
			self.win_join_netsh_cmd()
			
	
	def win_join_netsh_cmd(self):
		self.pfw_cmd = "netsh.exe"
		for cmd in self.pfw_cmdlist:
			fullstring = "%s %s" % (self.pfw_cmd,cmd)			
			try: 
				response = subprocess.check_output("%s" % (fullstring),shell=True)
				self.debug(text="pfwOK: %s" % (fullstring))
			except:
				self.debug(text="pfwFAIL: %s" % (fullstring))

	def make_menubar(self):
		self.load_ovpn_server()
		#self.make_systray()
		if not self.menubar == False:
			self.menubar.destroy()
		
		menubar = Menu(self.root)
		self.root.config(menu=menubar)

		ovpnMenu = Menu(menubar)     
		submenu = Menu(ovpnMenu)
		for menuserver in self.OVPN_SERVER:
			self.countrycode = menuserver[:2]
			servershort = menuserver[:3]
			if self.OVPN_CONNECTEDto == menuserver:
				servershort = "[ "+servershort+" ]"
				submenu.add_command(label=servershort)
			else:
				servershort = menuserver[:3]
				submenu.add_command(label=servershort,command=lambda menuserver=menuserver: self.openvpn(menuserver))
		ovpnMenu.add_cascade(label='Server', menu=submenu, underline=0)

		ovpnMenu.add_separator()

		if self.STATE_OVPN == False and not self.OVPN_FAV_SERVER == False:
			ovpnMenu.add_command(label="Connect",command=self.openvpn)
		elif self.STATE_OVPN == True:
			ovpnMenu.add_command(label="Disconnect",command=self.kill_openvpn)		
		menubar.add_cascade(label="oVPN", underline=0, menu=ovpnMenu)
		
		#self.make_statusbar()
		
	
	def make_statusbar(self):
		#if not self.statusbar == False:
		#	self.statusframe.destroy()
		if self.SMALL_WINDOW == False:
			self.statusbar = Label(self, bd=1, relief=SUNKEN, anchor=W, textvariable=self.statusbar_text,font=('Courier','12','normal')).pack(side=BOTTOM, fill=X)		
		#if self.SMALL_WINDOW == True:
		#	self.statusbar = Label(self, bd=1, relief=SUNKEN, anchor=W, textvariable=self.statusbar_text,font=('Courier','12','normal')).pack(side=BOTTOM, fill=X)
			
		#self.statusbar_text.set("Statusbar-Text")
		if self.timer_statusbar_running == False: 
			self.timer_statusbar()
		
	def timer_statusbar(self):
		#if self.isLOGGEDin: 
		#return True
		self.timer_statusbar_running = True
		text = False
		
		if self.isLOGGEDin == True:	
			if self.STATE_OVPN == False:
				text = "oVPN disconnected!"
			elif self.STATE_OVPN == True:		

				if self.OVPN_PING_STAT == -1:
					text = "oVPN is connecting to %s"%(self.OVPN_CONNECTEDto)
					self.SWITCH_SMALL_WINDOW = True
					
				elif self.OVPN_PING_STAT == -2:
					text = "oVPN is testing connection to %s" % (self.OVPN_CONNECTEDto)
					self.OVPN_isTESTING = True
					self.SWITCH_SMALL_WINDOW = True					
				else:
					if self.OVPN_isTESTING == True:
						self.OVPN_PING = list()
						self.OVPN_PING_STAT = self.OVPN_PING_LAST
						self.OVPN_isTESTING = False
					text = "oVPN is connected to %s (%s/%s ms)"%(self.OVPN_CONNECTEDto,self.OVPN_PING_LAST,self.OVPN_PING_STAT)
					self.SWITCH_SMALL_WINDOW = True	

		else:
			text = "Please enter your Passphrase!"
			
		if self.SWITCH_SMALL_WINDOW == True and self.SMALL_WINDOW == False:
			self.screen_width = 480
			self.screen_height = 24
			self.root.geometry("%sx%s"%(self.screen_width,self.screen_height))
			self.removethis()
			self.SMALL_WINDOW = True
		#elif self.SWITCH_FULL_WINDOW == True and self.SMALL_WINDOW == True:
		#	self.screen_width = 480
		#	self.screen_height = 320
		#	self.root.geometry("%sx%s"%(self.screen_width,self.screen_height))
		#	self.removethis()
		#	self.SMALL_WINDOW = False			
			
		if not self.statustext_from_before == text:
			self.statusbar_text.set(text)
			self.statustext_from_before = text
			
		if self.isLOGGEDin and self.UPDATE_MENUBAR: 
			self.make_menubar()
			self.UPDATE_MENUBAR = False
			
		self.root.after(1000,self.timer_statusbar)
		return True
		
	def on_closing(self,root):
		if self.STATE_OVPN == True:
			tkMessageBox.showwarning("Warning", "Quit blocked while oVPN is connected.\nDisconnect oVPN from %s first."%(self.OVPN_CONNECTEDto[:3]))
			return False
		elif tkMessageBox.askokcancel("Quit", "Quit oVPN Client?"):
			self.win_netsh_restore_dns_from_backup()
			if tkMessageBox.askokcancel("Disable Firewall Protection?", "Unload Firewall and allow OUT to Internet again?"):
				self.win_firewall_allow_outbound()
				self.msgwarn(text="Firewall rules unloaded.\nSettings restored.")
			else:
				self.win_firewall_start()
				self.msgwarn(text="Firewall enabled!\nInternet is blocked!")
			root.destroy()
			sys.exit()	
"""		
	#from infi.systray import SysTrayIcon
	def make_systray(self):
		if self.SYSTRAYon == True: self.systray.destroy()
		self.systray = False
		traymenu_options = (
						("...", None, systray_say_hello),
						#("Quit", "ico\earth.ico", lambda systray=systray,root=root: self.systray_quit(systray,root))
						#("Quit", "ico\earth.ico", lambda systray=systray: self.systray_quit(systray))
						("Quit", "ico\earth.ico", self.systray_quit)
					)
		self.systray = SysTrayIcon("ico\earth.ico", "oVPN.to Client", traymenu_options)
		self.systray.start()
		self.SYSTRAYon = True

	def systray_quit(self,systray):
		if self.STATE_OVPN == False:
			print("quit systray")
			self.root.quit()
			#self.root.destroy()
			systray.shutdown()
		else:
			if tkMessageBox.askokcancel("Quit", "You can not quit while openVPN is running!"):			
				return True

"""		
		
"""
		
	def make_menubar(self):	
		if not self.menubar == False:
			self.menubar.destroy()
		self.menubar = Menu(self.parent)

		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="Menu", menu=menu)
		menu.add_command(label="Settings")
		menu.add_command(label="Logout",command=self.dologout)		
		menu.add_command(label="Quit",command=menu.quit)

		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="oVPN", menu=menu)
		menu.add_command(label="Server")
		
		if self.STATE_OVPN == False:
			menu.add_command(label="Connect",command=self.openvpn)
		elif self.STATE_OVPN == True:
			menu.add_command(label="Disconnect",command=self.openvpn)
			
		menu.add_command(label="Update")
		
		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="3proxy", menu=menu)
		menu.add_command(label="Config")
		
		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="Stunnel", menu=menu)
		menu.add_command(label="Config")		
		
		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="?", menu=menu)
		menu.add_command(label="Info")		

		#try:
		self.parent.config(menu=self.menubar)
		#except AttributeError:
			# master is a toplevel window (Python 1.4/Tkinter 1.63)
		#	self.master.tk.call(master, "config", "-menu", self.menubar)
		return True
		#self.canvas = Canvas(self, bg="#1a1a1a", width=self.screen_width, height=self.screen_height,bd=0, highlightthickness=0)
		#self.canvas.pack()

"""		


		
#	def menu_info(self):
#		pass





def systray_say_hello(systray):
	print "Hello, World!"
	


def main():
	
	root = Tk()
	root.screen_width = 320
	root.screen_height = 240	
	root.geometry("%sx%s"%(root.screen_width,root.screen_height))
	root.resizable(0,0)
	root.attributes("-toolwindow", False)
	root.title("oVPN.to v"+BUILT+STATE)	
	app = AppUI(root).pack()	
	root.mainloop()
	print("Ending")
	sys.exit()
	
if __name__=='__main__':
    main()
