'''Script used to generate Reddit content jsons that can
be used downstream to create TikTok Videos.'''
from typing import NoReturn
import json
from os.path import join
from argparse import ArgumentParser, Namespace

from lib.generate_reddit_content import ContentGenerator
from config.base import CONFIG

def create_parser() -> ArgumentParser:
    '''Generate Argparse instance for use in script. The function
    will define various options that can be used to customize the output
    of the reddit content json.
    
    :return: customized argparse instance
    '''
    parser = ArgumentParser('CreateRedditContent',
                             description='Script generate reddit content json for'
                                         ' use to create TikTok Videos.')
    parser.add_argument('--credential_json',
                        default=CONFIG['reddit_credential'],
                        type=str,
                        help='filepath to reddit credentials used to query Reddit API')
    parser.add_argument('--output_folder',
                        default='',
                        type=str,
                        help='folder path to store reddit json, defaults to run location if not specified')
    parser.add_argument('--subreddit',
                        default='askreddit',
                        type=str,
                        help='subreddit name to query top posts')
    parser.add_argument('--subreddit_type',
                        type=str,
                        default='qna',
                        choices=['qna', 'advice'],
                        help='subreddit type (Question & Answers [AskReddit] or Advice [AmItheAsshole])')
    parser.add_argument('--post_limit',
                        type=int,
                        default=1,
                        help='number of posts to query for json output')
    parser.add_argument('--time_filter',
                        type=str,
                        default="day",
                        choices=['all', 'day', 'hour', 'month', 'week', 'year'],
                        help='time filter for top posts')
    parser.add_argument('--comment_score_min',
                        type=int,
                        default=1000,
                        help='number of upvotes required before comment is considered (QnA only)')
    parser.add_argument('--comment_char_limit',
                        type=int,
                        default=250,
                        help='character limit for comments to be considered (QnA only)')
    parser.add_argument('--comment_sort',
                        type=str,
                        default='confidence',
                        choices=['confidence', 'controversial', 'new', 'old', 'top'],
                        help='heurisitic used to sort comments (QnA only)')
    
    return parser

def generate_reddit_json(args: Namespace) -> NoReturn:
    '''Given the inputs from the script args, create an instance of
    ContentGenerator and use it to create a json with content
    using the provided inputs.
    
    :param args: arguments passed to script
    :return: NoReturn
    '''
    try:
        with open(args.credential_json, 'r') as json_file:
            credential_info = json.load(json_file)
        
        content_gen = ContentGenerator(**credential_info)

        if args.subreddit_type == 'qna':
            output_filepath = 'reddit_qna_content.json'

            if args.output_folder:
                output_filepath = join(args.output_folder, 'reddit_qna_content.json')

            qna_content = content_gen.get_top_qna_posts(sub_name=args.subreddit,
                                                        post_limit=args.post_limit,
                                                        time_filter=args.time_filter,
                                                        comment_score_min=args.comment_score_min,
                                                        comment_char_limit=args.comment_char_limit,
                                                        comment_sort=args.comment_sort)
            
            with open(output_filepath, 'w') as json_file:
                json.dump(qna_content, json_file, indent=3)

        elif args.subreddit_type == 'advice':
            output_filepath = 'reddit_advice_content.json'

            if args.output_folder:
                output_filepath = join(args.output_folder, 'reddit_qna_content.json')

            advice_content = content_gen.get_top_advice_posts(sub_name=args.subreddit,
                                                              post_limit=args.post_limit,
                                                              time_filter=args.time_filter)

            with open(output_filepath, 'w') as json_file:
                json.dump(advice_content, json_file, indent=3)

        print('Successfully generated reddit content JSON as chosen output folder, please review to finalize text.')
    
    except Exception as err:
        print('---------------------------------------------------')
        print('Exception was raised during the execution of script')
        print(f'Err Type: {str(type(err))}')
        print(f'Err Msg: {str(err)}')
        print('---------------------------------------------------')


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    generate_reddit_json(args)