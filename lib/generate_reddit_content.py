'''Content Generator Class to query Reddit api
using PRAW to get top SubReddit posts based on post style.
QnA - user asks reddit population a question and comments are aggregated on score limit
Advice - user explains their situation and asks reddit population for advice'''
from typing import Dict, Union, List
import json
from uuid import uuid4
import praw
from better_profanity import profanity

class ContentGenerator:
    '''Class based utility to query Reddit api for various subreddit
    for their top posts and comments. The class will organize
    posts into dicts with the post title & the top comments filtered
    by Score.
    '''
    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 username: str,
                 password: str):
        '''initialize the Content Generation Class for use. The method
        initializes an instance of PRAW class to be used to query the Reddit
        API for subreddit posts.
        
        :param client_id: Reddit Client ID
        :param client_secret: Reddit Client Secret
        :param username: reddit account username
        :param password: reddit account password
        '''
        
        self.client = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=f'automatedTikToks_{uuid4().hex}',
        )
        # load profanity censor
        profanity.load_censor_words()

    def get_top_advice_posts(self,
                             sub_name: str = 'AmItheAsshole',
                             post_limit: int = 1,
                             time_filter: str = 'day') -> List[Dict[str, str]]:
        '''Given a reddit subreddit name that is advice format (long postbody) and time filter
        query reddit's api through the PRAW client and return the provided time filter's posts with the
        post's title & the postbody.

        :param sub_name: subreddit name to query for top post, (default: "AmItheAsshole")
        :param post_limit: number of posts to return for provided time filter (default: 1)
        :param time_filter: time filter for post, Can be one of: "all", "day", "hour", "month",
                            "week", or "year" (default: "day")
        :return: List of dictionaries containing the subreddit's top post "title" and "postbody" for provided time filter
        '''
        subreddit = self.client.subreddit(sub_name)
        top_posts = []

        for submission in subreddit.top(limit=post_limit, time_filter=time_filter):
            post_title = submission.title
            post_selftext = submission.selftext

            top_posts.append({
                'title': post_title,
                'postbody': post_selftext,
            })

        return top_posts

    def get_top_qna_posts(self,
                          sub_name: str = 'askreddit',
                          post_limit: int = 1,
                          time_filter: str = 'day',
                          comment_score_limit: int = 1000,
                          comment_char_limit: int = 250,
                          comment_reply_threshold: int = 50,
                          comment_sort: str = 'confidence') -> List[Dict[str, Union[str, List[str]]]]:
        '''Given a reddit subreddit name that is QnA format (comment answers), time filter and comment count,
        query reddit's api through the PRAW client and return the provided time filter's posts with the
        post's title & the top n (comment_count) comments.

        :param sub_name: subreddit name to query for top post, (default: "askreddit")
        :param post_limit: number of posts to return for provided time filter (default: 1)
        :param time_filter: time filter for post, Can be one of: "all", "day", "hour", "month",
                            "week", or "year" (default: "day")
        :param comment_sort: sort order for comments, Can be one of "confidence",
                             "controversial", "new", "old", "q&a", or "top" (default: "confidence")
        :param comment_score_limit: score limit for comment, only comments above limit will be returned (default: 1000)
        :param comment_char_limit: char limit for comment, only comments less than limit included (default: 250)
                                   stylistic choice to prevent long posts dominating the video, can be changed
        :param comment_reply_threshold: comment reply count threshold before being included in output (default: 50)
        :return: List of dictionaries containing the subreddit's top post "title" and "comments" for provided time filter
        '''
        subreddit = self.client.subreddit(sub_name)
        top_posts = []

        for submission in subreddit.top(limit=post_limit, time_filter=time_filter):
            post_title = submission.title
            submission.comment_sort = comment_sort
            submission.comments.replace_more(threshold=comment_reply_threshold)

            comments = []
            for top_level_comment in submission.comments:
                if top_level_comment.score > comment_score_limit and \
                    len(top_level_comment.body) <= comment_char_limit:
                    comments.append({
                        'comment': profanity.censor(top_level_comment.body),
                        'comment_score': top_level_comment.score,
                    })
            
            top_posts.append({
                'title': post_title,
                'comments': comments,
            })

        return top_posts