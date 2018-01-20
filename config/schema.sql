CREATE TABLE
    humidity
    (
        id bigint unsigned NOT NULL AUTO_INCREMENT,
        room VARCHAR(50),
        humidity DOUBLE,
        unit VARCHAR(25),
        measurement_date TIMESTAMP NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        PRIMARY KEY (id)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE
    temperature
    (
        id bigint unsigned NOT NULL AUTO_INCREMENT,
        room VARCHAR(50),
        temperature DOUBLE,
        unit VARCHAR(25),
        measurement_date TIMESTAMP NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        PRIMARY KEY (id)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8;
    