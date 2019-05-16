import pandas as pd
import matplotlib.pyplot as plt


def clean_formats(format_dict):
    seperate_together= ['text/html',
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
    count_removed = 0
    count_combined = 0
    count_other = 0
    for key in list(format_dict.keys()):
        # Combine entries with Null formats into 'No Format'.
        if key.startswith("#<Mime::NullType:") or key == '' or key == "N/A":
            format_dict['No Format'] = format_dict.get('No Format', 0) + format_dict.pop(key)
            count_combined += 1
        # Remove entries with multiple formats (comma separated).
        elif len(key.split(",")) > 1:
            format_dict['Other'] = format_dict.get('Other', 0) + format_dict.pop(key)
            count_removed += 1
        # Cluster other media types
        elif key not in seperate_together:
            format_dict['Other'] = format_dict.get('Other', 0) + format_dict.pop(key)
            count_other += 1


def file_format_pie(format_dict, title=None):
    data = pd.DataFrame({'Content Format': list(format_dict.values())},
                        index=list(format_dict.keys()))
    no_labels = ['' for i in data.index]
    data.plot.pie(y='Content Format', startangle=90, labels=no_labels, counterclock=False)
    plt.legend(labels=data.index, fontsize='small', loc='center right', bbox_to_anchor=(1.5, 0.5))
    if title is not None:
        plt.title(title)


def file_format_bar(format_dict, title=None):
    data = pd.DataFrame({'Content Format': list(format_dict.values())},
                        index=list(format_dict.keys()))
    data.transpose().plot.bar()
    plt.legend(labels=data.index, fontsize='small', loc='center right', bbox_to_anchor=(1.4, 0.5))
    plt.xticks([])
    plt.ylabel('Response Count')
    if title is not None:
        plt.title(title)
