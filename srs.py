#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 11:04:01 2022

@author: saathvikdirisala
"""

import pandas as pd
import numpy as np


def stratified_random_sample(file_path):
    
    # Read csv in as a pandas DataFrame
    data = pd.read_csv(file_path)
    
    # Remove rows with nan values in StartDateTime column
    wo_nan = data[data.StartDateTime == data.StartDateTime]
    
    # Retrieve the hour from each StartDateTime value
    hours = wo_nan.get("StartDateTime").apply(lambda x: x.split(" ")[1] if type(x) == str else x)
    
    # Create a new column with the integer value of the hour (0-23)
    wo_nan["Hour"] = list(map(lambda x: int(x.split(":")[0]), hours))
    
    # Assuming the duration is measured in seconds, filter out only the minute-long clips
    minute_long = wo_nan[wo_nan.Duration >= 60]
    
    # Group the df by AudioMothCode and Hour columns to get the combinations in the index
    grp = minute_long.groupby(["AudioMothCode", "Hour"]).count()
    
    # Collect all the AudioMothCode values with missing hour values (insufficient clips)
    audio_moth = list(grp.index)
    insuff_clips = []
    counter = 0
    for i in range(len(audio_moth)):
        if i > 0:
            if audio_moth[i][0] != audio_moth[i-1][0]:
                if counter < 24:
                    insuff_clips += [audio_moth[i-1][0]]
                counter = 0
        counter += 1
            
    # Filter out the AudioMothCodes with insufficient clips
    strata_data = minute_long    
    for j in insuff_clips:
        strata_data = strata_data[strata_data.AudioMothCode != j]
    
    # Perform stratified random sampling on the filtered dataset
    # Select a random row for each strata (AudioMothCode-Hour pairing)
    new_audio_moth = np.unique(strata_data["AudioMothCode"])
    final_df = pd.DataFrame(columns = strata_data.columns)
    for k in new_audio_moth:
        for l in range(24):
            sub_strata = strata_data[(strata_data.AudioMothCode == k) & (strata_data.Hour == l)]
            final_df = final_df.append(sub_strata.sample(1), ignore_index = True)
            
    # Generate a new file path and save the df at that path
    new_file_path = file_path.split(".csv")[0] + "_filtered.csv"
    final_df.to_csv(new_file_path)
    
    return new_file_path
        
    

