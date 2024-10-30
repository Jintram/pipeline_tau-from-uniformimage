
########################################################################
# About this script

# See the readme file for more information

# The goal of this script is to offer functions that can extract mean 
# and median arrival times and intensities from a series of images. 
# Excel files are used to load metadata, which conveys information 
# about the images.
#
# For each sample, typically two measurements are conducted, for 
# which a difference in arrival time and intensity is calculated.

# This library script can be imported into python using the following command:
if False:
    import sys
    LIBSCRIPT_DIR = '/Users/m.wehrens/Documents/Python/Python_Libraries/'
    sys.path.append(LIBSCRIPT_DIR)
    import lib_pipeline_tauimages_getstats as imgstats

########################################################################

# When exporting the image from LAS-X, the intensity values are stored in a 16-bit image, 
# where the range is defined by the export settings. Ie 0 will be the minimum value
# and 2^16-1 will corresponed to the maximum value. By convenention, we have been using
# a range of 0-10 ns, which was set in the software using "10.000" (i.e. ten).

########################################################################
# Library (and thus dependencies)

import pandas as pd
from skimage import io as skio
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from adjustText import adjust_text

import os

cm_to_inch = 1/2.54

color_palette = [
    "#E69F00",  # Orange
    "#56B4E9",  # Sky Blue
    "#009E73",  # Bluish Green
    "#F0E442",  # Yellow
    "#0072B2",  # Blue
    "#D55E00",  # Vermillion
    "#CC79A7",  # Reddish Purple
    "#000000"   # Black
] 

########################################################################

CHANNEL_TAU = 1 # channel with mean arrival times
CHANNEL_INT = 0 # channel with intensity values

########################################################################

def initialize_analysis(path_sample_metadata):
    '''
    This functions simply loads the metadata table and creates an output table.
    
    Metadata should have the following columns:
    Analysis_ID	    This can be any string and will be used to store output related to this analysis.
    Datadir	        Directory with data, potentially with subdirectories, which can be defined per sample in the subdir column.
    File	        Filename of the image, without extension
    Sample	        Sample name, used in plots for identification
    Condition	    Condition of the sample, used to calculate differences between conditions, can be any string
    Condition_int	Condition labels as integers (usually 0 and 1)
    subdir          See "Datadir"
    '''
    # First load the metadata table
    df_sample_metadata = pd.read_excel(path_sample_metadata)
    # Create a copy of this table to also store output
    df_sample_data = df_sample_metadata.copy()
    
    return df_sample_metadata, df_sample_data

########################################################################
# Data analysis
# Now simply loop over all these samples and calculate the mean value of the image

def extract_means_and_medians(df_sample_data):
    '''
    '''
    
    # Determine relevant filepaths
    filepaths = df_sample_data['Datadir'] + '/' + df_sample_data['subdir'].values + '/' + df_sample_data['File'].values + '.tif'
    filenames_brief = df_sample_data['subdir'].values + '/' + df_sample_data['File'].values + '.tif'

    # Now calculate the mean values of the images
    # Initialize arrays to store the calculated values
    mean_values_tau = np.empty(len(filepaths))
    median_values_tau = np.empty(len(filepaths))
    mean_values_int = np.empty(len(filepaths))
    median_values_int = np.empty(len(filepaths))
    # Loop over all files
    for idx, filepath in enumerate(filepaths):
        try:
            
            # Load the image
            my_img = skio.imread(filepath)
            
            # Calculate the mean and median arrival times
            mean_values_tau[idx] = np.mean(my_img[CHANNEL_TAU,:,:]) / 6553.6 
            median_values_tau[idx] = np.median(my_img[CHANNEL_TAU,:,:]) / 6553.6 
            
            # Calculate the mean and median intensity
            # (This assumes samples were taken under same conditions)        
            mean_values_int[idx] = np.mean(my_img[CHANNEL_INT,:,:]) 
            median_values_int[idx] = np.median(my_img[CHANNEL_INT,:,:]) 
            
        except:
            
            # If missing file, tell user and set to NaN to indicate missing data
            print("Could not read file ", filenames_brief[idx])
            mean_values_tau[idx] = np.nan
            median_values_tau[idx] = np.nan
            mean_values_int[idx] = np.nan
            median_values_int[idx] = np.nan

    # Now add the mean values to the dataframe
    df_sample_data['mean_arrival'] = mean_values_tau
    df_sample_data['median_arrival'] = median_values_tau
    df_sample_data['mean_intensity'] = mean_values_int
    df_sample_data['median_intensity'] = median_values_int

    return df_sample_data

