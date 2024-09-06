
####### settings ########

# facial recognition
DEFAULT_CONFIDENCE = 30
FRAMES_REQUIRED = 5

#database password
HOST="localhost"
USER="root"
PASSWORD="123456"
DATABASE="facerecognition"

#email account 
EMAIL_ACCOUNT = "comp3278group21@gmail.com"
EMAIL_PASSWORD = "comp3278***"

#########################

import urllib
import numpy as np
import mysql.connector
import cv2
import pyttsx3
import pickle
from datetime import datetime
import sys
import PySimpleGUI as sg
import datetime as dt
import os

DEFAULT_WINDOW_SIZE = (720,576)

table_color_1 = "#ffffff"
table_color_2 = "#c4faff"
table_color_3 = "#a0e1ff"
table_text_color = "black"

default_button_textcolor = 'white'
default_button_color = '#00b48d'
highlight_button_color = '#f30089'

weekdays = [
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri"
]

DEFAULT_PAGE = "timetable"
DEFAULT_ARG = ""

DATE_FORMAT = "%H:%M %d/%m/%Y"

sg.theme('LightBlue')
sg.theme_input_background_color('white')

def table_cell(text="", color_odd=1, justify="center", color=None):
    if color == None:
        color = table_color_1 if color_odd else table_color_2
    return [sg.Text(
        text,
        text_color=table_text_color,
        background_color=color,
        justification=justify,
        size=(9,2),
        pad=(0,0)
    )]

def nav_button(name="Main Page", page=DEFAULT_PAGE, arg=DEFAULT_ARG):
    return  sg.Button(
        name,
        key=(str(page)+"%"+str(arg)),
        size=(len(name)+4,1)
    )

def title_element(text="title", justify="center"):
    return sg.Text(
        text,
        size=(100,1),
        justification=justify
    )

def header_element(text="header", justify="right"):
    return sg.Text(
        text,
        size=(100,1),
        justification=justify
    )


def content_element(text="", justify="right", _size=None):
    if _size == None:
        x = len(text)//60
        if x > 0:
            _size = (60,x+1)
        else:
            _size = (len(text),1)
    return sg.Text(
        text,
        size=_size,
        justification=justify
    )

def link_button(name, link, length = 10, color = default_button_color):
    return  sg.Button(
        name,
        key=("link%"+link),
        size=(length,1),
        button_color=(default_button_textcolor, color)
    )

