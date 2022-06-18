# Automated TikTok Content Generator

Flipping through tiktoks, I often find the minecraft parkour videos that have narrations of interesting stories or funny tweets as one of the most viewer engaging type of content on the platform. This tool allows one to generate their own `Minecraft Parkour Style videos` using Reddit as the source of stories and content.

The steps outlined below showcase all the steps needed to set up the tool for yourself and generate videos for your tiktok account. This code was written to be python3.7+ compatible. All of the code was developed with MacOS, so all commands are written for Mac. However, this library will works on windows too as I have tested it on both.

# My TikTok Account

Check out my [TikTok Account](https://www.tiktok.com/@dailyreddituploads) to see videos I've generated using the library code.

# Setting up the Repo

## Creating the Virtual Environment

Clone/fork the repo locally to your machine. Then, navigate to the repo using a Terminal/ CMD window and create a venv.

```
python -m venv venv
```

Once the venv is created, activate it using the following command.

```
source venv/bin/activate
```

Then, install the required packages by running the following command.

```
pip install -r requirements/requirements.txt
```

Finally, please insure that you have the following programs installed (needed for [moviepy](https://zulko.github.io/moviepy/install.html)

```
ffmpeg
ImageMagick
```

## Getting Reddit Credentials

In order to use the PRAW client that the library uses, you will need a Reddit API client ID and secret. To create those for yourself, you must first have a reddit account. Once you do, feel free to follow the instructions below.

1. Create a Reddit Account and navigate to [Reddit](https://www.reddit.com/prefs/apps)
2. Click _Create another app_ button
3. Set the `name` for your script, click `script` radio button from the options and add a `description`, if a URI is required, feel free to use anything
4. Click on _Create App_ button
5. Save your client id and client secret

Once you have your info, navigate to the secrets folder and copy the `default_credentials.json` to a new file named `reddit_credentials.json`. Fill in the `reddit_credentials.json` your client id, client secret, reddit username and reddit password. The code assumes that the credentials are in a file named `reddit_credentials.json` but you can change it via cmd line arguments.

## Get Background Videos for your TikToks

The last step needed to set up is to find long videos that the library can use as background imagery. Feel free to use any video, the code will resize it for TikTok and also cut to down to length.

The library will pick a randomized section of the video so ensure that your chosen videos are all exciting and fun to watch over its length. All background videos must be placed in `videos` folder if using default cmd line arguments.

# Running the Scripts

## Generate the Reddit Content

To create your own automated TikToks, first run the `process_reddit_posts.py` script. Feel free to look at all the command line arguments using the following cmd.

```
python process_reddit_posts.py --help
```

One specific cmd I would like to highlight is `--subreddit_type`. This can be `qna` or `advice`. `qna` retrieves the question text and user comments. `advice` retrieves the question text and question postbody. AskReddit would be a `qna` type subreddit, while AITA or relationships would be `advice` type
subreddits.

`qna` type will generate a json named `reddit_qna_content.json` with the reddit data.

`advice` type will generate a json named `reddit_advice_content.json` with the reddit data.

Look through the json to edit/ remove comments/ postbody that you deem not interesting or repetitive (optional)

## Generating the Video

Depending on if you created a `qna` or `advice` json, run the corresponding video scripts, `create_qna_tiktok.py` or `create_advice_tiktok.py` respectively. The output video will be stored by default in the `output` folder. There are several configurable attributes to the video which be viewed using the following cmds.

```
python create_qna_tiktok.py --help
python create_advice_tiktok.py --help
```

Once the scripts are finished running, you can navigate to the `output` folder and check out the completed video, ready for upload to your TikTok account.
