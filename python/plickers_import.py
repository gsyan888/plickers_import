# -*- coding: UTF-8 -*-
# importing library 
import sys
import requests 
import json
import datetime
import random 
import string
import csv

# importing Tkinter library
if sys.version_info < (3,): 
	import Tkinter as tk
	import tkFileDialog
	import tkMessageBox
else :
	import tkinter as tk
	from tkinter import filedialog as tkFileDialog
	from tkinter import messagebox as tkMessageBox

debug = False 
enableSet = False

# defining the api-endpoint 
API_URL_BASE = "https://api.plickers.com/"

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5"

#session data
id = ''
token = ''

# if filesytem encoding is not utf-8 , encode name to utf-8
def getUTF8filename(fName) :
	if sys.getfilesystemencoding() != 'utf-8' :
		fName = fName.encode('utf-8')
	return fName

# add zero to the number less than 10
def prefix_zero(n) :
	return '0'+str(n) if n < 10 else str(n)

# defining function for random 
# source from : https://www.geeksforgeeks.org/generating-random-ids-python/
# string id with parameter 
def get_random_id(size, chars=string.ascii_uppercase + string.digits): 
    return ''.join(random.choice(chars) for x in range(size)) 
  
# convert answer to digit
def answer_convert_to_digit(s) :
	s = s.encode('utf-8').decode()
	ans = 0
	if s=='1' or s=='A' or s=='a' or s=='ㄅ' or s=='甲' or s=='１' or s=='Ａ' or s=='一' :
		ans = 1
	elif s=='2' or s=='B' or s=='b' or s=='ㄆ' or s=='乙' or s=='２' or s=='Ｂ' or s=='二' :
		ans = 2
	elif s=='3' or s=='C' or s=='c' or s=='ㄇ' or s=='丙' or s=='３'  or s=='Ｃ' or s=='三' :
		ans = 3
	elif s=='4' or s=='D' or s=='d' or s=='ㄈ' or s=='丁' or s=='４'  or s=='Ｄ' or s=='四' :
		ans = 4
	return ans

#login in plickers and gets the session token	
def api_get_id_and_token(email, password) :
	# data to be sent to api 
	data = {
		"email":email,
		"password":password
	}

	headers = {
		"Referer": "https://www.plickers.com/login",
		"Origin": "https://www.plickers.com/",
		"User-Agent": USER_AGENT,
		"Content-Type": "application/json"
	}
	# join the api url
	API_URL = API_URL_BASE+"sessions"
	# sending login post request to get token and uid
	response = requests.post(url = API_URL, data = json.dumps(data), headers=headers) 
	
	id = ''
	token = ''
	if response.status_code == 201 :
		session_json = response.json()
		id = session_json['id']
		token = session_json['token']
	return id, token

#get the current time of plickers server
def api_get_current_time(token) :
	current_time = ''
	# get current time
	API_URL = API_URL_BASE+'current-time'
	headers = { 
		"Referer": "https://www.plickers.com/library",
		"Origin": "https://www.plickers.com/",
		"User-Agent": USER_AGENT,
		'x-auth-token' : token 
	}
	response = requests.get(url = API_URL, params = {}, headers=headers) 	
	if response.status_code == 200 :
		current_time = response.json()['currentTime']
	return current_time

