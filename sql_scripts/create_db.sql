create table teams
	(owner			varchar(40),
     year			int,
     team_name		varchar(40),
     division		varchar(40),
     draft_pos		int,
     rd1_pick		varchar(40),
     rd1_pos		varchar(2),
     ovr_rank		int,
     div_rank		int,
     primary key (owner, year),
     check (division in("East", "West"))
	);

create table games
	(year			int,
     week			int,
     away_owner		varchar(40),
     away_seed		int,
     away_score		float(5, 2),
     away_proj		float(5, 2),
     home_owner		varchar(40),
     home_seed		int,
     home_score		float(5, 2),
     home_proj		float(5, 2),
     winner			varchar(40),
     primary key (year, week, home_owner),
     foreign key (home_owner) references teams(owner),
     foreign key (away_owner) references teams(owner),
     check (winner in("Home", "Away", "Tie"))
	);

delimiter |

create trigger determine_winner before update on games
for each row
begin
	if new.away_score > new.home_score then set new.winner = "Away";
	elseif new.away_score = new.home_score then set new.winner = "Tie";
	elseif new.away_score < new.home_score then set new.winner = "Home";
    end if;
end;
|

delimiter ;

delimiter |

create procedure get_weekly_scoreboard(in input_year int, input_week int)
begin
	select g.*, a.team_name away_team_name, a.division away_division,
    (select
		concat(
			sum(case
			   when away_owner = a.owner and winner = "Away" and week < 16 then 1
			   when home_owner = a.owner and winner = "Home" and week < 16 then 1
			   else 0
			   end), "-",
			sum(case
			   when away_owner = a.owner and winner = "Home" and week < 16 then 1
			   when home_owner = a.owner and winner = "Away" and week < 16 then 1
			   else 0
			   end), "-",
			sum(case
			   when away_owner = a.owner and winner = "Tie" and week < 16 then 1
			   when home_owner = a.owner and winner = "Tie" and week < 16 then 1
			   else 0
			   end)
        )
	 from games gg
	 where gg.year = g.year and (gg.away_owner = a.owner or gg.home_owner = a.owner)
    ) as away_record,
    h.team_name home_team_name, h.division home_division,
    (select
		concat(
			sum(case
			   when away_owner = h.owner and winner = "Away" and week < 16 then 1
			   when home_owner = h.owner and winner = "Home" and week < 16 then 1
			   else 0
			   end), "-",
			sum(case
			   when away_owner = h.owner and winner = "Home" and week < 16 then 1
			   when home_owner = h.owner and winner = "Away" and week < 16 then 1
			   else 0
			   end), "-",
			sum(case
			   when away_owner = h.owner and winner = "Tie" and week < 16 then 1
			   when home_owner = h.owner and winner = "Tie" and week < 16 then 1
			   else 0
			   end)
        )
	 from games gg
	 where gg.year = g.year and (gg.away_owner = h.owner or gg.home_owner = h.owner)
    ) as home_record
    from games g
    join teams a on a.owner = g.away_owner and a.year = g.year
    join teams h on h.owner = g.home_owner and h.year = g.year
    where g.year = input_year and g.week = input_week
    order by g.home_seed;
end |

delimiter ;

delimiter |

create procedure get_yearly_head_to_head_record(in input_year int, in owner1 varchar(40), in owner2 varchar(40))
begin
	select sum(case
			   when away_owner = owner1 and home_owner = owner2 and winner = "Away" and week < 16 then 1
               when away_owner = owner2 and home_owner = owner1 and winner = "Home" and week < 16 then 1
               else 0
               end) as wins,
		   sum(case
			   when away_owner = owner1 and home_owner = owner2 and winner = "Home" and week < 16 then 1
               when away_owner = owner2 and home_owner = owner1 and winner = "Away" and week < 16 then 1
               else 0
               end) as losses,
		   sum(case
		       when away_owner = owner1 and home_owner = owner2 and winner = "Tie" and week < 16 then 1
               when away_owner = owner2 and home_owner = owner1 and winner = "Tie" and week < 16 then 1
               else 0
               end) as ties,
		   sum(case
			   when away_owner = owner1 and home_owner = owner2 and winner is NULL and week < 16 then 1
               when away_owner = owner2 and home_owner = owner1 and winner is NULL and week < 16 then 1
               else 0
               end) as remaining_games
    from games
    where year = input_year;
end |

delimiter ;

delimiter |

