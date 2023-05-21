from flask import Flask, render_template, flash, request,session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from werkzeug.utils import secure_filename
import mysql.connector
import tkinter as tk
from tkinter import *
import cv2

import csv
import os
import numpy as np
from PIL import Image,ImageTk
import pandas as pd
import datetime
import time
import urllib
import urllib.request
import urllib.parse

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
def trainimg():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    global detector
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    try:
        global faces,Id
        faces, Id = getImagesAndLabels("TrainingImage")
    except Exception as e:
        l='please make "TrainingImage" folder & put Images'
       # Notification.configure(text=l, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
        #Notification.place(x=350, y=400)

    recognizer.train(faces, np.array(Id))
    try:
        recognizer.save("TrainingImageLabel\Trainner.yml")
    except Exception as e:
        q='Please make "TrainingImageLabel" folder'
        #Notification.configure(text=q, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
        #Notification.place(x=350, y=400)

    res = "Model Trained"  # +",".join(str(f) for f in Id)
    #Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
    #Notification.place(x=250, y=400)
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # create empth face list
    faceSamples = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image

        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces = detector.detectMultiScale(imageNp)
        # If a face is there then append that in the list as well as Id of it
        for (x, y, w, h) in faces:
            faceSamples.append(imageNp[y:y + h, x:x + w])
            Ids.append(Id)
    return faceSamples, Ids
def del_sc1():
    sc1.destroy()
def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry('300x100')
    sc1.iconbitmap('AMS.ico')
    sc1.title('Warning!!')
    sc1.configure(background='snow')
    Label(sc1,text='Enrollment & Name required!!!',fg='red',bg='white',font=('times', 16, ' bold ')).pack()
    Button(sc1,text='OK',command=del_sc1,fg="black"  ,bg="lawn green"  ,width=9  ,height=1, activebackground = "Red" ,font=('times', 15, ' bold ')).place(x=90,y= 50)

def del_sc2():
    sc2.destroy()
def err_screen1():
    global sc2
    sc2 = tk.Tk()
    sc2.geometry('300x100')
    sc2.iconbitmap('AMS.ico')
    sc2.title('Warning!!')
    sc2.configure(background='snow')
    Label(sc2,text='Please enter your subject name!!!',fg='red',bg='white',font=('times', 16, ' bold ')).pack()
    Button(sc2,text='OK',command=del_sc2,fg="black"  ,bg="lawn green"  ,width=9  ,height=1, activebackground = "Red" ,font=('times', 15, ' bold ')).place(x=90,y= 50)

