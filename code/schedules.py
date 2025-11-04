# TO DO
# 1: Create basic layout

import os
import sys
import pandas as pd
from mysql import connector
from scipy.stats import rankdata

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
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
    return head2head.to_numpy().astype(float)


class LeagueTable(QWidget):
    def __init__(self, db, cursor, years_list, current_year):
        super().__init__()
        self.db, self.cursor, self.current_year = db, cursor, current_year
        self.years_list = years_list

        self.table_columns = ["team_name", "owner", "clinch", "W-L-T", "win_pct", "GB",
                              "pts_for", "pts_against", "pts_diff",
                              "HOME", "AWAY", "DIV", "NON-DIV", "UPSET"]
        self.column_titles = ["", "", "", "W-L-T", "PCT", "GB",                 # team_name, (owner), playoff berth
                              "PF", "PA", "DIFF",
                              "HOME", "AWAY", "DIV", "NON-DIV", "UPSET"]
        self.column_descriptions = ["", "", "", "Wins-Losses-Ties", "Winning Percentage", "Games Back",
                                    "Points For", "Points Against", "Point Differential (Points For - Points Against)",
                                    "Home Record", "Away Record", "Divisional Record", "Non-Divisional Record",
                                    "Upset Record (an upset is defined as a\ngame where the result " +
                                    "contradicts the\nresult predicted by ESPN's projections)"]

        self.setWindowTitle("League Table")
        self.resize(990, 951)
        self.setMinimumSize(990, 951)

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
        wc = table.loc[(table["owner"] != east["owner"].iloc[0]) & (table["owner"] != west["owner"].iloc[0])].copy()
        games_played = table["wins"].iloc[0] - table["losses"].iloc[0] - table["ties"].iloc[0]
        games_remaining = 14 - games_played

        for t in [wc, east, west]:
            t.reset_index(drop=True, inplace=True)
            if len(t) > 5:
                t["GB"] = t["wins"].iloc[1] - t["wins"].astype("int")
                # t["GB"] = t["GB"].apply(lambda x: "+%s" % abs(x) if x < 0 else x)
            else:
                t["GB"] = t["wins"].iloc[0] - t["wins"].astype("int")
            t["RANK"] = len(t) - rankdata(t["win_pct"], method="max") + 1
            # t["GB"].replace({0: "-"}, inplace=True)
            t["clinch"] = ""

            # handle head-to-head tie-breakers
            ranks = t["RANK"].unique()
            for rank in ranks:
                idxs = t.loc[t["RANK"] == rank].index.tolist()
                if len(idxs) == 1:                                  # ignore ranks held by only one team
                    continue
                owners = t["owner"].iloc[idxs]
                pcts = []
                for owner in owners:
                    h2h = get_head_to_head_records(self.cursor, year, owner, owners).sum(axis=0)[:-1]
                    if h2h.sum() == 0.0:
                        h2h_pct = 1.0
                    else:
                        h2h_pct = (h2h[0] + 0.5 * h2h[2]) / h2h.sum()
                    pcts.append(h2h_pct)
                sorted_idxs = [x for _, x in sorted(zip(pcts, idxs), reverse=True)]
                sorted_rows = [t.iloc[i].copy() for i in sorted_idxs]
                for idx, row in zip(idxs, sorted_rows):
                    t.iloc[idx] = row

            # determine playoff berths
            if len(t) > 5:
                if games_remaining == 0:
                    t["clinch"].iloc[0] = "-x"
                    t["clinch"].iloc[1] = "-x"
                else:
                    for i in range(2):
                        if t["GB"].iloc[2] - t["GB"].iloc[i] > games_remaining:
                            t["clinch"].iloc[i] = "-x"
                        elif t["GB"].iloc[2] - t["GB"].iloc[i] == games_remaining:
                            rank = t["RANK"].iloc[2]
                            idxs = t.loc[t["RANK"] == rank].index.tolist()
                            owners = t["owner"].iloc[idxs]
                            h2h = get_head_to_head_records(self.cursor, year, t["owner"].iloc[i], owners).sum(axis=0)
                            if h2h[1:].sum() == 0:
                                t["clinch"].iloc[i] = "-x"
                        else:
                            continue

                t["GB"] = t["GB"].apply(lambda x: "+%s" % abs(x) if x < 0 else x)
            else:
                # handle wildcard playoff berths for divisional standings
                leader_diff = t["wins"].iloc[0] - wc["wins"].iloc[2]                # handle for leading team
                if leader_diff > games_remaining:
                    t["clinch"].iloc[0] = "-x"
                elif leader_diff == games_remaining:
                    rank = wc["RANK"].iloc[2]
                    idxs = wc.loc[wc["RANK"] == rank].index.tolist()
                    owners = wc["owner"].iloc[idxs]
                    h2h = get_head_to_head_records(self.cursor, year, t["owner"].iloc[0], owners).sum(axis=0)
                    if h2h[1:].sum() == 0:
                        t["clinch"].iloc[0] = "-x"
                for owner in t["owner"][1:]:                                        # handle for non-leading teams
                    if wc.loc[wc["owner"] == owner, "clinch"].iloc[0] == "-x":
                        t.loc[t["owner"] == owner, "clinch"] = "-x"

                # handle divisional playoff berth
                if games_remaining == 0:
                    t["clinch"].iloc[0] = "-y"
                else:
                    if t["GB"].iloc[1] > games_remaining:
                        t["clinch"].iloc[0] = "-y"
                    elif t["GB"].iloc[1] == games_remaining:
                        rank = t["RANK"].iloc[1]
                        idxs = t.loc[t["RANK"] == rank].index.tolist()
                        owners = t["owner"].iloc[idxs]
                        h2h = get_head_to_head_records(self.cursor, year, t["owner"].iloc[0], owners).sum(axis=0)
                        if h2h[1:].sum() == 0:
                            t["clinch"].iloc[0] = "-y"
                    else:
                        continue
            t["GB"].replace({0: "-"}, inplace=True)

        print(table.iloc[:, list(range(6)) + [-1]], "\n")
        print(east.iloc[:, list(range(6)) + list(range(-3, 0))], "\n")
        print(west.iloc[:, list(range(6)) + list(range(-3, 0))], "\n")
        print(wc.iloc[:, list(range(6)) + list(range(-3, 0))], "\n")

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
                else:
                    label.setFixedSize(65, 35)
                if j == 1:
                    label.setText("(%s)" % row[col])
                    label.setFont(sidenoteFont)
                if j < 3:
                    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                elif 3 < j < 9:
                    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    label.setAlignment(Qt.AlignCenter)
                if i % 2 == 0:
                    label.setStyleSheet(label.styleSheet() + " background-color: gainsboro;")
                if row["sb_wins"] == 1:
                    label.setStyleSheet(label.styleSheet() + " font-weight: bold;")
                if j == 0:
                    label.setStyleSheet(label.styleSheet() + " padding-left: 2px;")
                elif 3 < j < 9:
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

    def change_years(self, year):
        layout = self.LeagueTableLayout(year)

        temp_widget = QWidget()
        temp_widget.setLayout(self.layout())

        self.setLayout(layout)

        temp_widget.deleteLater()
        return

    def closeEvent(self, event):
        self.resize(990, 951)
        return
