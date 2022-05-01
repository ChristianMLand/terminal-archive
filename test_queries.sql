-- INSERT INTO terminals (name, auth_email, auth_password, auth_url, auth_required, data_url)
-- VALUES ("t18","OISKENTDISPATCH@ODYSSEYLOGISTICS.COM","GOHAWKS12!","https://t18.tideworks.com",1,"https://t18.tideworks.com/fc-T18/home/default.do?method=page&id=4");

-- INSERT INTO ssls (name)
-- VALUES ("CMA"), ("APL"), ("ANL"), ("COS"), ("HDM"), ("HLC"), ("MAE"), ("SUD"), ("SAF"), ("SEA"), ("MSC"), ("ONE"), ("OOCL"), ("SMC"), ("WHL"), ("WWS"), ("YML"), ("ZIM");

-- INSERT INTO partnerships (terminal_id, ssl_id)
-- VALUES (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (1, 14), (1, 15), (1, 16), (1, 17), (1, 18);

-- INSERT INTO containers (size)
-- VALUES ("20"), ("40DR"), ("40DH"), ("45DH"), ("20RFR"), ("40RFR"), ("SPECIAL");

INSERT INTO availabilities (partnership_id, container_id, type)
VALUES (3, 1, "drop,pick"), (3, 2, "drop,pick"), (3, 3, "drop,pick"), (3, 4, "drop,pick"), (3, 5, "drop,pick"), (3, 6, "drop,pick"), (3, 7, "drop,pick");


SELECT terminals.name as "terminal", ssls.name AS "ssl", containers.size as "container", availabilities.type as "available",  availabilities.created_at AS "available_on"
FROM availabilities
JOIN partnerships ON partnerships.id = availabilities.partnership_id
JOIN terminals ON partnerships.terminal_id = terminals.id
JOIN ssls ON partnerships.ssl_id = ssls.id
JOIN containers ON availabilities.container_id = containers.id
WHERE 2022-04-30 <= DATE(availabilities.created_at) >= 2022-04-30
AND ssls.id in (1, 2, 3);

SELECT * FROM availabilities;
