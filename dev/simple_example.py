



# Let's first try to see whether I can process the data to be consistent 
# with the plugin Dorus made. 

# The essential point is that these images were exported by LAS-X with
# a custom range, which holds the photon mean arrival time information.


# Let's first see what average I get for a specific image.

import numpy as np
import matplotlib.pyplot as plt

from skimage import io as skio
from skimage.filters import median
from skimage.exposure import adjust_gamma
from skimage.morphology import disk

location_example_image = "/Users/m.wehrens/Data_UVA/2024_10_Sebastian_cAMPING_screen/241018 Lysis_Data/1mM_cAMP_T0/A11_1mMCAMP.tif"
# Value according to Dorus' plugin: 
tau_dorus = 3.7961 # ns
tau_dorus_noproc = 3.9876 # obtained from setting min and max tau to 0 and 10 ns, intensity thresholds to 0 and 99999, gamma to 1, and median to 0, deactivating zero lifetime outisde thresholds

# read the tiff image at location_example_image using skimage
my_img = skio.imread(location_example_image)
image_intensity=my_img[0,:,:]
image_meanarrival=my_img[1,:,:] # if i understand setslice correctly, this is the slice with photon information

# Now determine mean value and histogram
np.mean(image_intensity)
np.mean(image_meanarrival)/6553.6
mean_value0 = np.mean(my_img[0,:,:])
mean_value1 = np.mean(my_img[1,:,:]) 
np.max(my_img[0,:,:])
np.max(my_img[1,:,:])
tau_dorus_noproc
print("Mean value of the image: ", mean_value)

# Now also calculate mean using a histogram like dorus does
# First he also applies a median filter (line 154 -- this is done both on intensity and mean arrival time)
# but this is not relevant when in his script i set median footprint to 0
# image_meanarrival_filtered = median(image_meanarrival, footprint=disk(3))
# using the histogram
hist_, bin_edges = np.histogram(image_meanarrival.flatten(), bins=round(my_img.shape[1]*2/3))
# calculate the mean based on the hist, ignoring the outer values
bin_centers = (bin_edges[:-1] + bin_edges[1:])/2
hist=hist_
hist[0]=0
hist[-1]=0
mean_tau_hist = np.sum([bin_centers[idx]*hist[idx] for idx in range(len(bin_centers))]) / np.sum(hist) / 6553.5 # (2**16-1)/10
mean_tau_hist
tau_dorus_noproc
tau_dorus_noproc/mean_tau_hist

# Factor by which the mean value should be multiplied to get the correct value
# tau_dorus = mean_value/factor --> factor = mean_value/tau_dorus
mean_value0/tau_dorus # 7.198..
mean_value1/tau_dorus # 7028.4..

# This doesn't quite work
# Using https://zmb.dozuki.com/Guide/Export+Leica+Falcon+LAS+X+FLIM+Image+Data/133
# and using some assumptions;
# (1) the scale 0-10.000 gets distributed over the whole range of possible tif values, 65536, so 10.000 equals 65536
# thus to convert back, we'd have to divide by 65536/10000 = 6.5536
# Wait, were these settings 0-10.000 or 0-1000? (ie ten or ten thousand)
# (2) According to above website, it's important to remove values which are outside
# the LAS-X intensity treshold.
# 
# --> asked Dorus:
# indeed, the intensity range is 0-10 ns, where 10.000 in the software means 10.0.
np.mean(my_img[1,:,:]/6553.6)
np.mean(my_img[1,:,:])/6553.6
# Now let's see whether we can also apply treshold

# Show a thresholded intensity image
thr_low=50
thr_high=250
mask_intensity = (image_intensity>thr_low) & (image_intensity<thr_high)

# now plot that mask]
plt.imshow(mask_intensity)
plt.show()
plt.close('all')

# Now calculate a new mean based on the intensity mask
mean_tau = np.mean(image_meanarrival[mask_intensity]/6553.6)
print("Mean value of the image: ", mean_tau)

mean_tau/tau_dorus

mean_tau
tau_dorus

# Still not 100% match, probably because Dorus also applies median and gamma filter
# to the intensity image

# 
# (Dorus script line 147 runs gamma filter using value stored in "gamma")
# (Dorus script line 154 runs a median filter using size value stored in "median")

# Let's regenarate the mask using the same strategy
image_intensity_filtered = image_intensity.copy()
image_intensity_filtered = adjust_gamma(image_intensity_filtered, gamma=.7)
image_intensity_filtered = median(image_intensity_filtered, footprint=disk(3))

# the automatic settings of intensity min/max are stored in imin and imax in dorus' script
# and they are simply 10% of max as the minimum threshold.
thr_low = np.max(image_intensity_filtered)/10
thr_high = np.max(image_intensity_filtered)
mask_intensity_filtered  = (image_intensity_filtered>thr_low) & (image_intensity_filtered<thr_high)
# below settings are only applied if auto is not applied
# note: i'm guessing the image is converted to 0-255 range, so that's why these values make sense.
# mask_intensity_filtered2 = (image_intensity_filtered>50) & (image_intensity_filtered<250)

# Calculate median
mean_tau_filtered = np.mean(image_meanarrival[mask_intensity_filtered]/6553.6)
mean_tau_filtered
#mean_tau_filtered2 = np.mean(image_meanarrival[mask_intensity_filtered2]/6553.6)
#mean_tau_filtered2

# also plot the mask
plt.imshow(mask_intensity_filtered)
plt.show()
plt.close('all')

