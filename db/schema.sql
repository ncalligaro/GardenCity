#Main DB
CREATE DATABASE gardenCity;
USE gardenCity;

DROP TABLE event;
CREATE TABLE event (id bigint unsigned NOT NULL AUTO_INCREMENT, name varchar(50), description varchar(255), affected_measures varchar(50), start_date timestamp NULL, end_date timestamp NULL, affected_places varchar(50), replicated tinyint(1), PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_general_ci;
DROP TABLE heater;
CREATE TABLE heater (id bigint unsigned NOT NULL AUTO_INCREMENT, state varchar(50), reason varchar(50), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, reason_explanation varchar(255), replicated tinyint(1), PRIMARY KEY (id), INDEX measurement_date_ix (measurement_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_general_ci;
DROP TABLE measurement;
CREATE TABLE measurement (id bigint unsigned NOT NULL AUTO_INCREMENT, place varchar(50), value double, unit varchar(25), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, type varchar(50), value2 varchar(50), replicated tinyint(1), PRIMARY KEY (id), INDEX place_ix (place), INDEX type_ix (type), INDEX measurement_date_ix (measurement_date), INDEX value_ix (value)) ENGINE=InnoDB DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_general_ci;
DROP TABLE presence;
CREATE TABLE presence (id bigint unsigned NOT NULL AUTO_INCREMENT, place varchar(50), person varchar(50), presence tinyint(1), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, replicated tinyint(1), PRIMARY KEY (id), INDEX place_ix (place), INDEX person_ix (person), INDEX measurement_date_ix (measurement_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8 DEFAULT COLLATE=utf8_general_ci;

#Temporary Satellite
#CREATE DATABASE gardenCity;
#USE gardenCity;

#DROP TABLE event;
#CREATE TABLE event (id bigint unsigned NOT NULL AUTO_INCREMENT, name varchar(50), description varchar(255), affected_measures varchar(50), start_date timestamp NULL, end_date timestamp NULL, affected_places varchar(50), replicated BOOLEAN, PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
#DROP TABLE heater;
#CREATE TABLE heater (id bigint unsigned NOT NULL AUTO_INCREMENT, state varchar(50), reason varchar(50), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, reason_explanation varchar(255), replicated BOOLEAN, PRIMARY KEY (id), INDEX measurement_date_ix (measurement_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
#DROP TABLE measurement;
#CREATE TABLE measurement (id bigint unsigned NOT NULL AUTO_INCREMENT, place varchar(50), value double, unit varchar(25), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, type varchar(50), value2 varchar(50), replicated BOOLEAN, PRIMARY KEY (id), INDEX place_ix (place), INDEX type_ix (type), INDEX measurement_date_ix (measurement_date), INDEX value_ix (value)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
#DROP TABLE presence;
#CREATE TABLE presence (id bigint unsigned NOT NULL AUTO_INCREMENT, place varchar(50), person varchar(50), presence tinyint(1), measurement_date timestamp NULL, created_at timestamp NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, replicated BOOLEAN, PRIMARY KEY (id), INDEX place_ix (place), INDEX person_ix (person), INDEX measurement_date_ix (measurement_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8;

