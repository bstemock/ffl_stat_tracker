# TO DO
# 1: refresh button

import os
import sys
import numpy as np
import pandas as pd
from mysql import connector
from scipy.stats import rankdata

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QComboBox,
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


def get_standings(cursor, year):
    cursor.callproc("get_league_table", [year])
    proc_results = next(cursor.stored_results(), None)
    if proc_results:
        results = proc_results.fetchall()
        field_names = proc_results.column_names
    else:
        sys.exit("ERROR: No results returned by get_weekly_scoreboard process.")
    standings = pd.DataFrame(results, columns=field_names)
    return standings


def get_head_to_head_records(cursor, year, owner, opp_list):
    head2head = pd.DataFrame(columns=["wins", "losses", "ties", "remaining_games"])
    for i, opp in enumerate(opp_list):
        if opp == owner:
            continue
        cursor.callproc("get_yearly_head_to_head_record", [year, owner, opp])
        proc_results = next(cursor.stored_results(), None)
        if proc_results:
            results = proc_results.fetchall()
        else:
            sys.exit("ERROR: No results returned by get_head_to_head process.")
        head2head = pd.concat([head2head, pd.DataFrame(results, columns=["wins", "losses", "ties",
                                                                         "remaining_games"])], ignore_index=True)
    return head2head.to_numpy().astype(int)


