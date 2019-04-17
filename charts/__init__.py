from charts import progress_chart, file_format_chart, size_histogram
import harvester
import matplotlib.pyplot as plt
import os
import shutil

if __name__ == '__main__':
    DATABASE_FILE = "ld-database.db"
    DATABASE_VERIFICATION_TEMPLATE = '../database/create_database.sql'
    SAVE_CHART = True
    SAVE_CHART_DIRECTORY = './figures/'  # Should end with '/'
    SHOW_CHART = False
    TOTAL_DOMAINS = 7460919

    # Connect to Database
    dbconnector, crawl_id = harvester.connect(DATABASE_FILE, crawl=False)
    if harvester.verify_database(dbconnector, DATABASE_VERIFICATION_TEMPLATE):
        print("Database schema integrity has been verified.")
    else:
        print("Error, database schema does not match the provided template.")
        exit(1)

    # Override existing output folder if it exists
    if not os.path.exists(SAVE_CHART_DIRECTORY):
        os.mkdir(SAVE_CHART_DIRECTORY)
    else:
        shutil.rmtree(SAVE_CHART_DIRECTORY)
        os.mkdir(SAVE_CHART_DIRECTORY)

    # Plot Progress Pie Chart
    dbconnector.cursor.execute("""
        SELECT COUNT(DISTINCT originSeedUri) 
        FROM LINK
    """)
    VISITED_DOMAINS = dbconnector.cursor.fetchone()[0]
    progress_chart.progress_chart_pie(VISITED_DOMAINS, TOTAL_DOMAINS, "Project Progress")
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'project_progress.png', bbox_inches="tight", dpi=300)
    plt.close()

    # Plot Response Format Pie Chart
    dbconnector.cursor.execute("""
        SELECT contentFormat, COUNT(contentFormat) 
        FROM LINK
        GROUP BY contentFormat;
    """)
    content_format_dict = dict(dbconnector.cursor.fetchall())
    file_format_chart.clean_formats(content_format_dict)
    file_format_chart.file_format_pie(content_format_dict, 'Response Format Breakdown')
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'content_format_pie.png', bbox_inches="tight", dpi=300)
    plt.close()

    # Plot Response Format Bar Chart
    file_format_chart.file_format_bar(content_format_dict, 'Response Format Breakdown')
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'content_format_bar.png', bbox_inches="tight", dpi=300)
    plt.close()

    # Plot RDF Response Format Pie Chart
    dbconnector.cursor.execute("""
            SELECT contentFormat, COUNT(contentFormat) 
            FROM RdfURI
            GROUP BY contentFormat;
        """)
    content_format_dict = dict(dbconnector.cursor.fetchall())
    file_format_chart.clean_formats(content_format_dict)
    file_format_chart.file_format_pie(content_format_dict, 'RDF Format Breakdown')
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'rdf_content_format_pie.png', bbox_inches="tight", dpi=300)
    plt.close()

    # Plot RDF Response Format Bar Chart
    file_format_chart.file_format_bar(content_format_dict, 'RDF Format Breakdown')
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'rdf_content_format_bar.png', bbox_inches="tight", dpi=300)
    plt.close()

    # Plot Site Size Histogram
    dbconnector.cursor.execute("""
        SELECT originSeedURI, COUNT(DISTINCT address)
        FROM Link
        GROUP BY originSeedURI
        HAVING COUNT(DISTINCT address) > 1;
    """)
    seed_size_data = dbconnector.cursor.fetchall()
    size_histogram.plot_size_histogram(seed_size_data, 200, "Domain Size Distribution")
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'domain_size_histogram.png', bbox_inches="tight", dpi=300)
    plt.close()

    # Plot RDF Per Site Histogram
    dbconnector.cursor.execute("""
            SELECT originSeedURI, COUNT(DISTINCT rdfSeedURI)
            FROM RdfURI
            GROUP BY originSeedURI
            HAVING COUNT(DISTINCT rdfSeedURI) > 1;
        """)
    seed_size_data = dbconnector.cursor.fetchall()
    size_histogram.plot_size_histogram(seed_size_data, 200, "RDF Domain Size Distribution")
    if SHOW_CHART:
        plt.show()
    if SAVE_CHART:
        plt.savefig(SAVE_CHART_DIRECTORY + 'rdf_domain_size_histogram.png', bbox_inches="tight", dpi=300)
    plt.close()
