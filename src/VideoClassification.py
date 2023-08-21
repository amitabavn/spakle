# List a video's categories topics list ( parent, sub topics)
# If from a series, list all from its episodes.
# Output: video-1: parent-topics: [], sub-topics: [], type: video
#           series-1: parent-topics: [], sub-topics: [], type: series
# Create a prompt message to call AI api to sort to a new category topic in the new list.
# Prompt message: classify the series [video] <title> to a new parent topic and sub topic of the new categories list.
# Refer to the series [video] old parent topic: [], and old sub topics: []. Notice that you must pick only one parent
# and sub topic for it. This is the new categories list: <list>
import csv
import requests
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import InferenceClient
from enum import Enum


class Llama2Model(Enum):
    Llama_2_7B = "EleutherAI/gpt-neo-2.7B"
    Llama_2_13B = "EleutherAI/gpt-neo-1.3B"
    Llama_2_70B = "meta-llama/Llama-2-70b-hf"
    Llama_2_7B_chat = "EleutherAI/gpt-neo-2.7B-chat"
    Llama_2_13B_chat = "EleutherAI/gpt-neo-1.3B-chat"
    Llama_2_70B_chat = "meta-llama/Llama-2-70b-chat-hf"


class LlamaTask(Enum):
    Summarization = "summarization"
    Text_classification = "text-classification"
    Question_answering = "question-answering"
    Text2text_generation = "text2text-generation"
    Text_generation = "text-generation"


def aggregate_titles(csv_data):
    videos_titles = {}

    for entry in csv_data:
        if entry['title_type'] in ['videos', 'series']:
            title = entry['title']
            if entry['title_type'] == 'episodes':
                series_title = entry['episode_series']
                if series_title not in videos_titles:
                    videos_titles[series_title] = {
                        'link': entry['episode_series_link'],
                        'title_type': 'series',
                        'parent_topic_name': [],
                        'sub_topic_name': [],
                    }
                videos_titles[series_title]['parent_topic_name'].append(entry['parent_topic_name'])
                videos_titles[series_title]['sub_topic_name'].append(entry['sub_topic_name'])
            else:
                if title not in videos_titles:
                    videos_titles[title] = {
                        'link': entry['link'],
                        'title_type': entry['title_type'],
                        'parent_topic_name': [],
                        'sub_topic_name': [],
                    }
                videos_titles[title]['parent_topic_name'].append(entry['parent_topic_name'])
                videos_titles[title]['sub_topic_name'].append(entry['sub_topic_name'])

    return videos_titles


def write_csv_file(output_file, titles):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['title', 'title_type', 'link', 'parent_topic_name', 'sub_topic_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for title, details in titles.items():
            writer.writerow({
                'title': title,
                'link': details['link'],
                'title_type': details['title_type'],
                'parent_topic_name': ', '.join(details['parent_topic_name']),
                'sub_topic_name': ', '.join(details['sub_topic_name']),
            })


class VideoClassification:

    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def read_csv_file(self):
        csv_data = []
        with open(self.csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['parent_topic_name'] != '':
                    csv_data.append(row)
        return csv_data

    def main(self, output_file):
        csv_data = self.read_csv_file()
        titles = aggregate_titles(csv_data)

        write_csv_file(output_file, titles)


class LlamaService:
    def __init__(self):
        self.api_token = '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'

    def query(self, prompt, model_id, task):
        headers = {"Authorization": f"Bearer {self.api_token}"}
        model = AutoModelForCausalLM.from_pretrained(model_id, headers=headers)
        tokenizer = AutoTokenizer.from_pretrained(model_id, headers=headers)
        generator = pipeline(task, model=model, tokenizer=tokenizer)
        return generator(prompt, max_length=1000, do_sample=True, temperature=0.7)


if __name__ == "__main__":
    llama = LlamaService()
    prompt = "Write a story about a detective who solves a murder case in a small town."
    output = llama.query(prompt, Llama2Model.Llama_2_7B.value, LlamaTask.Summarization.value)
    print(output)
    print(output[0]['generated_text'])

# file_path = '/topics_videos_list.csv'
# output_file_path = '/videos_old_categories.csv'
# video_classification = VideoClassification(file_path)
# video_classification.main(output_file_path)
