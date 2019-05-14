import harvester
import pandas as pd
import numpy as np
import xlsxwriter


def outer_merge_frames(baseframe, appendframe, focal_point):
    return pd.merge(baseframe, appendframe, on=focal_point, how='outer')

if __name__ == '__main__':
    DATABASE_FILE = "C:\\Users\\Has112\\Documents\\ld-database.db"
    DATABASE_VERIFICATION_TEMPLATE = 'database/create_database.sql'
    WORKBOOK_NAME = 'Summary.xlsx'
    TOTAL_DOMAINS = 7460919
    # Open Workbook
    workbook = xlsxwriter.Workbook(WORKBOOK_NAME)
    format_index_label = workbook.add_format({'bold': True,
                                              'align': 'right',
                                              'shrink': True})
    format_sheet_heading = workbook.add_format({'font_size': 16,
                                              'bold': True,
                                              'font_color': '#1f497d',
                                              'bottom': 5,
                                              'border_color': '#4f81bd'})
    format_data_cell = workbook.add_format({'align': 'right'})

    # Connect to Database
    dbconnector, crawl_id = harvester.connect(DATABASE_FILE, crawl=False)
    if harvester.verify_database(dbconnector, DATABASE_VERIFICATION_TEMPLATE):
        print("Database schema integrity has been verified.")
    else:
        print("Error, database schema does not match the provided template.")
        exit(1)

    # Request Summary Data from Database
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

    total_failed_requests = dbconnector.cursor.execute("""
        SELECT COUNT(*) FROM Link WHERE failed=1;
    """).fetchone()[0]

    # Create 'Summary' Worksheet and Write Data To It.
    summary_worksheet = workbook.add_worksheet('Summary')
    summary_worksheet.write(0, 0, 'Summary', format_sheet_heading)
    summary = pd.DataFrame([total_crawls, total_seeds_visited, total_failed_seeds, total_links_visited, total_failed_requests, total_rdf_links_found, round((total_seeds_visited / TOTAL_DOMAINS)*100, 2)], index=['Total Crawls Made', 'Total Seeds Visited', 'Total Failed Seeds', 'Total Links Visited', 'Total Failed Link Requests', 'Total RDF Links Found', "Percentage of .au Domain Crawled"])
    #summary.to_excel('Summary.xlsx', header=False, sheet_name="Summary", startrow=1, startcol=1, merge_cells=False)
    row_idx = 2
    max = 0
    for index in summary.index:
        if len(index) > max:
            max = len(index)
    summary_worksheet.set_column(1, 1, max)
    for record in summary.iterrows():
        summary_worksheet.write(row_idx, 1, record[0], format_index_label)
        if record[0] == "Percentage of .au Domain Crawled":
            summary_worksheet.write(row_idx, 2, str(summary.loc["Percentage of .au Domain Crawled", 0]) + "%", format_data_cell)
        else:
            summary_worksheet.write(row_idx, 2, record[1], format_data_cell)
        row_idx += 1

    # Create a Crawl Summary Sheet in the WorkBook
    crawl_records = dbconnector.cursor.execute("""
        SELECT 
            c.crawlID, 
            startDate, 
            endDate, endDate - startDate AS duration
        FROM 
	        CRAWL as c;
    """).fetchall()
    seeds_per_crawl = dbconnector.cursor.execute("""
        SELECT 
            c.crawlID, 
            COUNT(distinct originseedURI)
        FROM 
            Crawl as c,
            Link as l
        WHERE c.crawlID = l.crawlID
        GROUP BY c.crawlID;
    """).fetchall()
    failed_seeds_per_crawl = dbconnector.cursor.execute("""
        SELECT 
            c.crawlID, 
            COUNT(distinct seedURI)
        FROM 
            Crawl as c,
            FailedSeed as fs
        WHERE c.crawlID = fs.crawlID
        GROUP BY c.crawlID;
    """).fetchall()
    links_visited_per_crawl = dbconnector.cursor.execute("""
        SELECT 
            crawlID, 
            COUNT(address) as linksvisited, 
            COUNT(address)/COUNT(distinct originseedURI) as averagedomain
        FROM Link
        GROUP BY crawlID;    
    """).fetchall()
    links_failed_per_crawl = dbconnector.cursor.execute("""
        SELECT 
            crawlID, 
            COUNT(address) as failedlinks
        FROM Link
        WHERE failed = 1
        GROUP BY crawlID;
    """).fetchall()
    rdf_links_found_per_crawl = dbconnector.cursor.execute("""
        SELECT 
            c.crawlID, 
            COUNT(rdfseeduri)
        FROM
            Crawl as c,
            RdfURI as r
        WHERE c.crawlID = r.crawlID
        GROUP BY c.crawlID;
    """).fetchall()
    crawls = pd.DataFrame(crawl_records, columns=['Crawl ID', 'Start', 'End', 'Duration'])
    seeds_per_crawl = pd.DataFrame(seeds_per_crawl, columns=['Crawl ID', 'Seeds Processed'])
    crawls = outer_merge_frames(crawls, seeds_per_crawl, 'Crawl ID')
    failed_seeds_per_crawl = pd.DataFrame(failed_seeds_per_crawl, columns=['Crawl ID', 'Failed Seeds'])
    crawls = outer_merge_frames(crawls, failed_seeds_per_crawl, 'Crawl ID')
    links_visited_per_crawl = pd.DataFrame(links_visited_per_crawl, columns=['Crawl ID', 'Links Visited', 'Average Domain Size'])
    links_visited_per_crawl['Crawl ID'] = links_visited_per_crawl['Crawl ID'].astype(np.int64)
    crawls = outer_merge_frames(crawls, links_visited_per_crawl, 'Crawl ID')
    links_failed_per_crawl = pd.DataFrame(links_failed_per_crawl, columns=['Crawl ID', 'Failed Requests'])
    links_failed_per_crawl['Crawl ID'] = links_failed_per_crawl['Crawl ID'].astype(np.int64)
    crawls = outer_merge_frames(crawls, links_failed_per_crawl, 'Crawl ID')
    rdf_links_found_per_crawl = pd.DataFrame(rdf_links_found_per_crawl, columns=['Crawl ID', 'RDF Links Found'])
    rdf_links_found_per_crawl['Crawl ID'] = rdf_links_found_per_crawl['Crawl ID'].astype(np.int64)
    crawls = outer_merge_frames(crawls, rdf_links_found_per_crawl, 'Crawl ID')
    crawls[['Duration', 'Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests', 'RDF Links Found']] = crawls[['Duration', 'Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests', 'RDF Links Found']].fillna(0)
    crawls[['Duration', 'Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests','RDF Links Found']] = crawls[['Duration', 'Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests','RDF Links Found']].astype(np.int64)
    crawl_records_worksheet = workbook.add_worksheet('Crawl Records')
    crawl_records_worksheet.write(0, 0, 'Crawl Records', format_sheet_heading)
    row_idx = 2
    # for record in crawls.iterrows():
    #     print(record)
    #     crawl_records_worksheet.write(row_idx, 1, record[0], format_index_label)
    #     crawl_records_worksheet.write(row_idx, 2, str(record[1]), format_index_label)
    #     crawl_records_worksheet.write(row_idx, 3, record[2], format_index_label)
    #     crawl_records_worksheet.write(row_idx, 4, record[3], format_index_label)
    #     crawl_records_worksheet.write(row_idx, 5, record[4], format_index_label)
    #     crawl_records_worksheet.write(row_idx, 6, record[5], format_index_label)
    #     crawl_records_worksheet.write(row_idx, 7, record[6], format_index_label)
    #     row_idx += 1
    # workbook.close()


