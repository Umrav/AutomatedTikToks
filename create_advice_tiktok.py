'''Script used to process Advice Reddit Json to create
both the audio & video for upload to TikTok'''
from typing import NoReturn
import json
from os.path import join
from argparse import ArgumentParser, Namespace
from datetime import datetime

from lib.generate_audio import AudioGenerator
from lib.generate_video import VideoGenerator
from config.base import CONFIG


def create_parser() -> ArgumentParser:
    '''Generate Argparse instance for use in script. The function
    will define various options that can be used to customize the output
    of the Advice Style TikTok.

    :return: customized argparse instance
    '''
    parser = ArgumentParser('CreateAdviceTikTok',
                            description='Script generates Advice style video'
                            ' for upload to TikTok.')
    parser.add_argument('--reddit_json',
                        default='reddit_advice_content.json',
                        type=str,
                        help='filepath to reddit Advice json, defaults to current run folder')
    parser.add_argument('--background_folder',
                        default=CONFIG['background_videos_path'],
                        type=str,
                        help='folder path to background videos for use in TokTok')
    parser.add_argument('--output_folder',
                        default=CONFIG['base_output_folder'],
                        type=str,
                        help='folder path to store audio & video for TikTok')
    parser.add_argument('--char_count',
                        default=30,
                        type=int,
                        help='count of characters before newlines are added in video text subtitle')
    parser.add_argument('--max_vid_length',
                        type=int,
                        default=180,
                        help='length in seconds for output video')

    return parser


def generate_advice_tiktok_video(args: Namespace) -> NoReturn:
    '''Given the script arguments, generate both the audio and video
    for TikTok for each post in the json provided. The output files are
    stored in the output folder within a folder named advice_<datetime>_#.

    :param args: arguments passed to script
    '''
    try:
        now = datetime.now()
        audio_gen = AudioGenerator()
        video_gen = VideoGenerator(args.background_folder)

        with open(args.reddit_json, 'r') as json_file:
            advice_contents = json.load(json_file)

        for i, advice_post in enumerate(advice_contents):
            output_folder = join(args.output_folder,
                                 f'advice_{now.day}{now.month}{now.year}_{now.hour}{now.minute}_{i}')

            audio_info = audio_gen.generate_audio_from_advice_submission(output_folder,
                                                                         advice_post)

            video_gen.generate_video_from_advice_submission(audio_info,
                                                            output_folder,
                                                            char_count=args.char_count,
                                                            max_vid_length=args.max_vid_length)

            print(f'Successfully Generated Advice Video for {i+1} post.')

    except Exception as err:
        print('---------------------------------------------------')
        print('Exception was raised during the execution of script')
        print(f'Err Type: {str(type(err))}')
        print(f'Err Msg: {str(err)}')
        print('---------------------------------------------------')


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    generate_advice_tiktok_video(args)
