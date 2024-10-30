

########################################################################

# When exporting the image from LAS-X, the intensity values are stored in a 16-bit image, 
# where the range is defined by the export settings. Ie 0 will be the minimum value
# and 2^16-1 will corresponed to the maximum value. By convenention, we have been using
# a range of 0-10 ns, which was set in the software using "10.000" (i.e. ten).

########################################################################

import pandas as pd
from skimage import io as skio
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from adjustText import adjust_text

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

# Excel with list of all samples
path_sample_metadata = '/Users/m.wehrens/Data_UVA/2024_10_Sebastian_cAMPING_screen/241018 Lysis_Data/SampleList.xlsx'
path_datadir         = '/Users/m.wehrens/Data_UVA/2024_10_Sebastian_cAMPING_screen/241018 Lysis_Data/'
path_outputdir       = '/Users/m.wehrens/Data_UVA/2024_10_Sebastian_cAMPING_screen/analysis_output/'

# First load the metadata table
df_sample_metadata = pd.read_excel(path_sample_metadata)
df_sample_data = df_sample_metadata.copy()

CHANNEL_TAU = 1 # channel with mean arrival times
CHANNEL_INT = 0 # channel with intensity values

########################################################################
# Data analysis
# Now simply loop over all these samples and calculate the mean value of the image

# Determine relevant filepaths
filepaths = path_datadir + '/' + df_sample_metadata['subdir'].values + '/' + df_sample_metadata['File'].values + '.tif'
filenames_brief = df_sample_metadata['subdir'].values + '/' + df_sample_metadata['File'].values + '.tif'

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

# Now save the dataframe
df_sample_data.to_excel(path_outputdir + 'SampleList_with_mean_arrival.xlsx')




########################################################################
# Plotting

# now create a little plot like Sebastian showed before
fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
# create a line plot with seaborn, using the mean intensity as the y-axis, and cAMP as x-axis
_ = sns.lineplot(df_sample_data, x='Condition_int', y='median_arrival', hue='Sample', ax=ax, markers=True, 
             markersize=10, marker='o', palette=color_palette)
# put the legend on the right outside of the plot
_ = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Now set custom tickmarks
plt.tight_layout()
# plt.show()
# save it:
plt.savefig(path_outputdir + 'lineplot_arrival.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# now a similar plot for the intensity
fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
# create a line plot with seaborn, using the mean intensity as the y-axis, and cAMP as x-axis
_ = sns.lineplot(df_sample_data, x='Condition_int', y='median_intensity', hue='Sample', ax=ax, markers=True, 
             markersize=10, marker='o', palette=color_palette)
# put the legend on the right outside of the plot
_ = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Now set custom tickmarks
plt.tight_layout()
# plt.show()
# save it:
plt.savefig(path_outputdir + 'lineplot_intensity.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# now create a more advance plot, showing a scatter of the two differences, and also color-code the 
# points by the mean intensity, and annotate each point with the sample name
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
plt.savefig(path_outputdir + 'scatterplot_diff_intensity_diff_arrival.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# The same can be done with seaborn
plt.rcParams.update({'font.size': 8}) # actually applies to all plots
fig, ax = plt.subplots(1,1,figsize=(10*cm_to_inch,10*cm_to_inch))
_ = sns.scatterplot(df_sample_data_subset, x='diff_intensity', y='diff_arrival', hue='mean_intensity', ax=ax, palette='viridis')
# Now annotate each point with the sample name
# (Code generated using co-pilot)
texts = []
for idx, row in df_sample_data_subset.iterrows():
    texts.append( ax.text(row['diff_intensity'], row['diff_arrival'], row['Sample'], color='darkgrey', size= plt.rcParams['font.size'] ) )
_ = adjust_text(texts,arrowprops=dict(arrowstyle='->', color='darkgrey', linewidth=.5) )
# Set the legend location to the outisde
_ = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Add labels, set font size etc
plt.xlabel('Difference in intensity (a.u.)')
plt.ylabel('Difference in arrival time (ns)')
plt.tight_layout()
# plt.show()
# or save it:
plt.savefig(path_outputdir + 'scatterplot_diff_intensity_diff_arrival_seaborn.png', dpi=300, bbox_inches='tight')
plt.close(fig)
