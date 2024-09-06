from DEFINE import *

def connect(method=None, _db="facerecognition"):
    if (method != 0):
        return mysql.connector.connect(host=HOST, user=USER, passwd=PASSWORD, database=_db)

def getUserInfo(conn, userID):
    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT user_name, login_time
    FROM users
    WHERE user_id = """+str(userID)
    mycursor.execute(query)
    return mycursor.fetchall()[0]

def getCourseList(conn, userID, isTeacher):
    if isTeacher:
        table = "teaches"
    else:
        table = "takes"

    mycursor = conn.cursor()
    query = """
    SELECT c.course_id, c.course_code
    FROM """ +table + """ t
        INNER JOIN courses c on t.course_id = c.course_id
    WHERE t.user_id = 
    """+str(userID)
    mycursor.execute(query)
    return mycursor.fetchall()

def getUserTimeslots(conn, userID, isTeacher):
    if isTeacher:
        table = "teaches"
    else:
        table = "takes"

    timeslots = {}
    
    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT c.course_code, ct.course_venue, ct.start_time, ct.duration
    FROM coursetimeslots ct
        INNER JOIN """ +table + """ t on ct.course_id = t.course_id
        INNER JOIN courses c on c.course_id = ct.course_id
    WHERE t.user_id = """ + str(userID) + " AND weekday = " 
    
    for i in range(1,6):
        mycursor.execute(query+str(i)+" ORDER BY start_time")
        coursetimeslots = mycursor.fetchall()
        for course in coursetimeslots:
            course['start_time'] = int(course['start_time'][0:2])-8
        timeslots[i] = coursetimeslots
    
    return timeslots

def getWeekdayTimeslots(conn, user_id, weekday, isTeacher):
    if isTeacher:
        table = "teaches"
    else:
        table = "takes"

    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT c.course_id, ct.start_time
    FROM coursetimeslots ct
        INNER JOIN """ +table + """ t on ct.course_id = t.course_id
        INNER JOIN courses c on c.course_id = ct.course_id
    WHERE t.user_id = """ + str(user_id) + " AND weekday = " + str(weekday) + " ORDER BY start_time"
    
    mycursor.execute(query)
    return mycursor.fetchall()


def getCourseTimeslots(conn, course_id):
    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT ct.weekday, ct.course_venue, ct.start_time, ct.duration, ct.zoom_link
    FROM coursetimeslots ct
        INNER JOIN courses c on c.course_id = ct.course_id
    WHERE c.course_id = """ + str(course_id)
    mycursor.execute(query)
    return mycursor.fetchall()

def getCourseMaterials(conn, course_id):
    mycursor = conn.cursor()
    query = """
    SELECT material_name, material_link
    FROM coursematerials
    WHERE visible_to_students = TRUE AND course_id = 
    """+str(course_id)
    mycursor.execute(query)
    return mycursor.fetchall()

def getTeachingMaterials(conn, course_id):
    mycursor = conn.cursor()
    query = """
    SELECT material_id, material_name, material_link, visible_to_students
    FROM coursematerials
    WHERE course_id = 
    """+str(course_id)
    mycursor.execute(query)
    return mycursor.fetchall()

def checkCourseInfo(conn, course_id):
    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT course_code, course_name, course_info
    FROM courses
    WHERE course_id = 
    """ +str(course_id)
    mycursor.execute(query)
    return mycursor.fetchall()[0]

def getTeachersMessages(conn, course_id):
    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT u.user_name, th.welcome_message
    FROM users u
        INNER JOIN teaches th on u.user_id = th.user_id
    WHERE th.course_id = 
    """ +str(course_id)
    mycursor.execute(query)
    return mycursor.fetchall()


###  discussions and forum  ###

def getDiscussionTopics(conn, course_id):
    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT d.topic_id, d.content, u.user_name, d2.replyNum 
    FROM discussions d
        INNER JOIN users u on u.user_id = d.user_id
        INNER JOIN (
            SELECT topic_id, COUNT(1)-1 as replyNum FROM discussions GROUP BY topic_id
            ) d2 on d.topic_id = d2.topic_id
    WHERE d.discussion_id = 1 AND course_id = 
    """ +str(course_id)
    mycursor.execute(query)
    return mycursor.fetchall()

def getDiscussions(conn, arg):
    (course_id, topic_id) = arg.split("%",1)

    mycursor = conn.cursor(dictionary = True)
    query = """
    SELECT d.discussion_id, d.content, u.user_name
    FROM discussions d
        INNER JOIN users u on u.user_id = d.user_id 
    WHERE d.topic_id = """ + str(topic_id) + " AND course_id = " + str(course_id) + """
    ORDER BY discussion_id
    """
    mycursor.execute(query)
    return mycursor.fetchall()



def checkTeacher(conn, user_id):
    mycursor = conn.cursor()
    query = """
    SELECT COUNT(1)
    FROM teachers
    WHERE user_id = """ + str(user_id)
    mycursor.execute(query)
    return mycursor.fetchall()[0][0]>0



################## updates ##################



def updateLoginTime(conn, user_id, login_time):
    mycursor = conn.cursor()
    query = "UPDATE users SET login_time = '" + login_time + "' WHERE user_id = " + str(user_id)
    mycursor.execute(query)
    conn.commit()

def updateLogoutTime(conn, user_id, logout_time):
    mycursor = conn.cursor()
    query = "UPDATE users SET logout_time = '" + logout_time + "' WHERE user_id = " + str(user_id)
    mycursor.execute(query)
    conn.commit()

def addTopic(conn, user_id, course_id, content):
    mycursor = conn.cursor()
    query = """
    SELECT MAX(topic_id)
    FROM discussions
    WHERE course_id = """ + str(course_id)
    mycursor.execute(query)
    topic_id = mycursor.fetchall()[0][0]+1

    query = """INSERT INTO discussions (course_id, topic_id, discussion_id, user_id, content) VALUES (
        """ + ','.join([str(course_id), str(topic_id), "1", str(user_id), "'"+content+"'"]) + ")"
    mycursor.execute(query)
    conn.commit()

def addDiscussion(conn, user_id, course_id, topic_id, content):
    #find the max of discussion id
    #insert into
    mycursor = conn.cursor()
    query = """
    SELECT MAX(discussion_id)
    FROM discussions
    WHERE course_id = """ + str(course_id) + " AND topic_id = " + str(topic_id)
    mycursor.execute(query)
    discussion_id = mycursor.fetchall()[0][0]+1

    query = """INSERT INTO discussions (course_id, topic_id, discussion_id, user_id, content) VALUES (
        """ + ','.join([str(course_id), str(topic_id), str(discussion_id), str(user_id), "'"+content+"'"]) + ")"
    mycursor.execute(query)
    conn.commit()



def addMaterial(conn, course_id, user_id, material_name, material_link, visible_to_students):
    mycursor = conn.cursor()
    query = """INSERT INTO CourseMaterials (course_id, user_id, material_name, material_link, visible_to_students) VALUES (
        """ + ','.join([str(course_id), str(user_id), "'"+material_name+"'", "'"+material_link+"'", str(int(visible_to_students))]) + ")"
    mycursor.execute(query)
    conn.commit()

def changeMaterialVisibility(conn, material_id):
    mycursor = conn.cursor()
    query = "UPDATE CourseMaterials SET visible_to_students = NOT(visible_to_students) WHERE material_id = " + str(material_id)
    mycursor.execute(query)
    conn.commit()

def deleteMaterial(conn, material_id):
    mycursor = conn.cursor()
    query = "DELETE FROM CourseMaterials WHERE material_id = " + str(material_id)
    mycursor.execute(query)
    conn.commit()