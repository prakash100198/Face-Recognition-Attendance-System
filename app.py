##installing libraries
from imutils import paths
import cv2
import os
from datetime import datetime
import face_recognition
import pickle
import numpy as np
import pandas as pd
import streamlit as st



st.title('Face Recognition Attendance System')
st.sidebar.image('camera.png')

path = st.sidebar.text_input('Enter File Destination',value=r'D:\\Images',help="Path is Images folder in D drive, add your path with double backslash otherwise it won't work")
email=st.sidebar.text_input('Enter E-mail address')
@st.cache
def face_encodings(Path):
    image_paths = paths.list_images(Path)
    known_encodings= []
    known_names = []

    for (i,image_path) in enumerate(image_paths):
        ##extracting names
        name = image_path.split(os.path.sep)[-2]
        ##reading images
        image = cv2.imread(image_path)
        ##converting to RGB
        rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        ##locating face of each person
        boxes = face_recognition.face_locations(rgb,model='hog')
        #computing face embedding
        encodings = face_recognition.face_encodings(rgb,boxes)[0]
        known_encodings.append(encodings)
        known_names.append(name)
        #for encoding in encodings:

    ##saving data in form of dictionary
    data = {'encodings': known_encodings,'names':known_names}
    return data


def attendance(name):
    with open('attendance.csv','r+') as f:
        datalist = f.readlines()
        namelist= set()

        for lines in datalist:
            line = lines.split(',')
            namelist.add(line[0])
            #namelist.remove('Employee Name')

            if name not in namelist:
                now = datetime.now()
                dtString = now.strftime('%D  %H:%M:%S')
                f.writelines(f'\n{name},{dtString}')


def recording(data):
    start = st.checkbox('Start Recording')
    FRAME_WINDOW = st.image([])
    if start:
        st.write('Recording...')
    encodings = data['encodings']
    names = data['names']
    cap = cv2.VideoCapture(0)
    while start:
        success,img = cap.read()
        imgS = cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

        face_loc = face_recognition.face_locations(imgS)
        face_enc = face_recognition.face_encodings(imgS,face_loc)

        for encodeface,faceloc in zip(face_enc,face_loc):
            matches = face_recognition.compare_faces(encodings,encodeface)
            distance = face_recognition.face_distance(encodings,encodeface)

            match_index = np.argmin(distance)
            if matches[match_index]:
                name = names[match_index]
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.rectangle(img, (x1, y2 - 25), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.45, (255, 255, 255), 2)
                attendance(name)
            else: 
                name = 'Unknown'
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.rectangle(img, (x1, y2 - 25), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.45, (255, 255, 255), 2)
                attendance(name)   
        # cv2.imshow('Webcam',img)
        FRAME_WINDOW.image(img)
    else:
        st.write('Not Recording')

def send_email(filename,inp_email):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "prakash100198@gmail.com"
    toaddr = inp_email

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    t = datetime.now()
    dt = t.strftime('%D')
    msg['Subject'] = "Attendance list for : "+dt

    # string to store the body of the mail
    body = "Thank You for using our service!"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = filename
    attachment = open(path[:-6]+'final.csv', "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "bietzfcfgqjhoicd")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

data=face_encodings(path)
if len(data['names'])==0:
    st.write('First Enter Correct Path to Images in the Side Panel')
else:
    recording(data)

df = pd.read_csv('attendance.csv')
name_list=list(df['Employee Name'].unique())
time_list = []
for index in range(len(df['Employee Name'].unique())):
    time_list.append(df[df['Employee Name']==df['Employee Name'].unique()[index]]['Time'].iloc[0])
final_df = pd.DataFrame({'Employee Name':name_list,'Time Entered':time_list})
final_df.to_csv('final.csv',index=False)
if email:
    send_email('final.csv',email)
else:
    st.sidebar.write('Enter email to send attendance list for today')

st.text('\n\n\n\n\n\n\n\n\n\n\n\n')
st.text('Important Note:\nStore all your employee photos with name inside Images folder and make one dedicated\nfolder for one employee and store their image in that dedicated folder(with employee name). ')
