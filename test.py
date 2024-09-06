import sys

#local classes
from interface import *

# 1 Create database connection


def main():
    conn = db.connect()
    userID = int(sys.argv[1])
    try:
        _datetime = sys.argv[2]
    except:
        _datetime = "16/03/21-09:50:20"

    session = Session(conn, userID, dt.datetime.strptime(_datetime,'%d/%m/%y-%H:%M:%S'))

    win = session.getLoginnedWindow()

    while True:
        event, values = win.Read()
        if event is None or event =='Cancel':
            break
        #update window
        print(event)
        print(values)
        if session.update(event, values) == True:
            win.Close()
            win = session.getWindow()
    win.Close()
    session.logout()

main()

# conn = db.connect()
# print(db.getCourseList(conn,1))