#create a folder and gets the folder id
def api_create_folder_and_get_id(token, folder_name) :
	folder_id = ''

	current_time = api_get_current_time(token)
	
	# create new folder
	t = datetime.datetime.now()
	#folder_name = str(t.year)+'-'+prefix_zero(t.month)+'-'+prefix_zero(t.day)+'-'+prefix_zero(t.day)+'T'+prefix_zero(t.hour)+':'+prefix_zero(t.minute)+':'+prefix_zero(t.second)
	#folder_name = folder_name.decode('utf-8').encode('utf-8')
	API_URL = API_URL_BASE+'folders'
	data = {
		"name":folder_name,
		"parent":None,
		"clientModified":current_time,
		"userCreated":current_time,
		"archived":False
	}
	headers = {
		"Referer": "https://www.plickers.com/library",
		"Origin": "https://www.plickers.com/",
		"User-Agent": USER_AGENT,
		'x-auth-token' : token, 
		'x-api-version' : "4.0.0",
		'x-client-info' : '{"platform":"Web","appVersion":"58.21"}',
		
		"Content-Type": "application/json"
	}
	# sending post request 
	response = requests.post(url = API_URL, data = json.dumps(data), headers=headers) 
	if response.status_code == 201 :
		folder_id = response.json()['id']
	
	return folder_id

#import data in csv file and send create questions requests to plickers
def api_newquestions(token, folder_id, csv_file_name, column_numbers) :
	import_total = 0
	failure_total = 0
	is_header = True

	#send get currentTime API request
	current_time = api_get_current_time(token)
	
	# open CSV file and import to plickers
	#csvfile = open(csv_file_name, 'r')
	#for csv_data in csv.reader(csvfile, encoding='utf-8'):
	if sys.version_info < (3,):
		csvfile = open(csv_file_name, 'r')
	else :
		csvfile = open(csv_file_name, 'r', encoding='utf-8')
	for csv_data in csv.reader(csvfile):
		#skip first row (fields captions)
		if is_header :
			is_header = False
			continue
		
		if sys.version_info < (3,):
			#Python 2 convert string to utf-8
			i = 0
			for d in csv_data :
				csv_data[i]=d.decode('utf-8')
				i=i+1
				
		#question body
		question_body = csv_data[column_numbers[0]] #.encode('utf-8')
		
		#new question data
		data = {
			"body":question_body,
			"bodySource": [{
				"type": "paragraph",
				"content": [{
				"type": "text",
				"text": question_body
				}]
			}],
			"bodyHtml":"<p>"+question_body+"</p>",			
			"media":None,
			
			# "xLayout":{"bodyFS":64,"choiceFS":38,"bodyH":365,"version":2},
			"template":"standard",
			"image":"",
			"measurements": {
				"bodyFS": 64,
				"choiceFS": 42
			},
			"layout": "bodyLeft",			
			"folder":folder_id,
			"repo":None,
			"archived":False,
			"createdOnMobile":False,
			"version":0,
			"clientModified":current_time,
			"userCreated":current_time,
			"lastEditedAt":current_time
		}
		#choices 
		choices = []
		for c in range(4) :
			body = csv_data[column_numbers[2+c]] #.encode('utf-8')
			if body != '' :
				#if (c+1) == answer_convert_to_digit(csv_data[column_numbers[1]].encode('utf-8')) :
				if (c+1) == answer_convert_to_digit(csv_data[column_numbers[1]]) : 
					correct = True
				else :
					correct = False
				choice = { 
					'body': body, 
					"bodyHtml": body,
					"bodySource": [{
					  "type": "text",
					  "text": body
					}],
					'correct': correct,
					"media": None
				}				
				choices.append(choice)
		data.update(choices=choices)
		
		headers = {
			"Referer": "https://www.plickers.com/editor/newquestion",
			"Origin": "https://www.plickers.com/",
			"User-Agent": USER_AGENT,
			'x-auth-token' : token, 
			'x-api-version' : "4.0.0",
			'x-client-info' : '{"platform":"Web","appVersion":"58.21"}',
			"Content-Type": "application/json"
		}

		API_URL = API_URL_BASE+'questions'
		# sending post request 
		if debug :
			import_total = import_total + 1
			print("\n-----"+str(import_total)+"------\n")
			print(json.dumps(data))
		else :
			response = requests.post(url = API_URL, data = json.dumps(data), headers=headers) 
			if response.status_code == 201 :
				import_total = import_total + 1
				question_id = response.json()['id']
				print(str(import_total)+' created id: '+question_id)
			else :
				failure_total = failure_total + 1
	csvfile.close()
	return import_total, failure_total

