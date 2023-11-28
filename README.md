# DataProcessing_EmoAnnotation
This repository contains the code for the research software I wrote to process the data to make them suitable for manual annotation of emotional tags. The software is part of my MA thesis research where I am carrying out a preliminary domain analysis for emotional annotation od Public television content. <br>
The projcet is done in collaboration with the Netherlands Institute for Sound and Vision.

### Naming conventions of files
(data are under copyright, so this is mainly for personal use)<br>

The raw data in input consist in **1) a mp4 file for each item, 2) a json with metadata for each item, 3) an ASR transcript for each item**, additionally, I have **4) another json file for each item containing annotations added manually through the media suite**. <br>
This is the naming convention for these mentioned 4 input files:
1) full_mp4
2) json_full_metadata
3) full_asr
4) json_annotations

**Disclaimer:** an *utterance* here is defined as a spoken sentence delimited by silences or by a change of speaker. An utterance extracted from the text transcripts is a single line of transcript as found in json_full_metadata (already delimited by timecodes). These were manually produced by data providers VS An utterance extracted from asr transcripts is automatically delimited by silences identified by the automatic speech recognition tool. As found in the asr these utterances are long and they do not account for change of speakers, therefore they need to be manipulated to make them more aligned to the other modalities (this will be done later in the work) 

In the workflow I will create sub clips of full_mp4 and extract relevant information from json_full_metadata (where the text transcripts are also contained) and full_asr. The result for the textual processing some files will be created (I still don't know which ones will be exported and which will be just set as outcomes of methods)

1) **dictionary_video_ID** a dictionary containing video_ID, video_file_title, video_desc, segments_timecodes (to describe better)

2) **full_text** a dataframe, possibly exported as a csv, containing:


| _id' | 'video_title' | 'seg_start' | 'seg_end' | 'tt_text'| 
|------|---------------|-------------|-----------|-----------| 

- **_id** is the numeric string used as a unique id for each item, found in the json_full_metadata name and full_asr name : 2101608130110174831
- **video_title** is the title of the full_mp4 file (different from the title of the video as found in the Media Suite), this can also be retrieved in json_full_metadata under <code>source > assetItems > carriernumber</code> : "DE_WERELD_DRA-WON00662997.mxf"
- **seg_start** is the the time at which an utterance starts, in seconds
- **seg_end** is the time at which an utterance ends, in seconds
- **tt_text** is the text string of the utterance (if coming from the full_asr file, the column name is **asr_text**)

2) a folder called *segmentation_upper* containing the subclips of full_mp4, segmented according to timecodes found in json_annotations:

I refer to these subclips as **subclip_mp4**. <br>
in the segmentation_upper folder they are named according to the following naming convention:

_id + "_subclip _" + number of subclip : **2101608060045413031_subclip_0**

3) **utterance_text** the dataframe with text utterances matching the subclip
4) 
5) a folder called *segmentation_utt* containing single utterance subclips, split on the basis of the timecodes found in utterance_text. I refer to these as **utterance_mp4**

in the segmentation_utt folder they are named according to the following naming convention:

id + "_utt _" + number of ut : **2101608060045413031_utt_0**



### Data processing flowchart
![workflow_data_processing1](https://github.com/MaddaGh/DataProcessing_EmoAnnotation/assets/92437363/4117b7b3-2005-4746-8b79-27ad294b53a9)

