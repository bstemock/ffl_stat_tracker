# TO DO
# update other windows when scores or other stats are entered
# use python code to determine berth status
# implement overall statistics
# add head-to-head stats button and window
# add individual stats window

import os
import sys
import pandas as pd
from mysql import connector

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
    QStackedWidget,
    QWidget
)

from code.scoreboard import WeeklyScoreboard
from code.league_table import LeagueTable

os.environ["XDG_SESSION_TYPE"] = "xcb"


titleFont = QFont("Ubuntu", 14)
headerFont = QFont("Ubuntu", 12, QFont.Bold)
boldFont = QFont("Ubuntu", 11, QFont.Bold)
sidenoteFont = QFont("Ubuntu", 8)


def get_current():
    sql1 = "select max(year) as m from games"
    try:
        cursor.execute(sql1)
    except connector.Error as error:
        sys.exit("Error in get_current():\n" + error)
    current_year_ = list(map(list, cursor.fetchall()))[0][0]

    sql2 = """select max(week) as m 
              from (select * from games where away_score is not null) t 
              where t.year = %s""" % current_year_
    try:
        cursor.execute(sql2)
    except connector.Error as error:
        sys.exit("Error in get_current():\n" + error)
    current_week_ = list(map(list, cursor.fetchall()))[0][0]
    if current_week_ is None:
        current_week_ = 1
    return current_year_, current_week_


def get_years():
    sql = """select distinct(year) from games order by year desc"""
    try:
        cursor.execute(sql)
    except connector.Error as error:
        sys.exit("SQL Error in get_years():\n" + error)
    results = list(map(list, cursor.fetchall()))
    results = [i[0] for i in results]
    return results


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        current_year, current_week = get_current()
        years_list = get_years()
        self.window_titles = ["Main Menu", "League Table", "Weekly Scoreboard", "Schedules"]
        self.WeeklyScoreboard = WeeklyScoreboard(db, cursor, years_list, current_year, current_week)
        self.LeagueTable = LeagueTable(db, cursor, years_list, current_year)

        self.Stack = QStackedWidget()
        self.stack0 = QWidget()
        self.stack3 = QWidget()

        self.MainMenu()
        self.Schedules("Bryson")

        self.Stack.addWidget(self.stack0)
        self.Stack.addWidget(self.stack3)

        self.setWindowTitle(self.window_titles[0])
        self.Stack.setCurrentIndex(0)
        self.setCentralWidget(self.Stack)

    def MainMenu(self):
        layout = QVBoxLayout()

        label = QLabel("Please select an option.")
        label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        layout.addWidget(label)

        text1 = "League Table"
        button1 = QPushButton(text1)
        button1.clicked.connect(lambda checked: self.open_window(self.LeagueTable))
        layout.addWidget(button1)

        text2 = "Weekly Scoreboard"
        button2 = QPushButton(text2)
        button2.clicked.connect(lambda checked: self.open_window(self.WeeklyScoreboard))
        layout.addWidget(button2)

        text3 = "Schedules"
        button3 = QPushButton(text3)
        button3.clicked.connect(lambda checked: self.toggle_window(3))
        layout.addWidget(button3)

        self.stack0.setLayout(layout)

    def Schedules(self, owner):
        layout = QVBoxLayout()

        label = QLabel("%s's Statistics" % owner)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(label)

        self.stack3.setLayout(layout)

    def toggle_window(self, i):
        self.setWindowTitle(self.window_titles[i])
        self.Stack.setCurrentIndex(i)

    def open_window(self, w):
        if w.isVisible():
            w.hide()
        else:
            w.show()


# set up database access
db = connector.connect(host="localhost",
                       user="root",
                       password="password",
                       database="family_ffl")
cursor = db.cursor()

# run app
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