#import data in csv file and send new set request to plickers 
def api_new_set(token, folder_name, csv_file_name, column_numbers) :
	#send get currentTime API request
	current_time = api_get_current_time(token)
	
	# open CSV file and import to plickers
	if sys.version_info < (3,):
		csvfile = open(csv_file_name, 'r')
	else :
		csvfile = open(csv_file_name, 'r', encoding='utf-8')
	import_total = 0
	failure_total = 0
	is_header = True
	
	questions = []
	#for csv_data in csv.reader(csvfile, encoding='utf-8'):
	for csv_data in csv.reader(csvfile): 
		if is_header :
			is_header = False
			continue
		#Python 2 convert string to utf-8
		if sys.version_info < (3,):
			i=0
			for d in csv_data :
				csv_data[i] = d.decode('utf-8')
				i=i+1
		
		#ex. 0a58ae5f
		questionId = get_random_id(8, "ilovetaiwain2019")
		
		#question body
		body = csv_data[column_numbers[0]] #.encode('utf-8')

		question = {
			# "xLayout":{"bodyFS":64,"choiceFS":38,"bodyH":365,"version":2},
			"xLayout":None,
			"template":"standard",
			"image":"",
			"questionId":questionId,
			"body":body,
			"bodySource": [{
				"type": "paragraph",
				"content": [{
				"type": "text",
				"text": body
				}]
			}],
			"bodyHtml": "<p>"+body+"</p>",
			"measurements": {
				"bodyFS": 64,
				"choiceFS": 42
			},
			"layout": "bodyLeft",
			"media": None			
		}
		#question.update(body=body)
		#choices 
		choices = []
		for c in range(4) :
			body = csv_data[column_numbers[2+c]] #.encode('utf-8')
			if body != '' :
				#if (c+1) == answer_convert_to_digit(csv_data[column_numbers[1]].encode('utf-8')) :
				if (c+1) == answer_convert_to_digit(csv_data[column_numbers[1]]) :
					correct = True
				else :
					correct = False
				choice = { 
					'body': body, 
					"bodyHtml": body,
					"bodySource": [{
					  "type": "text",
					  "text": body
					}],
					'correct': correct,
					"media": None
				}				
				choices.append(choice)
		question.update(choices=choices)
		questions.append(question)

	data = {
		"folder":None,
		"archived":False,
		"repo":None,
		"name":folder_name,
		"description":"Empty description",
		"clientModified":current_time,
		"userCreated":current_time,
		"lastEditedAt":current_time		
	}		
	data.update(questions=questions)
	
	headers = {
		"Referer": "https://www.plickers.com/seteditor/newSet",
		"Origin": "https://www.plickers.com/",
		"User-Agent": USER_AGENT,
		'x-auth-token' : token, 
		'x-api-version' : "4.0.0",
		'x-client-info' : '{"platform":"Web","appVersion":"58.21"}',
		"Content-Type": "application/json"
	}

	API_URL = API_URL_BASE+'sets'
	# sending post request 
	if debug :
		import_total = import_total + 1
		print("\n-----"+str(import_total)+"------\n")
		print(json.dumps(data))
	else :
		response = requests.post(url = API_URL, data = json.dumps(data), headers=headers) 
		if response.status_code == 201 :
			import_total = import_total + 1
			set_id = response.json()['id']
			print(str(import_total)+' => created set id: '+set_id)
		else :
			failure_total = failure_total + 1
	csvfile.close()
	return import_total, failure_total

