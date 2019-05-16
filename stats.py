import harvester
import pandas as pd
import numpy as np
import xlsxwriter
from charts.file_format_chart import clean_formats


def outer_merge_frames(baseframe, appendframe, focal_point):
    return pd.merge(baseframe, appendframe, on=focal_point, how='outer')


if __name__ == '__main__':
    DATABASE_FILE = "C:\\Users\\Has112\\Documents\\ld-database.db"
    DATABASE_VERIFICATION_TEMPLATE = 'database/create_database.sql'
    WORKBOOK_NAME = 'Summary.xlsx'
    TOTAL_DOMAINS = 7460919
    INSERT_FIGURES = True

    # Open Workbook
    workbook = xlsxwriter.Workbook(WORKBOOK_NAME)

    # Define formats for the xlsxwriter to use.
    format_index_label = workbook.add_format({'bold': True,
                                              'align': 'right',
                                              'italic': True,
                                              'bg_color': '#95b3d7'})
    format_sheet_heading = workbook.add_format({'font_size': 16,
                                              'bold': True,
                                              'font_color': '#1f497d',
                                              'bottom': 5,
                                              'border_color': '#4f81bd'})
    format_column_summary = workbook.add_format({'bold': True,
                                                 'font_color': '#FFFFFF',
                                                 'font_size': 11,
                                                 'top': 5,
                                                 'border_color': '#3f4956',
                                                 'bg_color': '#4f81bd'})
    format_column_summary_extra = workbook.add_format({'bold': True,
                                                 'font_color': '#FFFFFF',
                                                 'font_size': 11,
                                                 'bg_color': '#4f81bd'})
    format_column_heading = workbook.add_format({'bold': True,
                                                 'font_color': '#FFFFFF',
                                                 'font_size': 13,
                                                 'bottom': 5,
                                                 'border_color': '#3f4956',
                                                 'bg_color': '#4f81bd'})
    format_even_data_cell = workbook.add_format({'align': 'right',
                                                 'bg_color': '#dce6f1'})
    format_odd_data_cell = workbook.add_format({'align': 'right',
                                                'bg_color': '#b8cce4'})

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
    row_idx = 2
    max = 0
    for index in summary.index:
        if len(index) > max:
            max = len(index)
    summary_worksheet.set_column(1, 1, max)
    for record in summary.iterrows():
        summary_worksheet.write(row_idx, 1, record[0], format_index_label)
        if record[0] == "Percentage of .au Domain Crawled":
            summary_worksheet.write(row_idx, 2, str(summary.loc["Percentage of .au Domain Crawled", 0]) + "%", format_even_data_cell)
        else:
            summary_worksheet.write(row_idx, 2, record[1], format_even_data_cell)
        row_idx += 1
    row_idx += 2
    if INSERT_FIGURES:
        summary_worksheet.insert_image(row_idx, 1, 'figures/project_progress.png')
    # Create a Crawl Summary Sheet in the WorkBook
    crawl_records = dbconnector.cursor.execute("""
        SELECT
            c.crawlID,
            strftime('%Y-%m-%d %H:%M:%S', startDate, 'unixepoch'),
            strftime('%Y-%m-%d %H:%M:%S', endDate, 'unixepoch'),
            (endDate - startDate) AS duration
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
    crawls['Duration'] = crawls['Duration'].apply(lambda x: x/3600)
    crawls['Duration'] = crawls['Duration'].round(3)
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
    crawls[['Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests', 'RDF Links Found']] = crawls[['Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests', 'RDF Links Found']].fillna(0)
    crawls[['Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests','RDF Links Found']] = crawls[['Seeds Processed', 'Failed Seeds', 'Links Visited', 'Average Domain Size', 'Failed Requests','RDF Links Found']].astype(np.int64)
    crawl_records_worksheet = workbook.add_worksheet('Crawl Records')
    crawl_records_worksheet.write(0, 0, 'Crawl Records', format_sheet_heading)
    row_idx = 2
    crawl_records_worksheet.set_column(2, 3, 19)
    crawl_records_worksheet.set_column(3, 10, 22.29)
    crawl_records_worksheet.write(row_idx, 1, 'CrawlID', format_column_heading)
    crawl_records_worksheet.write(row_idx, 2, 'Start Date', format_column_heading)
    crawl_records_worksheet.write(row_idx, 3, 'End Date', format_column_heading)
    crawl_records_worksheet.write(row_idx, 4, 'Duration (hours)', format_column_heading)
    crawl_records_worksheet.write(row_idx, 5, 'Seeds Processed', format_column_heading)
    crawl_records_worksheet.write(row_idx, 6, 'Failed Seeds', format_column_heading)
    crawl_records_worksheet.write(row_idx, 7, 'Links Visited', format_column_heading)
    crawl_records_worksheet.write(row_idx, 8, 'Average Domain Size', format_column_heading)
    crawl_records_worksheet.write(row_idx, 9, 'Failed Requests', format_column_heading)
    crawl_records_worksheet.write(row_idx, 10, 'RDF Links Found', format_column_heading)
    row_idx += 1
    for record in crawls.iterrows():
        if row_idx % 2 == 0:
            format_data_cell = format_even_data_cell
        else:
            format_data_cell = format_odd_data_cell
        crawl_records_worksheet.write(row_idx, 1, record[1][0], format_index_label)
        crawl_records_worksheet.write(row_idx, 2, record[1][1], format_data_cell)
        crawl_records_worksheet.write(row_idx, 3, record[1][2], format_data_cell)
        crawl_records_worksheet.write(row_idx, 4, record[1][3], format_data_cell) if not np.isnan(record[1][3]) else crawl_records_worksheet.write(row_idx, 4, '', format_data_cell)
        crawl_records_worksheet.write(row_idx, 5, record[1][4], format_data_cell)
        crawl_records_worksheet.write(row_idx, 6, record[1][5], format_data_cell)
        crawl_records_worksheet.write(row_idx, 7, record[1][6], format_data_cell)
        crawl_records_worksheet.write(row_idx, 8, record[1][7], format_data_cell)
        crawl_records_worksheet.write(row_idx, 9, record[1][8], format_data_cell)
        crawl_records_worksheet.write(row_idx, 10, record[1][9], format_data_cell)
        row_idx += 1
    crawl_records_worksheet.write(row_idx, 1, 'TOTAL', format_column_summary)
    crawl_records_worksheet.write(row_idx, 2, '', format_column_summary)
    crawl_records_worksheet.write(row_idx, 3, '', format_column_summary)
    crawl_records_worksheet.write(row_idx, 4, crawls['Duration'].sum().round(3), format_column_summary)
    crawl_records_worksheet.write(row_idx, 5, crawls['Seeds Processed'].sum(), format_column_summary)
    crawl_records_worksheet.write(row_idx, 6, crawls['Failed Seeds'].sum(), format_column_summary)
    crawl_records_worksheet.write(row_idx, 7, crawls['Links Visited'].sum(), format_column_summary)
    crawl_records_worksheet.write(row_idx, 8, crawls['Average Domain Size'].sum(), format_column_summary)
    crawl_records_worksheet.write(row_idx, 9, crawls['Failed Requests'].sum(), format_column_summary)
    crawl_records_worksheet.write(row_idx, 10, crawls['RDF Links Found'].sum(), format_column_summary)
    row_idx += 1
    crawl_records_worksheet.write(row_idx, 1, 'MEAN', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 2, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 3, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 4, crawls['Duration'].mean().round(3), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 5, crawls['Seeds Processed'].mean().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 6, crawls['Failed Seeds'].mean().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 7, crawls['Links Visited'].mean().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 8, crawls['Average Domain Size'].mean().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 9, crawls['Failed Requests'].mean().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 10, crawls['RDF Links Found'].mean().round(2), format_column_summary_extra)
    row_idx += 1
    crawl_records_worksheet.write(row_idx, 1, 'MEDIAN', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 2, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 3, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 4, crawls['Duration'].median().round(3), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 5, crawls['Seeds Processed'].median(), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 6, crawls['Failed Seeds'].median(), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 7, crawls['Links Visited'].median(), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 8, crawls['Average Domain Size'].median(), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 9, crawls['Failed Requests'].median(), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 10, crawls['RDF Links Found'].median(), format_column_summary_extra)
    row_idx += 1
    crawl_records_worksheet.write(row_idx, 1, 'STD', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 2, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 3, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 4, crawls['Duration'].std().round(3), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 5, crawls['Seeds Processed'].std().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 6, crawls['Failed Seeds'].std().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 7, crawls['Links Visited'].std().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 8, crawls['Average Domain Size'].std().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 9, crawls['Failed Requests'].std().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 10, crawls['RDF Links Found'].std().round(2), format_column_summary_extra)
    row_idx += 1
    crawl_records_worksheet.write(row_idx, 1, 'VAR', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 2, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 3, '', format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 4, crawls['Duration'].var().round(3), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 5, crawls['Seeds Processed'].var().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 6, crawls['Failed Seeds'].var().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 7, crawls['Links Visited'].var().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 8, crawls['Average Domain Size'].var().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 9, crawls['Failed Requests'].var().round(2), format_column_summary_extra)
    crawl_records_worksheet.write(row_idx, 10, crawls['RDF Links Found'].var().round(2), format_column_summary_extra)
    if INSERT_FIGURES:
        row_idx += 3
        crawl_records_worksheet.write(row_idx, 0, 'Analytics and Figures', format_sheet_heading)
        row_idx += 2
        crawl_records_worksheet.insert_image(row_idx, 1, 'figures/seeds_crawl_size_time.png')
        row_idx += 23
        crawl_records_worksheet.insert_image(row_idx, 1, 'figures/requests_crawl_size_time.png')
        row_idx += 23
        crawl_records_worksheet.insert_image(row_idx, 1, 'figures/seeds_requests_crawl_size_time.png')
        row_idx += 23
        crawl_records_worksheet.insert_image(row_idx, 1, 'figures/rdf_domain_size_histogram.png')
        row_idx += 23
        crawl_records_worksheet.insert_image(row_idx, 1, 'figures/domain_size_histogram.png')
        row_idx += 23

    # Create Format Summary Worksheet
    response_format_summary_sheet = workbook.add_worksheet('Format Summary')
    response_format_summary_sheet.write(0, 0, 'Format Summary', format_sheet_heading)
    response_formats = dbconnector.cursor.execute("""
        SELECT 
            crawlid, 
            contentFormat, 
            COUNT(contentFormat) 
        FROM LINK
        GROUP BY 
            crawlid, 
            contentFormat;
    """)
    response_format_data = pd.DataFrame(response_formats, columns=['Crawl ID', 'Format', 'Count']).pivot(index='Crawl ID', columns='Format', values='Count').fillna(0)
    format_types = response_format_data.columns
    collapse_map = {}
    focus_formats = ['text/html',
                        'text/xml',
                        'application/json',
                        'application/ld+json',
                        'application/rdf+xml',
                        'text/plain',
                        'text/turtle',
                        'application/owl+xml',
                        'text/trig',
                        'application/xml'
                        'application/n-quads']
    other_formats = []
    for format in format_types:
        if format.startswith("#<Mime::NullType:") or format == '' or format == "N/A":
            collapse_map[format] = 'No Format'
        elif len(format.split(",")) > 1:
            collapse_map[format] = 'Other Format'
        elif format not in focus_formats:
            collapse_map[format] = 'Other Format'
            other_formats.append(format)
        else:
            collapse_map[format] = format
    response_format_data = response_format_data.groupby(collapse_map, axis=1).sum().reset_index(level=0)
    response_format_data['Crawl ID'] = response_format_data['Crawl ID'].astype(np.int64)
    response_format_data = outer_merge_frames(crawls['Crawl ID'], response_format_data, 'Crawl ID')
    row_idx = 2
    i = 1
    max = 0
    for heading in response_format_data.columns:
        if len(heading) > max:
            max = len(heading)
        response_format_summary_sheet.write(row_idx, i, heading, format_column_heading)
        i += 1
    row_idx += 1
    response_format_summary_sheet.set_column(2, len(response_format_data.columns)+1, max + 1)
    for record in response_format_data.iterrows():
        if row_idx % 2 == 0:
            format_data_cell = format_even_data_cell
        else:
            format_data_cell = format_odd_data_cell
        response_format_summary_sheet.write(row_idx, 1, record[1][0], format_index_label)
        col_idx = 2
        for cell in record[1][1:]:
            response_format_summary_sheet.write(row_idx, col_idx, cell, format_data_cell) if not np.isnan(cell) else response_format_summary_sheet.write(row_idx, col_idx, '0', format_data_cell)
            col_idx += 1
        row_idx += 1
    response_format_summary_sheet.write(row_idx, 1, 'TOTAL', format_column_summary)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        response_format_summary_sheet.write(row_idx, col_idx, response_format_data[heading].sum(), format_column_summary)
        col_idx += 1
    row_idx += 1
    response_format_summary_sheet.write(row_idx, 1, 'MEAN', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        response_format_summary_sheet.write(row_idx, col_idx, response_format_data[heading].mean().round(2), format_column_summary_extra)
        col_idx += 1
    row_idx += 1
    response_format_summary_sheet.write(row_idx, 1, 'MEDIAN', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        response_format_summary_sheet.write(row_idx, col_idx, response_format_data[heading].median(), format_column_summary_extra)
        col_idx += 1
    row_idx += 1
    response_format_summary_sheet.write(row_idx, 1, 'STD', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        response_format_summary_sheet.write(row_idx, col_idx, response_format_data[heading].std().round(2), format_column_summary_extra)
        col_idx += 1
    row_idx += 1
    response_format_summary_sheet.write(row_idx, 1, 'VAR', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        response_format_summary_sheet.write(row_idx, col_idx, response_format_data[heading].var().round(2), format_column_summary_extra)
        col_idx += 1
    if INSERT_FIGURES:
        row_idx += 3
        response_format_summary_sheet.write(row_idx, 0, 'Charts and Figures', format_sheet_heading)
        row_idx += 2
        response_format_summary_sheet.insert_image(row_idx, 1, 'figures/content_format_pie.png')
        row_idx += 23
        response_format_summary_sheet.insert_image(row_idx, 1, 'figures/content_format_bar.png')
        row_idx += 23
        response_format_summary_sheet.insert_image(row_idx, 1, 'figures/rdf_content_format_pie.png')
        row_idx += 23
        response_format_summary_sheet.insert_image(row_idx, 1, 'figures/rdf_content_format_bar.png')
        row_idx += 23

    # Create Sheet Containing Data on ALL formats that are included under other.
    all_formats_worksheet = workbook.add_worksheet('All Formats')
    all_formats_worksheet.write(0,0, 'All Formats Detected')
    response_formats = dbconnector.cursor.execute("""
            SELECT 
                crawlid, 
                contentFormat, 
                COUNT(contentFormat) 
            FROM LINK
            GROUP BY 
                crawlid, 
                contentFormat;
        """)
    response_format_data = pd.DataFrame(response_formats, columns=['Crawl ID', 'Format', 'Count']).pivot(
        index='Crawl ID', columns='Format', values='Count').fillna(0)
    format_types = response_format_data.columns
    collapse_map = {}
    for format in format_types:
        if format.startswith("#<Mime::NullType:") or format == '' or format == "N/A":
            collapse_map[format] = 'No Format'
        elif len(format.split(",")) > 1:
            collapse_map[format] = 'Multiple Formats'
        else:
            collapse_map[format] = format
    response_format_data = response_format_data.groupby(collapse_map, axis=1).sum().reset_index(level=0)
    response_format_data['Crawl ID'] = response_format_data['Crawl ID'].astype(np.int64)
    response_format_data = outer_merge_frames(crawls['Crawl ID'], response_format_data, 'Crawl ID')
    row_idx = 2
    i = 1
    for heading in response_format_data.columns:
        all_formats_worksheet.set_column(i, i, len(heading) + 2)
        all_formats_worksheet.write(row_idx, i, heading, format_column_heading)
        i += 1
    row_idx += 1
    for record in response_format_data.iterrows():
        if row_idx % 2 == 0:
            format_data_cell = format_even_data_cell
        else:
            format_data_cell = format_odd_data_cell
        all_formats_worksheet.write(row_idx, 1, record[1][0], format_index_label)
        col_idx = 2
        for cell in record[1][1:]:
            all_formats_worksheet.write(row_idx, col_idx, cell, format_data_cell) if not np.isnan(
                cell) else all_formats_worksheet.write(row_idx, col_idx, '0', format_data_cell)
            col_idx += 1
        row_idx += 1
    all_formats_worksheet.write(row_idx, 1, 'TOTAL', format_column_summary)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        all_formats_worksheet.write(row_idx, col_idx, response_format_data[heading].sum(),
                                            format_column_summary)
        col_idx += 1
    row_idx += 1
    all_formats_worksheet.write(row_idx, 1, 'MEAN', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        all_formats_worksheet.write(row_idx, col_idx, response_format_data[heading].mean().round(2),
                                            format_column_summary_extra)
        col_idx += 1
    row_idx += 1
    all_formats_worksheet.write(row_idx, 1, 'MEDIAN', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        all_formats_worksheet.write(row_idx, col_idx, response_format_data[heading].median(),
                                            format_column_summary_extra)
        col_idx += 1
    row_idx += 1
    all_formats_worksheet.write(row_idx, 1, 'STD', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        all_formats_worksheet.write(row_idx, col_idx, response_format_data[heading].std().round(2),
                                            format_column_summary_extra)
        col_idx += 1
    row_idx += 1
    all_formats_worksheet.write(row_idx, 1, 'VAR', format_column_summary_extra)
    col_idx = 2
    for heading in response_format_data.columns[1:]:
        all_formats_worksheet.write(row_idx, col_idx, response_format_data[heading].var().round(2),
                                            format_column_summary_extra)
        col_idx += 1
        
    workbook.close()
    

