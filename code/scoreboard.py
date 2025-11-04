# TO DO
# 1: add team records
# 2: update league table on saving changes
# 3: implement playoff view/edit layouts
# 4: see about background gray bars behind second and fourth row

import os
import sys
import pandas as pd
from mysql import connector

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QWidget
)

titleFont = QFont("Ubuntu", 14)
headerFont = QFont("Ubuntu", 12, QFont.Bold)
boldFont = QFont("Ubuntu", 11, QFont.Bold)
sidenoteFont = QFont("Ubuntu", 8)


def get_scores(cursor, year, week):
    cursor.callproc("get_weekly_scoreboard", [year, week])
    proc_results = next(cursor.stored_results(), None)
    if proc_results:
        results = proc_results.fetchall()
        field_names = proc_results.column_names
    else:
        sys.exit("ERROR: No results returned by get_weekly_scoreboard process.")
    scores = pd.DataFrame(results, columns=field_names)
    return scores
#
#
# def get_years(cursor):
#     sql = """select distinct(year) from games order by year desc"""
#     try:
#         cursor.execute(sql)
#     except connector.Error as error:
#         sys.exit("SQL Error in get_years():\n" + error)
#     results = list(map(list, cursor.fetchall()))
#     results = [i[0] for i in results]
#     return results


def get_weeks(cursor, year):
    sql = """select distinct(week) from games where year = %s order by week asc""" % year
    try:
        cursor.execute(sql)
    except connector.Error as error:
        sys.exit("SQL Error in get_weeks():\n" + error)
    results = list(map(list, cursor.fetchall()))
    results = [i[0] for i in results]
    return results


