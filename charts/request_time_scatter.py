import pandas as pd
import matplotlib.pyplot as plt


def seed_count_time_scatter(data, title):
    data = pd.DataFrame(data, columns=['Crawl', 'Elapsed Time (s)', 'Seeds Visited (per crawl)'])
    data.plot.scatter(y='Elapsed Time (s)',
                      x='Seeds Visited (per crawl)')
    plt.title(title)


def request_count_time_scatter(data, title):
    data = pd.DataFrame(data, columns=['Crawl', 'Elapsed Time (s)', 'Total Links Visited (per crawl)'])
    data.plot.scatter(y='Elapsed Time (s)',
                      x='Total Links Visited (per crawl)')
    plt.title(title)


def seed_count_time_scatter_3d(data, title):
    data = pd.DataFrame(data, columns=['Crawl', 'Elapsed Time (s)', 'Seeds Visited (per crawl)', 'Total Links Visited (per crawl)'])
    data.plot.scatter(y='Elapsed Time (s)',
                      x='Seeds Visited (per crawl)',
                      c='Total Links Visited (per crawl)',
                      colormap='viridis')
    plt.title(title)
