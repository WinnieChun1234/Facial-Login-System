from DEFINE import *
import database as db
import email_reminder as mail

class Session:
    def __init__(self, conn, userID, time=dt.datetime.now()):
        self.conn = conn
        self.userID = userID
        self.isTeacher = False
        self.page = DEFAULT_PAGE
        self.arg = DEFAULT_ARG
        self.previousPage = DEFAULT_PAGE
        self.previousArg = DEFAULT_ARG
        self.time = time

    def update(self, event, values):
        func,arg = event.split("%",1)
        if func == "link":
            os.startfile(arg)
        elif func == "addTopic":
            self.addTopicForm()
            return True
            
        elif func == "addDiscussion":
            self.addDiscussionForm()
            return True
            

        elif func == "addMaterial":
            self.addMaterialForm()
            return True

        elif func == "deleteMaterial":
            self.deleteMaterial(arg)
            return True

        elif func == "changeMaterialVisibility":
            self.changeMaterialVisibility(arg)
            return True

        elif func == "sendReminder":
            weekday, start_time = arg.split("%")[0:2]
            self.sendReminder(weekday, start_time)

        elif func == "-previous-":
            page = self.previousPage
            arg = self.previousArg
            self.previousPage = self.page
            self.previousArg = self.arg
            self.page = page
            self.arg = arg
            return True

        elif self.page != func or self.arg != arg:
            self.previousPage = self.page
            self.previousArg = self.arg
            self.page = func
            self.arg = arg
            return True

        return False

########## windows/action ############

    def getLoginnedWindow(self):
        page, arg = self.checkCourse()
        if page is not None:
            self.page = page
            self.arg = arg
        return self.getWindow()

    def addTopicForm(self):
        layout = [ 
            [sg.Text('Start new discussion')],
            [sg.Multiline(key = "content", size = (80,5))],
            [sg.Submit(), sg.Cancel()]
            ]

        win = sg.Window("Add Topic", layout)
        event, values = win.Read()
        if event == 'Submit':
            db.addTopic(self.conn, self.userID, self.arg, values['content'])
        win.Close()

    def addDiscussionForm(self):
        layout = [ 
            [sg.Text('Add discussion')],
            [sg.Multiline(key = "content", size = (80,5))],
            [sg.Submit(), sg.Cancel()]
            ]

        win = sg.Window("Add Discussion", layout)
        event, values = win.Read()
        if event == 'Submit':
            course_id, topic_id = self.arg.split('%',1)
            db.addDiscussion(self.conn, self.userID, course_id, topic_id, values['content'])
        win.Close()

    def addMaterialForm(self):
        layout = [ 
            [sg.Text('Add Material')],
            [sg.Text('Name'), sg.InputText(key = "material_name")],
            [sg.Text('Link'), sg.InputText(key = "material_link")],
            [sg.Checkbox('Visible To Students', default=False,key='visible_to_students')],
            [sg.Submit(), sg.Cancel()]
            ]

        win = sg.Window("Add Material", layout)
        event, values = win.Read()
        if event == 'Submit':
            db.addMaterial(self.conn, self.arg, self.userID, values['material_name'], values['material_link'], values['visible_to_students'])
        win.Close()

    def changeMaterialVisibility(self, material_id):
        db.changeMaterialVisibility(self.conn, material_id)

    def deleteMaterial(self, material_id):
        confirm_exit = sg.popup_ok_cancel('Confirm to delete this matieral?', title='Delete', keep_on_top=True)
        if confirm_exit == "OK":
            db.deleteMaterial(self.conn, material_id)

    def sendReminder(self, weekday, start_time):
        course_id = self.arg
        mail.sendReminder(self.conn, self.userID, self.isTeacher, course_id, weekday, start_time)

