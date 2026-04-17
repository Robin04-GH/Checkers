-- Test SQL-query with JOIN
-- pc@debian:~/project/Checkers/database$ sqlite3 ci2004.db < query.sql

/*
-- test JOIN
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
*/

/*
-- test GROUP BY
SELECT
    g.result,
    COUNT(*) AS total
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE pl.name = 'Michele Borghetti'
   OR pd.name = 'Michele Borghetti'
GROUP BY g.result;
*/

/*
-- test GROUP BY (Manual subtotal)
-- SQLite compatible, without 'WITH ROLLUP'
SELECT 'R_DARK' AS result, COUNT(*) AS total
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE (pl.name = 'Michele Borghetti' OR pd.name = 'Michele Borghetti')
  AND g.result = 'R_DARK'

UNION ALL

SELECT 'R_LIGHT', COUNT(*)
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE (pl.name = 'Michele Borghetti' OR pd.name = 'Michele Borghetti')
  AND g.result = 'R_LIGHT'

UNION ALL

SELECT 'R_PARITY', COUNT(*)
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE (pl.name = 'Michele Borghetti' OR pd.name = 'Michele Borghetti')
  AND g.result = 'R_PARITY'

UNION ALL

SELECT 'SUM_ALL', COUNT(*)
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE pl.name = 'Michele Borghetti' OR pd.name = 'Michele Borghetti';
*/

/*
-- test GROUP BY (single line result)
SELECT
    SUM(CASE WHEN g.result = 'R_DARK'  THEN 1 ELSE 0 END) AS wins_dark,
    SUM(CASE WHEN g.result = 'R_PARITY' THEN 1 ELSE 0 END) AS parity,
    SUM(CASE WHEN g.result = 'R_LIGHT' THEN 1 ELSE 0 END) AS wins_light
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE pl.name = 'Michele Borghetti'
   OR pd.name = 'Michele Borghetti';
*/

/*
-- test GROUP BY (Counting the outcome of a player's matches)
SELECT
    g.result,
    COUNT(*) AS total
FROM games g
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE (pl.name = 'Michele Borghetti' AND g.result = 'R_LIGHT')
   OR (pd.name = 'Michele Borghetti' AND g.result = 'R_DARK')
GROUP BY g.result
HAVING total > 0;
*/

/*
SELECT
   ms.move_id,
   COUNT(*) AS total
FROM move_steps ms
JOIN moves m ON ms.move_id = m.id
JOIN games g ON m.pk_game = g.pk
JOIN players pl ON g.player_light_id = pl.id
JOIN players pd ON g.player_dark_id = pd.id
WHERE pl.name = 'Michele Borghetti'
   OR pd.name = 'Michele Borghetti'
GROUP BY ms.move_id
HAVING total > 2;
*/

-- Test implicit groupings (without GROUP BY)
SELECT
   COUNT(id)
FROM players 

/*
Database : ci2004.db, last match !
*/