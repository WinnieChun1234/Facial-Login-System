from database import *

conn = connect(_db = "")

def createDatabase(conn):
    mycursor = conn.cursor()

    query = """
        CREATE DATABASE IF NOT EXISTS facerecognition;
    """

    mycursor.execute(query)
    createTables(conn)

def createTables(conn):
    conn.database = "facerecognition"
    mycursor = conn.cursor()

    query = """
        DROP TABLE IF EXISTS Discussions CASCADE;
        DROP TABLE IF EXISTS CourseMaterials CASCADE;
        DROP TABLE IF EXISTS CourseTimeslots CASCADE;
        DROP TABLE IF EXISTS Teaches CASCADE;
        DROP TABLE IF EXISTS Takes CASCADE;
        DROP TABLE IF EXISTS Courses CASCADE;
        DROP TABLE IF EXISTS Teachers CASCADE;
        DROP TABLE IF EXISTS Students CASCADE;
        DROP TABLE IF EXISTS Users CASCADE;


        CREATE TABLE IF NOT EXISTS Users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(20),
            login_time VARCHAR(20),
            logout_time VARCHAR(20),
            email VARCHAR(200)
        );
        
        CREATE TABLE IF NOT EXISTS Students (
            user_id INT PRIMARY KEY,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
        
        CREATE TABLE IF NOT EXISTS Teachers (
            user_id INT PRIMARY KEY,
            office VARCHAR(1000),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Courses (
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(10),
            course_name VARCHAR(200),
            course_info VARCHAR(2000)
        );

        CREATE TABLE IF NOT EXISTS Takes (
            user_id INT,
            course_id INT,
            FOREIGN KEY (user_id) REFERENCES Students(user_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        );

        CREATE TABLE IF NOT EXISTS Teaches (
            user_id INT,
            course_id INT,
            welcome_message VARCHAR(2000),
            FOREIGN KEY (user_id) REFERENCES Teachers(user_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        );

        CREATE TABLE IF NOT EXISTS CourseTimeslots (
            course_id INT,
            weekday INT(1),
            start_time VARCHAR(5),
            duration INT,
            zoom_link VARCHAR(200),
            course_venue VARCHAR(10),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        );

        
        CREATE TABLE IF NOT EXISTS CourseMaterials (
            material_id INT AUTO_INCREMENT PRIMARY KEY,
            course_id INT,
            user_id INT,
            material_name VARCHAR(200),
            material_link VARCHAR(200),
            visible_to_students BOOLEAN,
            FOREIGN KEY (course_id) REFERENCES Courses(course_id),
            FOREIGN KEY (user_id) REFERENCES Teachers(user_id)
        );

        
        CREATE TABLE IF NOT EXISTS Discussions (
            course_id INT,
            topic_id INT,
            discussion_id INT,
            user_id INT,
            content VARCHAR(2000),
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        );
    """
    
    for q in query.split(";"):
        if q.strip()!="":
            mycursor.execute(q)

    mycursor.execute("SHOW TABLES")
    for x in mycursor:
        print(x)

    insertData(conn)

def insertData(conn):
    mycursor=conn.cursor()
    query = """
        INSERT INTO Users (user_id, user_name, email) VALUES (1,'Peter', 'hologram@connect.hku.hk');
        INSERT INTO Users (user_id, user_name, email) VALUES (2,'Yile', 'yile502733644@gmail.com');
        INSERT INTO Users (user_id, user_name, email) VALUES (3,'Teacher(demo)', 'hologram@connect.hku.hk');
        INSERT INTO Students (user_id) VALUES (1);
        INSERT INTO Students (user_id) VALUES (2);
        INSERT INTO Teachers (user_id, office) VALUES (3, "CB326");

        INSERT INTO Courses (course_id, course_code, course_name, course_info)
        VALUES (1,"COMP3278", 'Introduction to database management systems [Section 2B, 2020]', 'This course studies the principles, design, administration, and implementation of database management systems. Topics include: entity-relationship model, relational model, relational algebra, database design and normalization, database query languages, indexing schemes, integrity and concurrency control.') ;
        INSERT INTO Courses (course_id, course_code, course_name, course_info)
        VALUES (2,"COMP2396", 'Object-oriented programming and Java [Section 2B, 2020]', 'OOP and Java information') ;
        INSERT INTO Courses (course_id, course_code, course_name, course_info)
        VALUES (3,"COMP3297", 'Software engineering [Section 2B, 2020]', 'It is an introduction to the field of software engineering.') ;

        INSERT INTO Takes VALUES (1,1);
        INSERT INTO Takes VALUES (1,2);
        INSERT INTO Takes VALUES (1,3);
        INSERT INTO Takes VALUES (2,1);

        INSERT INTO Teaches VALUES (3,1,'Please feel free to contact me (Dr. Ping Luo), TA Mr. Jiannan Wu, Mr. Yuanfeng Ji, and Ms. Zhouxia Wang. If you have any questions with respect to the lecture/tutorial materials, we are very happy to help!');
        INSERT INTO Teaches VALUES (3,2,'Hello! Welcome to COMP2396 Object-oriented Programming and Java! Cheers, Dr. T.W. Chim');
        INSERT INTO Teaches VALUES (3,3,'This class is taught by George Mitcheson. Feel free to catch us online during consultation hours!');
        
        INSERT INTO CourseTimeslots VALUES (1,2,"09:30",1,"https://hku.zoom.com.cn/j/2640918958?pwd=UmFpek1YMkUzNTFoL0ljRW84M1VLUT09", "ONLINE");
        INSERT INTO CourseTimeslots VALUES (1,5,"09:30",2,"https://hku.zoom.us/j/97686555806?pwd=NWxSNVRKTlNDU0NjYTgremxaQ3pldz09", "ONLINE");
        
        INSERT INTO CourseTimeslots VALUES (2,2,"12:30",1,"https://hku.zoom.us/j/97902227890?pwd=QnlWWHdudGY0K21GeHhTa3JDQ3Urdz09", "ONLINE");
        INSERT INTO CourseTimeslots VALUES (2,5,"12:30",2,"https://hku.zoom.us/j/97902227890?pwd=QnlWWHdudGY0K21GeHhTa3JDQ3Urdz09", "ONLINE");
        
        INSERT INTO CourseTimeslots VALUES (3,2,"13:30",2,"https://hku.zoom.us/j/94819540377?pwd=STIzaGlyTytrZFZ4TGZHelZZTTgxUT09", "ONLINE");
        INSERT INTO CourseTimeslots VALUES (3,5,"14:30",1,"https://hku.zoom.us/j/94819540377?pwd=STIzaGlyTytrZFZ4TGZHelZZTTgxUT09", "ONLINE");
        

        INSERT INTO CourseMaterials (course_id, user_id, material_name, material_link, visible_to_students)
        VALUES (1,3,"Course Information","https://moodle.hku.hk/mod/resource/view.php?id=2076221", 1);
        INSERT INTO Discussions VALUES (1,1,1,1,"When will the group project be due?");
        INSERT INTO Discussions VALUES (1,1,2,3,"Presentation slide deadline on April 19.");
    """
    for q in query.split(";"):
        if q.strip()!="":
            mycursor.execute(q)
    conn.commit()


createDatabase(conn)


