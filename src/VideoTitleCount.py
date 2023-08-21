import csv


def count_distinct_titles(csv_file):
    series_titles = set()
    video_titles = set()

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title_type = row['title_type']
            title = row['title']

            if title_type == 'series':
                series_titles.add(title)
            elif title_type == 'videos':
                video_titles.add(title)

    return len(series_titles), len(video_titles)


def count_distinct_series_titles_by_episodes(csv_file):
    series_titles = set()

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title_type = row['title_type']
            if title_type == 'episodes':
                series_title = row['episode_series']
                if series_title:
                    series_titles.add(series_title)

    return len(series_titles)


if __name__ == "__main__":
    csv_file = "/home/lucy/Documents/my-code/openai-playground/topics_videos_list.csv"
    distinct_series_titles, distinct_video_titles = count_distinct_titles(csv_file)
    distinct_series_titles_by_episodes = count_distinct_series_titles_by_episodes(csv_file)

    print("Distinct Series Titles:", distinct_series_titles)
    print("Distinct Video Titles:", distinct_video_titles)
    print("Distinct Series Titles (from episodes):", distinct_series_titles_by_episodes)
