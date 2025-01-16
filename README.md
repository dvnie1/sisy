# sisy
### Description
Sisyphus - or short, Sisy - is a reddit post title scraper for creating machine learning datasets.
The repository includes a file **subreddits.txt** with more than 1300 different subreddits to collect from.

### Usage
You can run sisy by simply running the sisy.py script or by building a Docker Image and running it that way. A Dockerfile is already included.

CAUTION: you will need to include your Reddit API credentials (please refer to the section down below for instructions).

After you updated your credentials:

Option 1:
```
python3 sisy.py
```
Option 2:
```
docker build -t <image-name> .
```
```
docker run -d --name <container-name> <image-name>
```
Hint: you can choose arbitrary image and container names.

Now, the collection should have been started. You can print the logs with the following command:
```
docker logs -f <container-name-or-id>
```

### Getting your own Reddit API credentials

You can create your own, free credentials at https://www.reddit.com/prefs/apps.
