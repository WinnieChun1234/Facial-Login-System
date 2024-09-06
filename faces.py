from interface import *

def main():
    # 1 Create database connection
    myconn = db.connect()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    cursor = myconn.cursor()


    #2 Load recognize and read label from model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("train.yml")

    labels = {"person_name": 1}
    with open("labels.pickle", "rb") as f:
        labels = pickle.load(f)
        labels = {v: k for k, v in labels.items()}

    # create text to speech
    engine = pyttsx3.init()
    rate = engine.getProperty("rate")
    engine.setProperty("rate", 175)


    ################################# define the window layout #################################

    layout = [[sg.Text('Face Recognition', justification='center', font='Helvetica 20')],
            [sg.Image(filename='assets/main_campus-2.png', key='image')],
            [sg.Button(key='-main-', button_text = 'Login', size=(10, 1), font='Helvetica 14'),
            sg.Button('Exit', size=(10, 1), font='Helvetica 14'), ]]





    #############################################################################################







    # create the window and show it without the plot
    window = sg.Window('Face Recognition Login',
    layout,
    size = DEFAULT_WINDOW_SIZE,
    element_padding = None,
    margins = (None, None),
    element_justification = "center")

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    # Define camera and detect face
    face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    recording = False
    success=False
    login_id=None
    matched_frames=0

    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        elif event == '-main-':
            recording = not(recording)
            if recording:
                window['-main-'].update(text = 'Cancel')
            else:
                window['-main-'].Update(text = 'Login')
                window['image'].update(filename='assets/main_campus-2.png')

        if recording:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

            for (x, y, w, h) in faces:
                print(x, w, y, h)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                # predict the id and confidence for faces
                id_, conf = recognizer.predict(roi_gray)

                # If the face is recognized
                if conf >= DEFAULT_CONFIDENCE:
                    # print(id_)
                    # print(labels[id_])
                    font = cv2.QT_FONT_NORMAL
                    id = 0
                    id += 1
                    name = labels[id_]
                    current_name = name
                    color = (255, 0, 0)
                    stroke = 2
                    cv2.putText(frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), (2))

                    # Find the student's information in the database.
                    select = "SELECT user_id FROM Users WHERE user_name='%s'" % (name)
                    name = cursor.execute(select)
                    result = cursor.fetchall()
                    # print(result)
                    data = "error"

                    for x in result:
                        data = x[0]

                    # If the student's information is not found in the database
                    if data == "error":
                        print("The student", current_name, "is NOT FOUND in the database.")

                    # If the student's information is found in the database
                    else:
                        matched_frames +=1
                        if matched_frames >= FRAMES_REQUIRED:
                            """
                            Implement useful functions here.
                            Check the course and classroom for the student.
                                If the student has class room within one hour, the corresponding course materials
                                    will be presented in the GUI.
                                if the student does not have class at the moment, the GUI presents a personal class 
                                    timetable for the student.

                            """
                            success = True
                            login_id = data

                # If the face is unrecognized
                else: 
                    color = (255, 0, 0)
                    stroke = 2
                    font = cv2.QT_FONT_NORMAL
                    cv2.putText(frame, "UNKNOWN", (x, y), font, 1, color, stroke, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), (2))
                    print("Your face is not recognized")
                    success = False
                    login_id = None
                    
            if success:
                window.Close()
                cap.release()
                cv2.destroyAllWindows()
                break
            
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)



    if success:
        conn = db.connect()
        userID = login_id

        session = Session(conn, userID)
        session.login()
        
        win = session.getLoginnedWindow()

        while True:
            event, values = win.Read()
            if event is None or event =='Cancel':
                break
            # update window
            # print(event)
            # print(values)
            if session.update(event, values) == True:
                win.Close()
                win = session.getWindow()
        win.Close()
        session.logout()


        

main()