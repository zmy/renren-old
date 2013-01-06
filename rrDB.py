import mysql.connector


class RenrenDb:
	renren_relation='t_renren_relation'
	temp_relation='temp_relation'
	renren_profile='t_renren_profile'
	temp_profile='temp_profile'
	
	def __init__(self):
		pass
	
	def getConn(self, db='renren'):
		return mysql.connector.connect(host='127.0.0.1', port=3306, user='renren', passwd='renren', db=db, charset='utf8')
	
	def execute(self, sql=None):
		conn=self.getConn()
		cur=conn.cursor()
		cur.execute(sql)
		conn.commit()
		cur.close()
		conn.close()
	
	def deleteRelation(self, col, renrenId, table='net_renren'):
		conn=self.getConn()
		cur=conn.cursor()
		n=cur.execute("delete from FROM {} where renrenId{}={}".format(table,str(col),renrenId))
		cur.commit()
		cur.close()
		conn.close()
		return n 
	
	def getRenrenId(self, col, renrenId):
		conn = self.getConn()
		cur = conn.cursor()
		target = str(col)
		where = str(col%2+1)
		res = set()
		for table in [self.renren_relation, self.temp_relation]:
			cur.execute("SELECT renrenId{} FROM {} where renrenId{}={}".format(target, table, where, renrenId))
			for item in cur.fetchall():
				res.add(item[0])
		cur.close()
		conn.close()
		return list(res)
	
	def getSearched(self):
		conn=self.getConn()
		cur=conn.cursor()
		res=set()
		table=self.renren_relation
		cur.execute("SELECT renrenId1 FROM {} group by renrenId1".format(table))
		for item in cur.fetchall():
			res.add(item[0])
		cur.close()
		conn.close()
		return list(res)
	
	def getName(self,renrenId):
		conn=self.getConn()
		cur=conn.cursor()

		name=''
		for table in [self.renren_profile,self.temp_profile]:
			n=cur.execute('select name from {} where renrenId={}'.format(table,renrenId))
			if n>0:
				name=cur.fetchall()[0][0]
		cur.close()
		conn.close()
		return name
	
	def getNames(self,renrenIds):
		conn=self.getConn()
		cur=conn.cursor()

		names=dict()
		for table in [self.renren_profile,self.temp_profile]:
			cur.execute('select renrenId,name from {} where renrenId in ({})'.format(table,str(renrenIds).strip('[]{}')))
			for item in cur.fetchall():
				names[item[0]]=item[1]
		cur.close()
		conn.close()
		return names

	def getRelations(self,ids):
		conn=self.getConn()
		cur=conn.cursor()
		ids=set(ids)
		sql2="select renrenId1,renrenId2 from t_renren_relation where renrenId1 in ({}) and renrenId2 in({})"
		cur.execute(sql2.format(str(ids).strip('{}'),str(ids).strip('[]{}')))
		edge=cur.fetchall()
		cur.close()
		conn.close()
		return edge