#the action of login button (login in plickers)
def login_plickers() :
	global id
	global token
	if debug :
		email = 'aaaaa'	#fake e-mail
		password = 'bbbbb' #fake password
	else :
		email = email_entry.get()
		password = passwd_entry.get()
	if email == '' or password == '' :
		tkMessageBox.showwarning('資料填寫不完整', '請先填寫e-mail和密碼才能進行登入程序')
	else :
		# send session API request to get user id & session token
		if debug :
			s_id = 'debug'		#fake id
			s_token= 'debug'	#fake id
		else :
			s_id, s_token = api_get_id_and_token(email, password)
		
		# show login status 	
		if s_id == '' or s_token == '' :
			tkMessageBox.showwarning('Plickers登入失敗', 'e-mail或密碼可能有誤，請重新輸入後再試。')
		else :
			id = s_id
			token = s_token
			# hide email & password antry
			email_frame.pack_forget()
			passwd_frame.pack_forget()
			login_frame.pack_forget()
			# show login status
			login_status_text.set('Plickers 連線成功')
			login_status_label.config(font=('Times', 24))			
			# show step 2 : CSV file browser button
			step2_frame.pack(side=tk.TOP, fill="both", expand="no")
			filename_frame.pack(side=tk.TOP, fill='both')

#the action of submit button (send new folder / new question / new set request to plickers
def api_import() :
	#filename = cvs_file_name.get().encode('utf-8')
	#folder_name = new_folder_name.get().encode('utf-8')
	filename = cvs_file_name.get()
	folder_name = new_folder_name.get()

	# caculate the column index number
	import_at = []
	for v in import_at_column_number :
		import_at.append(int(v.get())-1)
	
	if is_import_to_set.get()==1 :	
		import_total, failure_total = api_new_set(token, folder_name, filename, import_at)
		#tkMessageBox.showinfo('完成匯入', '已將「'+filename.encode('utf-8')+ '」中的題目匯到 Plickers 的 SET「'+folder_name+'」中。')
		tkMessageBox.showinfo('完成匯入', '已將「'+getUTF8filename(filename)+ '」中的題目匯到 Plickers 的 SET「'+getUTF8filename(folder_name)+'」中。')
	else :
		# send create folder API request to create new folder & get folder_id
		if debug :
			folder_id = 'aaaaaaa'	#fake id
		else :
			folder_id = api_create_folder_and_get_id(token, folder_name)
			
		if folder_id == '' :
			tkMessageBox.showwarning('無法新增資料夾', '新資料夾 ' + getUTF8filename(folder_name) + ' 建立失敗!')
		else :
			# send new question API to create all questions in CSV file
			import_total, failure_total = api_newquestions(token, folder_id, filename, import_at)
			#tkMessageBox.showinfo('完成匯入', '已將「'+filename.encode('utf-8')+ '」中的題目匯到 Plickers 的資料夾「'+folder_name+'」中。')
			tkMessageBox.showinfo('完成匯入', '已將「'+getUTF8filename(filename)+ '」中的題目匯到 Plickers 的資料夾「'+getUTF8filename(folder_name)+'」中。')

