import firebase_admin as fba
from firebase_admin import firestore
from firebase_admin import auth
import datetime
import pytz
__accountname__='renzhili@oakland.edu'
#init database
cred = fba.credentials.Certificate('./serviceaccountkey.json')
mainapp = fba.initialize_app(cred)
db = firestore.client()
task = db.collection(u'Task')

def task_add(Task_name,Time_due,Task_discr=None,Task_prior=1,Task_leader=__accountname__,Task_parti=None,Time_accom=None,Time_Es=datetime.datetime.utcnow(),Is_accom=False,Has_subtask=False,maintask=None):
	# add a new task to database,could add a sub-task to one existing task
	# sample use: (return value is a doc instance)
	# a=task_add(u'tasknumber3',datetime.datetime(2018,10,22,22,22,0),u'discription3',[maintask='QmfuMOqiib23OOd9g8vy'])
	Time_due=Time_due+datetime.timedelta(hours=4)
	taskdict={
		u'Task_name': Task_name, u'Task_discr': Task_discr,
		u'Time_due': Time_due, u'Task_prior': Task_prior,
		u'Task_leader': Task_leader, u'Task_parti': Task_parti,
		u'Time_accom': Time_accom, u'Time_Es': Time_Es,
		u'Is_accom': Is_accom, u'Has_subtask': Has_subtask
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

for i in task.where(u'Task_leader','==','renzhili@oakland.edu').get():
	print(i.id)


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

for i in temp.collection(u'Subtasks').get():
	print(i.to_dict())
'''