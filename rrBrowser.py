import urllib.request as http #instead of urllib2
import urllib.parse #urlencode is used
import http.cookiejar as cookie
import re
import time
import logging
import os


# get friendList, profile, status
class RenrenBrowser:
	def __init__(self, user, passwd, path='.'):
		self.pwdRoot = path+'/'+user+'/renrenData'
		self.pwdLog = self.pwdRoot+'/spider_log'
		self.log = self.initLogger()
		self.user = user
		self.passwd = passwd

	def getPWDRoot(self):
		return self.pwdRoot

	def getPWDFriendPage(self):
		return self.pwdRoot+'/friendList'

	def getPWDProfilePage(self):
		return self.pwdRoot+'/profile'

	# renren has the maximum friend number of 7000
	def grabFriendListPages(self, rrID, pagelimit=400):
		self.iterPages('friendList', rrID, pagelimit)

	def grabStatusPages(self, rrID=None, pagelimit=100):
		self.iterPages('status', rrID, pagelimit)

	urlTemplate = {
		'status':'http://status.renren.com/status?curpage={}&id={}&__view=async-html',
		'friendList':"http://friend.renren.com/GetFriendList.do?curpage={}&id={}",
		'profile':"http://www.renren.com/{}/profile?v=info_ajax"}
	itemPattern = {
		'status':'id="status-',
		'friendList':'class="info"'}
	filenameTemplate = '{}{}_{}.html' #pageStyle, renrenId, page

	def iterPages(self, pageStyle=None, rrID=None, pagelimit=100):
		pwd = self.pwdRoot+'/{}/{}'.format(pageStyle, rrID)

		#only useful page is written, no end+1 page, no permission denied page
		self.log.info("start to get {} page of {}".format(pageStyle, rrID))
		#init pwd to write
		if not os.path.exists(pwd):
			os.makedirs(pwd)
			self.log.debug("mkdir {}".format(pwd))

		#request pages which not exist locally
		for page in range(len(os.listdir(pwd)), pagelimit+1):
			if(page%50==0):
				self.log.info('processing {}, getting page{} of {}'.format(pageStyle, page, rrID))
			else:
				self.log.debug('processing {}, getting page{} of {}'.format(pageStyle, page, rrID))
			#send request and decode response
			#print(self.urlTmplt[pageStyle].format(page,rrID))
			rsp = self.opener.open(self.urlTemplate[pageStyle].format(page, rrID))
			self.log.debug("{} recieved , page={}, renrenID={}".format(pageStyle, page, rrID))
			htmlStr = rsp.read().decode('UTF-8', 'ignore')

			items = re.compile(self.itemPattern[pageStyle]).findall(htmlStr)
			if len(items) < 1:
				#end of friend list page or permision denied
				self.log.debug("all {} page of {} saved in {}".format(pageStyle, rrID, pwd))
				break
			else:
				f = open(pwd+'/'+self.filenameTemplate.format(pageStyle, rrID, page), 'w', encoding='utf-8')
				f.write(htmlStr)
				f.close()

	def grabProfilePage(self, rrID):
		#init pwd to write
		pwd = self.getPWDProfilePage()
		if not os.path.exists(pwd):
			os.makedirs(pwd)
			self.log.debug("mkdir {}".format(pwd))
		filenameTemplate = 'profile_{}.html'#id
		filename = pwd+'/'+filenameTemplate.format(rrID)
		if os.path.exists(filename):
			self.log.debug("skip profile, renrenID={}".format(rrID))
			return 'skipped'
		else:
			#sending request and decode response
			self.log.debug("requesting detail profile, renrenID={}".format(rrID))
			rsp = self.opener.open(self.urlTemplate['profile'].format(rrID))
			self.log.debug("detail profile recieved, renrenID={}".format(rrID))
			htmlStr = rsp.read().decode('UTF-8', 'ignore')
			#write to file
			f = open(filename, 'w', encoding='utf-8')
			f.write(htmlStr)
			f.close()
			self.log.debug("detail profile write to file, file={}".format(filename))
			return 'grabbed'

	def login(self):
		user = self.user;
		passwd = self.passwd
		login_page = "http://www.renren.com/PLogin.do"
		try:
			#construct http request
			cj = cookie.CookieJar();
			self.opener = http.build_opener(http.HTTPCookieProcessor(cj));
			self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0')];
			data = urllib.parse.urlencode({"email":user, "password":passwd})
			data = data.encode(encoding='UTF8');#encoding is needed in python3.2

			#send request and decode response
			rsp = self.opener.open(login_page,data)
			homePage = rsp.read().decode('UTF-8','ignore')

			#check whether login is successful. 
			#paser response to find titlePtn
			titlePtn=r'<title>\w+\s+-\s+.+</title>'
			title=re.compile(titlePtn).findall(homePage)
			namePtn=r'-\s+.+<'
			name=re.compile(namePtn).findall(title[0])[0].strip('-<')
			self.log.info("user login successfully,name={},email={}".format(name,user))
			#return renrenId if login successful.
			return '233330059'
		except Exception as e:
			self.log.error("user login failed, email={}, msg={}".format(user,str(e)))
			return '0'

	def initLogger(self):
		pwd = self.pwdLog
		#init pwd to write
		if os.path.exists(pwd)==False:
			os.makedirs(pwd)	
		#init logfile name
		date = time.strftime("%Y%m%d", time.localtime())
		logfile = pwd+'/'+"renrenBrowser_{}.log".format(date)
		#init logger
		logger = logging.getLogger()
		hdlr = logging.FileHandler(logfile)
		formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr)
		logger.setLevel(20)#info
		return logger

	def setLogLevel(self,level):
		oldLevel=self.log.getEffectiveLevel()
		self.log.setLevel(level) #info 20, debug 10
		self.log.info("log level chanaged, from {} to {}".format(oldLevel,level))