#the action of file select button (select a csv file)
def file_browser() :
	global window
	global frame_height
	global frame_width
	global step3_frame	
	global step4_frame
	filename = tkFileDialog.askopenfilename(filetypes=[('CSV格式檔', '*.csv'),('所有檔案','*.*')])
	if filename != '' :
		cvs_file_name.set(filename)
		if sys.version_info < (3,):
			csvfile = open(filename, 'r')
		else :
			#first_row = csv.reader(csvfile, encoding='utf-8').next()
			csvfile = open(filename, 'r', encoding='utf-8')
		first_row = next(csv.reader(csvfile))
		if sys.version_info < (3,):
			i=0
			for d in first_row :
				first_row[i] = d.decode('utf-8')
				i=i+1
		csvDataLineTotalNumber = sum(1 for _ in csvfile)
		csvfile.close()
		
		if enableSet :
			set_checkbox_state = tk.NORMAL
		elif csvDataLineTotalNumber > 5 :
			set_checkbox_state = tk.DISABLED
		else :
			set_checkbox_state = tk.NORMAL

		#remove all elements exist
		if len(step3_frame.winfo_children()) > 0 :
			for c in step3_frame.winfo_children() :
				c.destroy()
		
		c = 1
		labels = []
		for f in first_row :
			labels.append(tk.Label(step3_frame, text=str(c)+"\n"+f, height=3, borderwidth=2, relief="groove"))
			#labels[len(labels)-1].pack(side=tk.LEFT)
			labels[len(labels)-1].grid(row=0, column=c)
			c = c+1
		
		fields_total = len(first_row)
		
		text = ['題幹', '答案', '選項1', '選項2', '選項3', '選項4']		
		frm = []
		lbl = []
		ent = []
		rad = []
		for i in range(0, len(import_at_column_number)) :
			frm.append(tk.Frame(step3_frame, height=frame_height, width=frame_width))
			frm[i].grid(row=1+i, column=0)
			lbl.append(tk.Label(frm[i], text=(text[i]+'由第幾欄位匯出:'), width=label_width))
			lbl[i].pack(side=tk.LEFT)
			ent.append(tk.Entry(frm[i], textvariable=import_at_column_number[i], width=3, justify=tk.CENTER))
			ent[i].pack(side=tk.LEFT)
			
			defaul_value = int(import_at_column_number[i].get())
			#default_value can't great then CSV columns total number
			if defaul_value > fields_total :
				import_at_column_number[i].set(1)
				defaul_value = int(import_at_column_number[i].get())
			radios = []
			for r in range(0, fields_total) :
				radios.append(tk.Radiobutton(step3_frame, value=(r+1), variable=import_at_column_number[i], justify=tk.CENTER, width=3))
				radios[len(radios)-1].grid(row=(i+1), column=(1+r))
				if (r+1) == defaul_value :
					radios[len(radios)-1].select()
			rad.append(radios)
		
		import_to_set_checkbutton = tk.Checkbutton(step3_frame, text = "所有題目變成一個 SET", variable = is_import_to_set,  onvalue = 1, offvalue = 0, height=2, state=set_checkbox_state)
		import_to_set_checkbutton.grid(row=1+len(import_at_column_number), column=0)
		
		# add submit button to step 4 frame
		if len(step4_frame.winfo_children()) == 0 :			
			new_folder_name_label = tk.Label(step4_frame, textvariable=new_folder_name, font=('Times',12))
			new_folder_name_label.pack(side=tk.TOP)
			submit_btn = tk.Button(step4_frame, text='送出資料', command=api_import)
			submit_btn.pack(side=tk.TOP, expand="yes")
		#update new folder name label	
		new_folder_name.set(filename.split('/')[-1:][0])
		#new_folder_name.set(filename)

#the action of menu item of about
def about_this() :		
	tkMessageBox.showinfo('關於本工具', "Plickers CSV題庫檔匯入工具 v.0.2\n\n2019.11.25 by TPET gsyan.雄")

#window width and height
window_width = 800	
window_height = 600

window = tk.Tk()

#set the title of window
window.title('Plickers CSV 題庫匯入工具')

# put the window to the center of the screen
w = window.winfo_screenwidth()
h = window.winfo_screenheight()
x = w/2 - window_width/2
y = h/2 - window_height/2
#set the window size and position => [width]x[height]+x+y
window.geometry("%dx%d+%d+%d" % ((window_width,window_height) + (x, y)))

#---------------------------
#some StringVar in form
#---------------------------
#show login status
login_status_text = tk.StringVar()

#CVS file name
cvs_file_name = tk.StringVar()
cvs_file_name.set('')

#import from cvs column number
# initial number
# in this order : question,answer,option1,option2,option3,option4
import_at_column_number = []
for i in range(6) :
	import_at_column_number.append(tk.StringVar())
	import_at_column_number[i].set(i+4)

