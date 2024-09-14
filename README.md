# End-to-End Facial Recognition Login System with Database

## Project Description

This project implements an end-to-end facial recognition login system using Python, OpenCV, and a MySQL database. It allows users to register their faces and subsequently log in using facial recognition instead of traditional passwords.

## Installation and Setup
#### 1 Collect Face Data 
      python face_capture.py
      
#### 2 Train a Facial Recognition Model 
      python train.py

#### 3 Import Database
      python create_database.py

#### 4 Build the System
      python faces.py

#### 5 Test the System
      python faces_gui.py [user_id] [datetime{'dd/mm/yy-hh:mm:ss'}, default: '16/03/21-09:50:20']

## Usage

1. Register a new user by providing their name and capturing their facial image.
2. Log in using facial recognition by presenting your face to the camera.
3. The system will verify your identity and grant access if successful.