create procedure get_individual_schedule(in input_year int, in owner varchar(40))
begin
	select week,
		   if(g.home_owner = owner, "vs", "at") as preposition,
           if(g.home_owner = owner, g.away_owner, g.home_owner) as opp_owner,
           if(g.home_owner = owner, at.team_name, ht.team_name) as opp_team_name,
           if(g.home_owner = owner, at.division, ht.division) as opp_division,
           if(g.home_owner = owner, g.away_proj, g.home_proj) as opp_proj,
           if(g.home_owner = owner, g.away_score, g.home_score) as opp_score,
           if(g.home_owner = owner, g.home_proj, g.away_proj) as proj,
           if(g.home_owner = owner, g.home_score, g.away_score) as score,
           case
           when g.home_owner = owner and g.winner = "Home" then "W"
           when g.home_owner = owner and g.winner = "Away" then "L"
           when g.away_owner = owner and g.winner = "Away" then "W"
           when g.away_owner = owner and g.winner = "Home" then "L"
           when g.winner = "Tie" then "T"
           else NULL
           end as result
    from games g
    join teams ht on g.home_owner = ht.owner and g.year = ht.year
    join teams at on g.away_owner = at.owner and g.year = at.year
    where g.year = input_year and (g.home_owner = owner or g.away_owner = owner) and week < 16
    order by week asc;
end |

delimiter ;

delimiter |

create procedure get_league_table(in input_year int)
begin
	select t.owner,
		   t.team_name,
		   t.division,
		   sum(case
			   when t.owner = g.away_owner and winner = "Away" and g.week < 16 then 1
			   when t.owner = g.home_owner and winner = "Home" and g.week < 16 then 1
			   else 0
			   end) as wins,
		   sum(case
			   when t.owner = g.away_owner and winner = "Home" and g.week < 16 then 1
			   when t.owner = g.home_owner and winner = "Away" and g.week < 16 then 1
               else 0
               end) as losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Tie" and g.week < 16 then 1
               when t.owner = g.home_owner and winner = "Tie" and g.week < 16 then 1
               else 0
               end) as ties,
	       round(sum(case
					 when t.owner = g.away_owner and winner = "Away" and g.week < 16 then 1
					 when t.owner = g.home_owner and winner = "Home" and g.week < 16 then 1
					 else 0
					 end) /
				 sum(case
					 when t.owner = g.away_owner and g.week < 16 and g.away_score is not NULL then 1
					 when t.owner = g.home_owner and g.week < 16 and g.home_score is not NULL then 1
					 else 0
					 end), 3) as win_pct,
	       sum(case
		       when t.owner = g.home_owner and g.winner = "Home" and g.week < 16 then 1
               else 0
               end) as home_wins,
	       sum(case
		       when t.owner = g.home_owner and g.winner = "Away" and g.week < 16 then 1
               else 0
               end) as home_losses,
	       sum(case
		       when t.owner = g.home_owner and g.winner = "Tie" and g.week < 16 then 1
               else 0
               end) as home_ties,
	       sum(case
		       when t.owner = g.away_owner and g.winner = "Away" and g.week < 16 then 1
               else 0
               end) as away_wins,
	       sum(case
		       when t.owner = g.away_owner and g.winner = "Home" and g.week < 16 then 1
               else 0
               end) as away_losses,
	       sum(case
		       when t.owner = g.away_owner and g.winner = "Tie" and g.week < 16 then 1
               else 0
               end) as away_ties,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Home" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as div_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Away" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as div_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Tie" and g.week < 16 and t.division = (select division
																							    from teams
																							    where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Tie" and g.week < 16 and t.division = (select division
																							    from teams
																							    where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as div_ties,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Home" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as nondiv_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Away" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as nondiv_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Tie" and g.week < 16 and t.division != (select division
																							     from teams
																							     where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Tie" and g.week < 16 and t.division != (select division
																							     from teams
																							     where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as nondiv_ties,
		   sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.away_proj < g.home_proj and g.week < 16 then 1
               when t.owner = g.home_owner and winner = "Home" and g.home_proj < g.away_proj and g.week < 16 then 1
               else 0
               end) as upset_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.away_proj > g.home_proj and g.week < 16 then 1
               when t.owner = g.home_owner and winner = "Away" and g.home_proj > g.away_proj and g.week < 16 then 1
               else 0
               end) as upset_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week > 14 then 1
               when t.owner = g.home_owner and winner = "Home" and g.week > 14 then 1
               else 0
               end) as playoff_wins,
	       sum(case
               when t.owner = g.away_owner and winner = "Home" and g.week > 14 then 1
               when t.owner = g.home_owner and winner = "Away" and g.week > 14 then 1
               else 0
               end) as playoff_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week = 16 then 1
               when t.owner = g.home_owner and winner = "Home" and g.week = 16 then 1
               else 0
               end) as sb_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.week = 16 then 1
               when t.owner = g.home_owner and winner = "Away" and g.week = 16 then 1
               else 0
               end) as sb_losses,
	       sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.away_score
               when t.owner = g.home_owner and g.week < 16 then g.home_score
               else 0
               end) as pts_for,
	       sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.home_score
               when t.owner = g.home_owner and g.week < 16 then g.away_score
               else 0
               end) as pts_against,
	       sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.away_score - g.home_score
               when t.owner = g.home_owner and g.week < 16 then g.home_score - g.away_score
               else 0
               end) as pts_diff,
		   sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.away_score - g.away_proj
               when t.owner = g.home_owner and g.week < 16 then g.home_score - g.home_proj
               else 0
               end) as proj_diff,
	       round(avg(case
				     when t.owner = g.away_owner and g.week < 16 then g.away_score
				     when t.owner = g.home_owner and g.week < 16 then g.home_score
				     end), 2) as avg_pts_for,
	       round(avg(case
				     when t.owner = g.away_owner and g.week < 16 then g.home_score
				     when t.owner = g.home_owner and g.week < 16 then g.away_score
				     end), 2) as avg_pts_against,
	       round(avg(case
				     when t.owner = g.away_owner and g.week < 16 then g.away_score - g.home_score
				     when t.owner = g.home_owner and g.week < 16 then g.home_score - g.away_score
				     end), 2) as avg_pts_diff,
	       sum(case
		       when t.owner = g.away_owner and g.week = 15 then 1
               when t.owner = g.home_owner and g.week = 15 then 1
               else 0
               end) as playoff_app,
	       sum(case
		       when t.owner = g.away_owner and g.week = 15 and g.away_seed > 2 then 1
               when t.owner = g.home_owner and g.week = 15 and g.home_seed > 2 then 1
               else 0
               end) as wc_berths,
	       sum(case
		       when t.owner = g.away_owner and g.week = 15 and g.away_seed < 3 then 1
               when t.owner = g.home_owner and g.week = 15 and g.home_seed < 3 then 1
               else 0
               end) as div_titles,
	       sum(case
		       when t.owner = g.away_owner and g.week = 16 then 1
               when t.owner = g.home_owner and g.week = 16 then 1
               else 0
               end) as sb_app
    from teams t
    left join games g on t.owner = g.home_owner or t.owner = g.away_owner
    where g.year = input_year
    group by t.owner, t.team_name, t.division
    order by win_pct desc,
		     pts_for desc;
