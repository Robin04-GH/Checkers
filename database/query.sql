-- Test SQL-query with JOIN
-- pc@debian:~/project/Checkers/database$ sqlite3 ci2004.db < query.sql

SELECT 
m.id, m.pk_game, m.number_move, m.player_turn, m.origin_cell,
s.seq_index, s.destination_cell, s.captured_piece_id,
pl.engine, pl.name,
pd.engine, pd.name
FROM moves m
JOIN move_steps s ON m.id = s.move_id
JOIN games g ON m.pk_game = g.pk
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE m.id = 11533;

/*
Database : ci2004.db, last match !
*/