class WeeklyScoreboard(QStackedWidget):
    def __init__(self, db, cursor, years_list, current_year, current_week):
        super().__init__()
        self.db, self.cursor, self.current_year, self.current_week = db, cursor, current_year, current_week
        self.years_list = years_list
        self.scoreboard_columns = ["away_team_name", "away_owner", "away_proj", "away_score", "",
                                   "home_score", "home_proj", "home_owner", "home_team_name"]
        self.column_widths = [180, 100, 60, 50, 30, 50, 60, 100, 180]
        self.setWindowTitle("Weekly Scoreboard")
        self.resize(850, 325)
        self.setMinimumSize(850, 325)

        self.stack1 = QWidget()
        self.stack2 = QWidget()

        layout1 = self.ViewRegularLayout(current_year, current_week)
        layout2 = self.EditRegularLayout(current_year, current_week)

        self.stack1.setLayout(layout1)
        self.stack2.setLayout(layout2)

        self.addWidget(self.stack1)
        self.addWidget(self.stack2)

        self.setCurrentIndex(0)

    def ViewRegularLayout(self, year, week):
        scores = get_scores(self.cursor, year, week)
        scores.replace({None: "--"}, inplace=True)

        layout = QVBoxLayout()

        label = QLabel("%s Week %s Scoreboard" % (year, week))
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        label.setFont(titleFont)
        layout.addWidget(label, stretch=1)

        score_layout = QGridLayout()
        score_layout.setContentsMargins(10, 10, 10, 10)
        score_layout.setSpacing(0)

        label = QLabel("Away")
        label.setFont(headerFont)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("padding-left: 2px;")
        score_layout.addWidget(label, 0, 0)

        label = QLabel("(Projected)")
        label.setFont(sidenoteFont)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 2)

        label = QLabel("Score")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 3)

        label = QLabel("|")
        label.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(label, 0, 4)

        label = QLabel("Score")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 5)

        label = QLabel("(Projected)")
        label.setFont(sidenoteFont)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 6)

        label = QLabel("Home")
        label.setFont(headerFont)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet("padding-right: 2px;")
        score_layout.addWidget(label, 0, 8)

        for i, row in scores.iterrows():
            for j, col in enumerate(self.scoreboard_columns):
                if j == 4:
                    label = QLabel("|")
                    label.setAlignment(Qt.AlignCenter)
                else:
                    label = QLabel(str(row[col]))

                label.setFixedSize(self.column_widths[j], 35)

                if j in [1, 2, 6, 7]:
                    label.setText("(%s)" % row[col])
                    label.setFont(sidenoteFont)
                if j in [0, 1, 5, 6]:
                    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                elif j in [2, 3, 7, 8]:
                    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if i % 2 == 1:
                    label.setStyleSheet("background-color: gainsboro")
                if j < 4 and row["winner"] == "Away":
                    label.setStyleSheet(label.styleSheet() + "; font-weight: bold")
                elif j > 4 and row["winner"] == "Home":
                    label.setStyleSheet(label.styleSheet() + "; font-weight: bold")
                if j == 0:
                    label.setStyleSheet(label.styleSheet() + "; padding-left: 2px")
                elif j == 8:
                    label.setStyleSheet(label.styleSheet() + "; padding-right: 2px")
                score_layout.addWidget(label, i + 1, j)

        layout.addLayout(score_layout, stretch=len(scores) + 1)

        options_layout = QHBoxLayout()
        weeks_list = get_weeks(self.cursor, year)

        button1 = QPushButton("Edit Scores")
        button1.setFixedWidth(120)
        button1.clicked.connect(self.toggle_layout)
        options_layout.addWidget(button1)

        label1 = QLabel("Year:")
        label1.setFixedWidth(35)
        options_layout.addWidget(label1)

        dropdown1 = QComboBox()
        dropdown1.addItems(map(str, self.years_list))
        dropdown1.setCurrentIndex(self.years_list.index(year))
        dropdown1.setFixedWidth(60)
        dropdown1.currentTextChanged.connect(lambda text:
                                             self.change_weeks(int(text), int(dropdown2.currentText())))
        options_layout.addWidget(dropdown1)

        label2 = QLabel("Week:")
        label2.setFixedWidth(40)
        options_layout.addWidget(label2)

        dropdown2 = QComboBox()
        dropdown2.addItems(map(str, weeks_list))
        dropdown2.setCurrentIndex(weeks_list.index(week))
        dropdown2.setFixedWidth(50)
        dropdown2.currentTextChanged.connect(lambda text:
                                             self.change_weeks(int(dropdown1.currentText()), int(text)))
        options_layout.addWidget(dropdown2)

        spacer = QSpacerItem(450, 0, QSizePolicy.Ignored, QSizePolicy.Minimum)
        options_layout.addItem(spacer)

        layout.addLayout(options_layout, stretch=1)

        return layout

    def EditRegularLayout(self, year, week):
        scores = get_scores(self.cursor, year, week)
        scores.replace({None: "--"}, inplace=True)

        layout = QVBoxLayout()

        label = QLabel("%s Week %s Scoreboard" % (year, week))
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        label.setFont(titleFont)
        layout.addWidget(label, stretch=1)

        score_layout = QGridLayout()
        score_layout.setContentsMargins(10, 10, 10, 10)
        score_layout.setSpacing(0)
        LineEdit_scores = [(QLineEdit(), QLineEdit()) for _ in range(len(scores))]
        LineEdit_projs = [(QLineEdit(), QLineEdit()) for _ in range(len(scores))]

        label = QLabel("Away")
        label.setFont(headerFont)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 0)

        label = QLabel("(Projected)")
        label.setFont(sidenoteFont)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 2)

        label = QLabel("Score")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 3)

        label = QLabel("|")
        label.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(label, 0, 4)

        label = QLabel("Score")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 5)

        label = QLabel("(Projected)")
        label.setFont(sidenoteFont)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 6)

        label = QLabel("Home")
        label.setFont(headerFont)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        score_layout.addWidget(label, 0, 8)

        for i, row in scores.iterrows():
            for j, col in enumerate(self.scoreboard_columns):
                if j == 4:
                    widget = QLabel("|")
                    widget.setAlignment(Qt.AlignCenter)
                elif j in [3, 5]:
                    widget = LineEdit_scores[i][int((j - 3) / 2)]
                    if isinstance(row[col], str):
                        widget.setPlaceholderText(str(row[col]))
                    else:
                        widget.setText(str(row[col]))
                elif j in [2, 6]:
                    widget = LineEdit_projs[i][int((j - 2) / 4)]
                    if isinstance(row[col], str):
                        widget.setPlaceholderText(str(row[col]))
                    else:
                        widget.setText(str(row[col]))
                else:
                    widget = QLabel(str(row[col]))

                widget.setFixedSize(self.column_widths[j], 35)

                if j in [1, 7]:
                    widget.setText("(%s)" % row[col])
                    widget.setFont(sidenoteFont)
                if j in [0, 1, 5, 6]:
                    widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                elif j in [2, 3, 7, 8]:
                    widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if i % 2 == 1:
                    widget.setStyleSheet("background-color: gainsboro")
                if j == 0:
                    label.setStyleSheet(label.styleSheet() + "; padding-left: 2px")
                elif j == 8:
                    label.setStyleSheet(label.styleSheet() + "; padding-right: 2px")
                score_layout.addWidget(widget, i + 1, j)

        layout.addLayout(score_layout, stretch=len(scores) + 1)

        options_layout = QHBoxLayout()

        button = QPushButton("Save Changes")
        button.setFixedWidth(120)
        button.clicked.connect(lambda checked: self.save_changes(scores, LineEdit_scores, LineEdit_projs, year, week))
        options_layout.addWidget(button)

        button = QPushButton("Cancel")
        button.setFixedWidth(120)
        button.clicked.connect(lambda checked: self.returntoView(year, week))
        options_layout.addWidget(button)

        spacer = QSpacerItem(530, 0, QSizePolicy.Ignored, QSizePolicy.Minimum)
        options_layout.addItem(spacer)

        layout.addLayout(options_layout, stretch=1)

        return layout

    def toggle_layout(self):
        self.setCurrentIndex(1)
        return

    def change_weeks(self, year, week):
        layout1 = self.ViewRegularLayout(year, week)
        layout2 = self.EditRegularLayout(year, week)

        temp_widget1, temp_widget2 = QWidget(), QWidget()
        temp_widget1.setLayout(self.stack1.layout())
        temp_widget2.setLayout(self.stack2.layout())

        self.stack1.setLayout(layout1)
        self.stack2.setLayout(layout2)

        temp_widget1.deleteLater(), temp_widget2.deleteLater()
        return

    def save_changes(self, scores, LineEdit_scores, LineEdit_projs, year, week):
        num_flag = self.checkFields(scores, LineEdit_scores, LineEdit_projs)
        if not num_flag:
            return

        for i, row in scores.iterrows():
            sql = """update games
                     set away_score = %s, away_proj = %s, home_score = %s, home_proj = %s
                     where year = %s and week = %s and home_owner = \"%s\"""" % (LineEdit_scores[i][0].text(),
                                                                                 LineEdit_projs[i][0].text(),
                                                                                 LineEdit_scores[i][1].text(),
                                                                                 LineEdit_projs[i][1].text(),
                                                                                 year, week, row["home_owner"])
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except connector.Error as error:
                sys.exit("SQL Error in save_changes():\n" + error)

        self.returntoView(year, week)
        return

    def returntoView(self, year, week):
        self.change_weeks(year, week)
        self.setCurrentIndex(0)
        return

    def checkFields(self, scores, LineEdit_scores, LineEdit_projs):
        flag = True
        titletext = "Data Entry Error"
        labeltext = "All fields must contain numbers before saving. The following fields raised an error:\n\n"
        for i, row in scores.iterrows():
            if not LineEdit_projs[i][0].text().replace(".", "", 1).isdigit():
                labeltext += "%s's Projected Score\n" % row["away_owner"]
                flag = False
            if not LineEdit_scores[i][0].text().replace(".", "", 1).isdigit():
                labeltext += "%s's Score\n" % row["away_owner"]
                flag = False
            if not LineEdit_projs[i][1].text().replace(".", "", 1).isdigit():
                labeltext += "%s's Projected Score\n" % row["home_owner"]
                flag = False
            if not LineEdit_scores[i][1].text().replace(".", "", 1).isdigit():
                labeltext += "%s's Projected Score\n" % row["home_owner"]
                flag = False

        if not flag:
            dlg = ErrorDialog(titletext, labeltext, self)
            if dlg.exec():
                return flag
            else:
                return flag
        elif flag:
            return flag

    def closeEvent(self, event):
        self.setCurrentIndex(0)
        self.resize(850, 325)
        return


class ErrorDialog(QDialog):
    def __init__(self, titletext, labeltext, parent=None):
        super().__init__(parent)

        self.setWindowTitle(titletext)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(labeltext))
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