end |

delimiter ;

delimiter |

create procedure get_league_statistics()
begin
	select t.owner,
		   t.division,
		   sum(case
			   when t.owner = g.away_owner and winner = "Away" and g.week < 16 then 1
			   when t.owner = g.home_owner and winner = "Home" and g.week < 16 then 1
			   else 0
			   end) as wins,
		   sum(case
			   when t.owner = g.away_owner and winner = "Home" and g.week < 16 then 1
			   when t.owner = g.home_owner and winner = "Away" and g.week < 16 then 1
               else 0
               end) as losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Tie" and g.week < 16 then 1
               when t.owner = g.home_owner and winner = "Tie" and g.week < 16 then 1
               else 0
               end) as ties,
	       round(sum(case
					 when t.owner = g.away_owner and winner = "Away" and g.week < 16 then 1
					 when t.owner = g.home_owner and winner = "Home" and g.week < 16 then 1
					 else 0
					 end) /
				 sum(case
					 when t.owner = g.away_owner and g.week < 16 and g.away_score is not NULL then 1
					 when t.owner = g.home_owner and g.week < 16 and g.home_score is not NULL then 1
					 else 0
					 end), 3) as win_pct,
	       sum(case
		       when t.owner = g.home_owner and g.winner = "Home" and g.week < 16 then 1
               else 0
               end) as home_wins,
	       sum(case
		       when t.owner = g.home_owner and g.winner = "Away" and g.week < 16 then 1
               else 0
               end) as home_losses,
	       sum(case
		       when t.owner = g.home_owner and g.winner = "Tie" and g.week < 16 then 1
               else 0
               end) as home_ties,
	       sum(case
		       when t.owner = g.away_owner and g.winner = "Away" and g.week < 16 then 1
               else 0
               end) as away_wins,
	       sum(case
		       when t.owner = g.away_owner and g.winner = "Home" and g.week < 16 then 1
               else 0
               end) as away_losses,
	       sum(case
		       when t.owner = g.away_owner and g.winner = "Tie" and g.week < 16 then 1
               else 0
               end) as away_ties,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Home" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as div_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Away" and g.week < 16 and t.division = (select division
																							     from teams
																							     where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as div_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Tie" and g.week < 16 and t.division = (select division
																							    from teams
																							    where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Tie" and g.week < 16 and t.division = (select division
																							    from teams
																							    where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as div_ties,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Home" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as nondiv_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Away" and g.week < 16 and t.division != (select division
																							      from teams
																							      where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as nondiv_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Tie" and g.week < 16 and t.division != (select division
																							     from teams
																							     where owner = g.home_owner and year = g.year) then 1
		       when t.owner = g.home_owner and winner = "Tie" and g.week < 16 and t.division != (select division
																							     from teams
																							     where owner = g.away_owner and year = g.year) then 1
		       else 0
               end) as nondiv_ties,
		   sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.away_proj < g.home_proj and g.week < 16 then 1
               when t.owner = g.home_owner and winner = "Home" and g.home_proj < g.away_proj and g.week < 16 then 1
               else 0
               end) as upset_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.away_proj > g.home_proj and g.week < 16 then 1
               when t.owner = g.home_owner and winner = "Away" and g.home_proj > g.away_proj and g.week < 16 then 1
               else 0
               end) as upset_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week > 14 then 1
               when t.owner = g.home_owner and winner = "Home" and g.week > 14 then 1
               else 0
               end) as playoff_wins,
	       sum(case
               when t.owner = g.away_owner and winner = "Home" and g.week > 14 then 1
               when t.owner = g.home_owner and winner = "Away" and g.week > 14 then 1
               else 0
               end) as playoff_losses,
	       sum(case
		       when t.owner = g.away_owner and winner = "Away" and g.week = 16 then 1
               when t.owner = g.home_owner and winner = "Home" and g.week = 16 then 1
               else 0
               end) as sb_wins,
	       sum(case
		       when t.owner = g.away_owner and winner = "Home" and g.week = 16 then 1
               when t.owner = g.home_owner and winner = "Away" and g.week = 16 then 1
               else 0
               end) as sb_losses,
	       sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.away_score
               when t.owner = g.home_owner and g.week < 16 then g.home_score
               else 0
               end) as pts_for,
	       sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.home_score
               when t.owner = g.home_owner and g.week < 16 then g.away_score
               else 0
               end) as pts_against,
	       sum(case
		       when t.owner = g.away_owner and g.week < 16 then g.away_score - g.home_score
               when t.owner = g.home_owner and g.week < 16 then g.home_score - g.away_score
               else 0
               end) as pts_diff,
	       round(avg(case
				     when t.owner = g.away_owner and g.week < 16 then g.away_score
				     when t.owner = g.home_owner and g.week < 16 then g.home_score
				     end), 2) as avg_pts_for,
	       round(avg(case
				     when t.owner = g.away_owner and g.week < 16 then g.home_score
				     when t.owner = g.home_owner and g.week < 16 then g.away_score
				     end), 2) as avg_pts_against,
	       round(avg(case
				     when t.owner = g.away_owner and g.week < 16 then g.away_score - g.home_score
				     when t.owner = g.home_owner and g.week < 16 then g.home_score - g.away_score
				     end), 2) as avg_pts_diff,
	       sum(case
		       when t.owner = g.away_owner and g.week = 15 then 1
               when t.owner = g.home_owner and g.week = 15 then 1
               else 0
               end) as playoff_app,
	       sum(case
		       when t.owner = g.away_owner and g.week = 15 and g.away_seed > 2 then 1
               when t.owner = g.home_owner and g.week = 15 and g.home_seed > 2 then 1
               else 0
               end) as wc_berths,
	       sum(case
		       when t.owner = g.away_owner and g.week = 15 and g.away_seed < 3 then 1
               when t.owner = g.home_owner and g.week = 15 and g.home_seed < 3 then 1
               else 0
               end) as div_titles,
	       sum(case
		       when t.owner = g.away_owner and g.week = 16 then 1
               when t.owner = g.home_owner and g.week = 16 then 1
               else 0
               end) as sb_app
    from teams t
    left join games g on t.owner = g.home_owner or t.owner = g.away_owner
    group by t.owner, t.division
    order by win_pct desc,
		     pts_for desc;
end |

delimiter ;
