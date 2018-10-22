from tkinter import *
from tkinter import ttk
gui = Tk()
username ='jia'
password = '1234'
gui.geometry("400x400")
gui.title("LOG IN")

usr = StringVar()
pwd = StringVar()

# pre = Label(gui ,text="LOG IN", background="#6666ee").grid(row=0,column = 0)
a = Label(gui ,text="username").grid(row=1,column = 0)
b = Label(gui ,text="password").grid(row=2,column=0)
e = Entry(gui, textvariable=usr).grid(row=1,column=1)
f = Entry(gui,show="*", textvariable=pwd).grid(row=2,column=1)
xx = Checkbutton(gui, text="remember me").grid(row=3, column = 1)
# c = Button(gui, text="Create account").grid(row=2,column=0)
# a1 = Label(gui ,text="username").grid(row=3,column = 0)
# b1 = Label(gui ,text="password").grid(row=4,column=0)
# e1 = Entry(gui).grid(row=3,column=1)
# f1 = Entry(gui,show="*").grid(row=4,column=1)
x = 0
y = 0


def login():
	
	name=usr.get()
	pword = pwd.get()
	print name, pword
	if name == username and pword==password:
		i=Label(gui,text='Login success').grid(row=7,column=0)
		print("login success")
	else:
		print("wrong password")
		j=Label(gui,text='Login failed').grid(row=7,column=0)


c1 = Button(gui, background="#6666ee", text = "LOGIN",command= lambda : login()).grid(row=6,column=1)

gui.mainloop()