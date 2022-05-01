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


select terminals.name as "terminal", ssls.name as "ssl", containers.size as "container", availabilities.type as "available",  availabilities.created_at as "available_on"
            from availabilities
            join partnerships on partnerships.id = availabilities.partnership_id
            join terminals on partnerships.terminal_id = terminals.id
            join ssls on partnerships.ssl_id = ssls.id
            join containers on availabilities.container_id = containers.id
            where date(created_at)
            between "2022-05-01"
            and "2022-05-01"
            ;

SELECT * FROM availabilities;
