import os
from utils import load_json, convert_video_to_audio_moviepy
from moviepy.editor import VideoFileClip # https://zulko.github.io/moviepy/getting_started/efficient_moviepy.html
from tqdm import tqdm
import pandas as pd

# full pipeline implementation

full_mp4_dir = "E:/NISV/data1/selection_mp4"
json_annotations_path = "data_with_asr.json"
json_full_metadata_dir = "E:/NISV/data1/selection"

export_dir = "segmentation_utterance_asr"
data_dir = "segmentation_upper_asr"

# asr are in the "source" > "layer_asr" : a list of 


# FUNCTION TO CREATE A DATAFRAME WITH ALL THE ASR TRANSCRIPTS OF ALL THE ITEMS IN THE DATASET OF VIDEOS (saved as text_df.csv)
# columns of the csv are: '_id', 'file_name', 'sequenceNr','seg_start', 'seg_end', 'asr_text', 'word_times'
def extract_asr(dir):
    count_yes = 0 # these counts are a check to see if there are items without 'layer_asr' and count how many
    count_no = 0
    list_dir = os.listdir(dir)
    dataframe_list = []

    # iterating over 'json_full_metadata_dir' where each json containing metadata for a video is stored
    for file in list_dir:
        if file[-4:] == "json":
            metadata_json = load_json(dir+"/"+file)
            asr_df = pd.DataFrame(columns = ['_id', 'file_name', 'sequenceNr','seg_start', 'seg_end', 'asr_text', 'word_times']) # initializing empty df to store transcripts

            try: 
                _id = metadata_json["_id"]

                asr_list = metadata_json["_source"]["layer__asr"] # a list of dictionaries, one for each text segment

                # iterates over dictionaries (1 dict for 1 utterance found in json's layer_asr)  
                for el in asr_list: 
                    file_name = el.get("carrierId")
                    seg_start = int(el.get("start")) # time start of segment in seconds it's a string
                    seg_start = str(seg_start) # just doing type conversion because I need a string like "6000" ant it was initially read as a float 6000.0
                    if len(seg_start) > 3:
                        seg_start = seg_start[:-3]
                        seg_start = int(seg_start) # i need it back to int
                    else: 
                        seg_start = int(seg_start)

                    seg_end = None # in the json I don't have the end of the sentences
                    sequenceNr = int(el.get("sequenceNr"))
                    asr_text = el.get("words") # it's a string
                    asr_text_words = asr_text.split(" ") # getting a list of words to match the wordTimes
                    word_times = el.get("wordTimes")

                    if len(asr_text_words) != len(word_times): # checking that there is a wordtime for each word
                        print("words and times do not match", len(asr_text_words), len(word_times))
                    else: 
                        asr_text_words = " ".join(asr_text_words) # doing this because 
                        word_times = " ".join(map(str, word_times))

                    asr_new_row = pd.DataFrame({'_id': _id, 'file_name': file_name, 'sequenceNr': sequenceNr, 'seg_start': seg_start, 'seg_end': seg_end, 'asr_text': [asr_text_words], 'word_times': [word_times]}) #creating new dataframe row
                    asr_df = pd.concat([asr_df, asr_new_row], ignore_index=True) # concatenating rows

                # sorting fragments in the correct order
                asr_df = asr_df.sort_values("seg_start", ascending=True)
                dataframe_list.append(asr_df)
                count_yes += 1                

            except:
                count_no += 1
    
    full_text_asr_df = pd.concat(dataframe_list, ignore_index=True) # need to fix INDEX 

    # video_w_asrlayer = full_text_asr_df["_id"].unique()  # uncomment to return these other information
    return full_text_asr_df#, count_yes, count_no, video_w_asrlayer


# FUNCTION TO FIND THE IDXS IN text_df CORRESPONDING TO THE RELEVANT SUBCLIP OF THE VIDEO
# This function is called in segmentation_upper_split, where the dataframe is also split
def find_closest_to_timecode(timecode, key_df):
    idx_timecode = None

    # getting low and high idxs
    low = 0
    high = len(key_df) - 1
    min_diff = float("inf")

    # edge cases. I don't have a idx end here!
    # len df can't be 0 
    if len(key_df) == 1:
        idx_timecode = 0
        closest_to_timecode = key_df[0]

    if len(key_df) == 2:
        diff1 = timecode - key_df.at[0, "seg_start"]
        diff2 = timecode - key_df.at[1, "seg_start"] # TAKE LAST WORDTIME FOR THE END

        # need to take the lower difference 
        if diff1 < diff2:
            idx_timecode = 0
            closest_to_timecode = key_df[0]
        else:
            idx_timecode = 1
            closest_to_timecode = key_df[1]
    
    while low <= high:
        mid = (low + high) // 2

        # ensure we don't look beyond the bounds of the df
        # and obtain the left and right difference value
        if mid + 1 < len(key_df):
            min_diff_right = abs(key_df.at[mid+1, "seg_start"] - timecode)
        if mid > 0:
            min_diff_left = abs(key_df.at[mid-1, "seg_start"] - timecode)
        
        # check if abs value between left and right elements
        # are smaller than any seen prior
        if min_diff_right < min_diff:
            min_diff = min_diff_right
            closest_to_timecode =  key_df.at[mid+1, "seg_start"]
            idx_timecode = mid+1
        if min_diff_left < min_diff:
            min_diff = min_diff_left
            closest_to_timecode = key_df.at[mid-1, "seg_start"]
            idx_timecode = mid-1
        
        # move the mid point accordingly as is done via binary search
        if key_df.at[mid, "seg_start"] < timecode:
            low = mid+1
        elif key_df.at[mid, "seg_start"] > timecode:
            high = mid-1
        # if it's target itself closest number it's itself
        else:
            closest_to_timecode = key_df.at[mid, "seg_start"]
            idx_timecode = mid

            return closest_to_timecode, idx_timecode
    
    return closest_to_timecode, idx_timecode


