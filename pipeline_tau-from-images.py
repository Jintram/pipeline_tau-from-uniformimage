

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

########################################################################
# Data analysis

# Now simply loop over all these samples and calculate the mean value of the image
filepaths = path_datadir + '/' + df_sample_metadata['subdir'].values + '/' + df_sample_metadata['File'].values + '.tif'
filenames_brief = df_sample_metadata['subdir'].values + '/' + df_sample_metadata['File'].values + '.tif'

# Now calculate the mean values of the images
mean_values = np.empty(len(filepaths))
median_values = np.empty(len(filepaths))
for idx, filepath in enumerate(filepaths):
    try:
        my_img = skio.imread(filepath)
        mean_values[idx] = np.mean(my_img[1,:,:]) / 6553.6 
        median_values[idx] = np.median(my_img[1,:,:]) / 6553.6 
    except:
        print("Could not read file ", filenames_brief[idx])
        mean_values[idx] = np.nan
        median_values[idx] = np.nan

# Now add the mean values to the dataframe
df_sample_data['mean_arrival'] = mean_values
df_sample_data['median_arrival'] = median_values
# Now save the dataframe
df_sample_data.to_excel(path_outputdir + 'SampleList_with_mean_arrival.xlsx')

########################################################################

# Also create a second dataframe that contains also the difference between two conditions
# Could also normalize using the "template" condition



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
plt.show()
plt.close(fig)


# Also add an example plot that shows the difference between the two datapoints
XXXX