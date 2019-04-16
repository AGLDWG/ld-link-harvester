import os
import harvester


def test_database_verification_bad():
    """
    If the database file provided to the function has an invalid schema that does not match the factory schema, the function should flag this.
    """
    bad_db = harvester.LDHarvesterDatabaseConnector('integrity_bad.sql')
    template = '../../database/create_database.sql'
    assert not harvester.verify_database(bad_db, template)
    bad_db.close()
    os.remove('integrity_bad.sql')


def test_database_verification_good():
    """
    If the database file provided to the function has a valid schema, it returns true.
    """
    good_db = harvester.LDHarvesterDatabaseConnector('integrity_good.sql')
    with open('../../database/create_database.sql', 'r') as script:
        good_db.cursor.executescript(script.read())
    template = '../../database/create_database.sql'
    assert harvester.verify_database(good_db, template)
    good_db.close()
    os.remove('integrity_good.sql')