# FUNCTION TO CREATE AN ITEM OF THE DICTIONARY_VIDEO 
# in main, each item is added to the dictionary independently
def get_dictionary_video(single_video_info, dictionary_video):

    video_ID = single_video_info["resourceId"]
    video_file_title = single_video_info["targetObjects"][0]["assetId"]
    
    try:
        video_desc = single_video_info["object"]["description"]
    except: 
        print("no description available")

    segments = [] # a list of start end tuple they should already be ordered sequentially from the json so the list of segments by default should be ordered
    for el in single_video_info["segments"]:
        start_end_tuple = (int(el["selector"]["refinedBy"]["start"]), int(el["selector"]["refinedBy"]["end"]))
        segments.append(start_end_tuple)
    
    # since IDs are unique I shouldn't have doubles, anyway consider if you have to enclose in some if clause check
    dictionary_video[video_ID] = {"video_file_title" : video_file_title, "video_desc" : video_desc, "segments": segments}

    return dictionary_video


# FUNCTION TO CUT VIDEOS AND TRANSCRIPTS' CSVS IN ORDER TO OBTAIN THE SELECTED SEGMENTS
def segmentation_upper_split(full_mp4_dir, dictionary_video, text_df): 
    
    path = "./segmentation_upper_asr"

    if os.path.isdir(path):
        print(f"files will be saved in {path}")
    else: 
        os.mkdir(path)

    idx = 0

    # !! if a video in the folder full_mp4_dir has no segmentation annotation it will be ignored by the algorithm and no csv will be generated
    # to follow this pipeline make sure to annotate in the media suite also the items that don't need segmentation so they can appear in the annotation_json
    # or feel free to update the code :)
    for key, value in tqdm(dictionary_video.items()):

        file_name = value.get("video_file_title")
        timecodes = value.get("segments")

        for timecode in timecodes: # timecodes in the dictionary is a list with start end tuples
            start = timecode[0]
            end = timecode[1]

            # cut clip
            subclippath_name = path + "/" + key + "_" + str(idx) + "_subclip" # ex: 2101608050040501131_6_subclip.mp4
            subclip = VideoFileClip(full_mp4_dir + "/" + file_name +".mp4").subclip(start, end)  # cut file
            subclip.write_videofile(subclippath_name + ".mp4")  # write file
            idx += 1 # augment idx to update sbclippath_name for the next iteration

            # split text_df to get sub dataframe corresponding to video 
            key_df = text_df.query(f"_id == '{key}'") # querying the full df for the section containing rows of the current cubclip
            key_df = key_df.reset_index()

            # returning the 'closest_to_start_timecode' in case one need to print for checks
            closest_to_start_timecode, idx_start = find_closest_to_timecode(start, key_df)
            closest_to_end_timecode, idx_end = find_closest_to_timecode(end, key_df)

            subclip_asr_df = key_df[idx_start:idx_end] # create a df for the current subclip
            subclip_asr_df.to_csv(subclippath_name + ".csv") # saving text with same file name as subclip
            
    return path # returning path to main function because i need it as paramenter of utterance_segmentation function later


