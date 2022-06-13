'''Audio Generator Class module to generate audio from Reddit posts.'''
from typing import Dict, Union, List, NoReturn, Tuple
from os.path import join
from pathlib import Path
import re
from gtts import gTTS
from moviepy.editor import *


class AudioGenerator:
    '''Class based utility that generates audio clips of reddit posts and stores
    them locally in provided output folder under a newly created audio folder.
    The audio clips are generated using gTTS and are stored within a newly
    created folder within the output folder. Comments are stored in a sub folder
    within the audio folder.
    '''

    def create_audio_folder_struct(self, base_dir: str) -> Dict[str, str]:
        '''Function creates the folder structure needed for generate_audio_from_submission
        to correctly store the mp3 files generated.
        Folder generated:
        <base_dir>/audio
        <base_dir>/audio/postbody
        <base_dir>/audio/comments
        
        :param base_dir: base directory needed to create the required folder(s).
        :return: dict containing the filepaths for audio, postbody & comments
        '''
        audio_dir = join(base_dir, 'audio')
        postbody_dir = join(audio_dir, 'postbody')
        comments_dir = join(audio_dir, 'comments')

        Path(audio_dir).mkdir(parents=True, exist_ok=True)
        Path(postbody_dir).mkdir(parents=True, exist_ok=True)
        Path(comments_dir).mkdir(parents=True,  exist_ok=True)

        return {
            'audio_dir': audio_dir,
            'postbody_dir': postbody_dir,
            'comments_dir': comments_dir,
        }
    
    def split_post_body_into_text_list(self,
                                       postbody: str,
                                       char_in_chunk: int = 300) -> List[str]:
        '''Given an arbitrary long reddit postbody. Split into smaller text chunks
        with each chunk have at most <char_in_chunk> characters. All \n are also
        removed from text.
        
        :return: list of strings with each string at most char_in_chunk words
        '''
        postbody = postbody.replace('\r', '').replace('\n', '')
        text_list = wrap(postbody, char_in_chunk, break_long_words=False)

        return text_list
    
    @staticmethod
    def sanitize_sentence_for_gtts(censored_sentence: str) -> str:
        '''Take a sentence that has potentially censored words "****" of
        arbitrary length and convert to word "beep" for audio recording. Additionally,
        remove all individual * as gTTS will recite each instance.
        
        :param censored_sentence: sentence that might contain censored words
        :return: sentence with censored words as "beep" and removed * instances
        '''
        beeped_sentence = re.sub('[\\*]{2,}', 'beep', censored_sentence)
        return re.sub('[\\*]{1}', '', censored_sentence)

    def generate_audio_and_save(self,
                                text: str,
                                output_filepath: str,
                                filename: str,
                                audio_accent: str = 'com',
                                multiplier: float = 1.2) -> str:
        '''Generate audio for the provided text and store the generated audio
        locally in the provided output_filepath.
        
        :param text: text to read using gTTS
        :param output_filepath: file path to store the generated audio
        :param audio_accent: tld to use for gTTS to change accent of audio (default: com)
        :param multiplier: multiplier used to speed up or slowdown audio
        :return: filepath to the finalized audio recording
        '''
        temp_filepath = join(output_filepath, 'temp.mp3')
        audio_filepath = join(output_filepath, filename)

        sanitized_text = self.sanitize_sentence_for_gtts(text)
        # generate audio using gTTS
        recording = gTTS(sanitized_text, tld=audio_accent)
        # create temp stored audiofile
        recording.save(temp_filepath)

        # speed up the audio using moviepy and store in final output
        audio = AudioFileClip(temp_filepath)
        audio.write_audiofile(audio_filepath,
                              ffmpeg_params = ["-filter:a",
                                               f"atempo={multiplier}"])
        audio.close()

        # remove temp mp3
        Path(temp_filepath).unlink(missing_ok=True)

        return audio_filepath

    def generate_audio_from_advice_submission(self,
                                              base_output_path,
                                              submission: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        '''Function generates audio recordings using the provided advice style submission data.
        The function stores audio files as mp3s within the output_folder. The file names are 
        defaulted to ['title.mp3', 'body_#.mp3']. The output folder is used to created a subfolder
        for audio where all files are stored.
    
        :param base_output_path: folder path to store generate audio.
        :param submission: reddit submission data generated by ContentGeneration
        :return: dictionary containing the title/ postbody text and their audio recording filepath
        '''
        audio_file_dict = {}
        # get submission title and postbody from submission dict
        submission_title = submission['title']
        submission_body = submission['postbody']

        # generate default set of directory needed to store audio files
        audio_dir_dict = self.create_audio_folder_struct(base_output_path)

        # generate the audio file
        title_path = self.generate_audio_and_save(submission_title,
                                                  audio_dir_dict['audio_dir'],
                                                  'title.mp3')
        # store text and filename
        audio_file_dict['title'] = {
            'text': submission_title,
            'audio_filepath': title_path,
        }

        postbody_list = self.split_post_body_into_text_list(submission_body)
        postbody_audio_list = []

        for i, chunk in enumerate(postbody_list):
            # generate the audio file
            postbody_filepath = self.generate_audio_and_save(chunk,
                                                             audio_dir_dict['postbody_dir'],
                                                             f'postbody_{i}.mp3')
            # store text and filename
            postbody_audio_list.append({
                'text': chunk,
                'audio_filepath': postbody_filepath,
            })
        
        audio_file_dict['postbody'] = postbody_audio_list

        return audio_file_dict

    def generate_audio_from_qna_submission(self,
                                           base_output_path: str,
                                           submission: Dict[str, Union[str, List[str]]]) -> Dict:
        '''Function generates audio recordings using the provided QnA tyle submission data. The function
        stores audio files as mp3s within the output_folder. The file names are defaulted to
        ['title.mp3', 'comment_#.mp3'].
        The output folder is used to created a subfolder for audio where all files are stored.
    
        :param base_output_path: folder path to store generate audio.
        :param submission: reddit submission data generated by ContentGeneration
        '''
        audio_file_dict = {}
        submission_title = submission['title']
        comments = submission['comments']

        audio_dir_dict = self.create_audio_folder_struct(base_output_path)

        # generate the audio file
        title_path = self.generate_audio_and_save(submission_title,
                                                  audio_dir_dict['audio_dir'],
                                                  'title.mp3')
        # store text and filename
        audio_file_dict['title'] = {
            'text': submission_title,
            'audio_filepath': title_path,
        }

        comment_audio_list = []
        for i, comment_dict in enumerate(comments):
            if comment_dict['comment']:
                # generate the audio file
                comment_filepath = self.generate_audio_and_save(comment_dict['comment'],
                                                                audio_dir_dict['comments_dir'],
                                                                f'comment_{i}.mp3')
                # store text, comment score and filename
                comment_audio_list.append({
                    'text': comment_dict['comment'],
                    'score': comment_dict['comment_score'],
                    'audio_filepath': comment_filepath,
                })

        audio_file_dict['comments'] = comment_audio_list
        
        return audio_file_dict