
########################################################################
# ABOUT

# This script loads the lib_pipeline_tauimages_getstats library and 
# runs it functions to get statistics. See readme.md and 
# lib_pipeline_tauimages_getstats.py for more information.

# ABOUT THE METADATA FILE
# See readme.md

# ASSUMPTIONS ON THE FILES
# See readme.md

########################################################################

# Set these to the location of these scripts on your computer
LIBSCRIPT_DIR = '/Users/m.wehrens/Documents/Python/Python_Libraries/' 

########################################################################
# Load the custom library

import sys    
sys.path.append(LIBSCRIPT_DIR)
import lib_pipeline_tauimages_getstats as taustats

# Code to reload the library (for debugging purposes)
# import importlib; importlib.reload(taustats)

########################################################################
# Load other libraries

# Now load some libraries for plotting and data manipulation
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from adjustText import adjust_text

########################################################################
# Perform an analysis

# Define metadata file and output directory
path_sample_metadata = '/Users/m.wehrens/Data_UVA/2024_10_Sebastian_cAMPING_screen/241018 Lysis_Data/SampleList.xlsx'
# set the directory where to save output files, a subdirectory will be automatically created there, using the unique identifier given in the metadata file
path_outputdir = '/Users/m.wehrens/Data_UVA/2024_10_Sebastian_cAMPING_screen/analysis_output'

# Note that you can also go into the library file (lib_pipeline_tauimages_getstats.py) and 
# select & run code from there, to see what it does.

# Load the metadata and initialize output data frame
df_sample_metadata, df_sample_data = taustats.initialize_analysis(path_sample_metadata)

# Now loop over the samples and analyze them
df_sample_data = taustats.extract_means_and_medians(df_sample_data)
df_sample_data = taustats.calculate_differences(df_sample_data)

# Save the dataframe as excel file
taustats.save_dataframe_to_excel(df_sample_data, path_outputdir)
    # If you later just want to plot some data, you can load the dataframe from the excel file
    # This requires you to provide analysis_ID, here '20241030_martijn' is given as example.
    # analysis_ID = '20241030_martijn'; df_sample_data = load_dataframe_from_excel(path_outputdir, analysis_ID)

# Now plot data
taustats.plot_differences_lines(df_sample_data, path_outputdir, mean_or_median='Median', arrival_or_intensity='intensity')
taustats.plot_differences_lines(df_sample_data, path_outputdir, mean_or_median='Mean', arrival_or_intensity='intensity')
taustats.plot_differences_lines(df_sample_data, path_outputdir, mean_or_median='Median', arrival_or_intensity='arrival')
taustats.plot_differences_lines(df_sample_data, path_outputdir, mean_or_median='Mean', arrival_or_intensity='arrival')

taustats.plot_differences_lines_fancylabels(df_sample_data, path_outputdir, mean_or_median='Median', arrival_or_intensity='intensity')
taustats.plot_differences_lines_fancylabels(df_sample_data, path_outputdir, mean_or_median='Mean', arrival_or_intensity='intensity')
taustats.plot_differences_lines_fancylabels(df_sample_data, path_outputdir, mean_or_median='Median', arrival_or_intensity='arrival')
taustats.plot_differences_lines_fancylabels(df_sample_data, path_outputdir, mean_or_median='Mean', arrival_or_intensity='arrival')

taustats.scatterplot_diff_intensity_diff_arrival(df_sample_data, path_outputdir)

# To further customize the plots, you can also simply look at the code in the library and copy it here,
# and then change the code to your liking.


########################################################################
# Perform another analysis

# Simply cut & paste the code above and change the metadata file and output directory
# I would recommend making some notes in the code about what you did and why
# You can also use separate files per data analysis.


# Note that excel files can contain any combination of files, so you can combine different
# samples. 

# Note that you can also combine/collect output files, either by manipulating the dataframes
# or by manipulating the excel files. 