def Fillattendances():
        sub = "trest"
        now = time.time()  ###For calculate seconds of video
        future = now + 20
        if time.time() < future:
            if sub == '':
                err_screen1()
            else:
                recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
                try:
                    recognizer.read("TrainingImageLabel\Trainner.yml")
                except:
                    e = 'Model not found,Please train model'
                   # Notifica.configure(text=e, bg="red", fg="black", width=33, font=('times', 15, 'bold'))
                   # Notifica.place(x=20, y=250)

                harcascadePath = "haarcascade_frontalface_default.xml"
                faceCascade = cv2.CascadeClassifier(harcascadePath)
                df = pd.read_csv("StudentDetails\StudentDetails.csv")
                cam = cv2.VideoCapture(0)
                font = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ['Enrollment', 'Name', 'Date', 'Time']
                attendance = pd.DataFrame(columns=col_names)
                while True:
                    ret, im = cam.read()
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        global Id

                        Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                        if (conf < 70):
                            print(conf)
                            global Subject
                            global aa
                            global date
                            global timeStamp
                            Subject = "sample5"
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            aa = df.loc[df['Enrollment'] == Id]['Name'].values
                            global tt
                            tt = str(Id) + "-" + aa
                            En = '15624031' + str(Id)
                            attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 7)
                            cv2.putText(im, str(tt), (x + h, y), font, 1, (255, 255, 0,), 4)

                        else:
                            Id = 'Unknown'
                            tt = str(Id)
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                            cv2.putText(im, str(tt), (x + h, y), font, 1, (0, 25, 255), 4)
                    if time.time() > future:
                        break

                    attendance = attendance.drop_duplicates(['Enrollment'], keep='first')
                    cv2.imshow('Filling attedance..', im)
                    key = cv2.waitKey(30) & 0xff
                    if key == 27:
                        break

                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                Hour, Minute, Second = timeStamp.split(":")
                fileName = "Attendance/" + Subject + "_" + date + "_" + Hour + "-" + Minute + "-" + Second + ".csv"
                attendance = attendance.drop_duplicates(['Enrollment'], keep='first')
                print(attendance)
                attendance.to_csv(fileName, index=False)

                ##Create table for Attendance
                date_for_DB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                DB_Table_name = str(Subject + "_" + date_for_DB + "_Time_" + Hour + "_" + Minute + "_" + Second)
                import pymysql.connections

                ###Connect to the database
                try:
                    global cursor
                    connection = pymysql.connect(host='localhost', user='root', password='', db='face')
                    cursor = connection.cursor()
                except Exception as e:
                    print(e)

                sql = "CREATE TABLE " + DB_Table_name + """
                (ID INT NOT NULL AUTO_INCREMENT,
                 ENROLLMENT varchar(100) NOT NULL,
                 NAME VARCHAR(50) NOT NULL,
                 DATE VARCHAR(20) NOT NULL,
                 TIME VARCHAR(20) NOT NULL,
                     PRIMARY KEY (ID)
                     );
                """
                ####Now enter attendance in Database
                insert_data = "INSERT INTO sample(ID,ENROLLMENT,NAME,DATE,TIME) VALUES (0, %s, %s, %s,%s)"
                VALUES = (str(Id), str(aa), str(date), str(timeStamp))
                try:
                    cursor.execute(sql)  ##for create a table
                    cursor.execute(insert_data, VALUES)  ##For insert data into table
                except Exception as ex:
                    print(ex)  #

                M = 'Attendance filled Successfully'
                print(M)
                print(Id)
                print(str(aa))
                print(date)
                listToStr = ''.join(map(str, aa))
                print(timeStamp)
                conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
                cursor = conn.cursor()
                cursor.execute("select * from studentatten where sid='" + str(Id)+ "' and name='" + str(listToStr) + "' and date='"+str(date)+"'")
                data = cursor.fetchone()
                if data is None:
                    print("hai")
                    conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
                    cursor = conn.cursor()
                    cursor.execute(
                        "insert into studentatten values('','" + str(Id) + "','" + str(listToStr) + "','" + str(
                            date) + "','" + str(timeStamp) + "','')")
                    conn.commit()
                    conn.close()

                else:
                    conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
                    cursor = conn.cursor()
                    cursor.execute("update studentatten set otime='"+str(timeStamp)+"'")
                    conn.commit()
                    conn.close()




                #Notifica.configure(text=M, bg="Green", fg="white", width=33, font=('times', 15, 'bold'))
                #Notifica.place(x=20, y=250)

                cam.release()
                cv2.destroyAllWindows()

                import csv
                import tkinter
                root = tkinter.Tk()
                root.title("Attendance of " + Subject)
                root.configure(background='snow')
                cs = 'C:/Users/acer/PycharmProjects/student/' + fileName
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            # i've added some styling
                            label = tkinter.Label(root, width=8, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="lawn green", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()
                print(attendance)
@app.route("/")
def homepage():

    return render_template('index.html')

@app.route("/admin")
def admin():

    return render_template('admin.html')

@app.route("/adminhome")
def adminhome():
    #trainimg()
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
    cursor = conn.cursor()
    cursor.execute("select * from register")
    data = cursor.fetchall()


    return render_template('adminhome.html',data=data)

@app.route("/addstudent")
def addstudent():

    return render_template('addstudent.html')

@app.route("/view")
def view():

    return render_template('view.html')

@app.route("/student")
def student():

    return render_template('student.html')

@app.route("/adminlog",methods=['GET','POST'])
def adminlog():
    if request.method == 'POST':
        uname=request.form['uname']
        password=request.form['password']
        print(uname)
        print(password)
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute("select * from admin where uname='"+uname+"' and password='"+password+"'")
        data=cursor.fetchone()
        if data is None:
            return "user name and password incorrect"
        else:
            return render_template("adminhome.html")

@app.route("/studentregister", methods=['GET', 'POST'])
def studentregister():
     if request.method == 'POST':
          studentid = request.form['staffid']
          name = request.form['name']
          gender = request.form['gender']
          bgroup = request.form['bgroup']
          desg = ''
          depart = request.form['depart']
          subject = ''
          email = request.form['email']
          pnumber = request.form['pnumber']
          address = request.form['address']
          conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
          cursor = conn.cursor()
          cursor.execute("insert into register values('','"+studentid+"','"+name+"','"+gender+"','"+bgroup+"','"+depart+"','"+email+"','"+pnumber+"','"+address+"','')")
          conn.commit()
          conn.close()

          cam = cv2.VideoCapture(0)
          cam.set(3, 640)  # set video width
          cam.set(4, 480)  # set video height

          # make sure 'haarcascade_frontalface_default.xml' is in the same folder as this code
          face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

          # For each person, enter one numeric face id (must enter number start from 1, this is the lable of person 1)

          face_id = studentid
          print(face_id)

          print("\n [INFO] Initializing face capture. Look the camera and wait ...")
          # Initialize individual sampling face count
          count = 0
          while (True):

              ret, img = cam.read()
              gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
              faces = face_detector.detectMultiScale(gray, 1.3, 5)

              for (x, y, w, h) in faces:
                  cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                  count += 1

                  # Save the captured image into the datasets folder
                  cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])

                  cv2.imshow('image', img)

              k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
              if k == 27:
                  break
              elif count >= 30:  # Take 30 face sample and stop video
                  break
          # Do a bit of cleanup
          print("\n [INFO] Exiting Program and cleanup stuff")
          cam.release()
          cv2.destroyAllWindows()
          path = 'dataset'

          recognizer = cv2.face.LBPHFaceRecognizer_create()
          detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

          def getImagesAndLabels(path):

              imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
              faceSamples = []
              ids = []

              for imagePath in imagePaths:

                  PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
                  img_numpy = np.array(PIL_img, 'uint8')

                  id = int(os.path.split(imagePath)[-1].split(".")[1])
                  faces = detector.detectMultiScale(img_numpy)

                  for (x, y, w, h) in faces:
                      faceSamples.append(img_numpy[y:y + h, x:x + w])
                      ids.append(id)

              return faceSamples, ids

          print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
          faces, ids = getImagesAndLabels(path)
          recognizer.train(faces, np.array(ids))

          # Save the model into trainer/trainer.yml
          recognizer.write('trainer/trainer.yml')  # recognizer.save() worked on Mac, but not on Pi

          # Print the numer of faces trained and end program
          print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

          return render_template("register1.html")

