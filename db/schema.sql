CREATE TABLE
    measurement
    (
        id bigint unsigned NOT NULL AUTO_INCREMENT,
        place VARCHAR(50),
        value DOUBLE,
        unit VARCHAR(25),
        measurement_date TIMESTAMP NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON
    UPDATE
        CURRENT_TIMESTAMP,
        type VARCHAR(50),
        PRIMARY KEY (id),
        INDEX place_ix (place),
        INDEX type_ix (type),
        INDEX measurement_date_ix (measurement_date)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8;