def calculate_differences(df_sample_data, illustrate_for_beginner=False):
    
    # Now also calculate the difference between the two conditions
    # This assumes that there's a reference condition and a test condition
    # And that these can be linked by the sample ID stored in "Sample" column

    # First order the dataframe such that rows are in the right order
    df_sample_data.sort_values(by=['Sample', 'Condition_int'], inplace=True) 

    # The values can be calculated using the groupby and diff function in one line
    df_sample_data['diff_arrival'] = df_sample_data.groupby('Sample')['median_arrival'].diff()
    df_sample_data['diff_intensity'] = df_sample_data.groupby('Sample')['median_intensity'].diff()

    # This is perhaps a bit hard to understand, and it can also be done using much more basic commands
    if illustrate_for_beginner:

        # First get a list of all the samples
        list_of_samples = df_sample_data['Sample'].unique()
        df_sample_data['diff_arrival2'] = np.nan
        df_sample_data['diff_intensity2'] = np.nan
        # Assuming Conditions_int holds either 0 or 1 to identify the two conditions
        for sample in list_of_samples:
            # difference in arrival times
            value1 = df_sample_data.loc[(df_sample_data['Sample'] == sample) & (df_sample_data['Condition_int'] == 1), 'median_arrival'].values
            value0 = df_sample_data.loc[(df_sample_data['Sample'] == sample) & (df_sample_data['Condition_int'] == 0), 'median_arrival'].values
            value_difference = value1 - value0
            df_sample_data.loc[(df_sample_data['Sample'] == sample) & (df_sample_data['Condition_int'] == 1), 'diff_arrival2'] = value_difference
            # difference in intensity
            value1 = df_sample_data.loc[(df_sample_data['Sample'] == sample) & (df_sample_data['Condition_int'] == 1), 'median_intensity'].values
            value0 = df_sample_data.loc[(df_sample_data['Sample'] == sample) & (df_sample_data['Condition_int'] == 0), 'median_intensity'].values
            value_difference = value1 - value0
            df_sample_data.loc[(df_sample_data['Sample'] == sample) & (df_sample_data['Condition_int'] == 1), 'diff_intensity2'] = value_difference
    
    # return the dataframe
    return df_sample_data

def save_dataframe_to_excel(df_sample_data, path_outputdir):
    '''
    Save the dataframe to an excel file.
    '''
    
    # Get the unique identifier for this analysis
    analysis_ID = df_sample_data['Analysis_ID'][0]
    
    path_outputdir_plussubdir = path_outputdir + '/output_' + analysis_ID + '/'
    
    # create a subdirectory if it does not exist
    os.makedirs(path_outputdir_plussubdir, exist_ok=True)

    df_sample_data.to_excel(path_outputdir_plussubdir + 'analysis_'+analysis_ID+'__df_sample_data.xlsx', index=False)

def load_dataframe_from_excel(path_outputdir, analysis_ID):
    # Load the dataframe from an excel file.
    
    analysis_ID = df_sample_data['Analysis_ID'][0]
    path_outputdir_plussubdir = path_outputdir + '/output_' + analysis_ID + '/' 
    
    df_sample_data = pd.read_excel(path_outputdir_plussubdir + 'analysis_'+analysis_ID+'__df_sample_data.xlsx')
    
    return df_sample_data