@app.route("/studentlogin",methods=['GET','POST'])
def studentlogin():
    if request.method == 'POST':
        uname=request.form['uname']
        password=request.form['password']
        session['sid']=password
        print(uname)
        print(password)
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute("select * from register where name='"+uname+"' and studentid='"+password+"'")
        data=cursor.fetchone()
        if data is None:
            return "user name and password incorrect"
        else:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
            cursor = conn.cursor()
            cursor.execute("select * from register where studentid='" + password + "'")
            data = cursor.fetchall()
            return render_template("studenthome.html",data=data)

@app.route("/getimage",methods=['GET','POST'])
def getimage():
    if request.method == 'POST':

        l1 =request.form['sid']
        l2 =request.form['name']
        cam = cv2.VideoCapture(0)
        cam.set(3, 640)  # set video width
        cam.set(4, 480)  # set video height

        # make sure 'haarcascade_frontalface_default.xml' is in the same folder as this code
        face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # For each person, enter one numeric face id (must enter number start from 1, this is the lable of person 1)

        face_id = l1
        print(face_id)

        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        # Initialize individual sampling face count
        count = 0
        while (True):

            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                count += 1

                # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])

                cv2.imshow('image', img)

            k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 30:  # Take 30 face sample and stop video
                break
        # Do a bit of cleanup
        print("\n [INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()
        path = 'dataset'

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

        def getImagesAndLabels(path):

            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
            faceSamples = []
            ids = []

            for imagePath in imagePaths:

                PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
                img_numpy = np.array(PIL_img, 'uint8')

                id = int(os.path.split(imagePath)[-1].split(".")[1])
                faces = detector.detectMultiScale(img_numpy)

                for (x, y, w, h) in faces:
                    faceSamples.append(img_numpy[y:y + h, x:x + w])
                    ids.append(id)

            return faceSamples, ids

        print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces, ids = getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))

        # Save the model into trainer/trainer.yml
        recognizer.write('trainer/trainer.yml')  # recognizer.save() worked on Mac, but not on Pi

        # Print the numer of faces trained and end program
        print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
        #Notification.place(x=450, y=400)
