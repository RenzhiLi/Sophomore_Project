import firebase_admin as fba
from firebase_admin import firestore
from firebase_admin import auth
import datetime
import pytz
import hashlib
__accountname__=''
#init database
cred = fba.credentials.Certificate('./serviceaccountkey.json')
mainapp = fba.initialize_app(cred)
db = firestore.client()
task = db.collection(u'Task')
users=db.collection(u'User')
groups=db.collection(u'Group')

def md5(str):
	#used for passward varification
	hmd5 = hashlib.md5()
	hmd5.update(str.encode(encoding='utf-8'))
	return hmd5.hexdigest()

def task_add(Task_name,Time_due,Task_discr=None,groupid=None,Task_prior=1,progress=0,Task_leader=__accountname__,Task_parti=None,Time_accom=None,Time_Es=datetime.datetime.utcnow(),Is_accom=False,Has_subtask=False,maintask=None):
	# add a new task to database,could add a sub-task to one existing task
	# sample use: (return value is a doc instance)
	# a=task_add(u'tasknumber3',datetime.datetime(2018,10,22,22,22,0),u'discription3',[maintask='QmfuMOqiib23OOd9g8vy'])
	Time_due=Time_due+datetime.timedelta(hours=4)
	taskdict={
		u'Task_name': Task_name, u'Task_discr': Task_discr,
		u'Time_due': Time_due, u'Task_prior': Task_prior,
		u'Task_leader': Task_leader, u'Task_parti': Task_parti,
		u'Time_accom': Time_accom, u'Time_Es': Time_Es,
		u'Is_accom': Is_accom, u'Has_subtask': Has_subtask,
		u'group':groupid, u'progress':progress
	}
	if maintask==None:
		return task.add(taskdict)[1]
	elif type(maintask)==str:
		target=task.document(maintask)
		task_update(target,u'Has_subtask',True)
		return target.collection(u'Subtasks').add(taskdict)[1]
	else:
		task_update(maintask, u'Has_subtask', True)
		return maintask.collection(u'Subtasks').add(taskdict)[1]

def task_update(target,tagname,tagvalue):
	#update one attr to the database
	#sample use: task_update(\doc instance(this could also be an id),u'Task_discr','this is a discription')
	if type(target)==str:
		tar=task.document(target)
		tar.update({tagname:tagvalue})
	else:
		target.update({tagname:tagvalue})

def time_remain(target):
	# return remaining time for one task
	#print(time_remain('XJ8j7PSM5Aap8cnl845W'))
	if type(target)==str:
		tar = task.document(target)
		result=tar.get().to_dict()['Time_due'] - datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
		return result
	else:
		result = target.get().to_dict()['Time_due'] - datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
		return result

def user_add(email,pwd,username):
	#add a new user to database system, passward encrypted.
	#will reject creation if username already exict(return a string to indicate that)
	if len(list(users.where(u'User_email','==',email).get()))>=1:
		raise EmailAlreadyExist('Failed: Email already exists')
	user_dict={u'User_email':email,u'User_pwd':md5(pwd),u'User_name':username,u'Last_login':None,u'Is_login':False}
	return users.add(user_dict)[1]

def user_login(email,pwd):
	#user login system, return a referance of one user if success
	#global var account name will be reset to this user id
	if len(list(users.where(u'User_email','==',email).get()))==0:
		raise EmailIncorrect('Failed: Email incorrect')
	user=list(users.where(u'User_email', '==', email).get())[0]
	if user.to_dict()['User_pwd']!= md5(pwd):
		raise PwdIncorrect('Failed: Password incorrect')
	global __accountname__
	__accountname__=user.id
	user=users.document(__accountname__)
	user.update({'Is_login':True,'Last_login':datetime.datetime.utcnow()})
	return user

def user_logout():
	#logout the current logged in account
	global __accountname__
	if __accountname__=='':
		return False
	user=users.document(__accountname__)
	user.update({u'Is_login':False})
	return True

def user_get(tag):
	# obtain one user object indicates by email or usernane
	if len(list(users.where(u'User_email', '==', tag).get())) != 0:
		return users.document(list(users.where(u'User_email', '==', tag).get())[0].id)
	elif len(list(users.where(u'User_name', '==', tag).get())) != 0:
		return users.document(list(users.where(u'User_name', '==', tag).get())[0].id)
	return None

def user_update(attr,newval,oldval=None):
	# modify the logged account, just provide attr name and the new value
	# pass old value if the changing attr is pwd
	user=users.document(__accountname__)
	if oldval is None:
		user.update({attr:newval})
	elif user.to_dict()['User_pwd']!= md5(oldval):
		raise PwdIncorrect('Failed: Password incorrect')
	else:
		user.update({attr:md5(newval)})

def group_add(name=None,leader=None,party=None):
	#add a new group to the database
	tardict = {u'Name': name,u'Leader':leader}
	if name==None and __accountname__!='':
		tardict['Name']=users.document(__accountname__).get().to_dict()['User_name']+"'s project"
	if leader==None and __accountname__!='':
		tardict['Leader']=__accountname__
	tardict['Participants'] = {__accountname__:True}
	if party!=None:
		for i in party:
			tardict['Participants'][user_get(i).id]=True
	return groups.add(tardict)[1]

def group_update(group,field_name,filed_value):
	if type(group)==str:
		tar=groups.document(group)
		tar.update({field_name:filed_value})
	else:
		group.update({field_name:filed_value})

def group_get(tag):
	#obtain a group instance by name
	#should have a more powerful verion in the frontend that could get groups by any participants
	if len(list(groups.where(u'Name', '==', tag).get())) != 0:
		return groups.document(list(groups.where(u'Name', '==', tag).get())[0].id)

def group_member_add(group,user_id):
	#group para could accept id/instance, must past a user_id
	if type(group) == str:
		thisgroup=groups.document(group)
		thisgroup.update({'Participants.'+user_id:True})
	else:
		group.update({'Participants.'+user_id:True})

def group_member_del(group,user_id):
	#group para could accept id/instance, must past a user_id
	if type(group) == str:
		thisgroup=groups.document(group)
		thisgroup.update({'Participants.'+user_id:firestore.DELETE_FIELD})
	else:
		group.update({'Participants.'+user_id:firestore.DELETE_FIELD})






'''
#This is a sample user system(login method not found yet)
sam_user=auth.get_user_by_email("renzhili@oakland.edu")
for i in auth.list_users().iterate_all():
	print(i.email)
	print(i.password_hash)
	print(i.password_salt)
print(sam_user.uid)
'''

'''
# back up code for reference
time=temp.get().to_dict()['Time_Es']
time=time+datetime.timedelta(hours=-4)
print(time.strftime('%Y-%m-%d %H:%M'))
task_update('QmfuMOqiib23OOd9g8vy','Task_parti.sample_4',True)
for i in temp.collection(u'Subtasks').get():
	print(i.to_dict())
for i in task.where(u'Task_leader','==','renzhili@oakland.edu').get():
	print(i.id)

try:
	user_login('renzhili@oakland.edu','123456')
except:
	print('email or passward incorrect')
'''