use example_league;

-- Teams --
insert into teams values ("Owner1", 2025, "Team1", "East", 1, "Player1", "RB", NULL, NULL);
insert into teams values ("Owner6", 2025, "Team6", "West", 2, "Player6", "WR", NULL, NULL);
insert into teams values ("Owner2", 2025, "Team2", "East", 3, "Player2", "WR", NULL, NULL);
insert into teams values ("Owner7", 2025, "Team7", "West", 4, "Player7", "RB", NULL, NULL);
insert into teams values ("Owner8", 2025, "Team8", "West", 5, "Player8", "RB", NULL, NULL);
insert into teams values ("Owner3", 2025, "Team3", "East", 6, "Player3", "RB", NULL, NULL);
insert into teams values ("Owner9", 2025, "Team9", "West", 7, "Player9", "WR", NULL, NULL);
insert into teams values ("Owner4", 2025, "Team4", "East", 8, "Player4", "WR", NULL, NULL);
insert into teams values ("Owner10", 2025, "Team10", "West", 9, "Player10", "WR", NULL, NULL);
insert into teams values ("Owner5", 2025, "Team5", "East", 10, "Player5", "RB", NULL, NULL);

-- Week 1 --
insert into games values (2025, 1, "Owner4", NULL, 118.78, 131.18, "Owner8", NULL, NULL, NULL, NULL);
insert into games values (2025, 1, "Owner9", NULL, 126.32, 124.03, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 1, "Owner5", NULL, 109.58, 124.21, "Owner10", NULL, NULL, NULL, NULL);
insert into games values (2025, 1, "Owner2", NULL, 121.86, 123.5, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 1, "Owner1", NULL, 123.42, 127.8, "Owner6", NULL, NULL, NULL, NULL);

-- Week 2 --
insert into games values (2025, 2, "Owner9", NULL, 98.1, 121.04, "Owner4", NULL, NULL, NULL, NULL);
insert into games values (2025, 2, "Owner8", NULL, 75.94, 107.88, "Owner10", NULL, NULL, NULL, NULL);
insert into games values (2025, 2, "Owner7", NULL, 119.44, 120.84, "Owner6", NULL, NULL, NULL, NULL);
insert into games values (2025, 2, "Owner5", NULL, 112.4, 118.79, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 2, "Owner3", NULL, 107.42, 118.05, "Owner1", NULL, NULL, NULL, NULL);

-- Week 3 --
insert into games values (2025, 3, "Owner3", NULL, NULL, NULL, "Owner4", NULL, NULL, NULL, NULL);
insert into games values (2025, 3, "Owner10", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 3, "Owner8", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 3, "Owner2", NULL, NULL, NULL, "Owner6", NULL, NULL, NULL, NULL);
insert into games values (2025, 3, "Owner1", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);

-- Week 4 --
insert into games values (2025, 4, "Owner3", NULL, NULL, NULL, "Owner10", NULL, NULL, NULL, NULL);
insert into games values (2025, 4, "Owner5", NULL, NULL, NULL, "Owner4", NULL, NULL, NULL, NULL);
insert into games values (2025, 4, "Owner9", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 4, "Owner2", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);
insert into games values (2025, 4, "Owner8", NULL, NULL, NULL, "Owner6", NULL, NULL, NULL, NULL);

-- Week 5 --
insert into games values (2025, 5, "Owner6", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 5, "Owner3", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 5, "Owner10", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 5, "Owner4", NULL, NULL, NULL, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 5, "Owner1", NULL, NULL, NULL, "Owner8", NULL, NULL, NULL, NULL);

-- Week 6 --
insert into games values (2025, 6, "Owner9", NULL, NULL, NULL, "Owner8", NULL, NULL, NULL, NULL);
insert into games values (2025, 6, "Owner10", NULL, NULL, NULL, "Owner6", NULL, NULL, NULL, NULL);
insert into games values (2025, 6, "Owner5", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 6, "Owner2", NULL, NULL, NULL, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 6, "Owner1", NULL, NULL, NULL, "Owner4", NULL, NULL, NULL, NULL);

