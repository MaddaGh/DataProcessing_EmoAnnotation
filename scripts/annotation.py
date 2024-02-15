import pandas as pd
import os
import shutil
from scenedetect import detect, ContentDetector
from utils import load_json, get_sec
from moviepy.editor import VideoFileClip
import re
import json

annotations_path ="annotation4frames.json"
video_annotations_path="video_annot.json"
label_studio_video_path ="C:/Users/ghiot/Documents/TESI/annotation/video"
label_studio_path = "C:/Users/ghiot/Documents/TESI/annotation"

annotated_data_json_path = "annotations.json"


def get_annotated_items(annotations_path, annotated_data_json_path = "annotations.json"):
    # Write an empty list to the JSON file

    j = load_json(annotations_path)
    annotated_videos = []

    for annotated_item in j: # single item level, json is a list of dictionsries)
        ts_data = annotated_item.get("data") # gett the data level where the dictionary storing the video url is
        video_url = ts_data.get("video_url") # get the path + filename of the item annotated
        annotations = annotated_item.get("annotations") # a list of dictionaries, one for each annotation type
        video_filename = video_url.split("/")[-1] # cleaning path to get video filename "2101608040029452931_15_40_utterance.webm"
        emo_utt_id = video_filename.split(".")[0] # cleaning video filename to get utt name "2101608040029452931_15_40_utterance"

        # now getting annotation types NB not all of them are necessarily there
        for dict in annotations: # getting the dictionary inside the annotations list
            results = dict.get("result") # again, a list of dictionaries
            
            for ann in results: # getting single annotations' dictionaries THIS IS THE MEANINGFUL LEVEL

                # piece to get the videos of annotated items
                if ('from_name', 'BasicEmotion') in ann.items(): # iterating over single annotations finds if one is basic emo and in that case it means the item is not neutral and it gets appended to videos 
                    annotated_videos.append(video_filename) # append video filename to list

    return annotated_videos


# extract videos of the utterances to annotate.
def extract_videos_to_annotate(filename_list):

    all_video_list = os.listdir(label_studio_video_path) # getting a list out of files in the directory with all video utterances
    for filename in filename_list: # iterate over filenames in the list of annotated video filenames
        if filename in all_video_list: # just checking...
            source_name = label_studio_video_path + "/" + filename

            if os.path.exists(label_studio_path+"/video_annotation"): # if export folder exists, just copy files in it
                shutil.copy(source_name, label_studio_path+"/video_annotation/"+filename)
            else:
                os.makedirs(label_studio_path+"/video_annotation") # if export folder does not exist, create it and then copy files
                shutil.copy(source_name, label_studio_path+"/video_annotation/"+filename)

    return True        
     

def scene_detect(video_folder):
    video_list = os.listdir(video_folder)

    for video in video_list:
        if video[-4:] == "webm":
            video_path = video_folder+"/"+video
            scene_list = detect(video_path, ContentDetector()) # detects shots and stores them in a list of tuples: (00:00:00.000 [frame=0, fps=25.000], 00:00:06.000 [frame=150, fps=25.000])
            mlsc_list = []

            video_shot_file = video.split(".")[0] # get filename without fileformat for writing shot filename later

            if len(scene_list) > 0: # if more than one shot is detected
                for tuple in scene_list: # iterate over each tuple with start and end in the list
                    start = str(tuple[0]).split(" ") # get the timecode as a string > ['00:00:00.000']
                    end = str(tuple[1]).split(" ") # ['00:00:06.000']
                    start = start[0].split(".")[0] # remove decimals > '00:00:00'
                    end = end[0].split(".")[0] # '00:00:06'
                    start = get_sec(start) # call converter > 0 
                    end = get_sec(end) # 6
                    mlsc_list.append((start, end)) # create new tuple with timecodes in mlsc

                i = 0
                for tuple in mlsc_list: # iterates over tuples with start and end timecodes of each shot
                    start = tuple[0]
                    end = tuple[1]

                    if end != 0: # there's a scene detect bug that creates tuples like (0, 0)
                        shot = VideoFileClip(video_path).subclip(start, end)  # cut file

                        if os.path.exists(video_folder+"/video_shots"):
                            shot.write_videofile(video_folder+"/video_shots/"+video_shot_file+"_"+str(i)+".webm") # write file
                            i = i+1
                        else: 
                            os.makedirs(video_folder+"/video_shots")
                            shot.write_videofile(video_folder+"/video_shots/"+video_shot_file+"_"+str(i)+".webm") # write file
                            i = i+1
                
            else: # if there's only one shot, copy the video directly
                if os.path.exists(video_folder+"/video_shots"):
                    shutil.copy(video_path, video_folder+"/video_shots/"+video_shot_file+"_0"+".webm")
                else: 
                    os.makedirs(video_folder+"/video_shots")
                    shutil.copy(video_path, video_folder+"/video_shots/"+video_shot_file+"_0"+".webm")

    return True

'''def extract_visual_content(string):
    string = re.sub('\"', '"', string)
    string = string.split('\n')
    vis_dict = {}
    for el in string: # vabbè raga wierd things happening... trying to handle
        key, value = el.split(':')
        vis_dict[key.strip('"')] = value.strip('"')
    
    return vis_dict

def get_video_annotation(video_annotations_path):
    j = load_json(video_annotations_path)

    for annotated_item in j: # single item level, json is a list of dictionsries)   
        data = annotated_item.get("data") # gett the data level where the dictionary storing the video url is
        video_url = data.get("video_url") # get the path + filename of the item annotated
        video_filename = video_url.split("/")[-1] # cleaning path to get video filename "1505e26d-2101608040029452931_15_78_utterance_1.webm" SBAGLIATO
        frame_id = video_filename.split(".")[0] # cleaning video filename to get utt name "2101608040029452931_15_40_utterance"
        annotations = annotated_item.get("annotations") # a list of dictionaries, one for each annotation type

        # now getting annotation types NB not all of them are necessarily there
        for dict in annotations: # getting the dictionary inside the annotations list
            results = dict.get("result") # again, a list of dictionaries
            for ann in results: # getting single annotations' dictionaries THIS IS THE MEANINGFUL LEVEL
                meta = ann.get("meta")
                text = meta.get("text")
                text = text[0]
                annotation_dict = extract_visual_content(text)
                print(annotation_dict)

                value = ann.get("value")
                seq = value.get("sequence")
                seq = seq[0]
                time = seq.get("time")
                print(time)
'''
            #should also get the main utt name so to connect

