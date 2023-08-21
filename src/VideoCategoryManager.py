import csv


def print_data(data):
    for parent_topic, sub_topics in sorted(data.items()):
        print(parent_topic + ':')
        for sub_topic, titles in sorted(sub_topics.items()):
            title_list = ', '.join(sorted(titles))
            print('- ' + sub_topic + ': ' + title_list)


class VideoCategoryManager:

    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def read_csv_file(self):
        data = {}
        with open(self.csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                parent_topic = row['parent_topic_name'].strip()
                sub_topic = row['sub_topic_name'].strip()
                title = row['title'].strip()

                if parent_topic not in data:
                    data[parent_topic] = {}
                if sub_topic not in data[parent_topic]:
                    data[parent_topic][sub_topic] = []
                data[parent_topic][sub_topic].append(title)

        return data

    def main(self):
        data = self.read_csv_file()
        print_data(data)


if __name__ == "__main__":
    file_path = "../topics_videos_list.csv"
    video_category_manager = VideoCategoryManager(file_path)
    video_category_manager.main()
