import pandas as pd
import matplotlib.pyplot as plt


def plot_size_histogram(seed_size_data, bins, title=None):
    """
    Generates a histogram based on the frequency of different link pool sizes of a specific domain.
    :param seed_size_data: array
    :param bins: int
    :param title: str
    :return: None
    """
    data = pd.DataFrame(seed_size_data, columns=['Domain', 'Size'])
    data = pd.DataFrame(seed_size_data, index=data['Domain'], columns=['Domain','Size'])
    data = data['Size']
    data.hist(bins=bins)
    plt.xlabel('Pages per site')
    plt.ylabel('Frequency')
    if title is not None:
        plt.title(title)

