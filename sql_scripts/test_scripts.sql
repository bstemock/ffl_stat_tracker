use family_ffl;

call get_league_table(2025);

call get_league_statistics();

call get_weekly_scoreboard(2025, 1);

call get_yearly_head_to_head_record(2025, "Bryson", "Jimmy");

call get_individual_schedule(2025, "Bryson");

select distinct(week)
from games
where year = 2025
order by week asc;

select *
from teams
where year = 2025
order by draft_pos;

update teams
set rd1_pick = "Ashton Jeanty", rd1_pos = "RB"
where year = 2025 and owner = "Killian";

select *
from games
where year = 2025 and week = 1;

select max(week) as m
from (select * from games where away_score is not null) t
where t.year = 2025;

select g.*, a.team_name away_team_name, a.division away_division, h.team_name home_team_name, h.division home_division
from games g
join teams a
on a.owner = g.away_owner and a.year = g.year
join teams h
on h.owner = g.home_owner and h.year = g.year
where g.year = 2025 and g.week = 1;

drop view if exists standings;

create view standings as
select t.owner,
	   t.team_name,
	   sum(case
		   when t.owner = g.away_owner and winner = "Away" then 1
           when t.owner = g.home_owner and winner = "Home" then 1
           else 0
           end) as wins,
	   sum(case
           when t.owner = g.away_owner and winner = "Home" then 1
           when t.owner = g.home_owner and winner = "Away" then 1
           else 0
           end) as losses,
	   sum(case
		   when t.owner = g.away_owner and winner = "Tie" then 1
           when t.owner = g.home_owner and winner = "Tie" then 1
           else 0
           end) as ties
from teams t
left join games g on t.owner = g.home_owner or t.owner = g.away_owner
group by t.owner, t.team_name;

select *
from standings;
