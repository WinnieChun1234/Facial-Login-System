from datetime import datetime, timedelta
import smtplib, ssl
from email.message import EmailMessage
from DEFINE import *

# conn = mysql.connector.connect(host="localhost", username="root", password="NewPassword", database = "face_db")

def CheckCourseInfo(connect):
	cursor = connect.cursor()
	now = datetime.now()
	##now = now - timedelta(hours=1)
	now_time = datetime.strptime(datetime.strftime(now,'%H:%M'),'%H:%M')
	query = """
		SELECT DISTINCT T.start_time, T.weekday, students.name, users.email
		FROM coursetimeslots AS T, takes, (SELECT student.user_name, student.user_id
		FROM (SELECT users.user_name, students.user_id
		FROM users, students
		WHERE users.user_id = students.user_id) AS student) AS S, students, users
		WHERE T.course_id = takes.course_id AND takes.user_id = T.course_id AND S.user_id = users.user_id AND S.user_name = users.user_name;
	"""
	cursor.execute(query)
	student = cursor.fetchall()
	##time = str(hour) + ":"+ str(minute).zfill(2)
	for timing in student:
		if (timing[1] == int(now.weekday() + 1)):
			time = datetime.strptime(datetime.strftime(datetime.strptime(timing[0],'%H:%M'), '%H:%M'),'%H:%M')
			time_difference = (time - now_time).seconds
			if (time_difference<=3600):
				sendemail(timing[2], str(timing[1]), timing[3])

def sendReminder(conn, user_id, isTeacher, course_id, weekday, start_time):
	mail_host = "smtp.gmail.com"
	mail_user = EMAIL_ACCOUNT
	mail_pass = EMAIL_PASSWORD

	info = getUserInfo(conn, user_id)
	FROM = EMAIL_ACCOUNT
	TO = info['email']

	msg = EmailMessage()
	msg['Subject'] = "Upcoming course reminder"
	msg['FROM'] = FROM
	msg['To'] = TO

	sql_select_Query = """
	SELECT c.course_code, c.course_name, ct.course_venue, ct.duration, ct.zoom_link
	FROM coursetimeslots as ct, courses as c
	WHERE c.course_id = ct.course_id AND ct.weekday = 
	""" + weekday + " AND ct.start_time = '" + start_time + "'"

	cursor = conn.cursor(dictionary = True)
	cursor.execute(sql_select_Query)

	record = cursor.fetchall()[0]
	end_time = str(int(start_time[0:2]) + record['duration'])+start_time[2:]

	sql_select_Query = """
    SELECT material_name, material_link
    FROM coursematerials
    WHERE course_id = """+str(course_id)
	
	if (not(isTeacher)):
		sql_select_Query += " AND visible_to_students = TRUE" 

	cursor = conn.cursor(dictionary = True)
	cursor.execute(sql_select_Query)

	materials = cursor.fetchall()


	newline = '\n'
	content = ""
	content += "Dear " + info['user_name'] + ","
	content += newline
	content += newline
	content += "Please be reminded for the upcoming course:"
	content += newline
	content += newline
	content += record['course_code'] + " - " + record['course_name'] 
	content += newline
	content += "Time: " + weekdays[int(weekday)] + " "+ start_time + " - " + end_time
	content += newline
	content += "Venue: " + record['course_venue']
	content += newline
	content += "Zoom link: " + record['zoom_link']
	content += newline
	content += "Materials: "
	if len(materials) > 0:
		content += newline
		for material in materials:
			content += "[" + material['material_name'] + "]" + material['material_link']
			content += newline
	else:
		content += "None"
	
	msg.set_content(content)

	try:
		if(isTeacher):
			print(TO)
			print(content)
		else:
			server = smtplib.SMTP_SSL(mail_host, 465)
			server.login(mail_user, mail_pass)
			server.send_message(msg)
			server.quit()
			print ("Email sending success")
	except Exception as e:
		print(e)
		print ("Error: unable to send email")

def getUserInfo(conn, user_id):
	sql_select_Query = "SELECT user_name, email from users where user_id = " + str(user_id)
	cursor = conn.cursor(dictionary = True)
	cursor.execute(sql_select_Query)
	info = cursor.fetchall()[0]
	return info