#plickers new folder name (parse from csv_file_name
new_folder_name = tk.StringVar()
new_folder_name.set('')
#check if import to set
is_import_to_set = tk.IntVar()
is_import_to_set.set(0)
#the flag to set [new questions] or [new set] action
set_checkbox_state = tk.DISABLED

#menu at the top of window
menubar = tk.Menu(window)
menubar.add_command(label="結束", command=window.quit)
menubar.add_command(label="關於", command=about_this)
window.config(menu=menubar)

#header label
header_label = tk.Label(window, text='Plickers CSV 題庫匯入工具', font=('times', 18, 'bold'), height=2)
header_label.pack()

frame_height = 6
frame_width = 50
label_width = 20
entry_width = 25

#label frames of 4 steps
step1_frame = tk.LabelFrame(window, text='步驟1 : 填寫 Plickers 登入資訊', font=('times', 12, 'bold'))
step1_frame.pack(side=tk.TOP, fill="both")

step2_frame = tk.LabelFrame(window, text='步驟2 : 選取 CSV 題庫檔', font=('times', 12, 'bold'))
step2_frame.pack(side=tk.TOP, fill="both", expand="yes")

step3_frame = tk.LabelFrame(window, text='步驟3 : 設定匯出哪些欄位', font=('times', 12, 'bold'))
step3_frame.pack(side=tk.TOP, fill="both", expand="yes")

step4_frame = tk.LabelFrame(window, text='步驟4 : 開始匯出', font=('times', 12, 'bold'))
step4_frame.pack(side=tk.TOP, fill="both", expand="yes")

#Step 1 elements : plickers login form
email_frame = tk.Frame(step1_frame)
email_frame.pack(side=tk.TOP, fill='both')
email_label = tk.Label(email_frame, text='登入 Plicker 的 e-mail:', width=label_width, height=2)
email_label.pack(side=tk.LEFT)
email_entry = tk.Entry(email_frame, width=entry_width)
email_entry.pack(side=tk.LEFT)

passwd_frame = tk.Frame(step1_frame)
passwd_frame.pack(side=tk.TOP, fill="both")
passwd_label = tk.Label(passwd_frame, text='登入 Plicker 的密碼:', width=label_width, height=2)
passwd_label.pack(side=tk.LEFT)
passwd_entry = tk.Entry(passwd_frame, show='*', width=entry_width)
passwd_entry.pack(side=tk.LEFT)

login_frame = tk.Frame(step1_frame)
login_frame.pack(side=tk.TOP)
login_btn = tk.Button(login_frame, text='送出資料，登入 Plickers', command=login_plickers)
login_btn.pack(side=tk.TOP)

login_status_label = tk.Label(step1_frame, text='', textvariable=login_status_text)
login_status_label.pack(side=tk.TOP)


#Step 2 elements : select CSV file
filename_frame = tk.Frame(step2_frame)
filename_frame.pack(side=tk.TOP, fill='both')
filename_label = tk.Label(filename_frame, text='CSV題庫檔檔名:', width=label_width, height=3)
filename_label.pack(side=tk.LEFT)
filename_entry = tk.Entry(filename_frame, textvariable=cvs_file_name)
filename_entry.pack(side=tk.LEFT)
filename_btn = tk.Button(filename_frame, text='按這裡選取', command=file_browser)
filename_btn.pack(side=tk.LEFT)

#hide step 2 elements before login (step1)
filename_frame.pack_forget()

# get the arguments
is_open_the_window = True
if len(sys.argv) >= 2 :
	for i in range(1, len(sys.argv)) :
		if sys.argv[i].startswith('--') :
			option = sys.argv[i][2:]
			if option == 'enableSet' :
				enableSet = True
				set_checkbox_state = tk.NORMAL
			elif option == 'debug' :
				debug = True
			else :
				is_open_the_window = False
				print("  --help : arg list\n  --debug : debug mode\n  --enableSet : enable import to set\n")
if is_open_the_window :
	#open the window 
	window.mainloop()
