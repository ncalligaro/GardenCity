#!/usr/bin/python
from config import config

import commonFunctions

import mysql.connector as mariadb

import traceback
import logging

import sys


logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

def replicate_table(table_name):
    if table_name is None:
        raise Exception("table_name must have a value")

    src_db_connection = None
    replicated_db_connection = None
    src_cursor = None
    try:
        src_db_connection = commonFunctions.connect_to_db(config.mysql)
        replicated_db_connection = commonFunctions.connect_to_db(config.replicator['db'])

        query_sentence = ("SELECT * FROM %s where %s = false or %s is null" % (table_name, config.replicator['replicated_attribute'], config.replicator['replicated_attribute']))
        logging.debug("Fetching records from src table: %s", query_sentence)

        logging.debug("Number of records to be replicated for table {}: {}".format(table_name,
                                                                                   count_pending_replication_records_for_table(
                                                                                       config.mysql, table_name)))
        src_cursor = src_db_connection.cursor()
        src_cursor.execute(query_sentence)

        while True:
            record = commonFunctions.fetch_one_record_as_dictionary(src_cursor)
            if record is None:
                logging.debug("Next record was empty")
                break
            logging.debug("duplicating record %s" % record['id'])
            insert_record_in_replicated_db(record, table_name, config.replicator['db'])
            update_record_as_replicated(record, table_name, config.mysql)
        return True

    except mariadb.Error as error:
        logging.debug("Error saving to DB: {}".format(error))
        logging.error("Query is %s", query_sentence)
        return False

    finally:
        if src_cursor is not None:
            src_cursor.close()
        if src_db_connection is not None:
            src_db_connection.close()
        if replicated_db_connection is not None:
            replicated_db_connection.close()

def count_pending_replication_records_for_table(db_connection_config, table_name):
    cursor = None
    connection = None
    try:
        query_sentence = ("SELECT count(*) FROM %s where %s = false or %s is null" % (table_name, config.replicator['replicated_attribute'], config.replicator['replicated_attribute']))
        logging.debug("Counting records from src table: %s", query_sentence)

        connection = commonFunctions.connect_to_db(db_connection_config)
        cursor = connection.cursor()
        cursor.execute(query_sentence)
        count = cursor.fetchone()
        return count[0];
    except mariadb.Error as error:
        logging.debug("Error saving to DB: {}".format(error))
        logging.error("Query is %s", query_sentence)
        return -1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def insert_record_in_replicated_db(original_record, table_name, db_connection_config):
    if original_record is None:
        raise Exception("record must have a value")
    if table_name is None:
        raise Exception("table_name must have a value")

    connection = None
    cursor = None

    try:
        #Don't duplicate the id, let the DB generate one
        connection = commonFunctions.connect_to_db(db_connection_config)
        record = original_record.copy()
        del record['id']
        del record[config.replicator['replicated_attribute']]

        insert_sentence = ("INSERT INTO %s (%s) VALUES (%s)" % (table_name, ", ".join(record.keys()), get_values_with_types_for_insert(record)))
        logging.debug("Inserting record using sentence %s" % (insert_sentence))
        cursor = connection.cursor()
        cursor.execute(insert_sentence)
        connection.commit()
        logging.debug("Insert successful")
    except mariadb.Error as error:
        logging.debug("Error saving to DB: {}".format(error))
        logging.error("Query is %s", insert_sentence)
        return -1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def get_values_with_types_for_insert(record):
    values_string = None
    for key in record.keys():
        value = record[key]
        logging.debug("is key %s a number %s" % (key, is_key_a_number(key)))
        if not is_key_a_number(key) and not is_value_null(value):
            value = "'%s'" % value

        if values_string is None:
            values_string = value
        else:
            values_string = "%s, %s" % (values_string, value)

    return values_string

def is_key_a_number(key):
    number_columns = ['id', 'replicated', 'value', 'presence']
    return (key in number_columns)

def is_value_null(value):
    return 'null' == value

def update_record_as_replicated(record, table_name, db_connection_config):
    if record is None:
        raise Exception("record must have a value")
    connection = None
    cursor = None
    try:
        connection = commonFunctions.connect_to_db(db_connection_config)
        update_sentence = ("UPDATE %s SET %s = true where id = %s LIMIT 1" % (table_name, config.replicator['replicated_attribute'], record['id']))
        logging.debug("Updating record %s with sentence %s" % (record['id'], update_sentence))
        cursor = connection.cursor()
        cursor.execute(update_sentence)
        connection.commit()
        logging.debug("Update successful")
    except mariadb.Error as error:
        logging.debug("Error saving to DB: {}".format(error))
        logging.error("Query is %s", update_sentence)
        logging.error(error)
        logging.error(traceback.format_exc())
        return -1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def delete_replicated_up_to(table_name, max_age_in_source_in_hours):
    return

def main():
    logging.info("Saving to file: %s" % (config.file['save_to_file']))
    logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
    logging.info("Starting loop")
    try:
        for table in config.replicator['tables_to_replicate']:
            logging.debug("replicating table %s" % table)
            result = replicate_table(table)
            if result:
                delete_replicated_up_to(table, config.replicator['max_age_in_source_in_hours'])

    except KeyboardInterrupt:
        logging.error("\nbye!")
        sys.exit(1)
    except Exception as e:
        logging.error("\nOther error occurred")
        logging.error (e)
        logging.error(traceback.format_exc())
        sys.exit(1)

# call main
if __name__ == '__main__':
   main()
