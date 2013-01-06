renren grabber and analysis
======
Thanks for Jiekun Yang
at https://github.com/JackonYang/dataBang

Directly run rrGrabber.py under the current directory.

By default the grabber won't use SQL database,
it store things in memory and finally backup python ojects in .p files.
You can change where to save data in rrGrabber.py

When using database you have to config MySQL database manually:
In MySQL you should provide a schema with enough privilege (see rrDB.py, the getConn function).
And before you run the grabber you should add tables into the schema:
	t_renren_relation with columns renrenId1 and renrenId2
	temp_relation with columns renrenId1 and renrenId2
	t_renren_profile with columns renrenId and name
	temp_profile with columns renrenId and name

For details please contact zmy.