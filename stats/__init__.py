import harvester
import pandas as pd
if __name__ == '__main__':
    DATABASE_FILE = "../charts/ld-database.db"

    DATABASE_VERIFICATION_TEMPLATE = '../database/create_database.sql'

    # Connect to Database
    dbconnector, crawl_id = harvester.connect(DATABASE_FILE, crawl=False)
    if harvester.verify_database(dbconnector, DATABASE_VERIFICATION_TEMPLATE):
        print("Database schema integrity has been verified.")
    else:
        print("Error, database schema does not match the provided template.")
        exit(1)

    total_links_visited = dbconnector.cursor.execute("""
        SELECT COUNT(*) FROM Link;
    """).fetchone()[0]

    total_seeds_visited = dbconnector.cursor.execute("""
        SELECT COUNT(*) FROM Seed;
    """).fetchone()[0]

    total_rdf_links_found = dbconnector.cursor.execute("""
        SELECT COUNT(*) FROM RdfURI;
    """).fetchone()[0]

    total_crawls = dbconnector.cursor.execute("""
        SELECT COUNT(DISTINCT crawlId) FROM Crawl;
    """).fetchone()[0]

    total_failed_seeds = dbconnector.cursor.execute("""
        SELECT COUNT(DISTINCT seedURI) FROM FailedSeed;
    """).fetchone()[0]

    total_failed_requests = total_links_visited = dbconnector.cursor.execute("""
        SELECT COUNT(*) FROM Link WHERE failed=1;
    """).fetchone()[0]

    summary = pd.DataFrame([total_crawls, total_seeds_visited, total_failed_seeds, total_links_visited, total_failed_requests, total_rdf_links_found])
    print(summary)
