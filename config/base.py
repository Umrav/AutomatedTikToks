'''Base Config to define folder paths to various locations
within repo for use in code'''
from os.path import dirname, realpath, join

# Repo Base Path
BASE_PATH = dirname(dirname(realpath(__file__)))

#Repo Secrets Path
SECRET_PATH = join(BASE_PATH, 'secrets')

CONFIG = {
    'reddit_credential': join(SECRET_PATH, 'reddit_credentials.json'), # reddit credential Json
    'background_videos_path': join(BASE_PATH, 'videos'), # folder containing background videos
    'base_output_folder': join(BASE_PATH, 'output') # folder to output finalized vids
}