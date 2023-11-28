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

In the workflow I will create sub clips of full_mp4 and extract relevant information from json_full_metadata (where the text transcripts are also contained) and full_asr. The result for the textual processing of these two files will be
1) **a dataframe, possibly exported as a csv** containing:


| _id' | 'video_title' | 'seg_start' | 'seg_end' | 'tt_text'| 
|------|---------------|-------------|-----------|-----------| 

- **_id** is the numeric string used as a unique id for each item, found in the json_full_metadata name and full_asr name : 2101608130110174831
- **video_title** is the title of the full_mp4 file (different from the title of the video as found in the Media Suite), this can also be retrieved in json_full_metadata under <code>source > assetItems > carriernumber</code> : "DE_WERELD_DRA-WON00662997.mxf"
- **seg_start** is the the time at which an utterance starts, in seconds
- **seg_end** is the time at which an utterance ends, in seconds
- **tt_text** is the text string of the utterance (if coming from the full_asr file, the column name is **asr_text**)

2) a folder called *segmentation_upper* containing the subclips of full_mp4, segmented according to timecodes found in json_annotations:

I refer to these subclips as **subclip_mp4**. <br>
in the segmentation_upper folder they are named according to the following naming conventions:

_id + "_subclip _" + number of subclip : **2101608060045413031_subclip_0**