########## functions ############
        
    def login(self):
        db.updateLoginTime(self.conn, self.userID, self.time.strftime(DATE_FORMAT))
        self.isTeacher = db.checkTeacher(self.conn, self.userID)

    def logout(self):
        db.updateLogoutTime(self.conn, self.userID, dt.datetime.now().strftime(DATE_FORMAT))

    def checkCourse(self):
        timeslots = db.getWeekdayTimeslots(self.conn, self.userID, self.time.weekday()+1, self.isTeacher)
        for timeslot in timeslots:
            if self.checkTimeslot(timeslot):
                return 'course', timeslot['course_id']
        return None, None

    def checkTimeslot(self, timeslot):
        timestamp_now = self.time.hour*60 + self.time.minute
        timestamp_timeslot = int(timeslot['start_time'][0:2])*60 + int(timeslot['start_time'][3:])
        diff = timestamp_timeslot - timestamp_now
        return diff < 60 and diff > -30


########## layout ############

    def getWindow(self):
        window = sg.Window("Main page",
                layout = self.getLayout(),
                size = DEFAULT_WINDOW_SIZE,
                default_element_size = (20,1),
                element_justification = "center",
                text_justification = "right",
                auto_size_text = False)
        return window

    def getLayout(self):
        layout =  [
            self.WelcomeMessage(),              #list of ele
            [content_element()],
            [sg.HorizontalSeparator()],
            self.MainSection()                  #list of ele
        ]
        return layout

    def WelcomeMessage(self):
        userInfo = db.getUserInfo(self.conn, self.userID)

        message = [
            content_element("Welcome "+ userInfo['user_name'] +"!"),
            content_element("Login Time: "+ userInfo['login_time'])
        ]
        return message

    def MainSection(self):
        if self.page == "timetable":
            justify = "center"
        else:
            justify = "right"
        section = [
            sg.Frame(title="", layout=self.getNavMenu(), size = (144,512), element_justification="center", border_width = 0),          #list of list
            sg.Frame(title="", layout=self.getContent(), size = (576,512), element_justification=justify, border_width = 0)           #list of list
        ]
        
        return section

    def getNavMenu(self):      #Column
        courses = db.getCourseList(self.conn, self.userID, self.isTeacher)

        menu = [
            [nav_button()],
            [content_element()]
        ]

        for (course_id,course_code) in courses:
            menu.append([nav_button(course_code, "course",course_id)])

        return menu

    def getContent(self):     #Column
        if self.page == "timetable":
            content = self.getTimetable()
        elif self.page == "course":
            content = self.getCoursePage()
        elif self.page == "discussiontopics":
            content = self.getDiscussionTopics()
        elif self.page == "discussions":
            content = self.getDiscussions()

        return content
    
    def getTimetable(self):     #column
        courseTimelist = db.getUserTimeslots(self.conn, self.userID, self.isTeacher)
        
        timetable=[]            #list of ele
        
        time_column = []
        time_column.append(table_cell("Time:", 1,"left"))
        for i in range(8,18):
            t = "{:0>2d}".format(i) + ":30-" + "{:0>2d}".format(i+1) + ":30"
            time_column.append(table_cell(t, i%2, "left"))

        timetable.append(sg.Column(time_column,pad=(0,0)))

        for day in range(1,6):
            day_column = [
                table_cell(weekdays[day-1], 1)
            ]

        # """
            time_pointer = 0
            for course in courseTimelist.get(day):
                while course["start_time"] != time_pointer:
                    day_column.append(table_cell(color_odd=time_pointer%2))
                    time_pointer += 1

                duration = course["duration"]
                br1 = (duration-1)*"\n"
                br2 = (duration-1)%2*"\n"
                text = (br1 + course["course_code"]+ br2 + "\n"+course["course_venue"]).split("\n\n")
                text += [""]*(duration-len(text))

                for i in range(duration):
                    day_column.append(table_cell(text[i],color=table_color_3))
                time_pointer += duration
                
            while time_pointer < 10:
                day_column.append(table_cell(color_odd=time_pointer%2))
                time_pointer += 1
        # """
            timetable.append(sg.Column(day_column,pad=(0,0)))
        
        return [
                [sg.T("Weekly Timetable", justification = "center", pad=(10,10))], #v spacing
                timetable
            ]  

    def getCoursePage(self):    #column
        page = []

        info = db.checkCourseInfo(self.conn, self.arg)

        page.append([title_element(info['course_code'] + " - " + info['course_name'])])

        timeslots = db.getCourseTimeslots(self.conn, self.arg)
        for timeslot in timeslots:
            end_time = str(int(timeslot['start_time'][0:2]) + timeslot['duration'])+timeslot['start_time'][2:]
            weekday = weekdays[timeslot['weekday']-1]
            if timeslot['weekday'] == self.time.weekday()+1 and self.checkTimeslot(timeslot):
                color = highlight_button_color
                prefix = "Upcoming: "
                page.append([
                    nav_button('Send reminder','sendReminder%'+str(timeslot['weekday'])+"%"+timeslot['start_time']),
                    content_element(prefix +weekday+ " "+ timeslot['start_time'] + " - " + end_time + " " + timeslot['course_venue']),
                    link_button("Zoom Link", timeslot['zoom_link'],color=color)
                ])
            else:
                page.append([
                    content_element(weekday+ " " + timeslot['start_time'] + " - " + end_time + " " + timeslot['course_venue']),
                    link_button("Zoom Link", timeslot['zoom_link'])
                ])

        page.append([content_element()])

        # page.append([header_element("Course information")])
        # page.append([sg.HorizontalSeparator()])
        # page.append([content_element(status['course_info'],_size=(50,5))])
        # page.append([content_element()])

        messages = db.getTeachersMessages(self.conn, self.arg)
        
        page.append([header_element("Teachers message")])
        page.append([sg.HorizontalSeparator()])
        for message in messages:
            page.append([content_element(message['welcome_message'])])
            page.append([content_element("["+message['user_name']+"]")])
        page.append([content_element()])
    
        page.append([nav_button("Discussion forum","discussiontopics",self.arg)])
        page.append([content_element()])

        
        page.append([header_element("Course Materials")])
        page.append([sg.HorizontalSeparator()])

        if self.isTeacher:
            courseMaterials = db.getTeachingMaterials(self.conn, self.arg)
            for (material_id, material_name, material_link, visible_to_students) in courseMaterials:
                text = "hide" if visible_to_students else "show"
                
                page.append([
                    nav_button("delete", "deleteMaterial",material_id),
                    content_element(material_name),
                    link_button("link",material_link),
                    nav_button(text, "changeMaterialVisibility",material_id)
                    ])

            page.append([nav_button('Add Material','addMaterial')])
        else:
            courseMaterials = db.getCourseMaterials(self.conn, self.arg)
            for (material_name, material_link) in courseMaterials:
                page.append([
                    content_element(material_name),
                    link_button("link",material_link)
                    ])
            page.append([content_element()])
        return page

    def getDiscussionTopics(self):   #column
        discussionTopics = db.getDiscussionTopics(self.conn, self.arg)
        page = []
        for topic in discussionTopics:
            page.append([content_element(topic['content'])])
            page.append([
                content_element("["+topic['user_name']+"]"),
                nav_button(str(topic['replyNum']) + " replies", "discussions", self.arg+"%"+str(topic['topic_id']))
            ])
            page.append([sg.HorizontalSeparator()])

        page.append([content_element()])
        page.append([nav_button('New Discussion','addTopic'), nav_button("Back", "-previous-")])
        return page

    def getDiscussions(self):   #column
        discussions = db.getDiscussions(self.conn, self.arg)
        
        page = []
        for discussion in discussions:
            page.append([content_element(discussion['content'])])
            page.append([content_element("["+discussion['user_name']+"]")])
            page.append([sg.HorizontalSeparator()])

        page.append([content_element()])
        page.append([nav_button('reply','addDiscussion'), nav_button("Back", "-previous-")])
        return page




