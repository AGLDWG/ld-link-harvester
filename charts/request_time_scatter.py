import pandas as pd
import matplotlib.pyplot as plt


def seed_count_time_scatter(data, title):
    """
    Produces a scatter plot based on the seeds visited (per crawl) and time.
    :param data: array
    :param title: str
    :return: None
    """
    data = pd.DataFrame(data, columns=['Crawl', 'Elapsed Time (s)', 'Seeds Visited (per crawl)'])
    data.plot.scatter(y='Elapsed Time (s)',
                      x='Seeds Visited (per crawl)')
    plt.title(title)


def request_count_time_scatter(data, title):
    """
    Produces a scatter plot based on the number of links visited per crawl and time.
    :param data: array
    :param title: str
    :return: None
    """
    data = pd.DataFrame(data, columns=['Crawl', 'Elapsed Time (s)', 'Total Links Visited (per crawl)'])
    data.plot.scatter(y='Elapsed Time (s)',
                      x='Total Links Visited (per crawl)')
    plt.title(title)


def seed_count_time_scatter_3d(data, title):
    """
    Produces a three-dimensional scatter plot of seeds and links visited per crawl against time.
    The third dimension (time) is represented by colour.
    :param data: array
    :param title: str
    :return: None
    """
    data = pd.DataFrame(data, columns=['Crawl', 'Elapsed Time (s)', 'Seeds Visited (per crawl)', 'Total Links Visited (per crawl)'])
    data.plot.scatter(y='Total Links Visited (per crawl)',
                      x='Seeds Visited (per crawl)',
                      c='Elapsed Time (s)',
                      colormap='viridis')
    plt.title(title)