-- Week 7 --
insert into games values (2025, 7, "Owner4", NULL, NULL, NULL, "Owner10", NULL, NULL, NULL, NULL);
insert into games values (2025, 7, "Owner7", NULL, NULL, NULL, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 7, "Owner6", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 7, "Owner8", NULL, NULL, NULL, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 7, "Owner9", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);

-- Week 8 --
insert into games values (2025, 8, "Owner4", NULL, NULL, NULL, "Owner6", NULL, NULL, NULL, NULL);
insert into games values (2025, 8, "Owner3", NULL, NULL, NULL, "Owner8", NULL, NULL, NULL, NULL);
insert into games values (2025, 8, "Owner5", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 8, "Owner2", NULL, NULL, NULL, "Owner10", NULL, NULL, NULL, NULL);
insert into games values (2025, 8, "Owner1", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);

-- Week 9 --
insert into games values (2025, 9, "Owner4", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 9, "Owner2", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 9, "Owner8", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 9, "Owner1", NULL, NULL, NULL, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 9, "Owner6", NULL, NULL, NULL, "Owner10", NULL, NULL, NULL, NULL);

-- Week 10 --
insert into games values (2025, 10, "Owner8", NULL, NULL, NULL, "Owner4", NULL, NULL, NULL, NULL);
insert into games values (2025, 10, "Owner3", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 10, "Owner10", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 10, "Owner7", NULL, NULL, NULL, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 10, "Owner6", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);

-- Week 11 --
insert into games values (2025, 11, "Owner6", NULL, NULL, NULL, "Owner7", NULL, NULL, NULL, NULL);
insert into games values (2025, 11, "Owner4", NULL, NULL, NULL, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 11, "Owner2", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 11, "Owner5", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);
insert into games values (2025, 11, "Owner10", NULL, NULL, NULL, "Owner8", NULL, NULL, NULL, NULL);

-- Week 12 --
insert into games values (2025, 12, "Owner7", NULL, NULL, NULL, "Owner8", NULL, NULL, NULL, NULL);
insert into games values (2025, 12, "Owner3", NULL, NULL, NULL, "Owner6", NULL, NULL, NULL, NULL);
insert into games values (2025, 12, "Owner4", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 12, "Owner1", NULL, NULL, NULL, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 12, "Owner9", NULL, NULL, NULL, "Owner10", NULL, NULL, NULL, NULL);

-- Week 13 --
insert into games values (2025, 13, "Owner7", NULL, NULL, NULL, "Owner9", NULL, NULL, NULL, NULL);
insert into games values (2025, 13, "Owner5", NULL, NULL, NULL, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 13, "Owner6", NULL, NULL, NULL, "Owner8", NULL, NULL, NULL, NULL);
insert into games values (2025, 13, "Owner2", NULL, NULL, NULL, "Owner4", NULL, NULL, NULL, NULL);
insert into games values (2025, 13, "Owner10", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);

-- Week 14 --
insert into games values (2025, 14, "Owner6", NULL, NULL, NULL, "Owner4", NULL, NULL, NULL, NULL);
insert into games values (2025, 14, "Owner8", NULL, NULL, NULL, "Owner3", NULL, NULL, NULL, NULL);
insert into games values (2025, 14, "Owner9", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 14, "Owner10", NULL, NULL, NULL, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 14, "Owner7", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);

-- Week 15 --
insert into games values (2025, 15, "Owner7", NULL, NULL, NULL, "Owner10", NULL, NULL, NULL, NULL);
insert into games values (2025, 15, "Owner8", NULL, NULL, NULL, "Owner5", NULL, NULL, NULL, NULL);
insert into games values (2025, 15, "Owner3", NULL, NULL, NULL, "Owner2", NULL, NULL, NULL, NULL);
insert into games values (2025, 15, "Owner9", NULL, NULL, NULL, "Owner6", NULL, NULL, NULL, NULL);
insert into games values (2025, 15, "Owner4", NULL, NULL, NULL, "Owner1", NULL, NULL, NULL, NULL);
