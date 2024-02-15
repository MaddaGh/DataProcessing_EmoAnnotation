import os
import pandas as pd
import deepl

# github of deepl-python https://github.com/DeepLcom/deepl-python?tab=readme-ov-file#configuration
# old code to count chars
# print(os.getcwd())

data_path = "segmentation_upper_asr"
auth_key = 'd2c14e48-4f57-7787-01d1-e6b3610d176b:fx'


def translation(df):

    translator = deepl.Translator(auth_key)
                        
    asr_text_list = list(df["asr_text"])
    print(asr_text_list)

    result = translator.translate_text(asr_text_list, source_lang="NL", target_lang="EN-US")
    text_eng = []

    for el in result: # should be a list of TextResults, where every TextResult have two params: .text and .detected_source_lang
        text_eng.append(el.text) # i get the text from every element of the result list and append it to a new list
    
    return text_eng


def add_eng_col(data_path):
    for file in os.listdir(data_path): # list dir where the dataframes are
        if file[-4:] == ".csv":
            try:
                utt_df = pd.read_csv(f"{data_path}/{file}", encoding="utf-8")
            except Exception as e:
                print(f"Error reading file: {e}")
            
            text_eng = translation(utt_df) # should return a list of translated utterances
            utt_df["text_eng"] = text_eng # add the column
            utt_df.to_csv(file, index=False) # overwrite the file with updated one
        print(utt_df)
    return True

print(add_eng_col(data_path))
      

# all csv have 127.780 characters