# FUNCTION TO CREATE A SUBCLIP FOR EACH MULTIMODAL UTTERANCE (namely, each row of the asr csv files)
def utterance_segmentation(export_dir, data_dir, full_mp4_dir, dictionary_video):
    list_dir = os.listdir(data_dir)

    if os.path.isdir(export_dir):
        print(f"files will be saved in {export_dir}")
    else: 
        os.mkdir(export_dir)

    for file in tqdm(list_dir): # list dir where the dataframes are
        if file[-4:] == ".csv":
            name = file[:-4]
            print(name)
                    
            subclip_parts = name.split("_") # split the name of files to get id + idx + 'subclip'
            identifier = subclip_parts[0] # extract the identifier here so I get the correct key in the dictionary to retrieve the end of the segment.

            subclip_ref = subclip_parts[1] # extracting this because I will add it to the utterances file names. 
            # this allows connectinc a cluster of audiovisual utterances with their respective csv file
            
            # now read the csv
            utt_df = pd.read_csv(f"{data_dir}/{name}.csv", encoding="utf-8")
            print(utt_df)

            timecodes_tup = []

            # this is working at a single dataframe level (one subclip)
            for el in utt_df["seg_start"]:
                idx = list(utt_df["seg_start"]).index(el) # i need the idx (and all the edge cases below) to get the seg_end
                sqN = utt_df.at[idx, "sequenceNr"]

                if idx < len(utt_df["seg_start"])-1: # if idx is == last idx of df it will raise an error
                    start = el
                    end = utt_df.at[idx+1, "seg_start"] # fing end timecode as the seg_start of next row
                    tup = (sqN, start, end) # add tuple with sequenceNr (for naming files later), start, end
                    timecodes_tup.append(tup)

                    end = str(end)
                    utt_df.at[idx, "seg_end"] = end # update dataframe with seg_end

                # cases for last row of the dataframe 
                else: 
                    el = list(utt_df["seg_start"])[-1]
                    start = el
                    # last row can't get seg_end by taking the following seg_start, but I have the final end timecode in the dictionary from the annotation
                    item_dictionary = dictionary_video.get(identifier) # getting item in the dict corresponding to current video
                    timecodes = item_dictionary.get("segments")
                    if len(timecodes) == 1: # if I just have one segment in a video I can take the end timecode directly
                        timecode = timecodes[0]
                        end = timecode[1]
                        tup = (sqN, start, end)
                        timecodes_tup.append(tup)

                        end= str(end)
                        utt_df.at[idx, "seg_end"] = end

                    else: # if I have more segments related to a single video I have to find the matching one starting from the seg_start in current csv
                        timecode_start = float("inf")

                        # i suspect this bit is wrong
                        for i, timecode in enumerate(timecodes): # iterates over timecode tuples, to get the timecodes of the related segment  
                            temp_start = timecode[0]
                            df_start = utt_df.at[0, "seg_start"] #extracting first seg_start of df

                            higher_num = max(temp_start, df_start)
                            lower_num = min(temp_start, df_start)

                            closer_start = abs(higher_num - lower_num)

                            if closer_start < timecode_start:
                                timecode_start = closer_start
                                idx_end = i

                        end = timecodes[idx_end][1]
                        tup = (sqN, start, end)
                        timecodes_tup.append(tup)
                
            print(timecodes_tup)
            # now I have a list of tuples with single utterances start and ends

            for tup in timecodes_tup: # iterate over the utterance timecodes just created
                sqN = tup[0]
                start = tup[1]
                end = tup[2]
                wrong_timecodes = []

                # putting this condition here because there was something wrong going on I think in segmentation_upper_split
                # now everything seems correct but I don't know what happened so I am leaving this part of code too
                if start < end:
                    file_name = item_dictionary.get("video_file_title")
                    subclip = VideoFileClip(full_mp4_dir + "/" + file_name +".mp4").subclip(start, end)  # cut file

                    utt_file_name = identifier + "_" + subclip_ref + "_" + str(sqN) + "_utterance" # ex: 2101608140123043831_12_16_utterance
                    print(utt_file_name)
                    export_name = export_dir + "/" + utt_file_name + ".mp4"

                    subclip.write_videofile(export_name)  # write file

                    # extract audio
                    convert_video_to_audio_moviepy(export_name)
                
                else:
                    x = (identifier, subclip_ref, timecodes)
                    wrong_timecodes.append(x)

    # add to save utt_df to rewrite it with the seg_end
    #print(wrong_timecodes)
    return True


# function to segment full_mp4 videos
def main(json_annotations_path, full_mp4_dir, json_full_metadata_dir):
    dictionary_video = {}


    text_df = extract_asr(json_full_metadata_dir)
    text_df.to_csv("text_df.csv")

    for item in load_json(json_annotations_path):
        dictionary_video = get_dictionary_video(item, dictionary_video)
    
    # cut clip and save in folder
    data_dir = segmentation_upper_split(full_mp4_dir, dictionary_video, text_df)
    utterance_subclips = utterance_segmentation(export_dir, data_dir, full_mp4_dir, dictionary_video)

    return utterance_subclips, dictionary_video



def load_dict(json_annotations_path):
    dictionary_video = {}
    for item in load_json(json_annotations_path):
        dictionary_video = get_dictionary_video(item, dictionary_video)
    return dictionary_video

print(main(json_annotations_path, full_mp4_dir, json_full_metadata_dir))
dictionary_video = load_dict(json_annotations_path)
#print(utterance_segmentation(export_dir, data_dir, full_mp4_dir, dictionary_video))