@app.route("/Attendance")
def testatten():
    now = time.time()  ###For calculate seconds of video
    future = now + 20
   # uid = request.form['uid']
    #print(uid)

    my_list = ['']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
    cursor = conn.cursor()
    cursor.execute("select * from register")
    data = cursor.fetchall()
    print(data)
    for data1 in data:
        my_list.append(data1[2])
    print(my_list)

    import cv2
    import numpy as np
    import os

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')  # load trained model
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    # iniciate id counter, the number of persons you want to include
    id = 0  # two persons (e.g. Jacob, Jack)

    names = my_list  # key in names, start from the second place, leave first empty

    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # set video widht
    cam.set(4, 480)  # set video height

    # Define min window size to be recognized as a face
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:

        ret, img = cam.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 50):
                id1 = id

                # id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
                cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)


            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
                tt = str(id)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 25, 255), 7)
                cv2.putText(img, str(tt), (x + h, y), font, 1, (0, 25, 255), 4)


        cv2.imshow('camera', img)
        print(id)
        if time.time() > future:
            break

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
    cursor1 = conn.cursor()
    cursor1.execute("select * from register where studentid='" + str(id) + "'")
    data2 = cursor1.fetchone()
    if data2 is None:
        return "Unknown User"
    else:
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        conn5 = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor5 = conn5.cursor()
        cursor5.execute("select * from register where studentid='" + str(id) + "'")
        data5 = cursor5.fetchone()
        print(data5[2])
        listToStr = data5[2]

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute(
            "select * from studentatten where sid='" + str(id) + "' and name='" + str(listToStr) + "' and date='" + str(
                date) + "'")
        data = cursor.fetchone()
        if data is None:
            print("hai")
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
            cursor = conn.cursor()
            cursor.execute(
                "insert into studentatten values('','" + str(id) + "','" + str(listToStr) + "','" + str(
                    date) + "','" + str(timeStamp) + "','')")
            conn.commit()
            conn.close()

        else:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
            cursor = conn.cursor()
            cursor.execute("update studentatten set otime='" + str(timeStamp) + "'")
            conn.commit()
            conn.close()
        # Do a bit of cleanup
        print("\n [INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()


        return "Attendance Successfully"

@app.route("/view1",methods=['GET','POST'])
def view1():
    if request.method == 'POST':
        date = request.form['date']
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute("select * from studentatten where date='" + date + "'")
        data = cursor.fetchall()
        return render_template("view.html",data=data)


@app.route("/studenthome")
def studenthome():

        sid = session['sid']
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute("select * from register where studentid='" + sid + "'")
        data = cursor.fetchall()
        return render_template("studenthome.html",data=data)

@app.route("/sview")
def sview():

        sid = session['sid']
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute("select * from studentatten where sid='" + sid + "'")
        data = cursor.fetchall()
        return render_template("studentview.html", data=data)
@app.route("/addattend")
def addattend():


        conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
        cursor = conn.cursor()
        cursor.execute("select * from register")
        data = cursor.fetchall()
        return render_template("addaten.html",data=data)


@app.route("/addatten1", methods=['GET', 'POST'])
def addatten1():
     if request.method == 'POST':
          studentid = request.form['studid']
          tw = request.form['tw']
          np = request.form['np']
          p = request.form['p']
          details = request.form['details']
          conn = mysql.connector.connect(user='root', password='', host='localhost', database='student')
          cursor = conn.cursor()
          cursor.execute("insert into addatten values('','"+studentid+"','"+tw+"','"+np+"','"+p+"','"+details+"')")
          conn.commit()
          conn.close()
          conn1 = mysql.connector.connect(user='root', password='', host='localhost', database='student')
          cursor1 = conn1.cursor()
          cursor1.execute("select * from register where studentid='"+studentid+"'")
          data = cursor1.fetchone()
          print(data[6])
          ph=data[6]

          url = 'http://bulksms.mysmsmantra.com:8080/WebSMS/SMSAPI.jsp?username=fantasy5535&password=1163974702&sendername=Sample&mobileno=91%s,&message=%s' % (
              ph, details)
          print(urllib.request.urlopen(url).read())




          return render_template("addaten.html")
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)