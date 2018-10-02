import firebase_admin as fba
from firebase_admin import firestore
#from google.cloud import firestore
cred=fba.credentials.Certificate('./serviceaccountkey.json')
mainapp=fba.initialize_app(cred)
db=firestore.client()

task=db.collection(u'Task')
temp=task.document('IkFUiMCcsuDLoa6TjI1L')
print(temp.get().to_dict()['Task_name'])
for i in task.get():
	print(i.id)
