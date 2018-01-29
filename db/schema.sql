DROP TABLE event;
CREATE TABLE event (id bigint unsigned NOT NULL AUTO_INCREMENT, name varchar(50), description varchar(255), affected_measures varchar(50), start_date timestamp NULL, end_date timestamp NULL, affected_places varchar(50), PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
DROP TABLE measurement;
CREATE TABLE measurement (id bigint unsigned NOT NULL AUTO_INCREMENT, place varchar(50), value double, unit varchar(25), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, type varchar(50), value2 varchar(50), PRIMARY KEY (id), INDEX place_ix (place), INDEX type_ix (type), INDEX measurement_date_ix (measurement_date), INDEX value_ix (value)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
DROP TABLE presence;
CREATE TABLE presence (id bigint unsigned NOT NULL AUTO_INCREMENT, place varchar(50), person varchar(50), presence tinyint(1), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), INDEX place_ix (place), INDEX person_ix (person), INDEX measurement_date_ix (measurement_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
