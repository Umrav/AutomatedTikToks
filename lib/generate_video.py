'''Video Generator Class to create Tiktok style videos'''
from typing import Dict, Union, List, NoReturn, Tuple
from os import listdir
from os.path import join
from pathlib import Path
from random import choice, randrange
from textwrap import wrap
from moviepy.editor import *  # recommended per moviepy Docs


class VideoGenerator:
    '''Class based utility that generates TikTok style videos using the given
    baseline videos and audio clips. The class expects that the audio generated
    follows the output outlined in Class AudioGeneration. The system can generate
    videos to provided time limit.'''

    def __init__(self,
                 videos_path: str,
                 title_buffer: float = .8):
        '''Initialize VideoGeneration class and store folder path to
        background filler videos.

        :param videos_path: folder location where background videos are stored
        :param title_buffer: seconds to wait before title is removed to screen after
                             being read. (default: .8)
        '''
        self.vid_path = videos_path
        self.title_buffer = title_buffer
        # hardcoded (doesnt really need to be configurable)
        self.last_used_vid_filename = 'last_used.txt'

    def pick_random_video(self) -> str:
        '''Randomly pick a background file for use in TikTok video.

        :return: file path to video randomly chosen
        :raises: ValueError (if no videos exist)
        '''
        video_files = []
        for maybe_vid in listdir(self.vid_path):
            if maybe_vid.endswith('.mp4'):
                video_files.append(maybe_vid)

        if not video_files:
            raise ValueError(f'There are no .mp4 files in {self.vid_path}')

        try:
            # to avoid repeated video content, check txt file for last used vid name
            with open(join(self.vid_path, self.last_used_vid_filename), 'r') as txt_file:
                last_video_file_used = txt_file.read().strip()
            video_files = list(
                filter(lambda vid: vid != last_video_file_used, video_files))
        except IOError:
            # first time run or new video folder, ignore error
            pass

        chosen_video = choice(video_files)

        # write vid name to txt file to avoid repeat background videos
        with open(join(self.vid_path, self.last_used_vid_filename), 'w') as txt_file:
            txt_file.write(chosen_video)

        return join(self.vid_path, chosen_video)

    def crop_video_to_tiktok_format(self,
                                    video_filepath: str,
                                    subclip_length: int,
                                    subclip_volume_multiplier: float = .2,
                                    x1_start: float = 1166.6,
                                    x2_end: float = 2246.6,
                                    y1_start: float = 0,
                                    y2_end: float = 1920) -> VideoFileClip:
        '''Given the filepath to video file, resize the horizontal video to vertical mode and
        create a random length subclip for use. The length provided is used to find a random subclip.
        The default crop positions center video vertically in the middle of the loaded video.

        :param video_filepath: filepath to video that will be loaded and resized
        :param subclip_length: length in seconds of resized video
        :param subclip_volume_multiplier: volume multiplier for clip (default: .2)
        :param x1_start: vertical starting position to start crop video (default: 1166.6)
        :param x2_end: vertical ending position to end crop video (default: 2246.6)
        :param y1_start: horizontal starting position to start crop of video (default: 0)
        :param y2_end: horizonal ending position to end crop of video (default: 1920)

        :return: resized video instance
        '''
        video = VideoFileClip(video_filepath)
        # pick a randompoint in the video duration for start of subclip
        # duration is float, so converted to int
        random_point = randrange(
            0, int(video.duration) - subclip_length, subclip_length)

        # create subclip of loaded video
        subclip = video.subclip(random_point, random_point+subclip_length)

        # resize video to vertical format (defaults center on middle of video)
        subclip = subclip.resize(height=y2_end)
        subclip = subclip.crop(x1=x1_start,
                               y1=y1_start,
                               x2=x2_end,
                               y2=y2_end)

        # reduce clip volume
        subclip = subclip.volumex(subclip_volume_multiplier)
        # return a subclip from the resized video
        return subclip

    def write_tiktok_video_to_file(self,
                                   video: VideoFileClip,
                                   output_path: str,
                                   video_codec: str = 'libx264',
                                   audio_codec: str = 'aac') -> NoReturn:
        '''Given a VideoFileClip instance that represents the finalized TikTok video,
        write the video to file using the provided output_path. The file defaults to using
        the codecs for mp4.

        :param video: finalized VideoFileClip instance
        :param output_path: filepath to write video
        :param video_codec: video codec format for output video (default: libx264)
        :param audio_codec: audito codec format for output video (default: aac)

        :return: NoReturn
        '''
        video.write_videofile(
            output_path, codec=video_codec, audio_codec=audio_codec)

    @staticmethod
    def process_text(text: str,
                     char_count) -> str:
        '''Add newlines to text so that textclips generated from the provided text do
        not exceed horizontal width of TikTok video.

        :param char_count: count of words before newline is inserted (default: 8)

        :return: text with newlines inserted at after each word count
        '''
        text_list = wrap(text, char_count, break_long_words=False)

        final_text = ''
        for i, block in enumerate(text_list):
            if i == 0:
                final_text = block
            else:
                final_text = f'{final_text}\n{block}'

        return final_text

    def add_ending_message(self,
                           video: VideoFileClip,
                           lst_msg_timestamp: float,
                           end_msg: str = "Like\n&\nFollow\nfor more!") -> VideoFileClip:
        '''Add an ending animation message to videos to invite viewers to like &
        follow the video. A default msg is used if none is provided and its shown for the
        minimum of 3 seconds or time left before max_vid_length input.

        :param video: edited video with reddit text overlayed on the video
        :param lst_msg_timestamp: last reddit text message's end timestamp
        :param end_msg: what message to put at the end of video (default: "Like & Follow for more!")
        :return: finalized video with ending msg added
        '''
        video_duration = video.duration
        # ending credit time length, tries to be 3 seconds
        end_msg_duration = min(video_duration-lst_msg_timestamp, 3)

        endmsg_textclip = TextClip(end_msg,
                                   fontsize=150,
                                   font='Calibri-Bold',
                                   align='center',
                                   color='white',
                                   stroke_color='black',
                                   stroke_width=2,
                                   method='label')
        # set textclip position in timeline and on screen
        endmsg_textclip = endmsg_textclip.set_pos(('center', 500))
        endmsg_textclip = endmsg_textclip.set_start(lst_msg_timestamp)

        video = CompositeVideoClip(
            [video, endmsg_textclip]).set_duration(lst_msg_timestamp+end_msg_duration)

        return video

    def write_title_to_video(self,
                             video: VideoFileClip,
                             title_info: Dict[str, str],
                             char_count: int) -> Tuple[VideoFileClip, float]:
        '''Add reddit post title as an overlay to the provided video. The overlay will be
        added for the audio duration and the audio dat and title text will be taken from the
        provided input.

        :param video: video that overlay will be added to
        :param title_info: dict containing the title text and title audio filepath
        :param char_count: count of words before newline is inserted

        :return: edited video with overlay of title text & timestamp for when title audio ends
        '''
        processed_text = self.process_text(title_info['text'], char_count)

        # hardcoding various text attrs for stylistic reasons
        # individual users can change as needed
        title_textclip = TextClip(processed_text,
                                  fontsize=70,
                                  font='Calibri-Bold',
                                  align='center',
                                  color='white',
                                  stroke_color='black',
                                  stroke_width=2,
                                  method='label')
        title_audioclip = AudioFileClip(title_info['audio_filepath'])

        # add textclip for duration of title audio
        title_duration = title_audioclip.duration

        # setting to harcoded location for stylistic purposes
        title_textclip = title_textclip.set_start(0)
        # stylistic add 1 second
        title_textclip = title_textclip.set_position(
            ('center', 300)).set_duration(title_duration + self.title_buffer)
        title_textclip = title_textclip.set_audio(title_audioclip)

        video = CompositeVideoClip(
            [video, title_textclip]).set_duration(video.duration)

        return video, title_duration + self.title_buffer

    def write_multi_text_to_video(self,
                                  video: VideoFileClip,
                                  title_offset: float,
                                  texts_list: List[Dict[str, str]],
                                  max_vid_length: float,
                                  char_count: int,
                                  time_offset: float) -> VideoFileClip:
        '''Add textclips and audio for each text dict defined in the provided list
        to the video clip. The offset is used to start inserting the text clips up to
        the max video length, all other text from list are discarded once the max vid length is reached.

        :param video: background video with title text and audio integrated
        :param title_offset: timestamp for end of title audio (used to start inserting text audios)
        :param texts_list: list of dict containing text and audio filepath
        :param max_vid_length: maximum length in seconds that video can be
        :param char_count: count of words before newline is inserted
        :param time_offset: seconds to wait between each text block

        :return: edited video containing the text & audio trimmed to final length of all audio
        '''
        # starting offset for text audio at title offset
        current_text_offset = title_offset
        text_clips = []

        for text_dict in texts_list:
            processed_text = self.process_text(text_dict['text'], char_count+8)
            text_audioclip = AudioFileClip(text_dict['audio_filepath'])
            text_duration = text_audioclip.duration

            # check that current text's audio length is within max video length
            if current_text_offset + text_duration <= max_vid_length:
                # create text clip for processed text
                # hardcoding various text attrs for stylistic reasons
                text_vidclip = TextClip(processed_text,
                                        fontsize=60,
                                        font='Calibri-Bold',
                                        align='center',
                                        color='white',
                                        stroke_color='black',
                                        stroke_width=2,
                                        method='label')

                # add audio to clip & set the clip's offset
                # to be starting at the end of the previous textclip's end
                text_vidclip = text_vidclip.set_audio(text_audioclip)
                text_vidclip = text_vidclip.set_start(current_text_offset)

                # set position of the clip and set duration to be length of audio
                text_vidclip = text_vidclip.set_position(
                    ('center', 320)).set_duration(text_duration)

                # append to the text clip list
                text_clips.append(text_vidclip)

                # add audio length to offset for next text to be processed, adding smaller buffer
                current_text_offset += text_duration + time_offset

        video = CompositeVideoClip(
            [video, *text_clips]).set_duration(video.duration)

        video = self.add_ending_message(video,
                                        current_text_offset)
        return video

    def preview_clip(self, video: VideoFileClip, timestamp: int = 0) -> NoReturn:
        '''Generate a png from the videoclip for testing/ quality control at provided time stamp.

        :param video: videofile to get static frame at provided timeframe
        :param timestamp: timestamp in seconds to capture still frame
        '''
        video.save_frame(f'frame_{timestamp}.png', t=timestamp)

    @staticmethod
    def make_filename(type: str) -> str:
        '''Function to create a filename for the output video file. The finalname is appended
        with the day, month, year, hr and min to ensure that when multiple vids are created in a
        run, the files arent overwritten.

        :param type: type of video (qna or advice)
        :return: unique timestamped filename for output tiktok video
        '''

        return f'finalized_{type}.mp4'

    def generate_video_from_qna_submission(self,
                                           submission: Dict[str, Union[Dict, List[Dict[str, str]]]],
                                           output_folder: str,
                                           char_count: int = 30,
                                           max_vid_length: float = 90) -> NoReturn:
        '''Generate a TikTok video using the provided QnA submission (no textbody) information from
        AudioGenerator Class. The background video is randomly chosen from provided
        folder and the video is edited to include both the text and audio from the
        submission information. The function also ensures that the output video doesnt exceed
        the max video length provided.

        :param submission: audio enriched submission dict generated by AudioGenerator
        :param output_folder: folder to store finalized TikTok video
        :param char_count: count of words before newline is inserted (default: 30)
        :param max_vid_length: maximum video length in seconds (default: 120)

        :return: NoReturn
        '''
        # choose random background video
        background_video = self.pick_random_video()

        # crop randomly chosen video to input length and resize to vertical video
        cropped_video = self.crop_video_to_tiktok_format(
            background_video, max_vid_length)

        # get video with title text and audio inserted along with title offset
        title_edited_vid, title_duration = self.write_title_to_video(cropped_video,
                                                                     submission['title'],
                                                                     char_count=char_count)

        # get video with comment text and audio inserted
        final_video = self.write_multi_text_to_video(title_edited_vid,
                                                     title_duration,
                                                     submission['comments'],
                                                     max_vid_length,
                                                     char_count,
                                                     .5)  # wait .5 seconds between answers

        # create final filepath to output video & write to file
        output_filepath = join(output_folder, self.make_filename('qna'))

        self.write_tiktok_video_to_file(final_video, output_filepath)

    def generate_video_from_advice_submission(self,
                                              submission: Dict[str, Union[Dict, List[Dict[str, str]]]],
                                              output_folder: str,
                                              char_count: int = 30,
                                              max_vid_length: float = 180) -> NoReturn:
        '''Generate a TikTok video using the "seeking advice" style reddit submission (textbody) 
        information from AudioGenerator Class. This function is called for posts with long
        textbody asking for advice (i.e. relationship, AITA).
        The background video is randomly chosen from provided folder and the video is edited
        to include both the text and audio from the submission information.
        The function also ensures that the output video doesnt exceed the max video length provided.

        :param submission: audio enriched submission dict generated by AudioGenerator
        :param output_folder: folder to store finalized TikTok video
        :param char_count: count of words before newline is inserted (default: 30)
        :param max_vid_length: maximum video length in seconds (default: 180)

        :return: NoReturn
        '''
        # choose random background video
        background_video = self.pick_random_video()

        # crop randomly chosen video to input length and resize to vertical video
        cropped_video = self.crop_video_to_tiktok_format(
            background_video, max_vid_length)

        # get video with title text and audio inserted along with title offset
        title_edited_vid, title_duration = self.write_title_to_video(cropped_video,
                                                                     submission['title'],
                                                                     char_count=char_count)

        # get video with postbody texts and audio inserted at title offset
        final_video = self.write_multi_text_to_video(title_edited_vid,
                                                     title_duration,
                                                     submission['postbody'],
                                                     max_vid_length,
                                                     char_count,
                                                     .1)  # wait .1 seconds between chunks

        # create final filepath to output video & write to file
        output_filepath = join(output_folder, self.make_filename('advice'))
        self.write_tiktok_video_to_file(final_video, output_filepath)
