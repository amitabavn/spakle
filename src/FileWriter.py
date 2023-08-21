import csv


def create_row(parent_topic, sub_topic, title_type, title):
    row = {
        'parent_topic_name': parent_topic['parent_topic_name'],
        'sub_topic_name': sub_topic['sub_topic_name'],
        'sub_topic_link': sub_topic['sub_topic_link'],
        'title_type': title_type,
        'title': title['title'],
        'link': title['link']
    }
    if title_type == 'episodes':
        row['episode_series'] = title['series']
        row['episode_series_link'] = title['series_link']
        row['episode_number'] = title['episode_number']
    return row


class FileWriter:
    def __init__(self, filename):
        self.filename = filename
        self.fieldnames = ['parent_topic_name', 'sub_topic_name', 'sub_topic_link', 'title_type', 'title', 'link',
                           'episode_series', 'episode_series_link', 'episode_number']

    def write_results_to_csv(self, parent_topic):
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            for sub_topic in parent_topic['sub_topics']:
                for title_type, titles in sub_topic['sub_topic_videos'].items():
                    for title in titles:
                        row = create_row(parent_topic, sub_topic, title_type, title)
                        writer.writerow(row)