########################################################################
# Plotting

def plot_differences_lines(df_sample_data, path_outputdir, mean_or_median='Median', arrival_or_intensity='arrival'):

    # Check input
    if arrival_or_intensity not in ['arrival', 'intensity']:
        raise ValueError('arrival_or_intensity should be either "arrival" or "intensity"')
    if mean_or_median.lower() not in ['mean', 'median']:
        raise ValueError('mean_or_median should be either "Mean" or "Median"')
    
    # Define the output directory
    analysis_ID = df_sample_data['Analysis_ID'][0]
    path_outputdir_plussubdir = path_outputdir + '/output_' + analysis_ID + '/' 

    # mean_or_median='Median'
    # mean_or_median='Mean'
    y_value_toplot = mean_or_median.lower() + '_' + arrival_or_intensity

    # now create a little plot like Sebastian showed before
    fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
    # create a line plot with seaborn, using the mean intensity as the y-axis, and cAMP as x-axis
    _ = sns.lineplot(df_sample_data, x='Condition_int', y=y_value_toplot, hue='Sample', ax=ax, markers=True, 
                markersize=10, marker='o', palette=color_palette)
    # put the legend on the right outside of the plot
    _ = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout() # required for better display
    # Axes labels
    plt.xlabel('Condition')
    # Add the correct y label
    if arrival_or_intensity == 'arrival':
        plt.ylabel(mean_or_median+' arrival time (ns)')
    else:
        plt.ylabel(mean_or_median+' intensity (a.u.)')
    # plt.show()
    # save it:
    plt.savefig(path_outputdir_plussubdir + 'lineplot_'+y_value_toplot+'.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)


def plot_differences_lines_fancylabels(df_sample_data, path_outputdir, mean_or_median='Median', arrival_or_intensity='arrival'):

    # Check input
    if arrival_or_intensity not in ['arrival', 'intensity']:
        raise ValueError('arrival_or_intensity should be either "arrival" or "intensity"')
    if mean_or_median.lower() not in ['mean', 'median']:
        raise ValueError('mean_or_median should be either "Mean" or "Median"')

    # Define the output directory
    analysis_ID = df_sample_data['Analysis_ID'][0]
    path_outputdir_plussubdir = path_outputdir + '/output_' + analysis_ID + '/' 

    # mean_or_median='Median'
    # mean_or_median='Mean'
    y_value_toplot = mean_or_median.lower() + '_' + arrival_or_intensity

    # now create a little plot like Sebastian showed before
    fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
    # create a line plot with seaborn, using the mean intensity as the y-axis, and cAMP as x-axis
    _ = sns.lineplot(df_sample_data, x='Condition_int', y=y_value_toplot, hue='Sample', ax=ax, markers=True, 
                markersize=10, marker='o', palette=color_palette)
    # remove the usual legend
    ax.get_legend().remove()
    # Set x axis to span 0-3
    ax.set_xlim(-0.5, 2.0)
    # now add text annotation
    texts = []
    df_sample_data_subset = df_sample_data.loc[df_sample_data['Condition_int'] == 1]
    for idx, row in df_sample_data_subset.iterrows():
        texts.append( ax.text(row['Condition_int'], row[y_value_toplot], row['Sample'], color='darkgrey', size= plt.rcParams['font.size'] ) )
    #        
    #_ = adjust_text(texts, arrowprops=dict(arrowstyle='->', color='darkgrey', linewidth=.5) )
    # as in comment above, but force the labels a bit to the right
    #_ = adjust_text(texts, arrowprops=dict(arrowstyle='->', color='darkgrey', linewidth=.5))
    _ = adjust_text(texts, arrowprops=dict(arrowstyle='->', color='darkgrey', linewidth=.5), min_arrow_len=0)
                    #target_x=df_sample_data_subset['Condition_int']+.5, target_y=df_sample_data_subset[y_value_toplot],
                    #x=df_sample_data_subset['Condition_int']+.5, y=df_sample_data_subset[y_value_toplot])
    plt.tight_layout() # required for better display
    # Axes labels
    plt.xlabel('Condition')
    # Add the correct y label
    if arrival_or_intensity == 'arrival':
        plt.ylabel(mean_or_median+' arrival time (ns)')
    else:
        plt.ylabel(mean_or_median+' intensity (a.u.)')
    # plt.show()
    # save it:
    plt.savefig(path_outputdir_plussubdir + 'lineplot_'+y_value_toplot+'_fancy.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)

def scatterplot_diff_intensity_diff_arrival(df_sample_data, path_outputdir):
    
    # now create a more advance plot, showing a scatter of the two differences, and also color-code the 
    # points by the mean intensity, and annotate each point with the sample name
    
    # Define the output directory
    analysis_ID = df_sample_data['Analysis_ID'][0]
    path_outputdir_plussubdir = path_outputdir + '/output_' + analysis_ID + '/' 
    
    # Select only the relevant data to plot, which is stored with Condition_int==1, this is strictly not necessary as nan values are not plotted
    df_sample_data_subset = df_sample_data.loc[df_sample_data['Condition_int'] == 1]

    # Now make the plot
    # Set global font size using rcParams
    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
    # seaborn has some weird behavior regarding color bars, so I'll extract the data first and then create a colorbar ..
    values_diff_intensity = df_sample_data_subset['diff_intensity']
    values_diff_arrival = df_sample_data_subset['diff_arrival']
    values_median_intensity = df_sample_data_subset['median_intensity']
    values_sample_name = df_sample_data_subset['Sample']
    ax.scatter(values_diff_intensity, values_diff_arrival, c=values_median_intensity, cmap='viridis')
    # add a colorbar
    plt.colorbar(ax.collections[0], ax=ax)
    # add sample annotation using the value_.. variables
    texts = []
    for idx in range(len(values_diff_intensity)):
        texts.append( ax.text(values_diff_intensity.iloc[idx], values_diff_arrival.iloc[idx], values_sample_name.iloc[idx], color='darkgrey', size= plt.rcParams['font.size'] ) )
    _ = adjust_text(texts,arrowprops=dict(arrowstyle='->', color='darkgrey', linewidth=.5) )
    # Add labels etc
    plt.xlabel('Difference in intensity (a.u.)')
    plt.ylabel('Difference in arrival time (ns)')
    plt.tight_layout()
    # and show the plot
    # plt.show()
    # or save it:
    plt.savefig(path_outputdir_plussubdir + 'scatterplot_diff_intensity_diff_arrival.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)

# The same can be done with seaborn, but seaborn showed some undesirably behavior with regard to the colorbar
# def scatterplot_diff_intensity_diff_arrival_seaborn(df_sample_data, path_outputdir):
#     plt.rcParams.update({'font.size': 8}) # actually applies to all plots
#     fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
#     _ = sns.scatterplot(df_sample_data_subset, x='diff_intensity', y='diff_arrival', hue='mean_intensity', ax=ax, palette='viridis')
#     # Now annotate each point with the sample name
#     # (Code generated using co-pilot)
#     texts = []
#     for idx, row in df_sample_data_subset.iterrows():
#         texts.append( ax.text(row['diff_intensity'], row['diff_arrival'], row['Sample'], color='darkgrey', size= plt.rcParams['font.size'] ) )
#     _ = adjust_text(texts,arrowprops=dict(arrowstyle='->', color='darkgrey', linewidth=.5) )
#     # Set the legend location to the outisde
#     _ = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#     # Add labels, set font size etc
#     plt.xlabel('Difference in intensity (a.u.)')
#     plt.ylabel('Difference in arrival time (ns)')
#     plt.tight_layout()
#     # plt.show()
#     # or save it:
#     plt.savefig(path_outputdir + 'scatterplot_diff_intensity_diff_arrival_seaborn.pdf', dpi=300, bbox_inches='tight')
#     plt.close(fig)