class LeagueTable(QWidget):
    def __init__(self, db, cursor, years_list, current_year):
        super().__init__()
        self.db, self.cursor, self.current_year = db, cursor, current_year
        self.years_list = years_list

        self.table_columns = ["team_name", "owner", "clinch", "W-L-T", "win_pct", "GB",
                              "pts_for", "pts_against", "pts_diff", "proj_diff",
                              "HOME", "AWAY", "DIV", "NON-DIV", "UPSET"]
        self.column_titles = ["", "", "", "W-L-T", "PCT", "GB",                 # team_name, (owner), playoff berth
                              "PF", "PA", "DIFF", "PROJ-DIFF",
                              "HOME", "AWAY", "DIV", "NON-DIV", "UPSET"]
        self.column_descriptions = ["", "", "", "Wins-Losses-Ties", "Winning Percentage", "Games Back",
                                    "Points For", "Points Against", "Point Differential (Points For - Points Against)",
                                    "Projection Differential (Points For - ESPN Projected Points For)",
                                    "Home Record", "Away Record", "Divisional Record", "Non-Divisional Record",
                                    "Upset Record (an upset is defined as a\ngame where the result " +
                                    "contradicts the\nresult predicted by ESPN's projections)"]

        self.setWindowTitle("League Table")
        self.minsize = QSize(1060, 951)
        self.resize(self.minsize)
        self.setMinimumSize(self.minsize)

        layout = self.LeagueTableLayout(current_year)

        self.setLayout(layout)

    def LeagueTableLayout(self, year):
        table = get_standings(self.cursor, year)
        table["W-L-T"] = table["wins"].astype(str) + "-" + table["losses"].astype(str) + "-" + table["ties"].astype(str)
        table["HOME"] = table["home_wins"].astype(str) + "-" + table["home_losses"].astype(str) + \
            "-" + table["home_ties"].astype(str)
        table["AWAY"] = table["away_wins"].astype(str) + "-" + table["away_losses"].astype(str) + \
            "-" + table["away_ties"].astype(str)
        table["DIV"] = table["div_wins"].astype(str) + "-" + table["div_losses"].astype(str) + \
            "-" + table["div_ties"].astype(str)
        table["NON-DIV"] = table["nondiv_wins"].astype(str) + "-" + table["nondiv_losses"].astype(str) + \
            "-" + table["nondiv_ties"].astype(str)
        table["UPSET"] = table["upset_wins"].astype(str) + "-" + table["upset_losses"].astype(str)

        east = table.loc[table["division"] == "East"].copy()
        west = table.loc[table["division"] == "West"].copy()
        games_played = table["wins"].iloc[0] + table["losses"].iloc[0] + table["ties"].iloc[0]
        games_remaining = 15 - games_played

        for t in [east, west]:
            t.reset_index(drop=True, inplace=True)
            t["GB"] = t["wins"].iloc[0] - t["wins"].astype("int")
            t["RANK"] = len(t) - rankdata(t["win_pct"], method="max") + 1
            t["clinch"] = ""
            t = self.h2h_reorder(t, year)

            # handle divisional playoff berth
            if games_remaining == 0:
                t.at[0, "clinch"] = "-y"
            else:
                if t["GB"].iloc[1] > games_remaining:
                    t.at[0, "clinch"] = "-y"
                elif t["GB"].iloc[1] == games_remaining:
                    rank = t["RANK"].iloc[1]
                    idxs = t.loc[t["RANK"] == rank].index.tolist()
                    owners = t["owner"].iloc[idxs]
                    h2h = get_head_to_head_records(self.cursor, year, t["owner"].iloc[0], owners).sum(axis=0)
                    if h2h[1:].sum() == 0:
                        t.at[0, "clinch"] = "-y"
                else:
                    pass

            t["GB"].replace({0: "-"}, inplace=True)

        # generate wildcard table
        wc = table.loc[(table["owner"] != east["owner"].iloc[0]) & (table["owner"] != west["owner"].iloc[0])].copy()
        wc.reset_index(drop=True, inplace=True)
        wc["GB"] = wc["wins"].iloc[1] - wc["wins"].astype("int")
        wc["GB"] = wc["GB"].apply(lambda x: "+%s" % abs(x) if x < 0 else x)
        wc["RANK"] = len(wc) - rankdata(wc["win_pct"], method="max") + 1
        wc["clinch"] = ""

        # handle wildcard playoff berths for wildcard standings
        if games_remaining == 0:
            wc.loc[wc.index < 2, "clinch"] = "-x"
        else:
            for i in [0, 1]:
                leader_diff = wc["wins"].iloc[i] - wc["wins"].iloc[2]
                if leader_diff > games_remaining:
                    wc.at[i, "clinch"] = "-x"
                elif leader_diff == games_remaining:
                    rank = wc["RANK"].iloc[2]
                    idxs = wc.loc[wc["RANK"] == rank].index.tolist()
                    owners = wc["owner"].iloc[idxs]
                    h2h = get_head_to_head_records(self.cursor, year, wc["owner"].iloc[i], owners).sum(axis=0)
                    if h2h[1:].sum() == 0:
                        wc.at[i, "clinch"] = "-x"
                else:
                    pass

        # handle wildcard playoff berths for division standings
        for t in [east, west]:
            # handle division leaders
            if t.loc[0, "clinch"] == "-y":
                pass
            elif t.loc[0, "clinch"] == "":
                leader_diff = t["wins"].iloc[0] - wc["wins"].iloc[2]
                if leader_diff > games_remaining:
                    t.at[0, "clinch"] = "-x"
                elif leader_diff == games_remaining:
                    rank = wc["RANK"].iloc[2]
                    idxs = wc.loc[wc["RANK"] == rank].index.tolist()
                    owners = wc["owner"].iloc[idxs]
                    h2h = get_head_to_head_records(self.cursor, year, t["owner"].iloc[0], owners).sum(axis=0)
                    if h2h[1:].sum() == 0:
                        t.at[0, "clinch"] = "-x"
                else:
                    pass

            # handle everyone else
            for i in range(1, len(t)):
                if wc.loc[wc["owner"] == t.at[i, "owner"], "clinch"].iloc[0] == "-x":
                    t.at[i, "clinch"] = "-x"
                else:
                    pass

        layout = QVBoxLayout()

        label = QLabel("%s League Table" % year)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        label.setFont(titleFont)
        layout.addWidget(label, stretch=1)

        label = QLabel("East")
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setFont(titleFont)
        label.setStyleSheet("font-weight: bold;")
        label.setFixedHeight(35)
        layout.addWidget(label, stretch=1)

        east_layout = self.get_table_layout(east)
        east_layout.setContentsMargins(10, 10, 10, 10)
        east_layout.setSpacing(0)
        layout.addLayout(east_layout, stretch=len(east) + 1)

        label = QLabel("West")
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setFont(titleFont)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label, stretch=1)

        west_layout = self.get_table_layout(west)
        west_layout.setContentsMargins(10, 10, 10, 10)
        west_layout.setSpacing(0)
        layout.addLayout(west_layout, stretch=len(west) + 1)

        label = QLabel("Wild Card")
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setFont(titleFont)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label, stretch=1)

        wc_layout = self.get_table_layout(wc)
        wc_layout.setContentsMargins(10, 10, 10, 10)
        wc_layout.setSpacing(0)
        layout.addLayout(wc_layout, stretch=len(wc) + 1)

        options_layout = QHBoxLayout()

        label = QLabel("Year:")
        label.setFixedWidth(35)
        options_layout.addWidget(label)

        dropdown = QComboBox()
        dropdown.addItems(map(str, self.years_list))
        dropdown.setCurrentIndex(self.years_list.index(year))
        dropdown.setFixedWidth(60)
        dropdown.currentTextChanged.connect(lambda text: self.change_years(int(text)))
        options_layout.addWidget(dropdown)

        spacer = QSpacerItem(925, 0, QSizePolicy.Ignored, QSizePolicy.Minimum)
        options_layout.addItem(spacer)

        layout.addLayout(options_layout, stretch=1)

        return layout

    def get_table_layout(self, table):
        table_layout = QGridLayout()
        table_layout.setContentsMargins(10, 10, 10, 10)
        table_layout.setSpacing(0)

        for t, title in enumerate(self.column_titles):
            label = QLabel(title)
            label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            label.setStyleSheet("font-weight: bold;")
            if t == 0:
                label.setFixedSize(180, 20)
            elif t == 2:
                label.setFixedSize(20, 20)
            elif t == 5:
                label.setFixedSize(35, 20)
            elif t == 9:
                label.setFixedSize(70, 20)
            else:
                label.setFixedSize(65, 20)
            if t > 2:
                label.setToolTip(self.column_descriptions[t])

            table_layout.addWidget(label, 0, t)

        for i, row in table.iterrows():
            for j, col in enumerate(self.table_columns):
                label = QLabel(str(row[col]))

                if j == 0:
                    label.setFixedSize(180, 35)
                elif j == 2:
                    label.setFixedSize(20, 35)
                elif j == 5:
                    label.setFixedSize(35, 35)
                elif j == 9:
                    label.setFixedSize(70, 35)
                else:
                    label.setFixedSize(65, 35)
                if j == 1:
                    label.setText("(%s)" % row[col])
                    label.setFont(sidenoteFont)
                if j < 3:
                    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                elif 3 < j < 10:
                    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    label.setAlignment(Qt.AlignCenter)
                if i % 2 == 0:
                    label.setStyleSheet(label.styleSheet() + " background-color: gainsboro;")
                if row["sb_wins"] == 1:
                    label.setStyleSheet(label.styleSheet() + " font-weight: bold;")
                if j == 0:
                    label.setStyleSheet(label.styleSheet() + " padding-left: 2px;")
                elif 3 < j < 10:
                    label.setStyleSheet(label.styleSheet() + " padding-right: 5px;")
                if i > 1 and len(table) > 5:
                    table_layout.addWidget(label, i + 2, j)
                else:
                    table_layout.addWidget(label, i + 1, j)

        if len(table) > 5:
            for j, col in enumerate(self.table_columns):
                line = QWidget()
                line.setAutoFillBackground(True)
                line.setStyleSheet("background-color: black;")
                line.setFixedHeight(1)
                table_layout.addWidget(line, 3, j)

        return table_layout

    def h2h_reorder(self, t, year):
        ranks = t["RANK"].unique()
        for rank in ranks:
            idxs = t.loc[t["RANK"] == rank].index.tolist()
            if len(idxs) == 1:                              # ignore ranks held by only one team
                continue
            owners = t.loc[idxs, "owner"].tolist()
            buckets = [[], [], []]                          # only won, mixed/missing results, only lost
            for i, owner in enumerate(owners):
                h2h = get_head_to_head_records(self.cursor, year, owner, owners)
                pair = (idxs[i], t.loc[idxs[i], "pts_for"])
                if np.any(h2h[:, 0] > 0) and np.all(h2h[:, 1] == 0):
                    buckets[0].append(pair)
                elif np.all(h2h[:, 0] == 0) and np.any(h2h[:, 1] > 0):
                    buckets[2].append(pair)
                else:
                    buckets[1].append(pair)
            for i in range(len(buckets)):
                buckets[i] = sorted(buckets[i], key=lambda x: x[1], reverse=True)
            sorted_idxs = [x[0] for xs in buckets for x in xs]
            sorted_rows = [t.iloc[i].copy() for i in sorted_idxs]
            for idx, row in zip(idxs, sorted_rows):
                t.iloc[idx] = row
        return t

    def change_years(self, year):
        layout = self.LeagueTableLayout(year)

        temp_widget = QWidget()
        temp_widget.setLayout(self.layout())

        self.setLayout(layout)

        temp_widget.deleteLater()
        return

    def closeEvent(self, event):
        self.resize(self.minsize)
        return
