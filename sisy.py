import csv
import json
import random
import sqlite3

import time
import praw

conn = sqlite3.connect('reddit.db')
cursor = conn.cursor()
per_sub_limit = 50000

with open("reddit_api_config.json") as config_file:
    config = json.load(config_file)

reddit_api = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent=config["user_agent"]
)


def db_init():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Subreddits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        collected_posts INTEGER DEFAULT 0,
        collection_done BOOLEAN DEFAULT FALSE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PostTitles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subreddit_id INTEGER NOT NULL,
        FOREIGN KEY (subreddit_id) REFERENCES Subreddits (id)
    )
    ''')

    conn.commit()


def update_subreddits(subreddit_list):
    with open(subreddit_list, 'r') as file:
        subreddits = file.readlines()

    for subreddit in subreddits:
        cursor.execute('''
        INSERT OR IGNORE INTO Subreddits (name)
        VALUES (?)
        ''', (subreddit.strip(),))

    conn.commit()


def collect():
    working_sub_list = cursor.execute('''
    SELECT id, name FROM Subreddits
    WHERE collection_done = FALSE
    ''').fetchall()

    print(f"Subreddits to collect from: {len(working_sub_list)}")

    for sub in working_sub_list:
        subreddit_id, subreddit_name = sub
        current = reddit_api.subreddit(subreddit_name)

        print(f"Collecting from {subreddit_name}")
        c = 0
        stop_collecting = False
        for time_filter in ['day', 'week', 'month', 'year', 'all']:
            if stop_collecting:
                break
            for post in current.top(limit=None, time_filter=time_filter):
                cursor.execute('''
                INSERT INTO PostTitles (title, subreddit_id)
                VALUES (?, ?)
                ''', (post.title, subreddit_id))
                c += 1
                print(f"{c}/{per_sub_limit} posts collected from {subreddit_name}")
                if c % 500 == 0:
                    time.sleep(1)
                if c >= per_sub_limit:
                    stop_collecting = True
                    break

        cursor.execute('''
        UPDATE Subreddits 
        SET collected_posts = collected_posts + ?, collection_done = TRUE
        WHERE id = ?
        ''', (per_sub_limit, subreddit_id))

        conn.commit()
        time.sleep(2)


def export():
    cursor.execute('''
    SELECT title, name FROM PostTitles
    JOIN Subreddits ON PostTitles.subreddit_id = Subreddits.id
    ''')

    rows = cursor.fetchall()

    with open('exported_posts.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['text', 'label'])  # Header: text = Post title, label = Subreddit name
        csv_writer.writerows(rows)


if __name__ == '__main__':
    db_init()
    update_subreddits('subreddits.txt')
    collect()
    export()
    conn.close()
