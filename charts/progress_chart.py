import pandas as pd
import matplotlib.pyplot as plt


def progress_chart_pie(visited_uri, total_uri, title):
    """
    Generates progress chart based on how much of the .au domain has been crawled already.
    :param visited_uri: int
    :param total_uri: int
    :param title: str
    :return: None
    """
    data = pd.DataFrame({'Proportion of AU Domains': [visited_uri, total_uri]},
                        index=['Visited', 'Not Visited'])
    no_labels =['','']
    data.plot.pie(y='Proportion of AU Domains', startangle=90, labels=no_labels, counterclock=False)
    plt.legend(labels=data.index, fontsize='small', loc='center right', bbox_to_anchor=(1.3, 0.5))
    if title is not None:
        plt.title(title)
