import re
import time
import logging
import os
from html.parser import HTMLParser
from RRDB import RenrenDb
from RRBrowser import RenrenBrowser


class InfoParser(HTMLParser):
	data = ''
	def handle_starttag(self, tag, attrs):
		if tag=='br':
			self.data = self.data+'\n'
	def handle_endtag(self, tag):
		pass
	def handle_data(self, data):
		self.data = self.data+' '+data.strip()

class RenrenParser:
	def __init__(self, browser, recorder=None):
		#self.log=self.initLogger()
		self.browser = browser
		self.recorder = recorder

	def friendPage(self, filename):
		#open and read 
		f = open(filename, 'r', encoding='utf-8')
		htmlStr = str(f.readlines())
		#parser all id/name pairs from profile urls
		urlPtn = r'<a\shref=\"http://www.renren.com/profile.do\?id=\d+\">[^<]+<\/a>'
		profileUrls = set(re.compile(urlPtn).findall(htmlStr))
		pairs = set()
		for item in profileUrls:
			renrenId = re.compile(r'=\d+\"').findall(item)[0].strip('="')
			name = re.compile(r'>[^<]+<').findall(item)[0].strip('<>')
			pairs.add((renrenId, name))
		return pairs

	def friends(self):
		cnt = 0
		for renrenId in os.listdir(self.browser.getPWDFriendPage()):
			print("parsing {}: {}".format(cnt, renrenId));
			cnt = cnt+1
			pwd = self.browser.getPWDFriendPage()+'/'+renrenId+'/'
			#parsered pages and assign to flist 
			pages = os.listdir(pwd)
			flist = set()
			#files that parsering, store for rename later
			parsering = []
			for page in pages:
				if page.find('parsered_')==0:
					#file parserd, continue
					continue
				else:
					parsering.append(page)
					flist = flist| self.friendPage(pwd+page)

			if len(pages)==0:
				#if empty, mkdir flag file and assign 1 to flist
				open(pwd+'parsered_{}_noPermision.html'.format(renrenId)).close()
				#os.mknod(pwd+'parsered_{}_noPermision.html'.format(renrenId))
				flist = {('1', 'unavailable')}
			elif len(flist)==0:
				#all files parser, continue
				continue
			#else:
			if self.recorder==None:
				#insert into table, pairs>temp_profile, relation>temp_relation
				db = RenrenDb()
				sqlProfile = 'insert into {} (renrenId,name) values {}'.format(db.temp_profile, str(flist).strip('{}'))
				relation = ''
				for pair in flist:
					relation = relation+'({},{}),'.format(renrenId, str(pair[0]))
				sqlRelation = 'insert into {} (renrenId1,renrenId2) values {}'.format(db.temp_relation, relation.strip(','))
				conn = db.getConn()
				cur = conn.cursor()
				m = cur.execute(sqlProfile)
				n = cur.execute(sqlRelation)
				#self.log.info('{} profiles and {} relations of {} inserted into db'.format(m,n,renrenId))
				conn.commit()
				cur.close()
				conn.close()
			else:
				self.recorder.addNames(flist)
				friends = set()
				for pair in flist:
					friends = friends | {str(pair[0])}
				self.recorder.addFriends(renrenId, friends)
			
			#rename parsering files
			for old in parsering:
				new = 'parsered_'+old
				os.rename(pwd+old, pwd+new)

	def profiles(self):
		for filename in os.listdir(self.browser.getPWDProfilePage()):
			rrID = self.browser.extractProfileID(filename)
			#print(filename, rrID)
			f = open(self.browser.getPWDProfilePage()+'/'+filename, 'r', encoding='utf-8')
			htmlStr = str(f.read())
			f.close()
			htmlStr = re.sub(r'<script>.*?</script>', '', htmlStr, 0, re.DOTALL)
			htmlStr = re.sub(r'</dt>\s*<dd>', '</dt><dd>', htmlStr)
			htmlStr = re.sub(r'</dt>(?!<dd>)', '</dt><dd></dd>', htmlStr)
			profile = {}
			infos = re.findall(r'<dt>(.+?)</dt>\s*<dd>(.*?)</dd>', htmlStr, re.DOTALL)
			company = ''
			for info in infos:
				key = re.sub(r'[:\s]', '', info[0]).strip()
				parser = InfoParser()
				parser.feed(info[1])
				parser.close()
				value = parser.data.strip()
				if key.encode('utf-8')=='公司'.encode('utf-8'):
					company = value
				else:
					if key.encode('utf-8')=='时间'.encode('utf-8'):
						if '工作信息' in profile:
							profile['工作信息'].append({'公司':company, '时间':value})
						else:
							profile['工作信息'] = [{'公司':company, '时间':value}]
					else:
						profile[key] = value
			#print(profile)
			self.recorder.setProfile(rrID, profile)

	def statusPage(self,filename,mainId=None):
		#open and read 
		f=open(filename, 'r', encoding='utf-8')
		htmlStr=str(f.readlines())
		f.close()

		#parser all id/name pairs from profile urls
		#itemPtn=r'<a\shref=\"http://www.renren.com/profile.do\?id=\d+\">[^<]+<\/a>'
		itemPtn=r'id="status-.+?ilike_icon'
		itemList=re.compile(itemPtn).findall(htmlStr)
		status=''
		for item in itemList:
			#statusId, content, duration, replycount
			statusIdPtn = r'"status-\d+">'
			statusId = (re.compile(statusIdPtn)).findall(item)[0].replace('status','').strip('-=<>"')

			contentPtn=r'<h3>.+</h3>'
			contentDraft=re.compile(contentPtn).findall(item)[0]
			#simplify content
			#no @ href
			atHrefPtn=r"<a\s+href=\\'http://www.renren.com/g/\d+.+?>"
			hrefs=re.compile(atHrefPtn).findall(contentDraft)
			for href in hrefs:
				#print(href)
				renrenId=re.compile(r'\d+').findall(href)[0]
				contentDraft=contentDraft.replace(href,'(renrenId={})'.format(renrenId))
			#no normal profile href
			profileHrefPtn=r'<a\shref="http://www.renren.com/profile.do\?id=.+?>'
			profile=re.compile(profileHrefPtn).findall(contentDraft)
			for href in profile:
				#print(href)
				renrenId=re.compile(r'\d+').findall(href)[0]
				contentDraft=contentDraft.replace(href,'(renrenId={})'.format(renrenId))
			#no public profile href
			profileHrefPtn=r'<a\shref="http://page.renren.com/.+?>'
			profile=re.compile(profileHrefPtn).findall(contentDraft)
			for href in profile:
				#print(href)
				renrenId=re.compile(r'\d+').findall(href)[0]
				contentDraft=contentDraft.replace(href,'(renrenId={})'.format(renrenId))
			#no alt img
			imgPtn=r"<img\s+src=.+?alt=\\'.+?\\'.+?/>"
			imgs=re.compile(imgPtn).findall(contentDraft)
			for img in imgs:
				#print(img)
				imgDesc=re.compile(r"\\'.+?\\").findall(img)[1].strip("=\\'")
				contentDraft=contentDraft.replace(img,'(img={})'.format(imgDesc))
			#no img in name
			nameImgPtn=r"<img class=.+?alt=.+?http://a.xnimg.cn/.+?/>"
			nameImg=re.compile(nameImgPtn).findall(contentDraft)
			for img in nameImg:
				#print(img)
				contentDraft=contentDraft.replace(img,'')
				#print(img,imgDesc)
			content = (re.compile(r'>:.+</')).findall(contentDraft)[0].replace('</a>','').replace('\\n','').strip("<>/:',\\ ")

			timePtn=r'"duration">.+?\\n'
			time=re.compile(timePtn).findall(item)[0]
			timestamp=re.compile(r'>.+\\n').findall(time)[0].strip('=<>"\\n')

			replyCountPtn=r'replyCount\d+">\(\d+\)'
			replyCountDraft=re.compile(replyCountPtn).findall(item)
			if len(replyCountDraft)<1:
				replyCount='0'
			else:
				replyCount=re.compile(r'\(\d+\)').findall(replyCountDraft[0])[0].strip('()')
			#status.append({'statusId':statusId,'timestamp':timestamp,'replyCount':replyCount,'content':content})
			#status={'statusId':statusId,'timestamp':timestamp,'replyCount':replyCount}
			status=status+",('{}','{}','{}','{}','{}')".format(statusId,mainId,content.replace("'",'"'),replyCount,timestamp)
		#TODO: add none sql code
		sql="INSERT INTO temp_status(statusId,renrenId,content,replyCount,timestamp) values {}".format(status.strip(','))
		#print(sql)
		db=RenrenDb()
		conn=db.getConn()
		cur=conn.cursor()
		try:
			n=cur.execute(sql)
			conn.commit()
		except Exception:
			print('error. filename={}'.format(filename))
			print(sql)
			n=0
		cur.close()
		conn.close()
		return n

	def status(self,pwdStatus):
		renrenIds=os.listdir(pwdStatus)
		for i,renrenId in zip(range(0,len(renrenIds)),renrenIds):
			pwd=pwdStatus+'/'+renrenId+'/'
			print('{}/{} parsering, renrenId={}'.format(i,len(renrenIds),renrenId))

			for page in os.listdir(pwd):
				try:
					self.statusPage(pwd+page,renrenId)
				except Exception:
					print('error. filename={}'.format(page))

	def initLogger(self):
		#init pwd to write
		pwd=RenrenBrowser.pwdLog
		if os.path.exists(pwd)==False:
			os.makedirs(pwd)	
		#init logfile name
		date=time.strftime("%Y%m%d", time.localtime())
		logfile=pwd+'/'+"renrenParser_{}.log".format(date)
		#init logger
		logger=logging.getLogger()
		hdlr=logging.FileHandler(logfile)
		formatter=logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr)
		logger.setLevel(20)#info
		return logger
	
	def setLogLevel(self,level):
		oldLevel=self.log.getEffectiveLevel()
		self.log.setLevel(level)#info 20, debug 10
		self.log.info("log level chanaged, from {} to {}".format(oldLevel,level))
