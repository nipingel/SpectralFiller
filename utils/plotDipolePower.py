"""
3/4/19
Script to read in FITS files from FLAG scans and plots the (normalized) total power as a function of total scan time. 
The resulting plot is a 4x5 panel image showing the XX/YY power vs. time for each of the 19 elements.  
Inputs:
/path/to/BANK/FITS/files - path to BANK FITS files on lustre
fileTimeStamp - time stamp in the format YYYY_MM_DD_HH:MM:SS
Usage:
ipython plotDipolePower.py /path/to/BANK/FITS/files fileTimeStamp
Example:
ipython plotDipolePower.py /lusture/projects/flag/AGBT16B_400_14/BF/ 2017_08_06_15:42:48
__author__ = "Nick Pingel"
__version__ = "1.0"
__email__ = "Nickolas.Pingel@anu.edu.au
__status__ = "produdction"
"""

## imports
from astropy.io import fits
import glob
import numpy as np 
import sys
import os
import matplotlib.patches as mpatches
import matplotlib.pyplot as pyplot
import matplotlib
from matplotlib.ticker import FormatStrFormatter
## plot parameters
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 12}
matplotlib.rc('font', **font)
matplotlib.rc('font', family='sans-serif')
matplotlib.rc('font', serif='Helvetica Neue')
matplotlib.rc('text', usetex='false')
matplotlib.rcParams.update({'font.size': 12})

# These are the "Tableau 20" colors as RGB.
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(tableau20)):
    r, g, b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)

## define dictionary to map vector indices to element/pol (key:value) = (Element_Pol:index). 
elemMapDict = {'1_X':0, '1_Y': 260, '2_X':3, '2_Y': 263, '3_X': 8, '3_Y': 308, '4_X': 11, '4_Y': 311,
'5_X': 20, '5_Y': 360, '6_X': 23, '6_Y': 363, '7_X': 36, '7_Y': 416, '8_X': 39, '8_Y': 419, '9_X': 56, '9_Y': 476,
'10_X': 59, '10_Y': 479, '11_X': 80, '11_Y': 540, '12_X': 83, '12_Y': 543, '13_X': 108, '13_Y': 608, '14_X': 111, '14_Y': 611,
'15_X': 140, '15_Y': 680, '16_X': 143, '16_Y': 683, '17_X': 176, '17_Y': 756, '18_X': 179, '18_Y': 759, '19_X': 216, '19_Y': 836} 

##progress bar function
def progressBar(value, endvalue,bar_length=20):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent of FITS files processed: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

dataDir = '/lustre/flag/'
path = sys.argv[1]
fileTimeStamp = sys.argv[2] ## file time stamp

## make data path
#dataPath = dataDir + path + '/BF/'
dataPath = '/users/npingel/'

## ERROR HANDLING
## test the validity of the user provided data path
if not os.path.exists(dataPath):
	print('Path to data directory is not valid. Exiting...')
	sys.exit(1)
## test fileTimeStamp format 
if not (fileTimeStamp[13] == ':') and (fileTimeStamp[16] == ':'):
	print('Time stamp is wrong format. It should be YYYY_MM_DD_HH:MM:SS')
	sys.exit(1)

## read in each FITS file
fitsList = glob.glob(dataPath+fileTimeStamp+'*.fits')

## if fitsList is empty, the provided time stamp is wrong
if len(fitsList) == 0:
	print('No files with provided timestamp found. Exiting...')
	sys.exit(1)

chanNum = 2112 ## number of raw correlations per channel
# read in each file, and extract power from each dipole (both XX and YY polarizations)
for i in range(0,len(fitsList)):
	hdu = fits.open(fitsList[i])
	data = hdu[1].data['DATA']
	if data.shape[0] == 0:
		continue
	## if this is first FITS file, get required header information
	if i == 0 :
		## get number of integrations
		numInt = len(data[:,0])
		## determine scan length from integration time
		intTime = np.float(hdu[0].header['REQSTI'])
		totTime = numInt*intTime

		##loop over integrations 
		timeAxis = np.linspace(0, np.int(totTime), num = numInt)
		"""
		create dictionary of data containers for "continuum data" of each element and each XX/YY polarization
		first 19 entries correspond to diploes 1-19 (XX pol); second 19 entries correspond to dipoes 1-19(YY pol)
		"""
		dataDict = {}
		for idx in range(0,38):
			dataDict[idx] = np.zeros([numInt])
	
	## loop to get power from individual elements/polarizations
	for j in range(0, 19): 
		##temporary array to hold data
		arrX = np.zeros([numInt])
		arrY = np.zeros([numInt])
		## corresponding elem/pol (see description of dataDict above)
		keyX = np.str(j+1)+'_X'
		keyY = np.str(j+1)+'_Y'
		## elem/pol index from dictionary
		elemIdxX = elemMapDict[keyX]
		elemIdxY = elemMapDict[keyY]
		## loop over integrations to get total power
		for z in range(0, numInt): 
			arrX[z] += np.sum(np.real(data[z,elemIdxX::2112]))
			arrY[z] += np.sum(np.real(data[z,elemIdxY::2112]))
		dataDict[j] += arrX
		dataDict[j+19] += arrY

	##update progress bar
	progressBar(i+1,len(fitsList))

## update user that we are about to plot
print '\n'
print 'Plotting...'
##Normalize data
for idx in range(0,38):
	dataDict[idx] = dataDict[idx]/np.max(dataDict[idx])

##determine time tick marks
major_ticks = np.linspace(0, totTime, num = 5)

##TODO create multi-panel plot
##update plot window
f, ((ax1,ax2, ax3, ax4), (ax5, ax6, ax7, ax8), (ax9, ax10, ax11, ax12), (ax13,ax14, ax15,ax16), (ax17,ax18, ax19, ax20)) = pyplot.subplots(nrows = 5, ncols = 4, sharex='col', figsize=(12,12))
f.suptitle('Normalized Power (' + fileTimeStamp + ')', fontsize=20)
## first element
dataX = dataDict[0]
dataY = dataDict[19]
ax1.set_ylabel('Normalized Power')
ax1.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax1.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax1.text(.9,.9,'1', horizontalalignment='right', verticalalignment='top',transform=ax1.transAxes, color='red')
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax1.set_ylabel('Normalized Power')

## second element
dataX = dataDict[1]
dataY = dataDict[20]
ax2.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax2.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax2.text(.9,.9,'2', horizontalalignment='right', verticalalignment='top',transform=ax2.transAxes, color='red')
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## third element
dataX = dataDict[2]
dataY = dataDict[21]
ax3.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax3.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax3.text(.9,.9,'3', horizontalalignment='right', verticalalignment='top',transform=ax3.transAxes, color='red')
ax3.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## fourth element
dataX = dataDict[3]
dataY = dataDict[22]
ax4.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax4.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax4.text(.9,.9,'4', horizontalalignment='right', verticalalignment='top',transform=ax4.transAxes, color='red')
ax4.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## fifth element
dataX = dataDict[4]
dataY = dataDict[23]
ax5.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax5.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax5.set_ylabel('Normalized Power')
ax5.text(.9,.9,'5', horizontalalignment='right', verticalalignment='top',transform=ax5.transAxes, color='red')
ax5.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## sixth element
dataX = dataDict[5]
dataY = dataDict[24]
ax6.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax6.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax6.text(.9,.9,'6', horizontalalignment='right', verticalalignment='top',transform=ax6.transAxes, color='red')
ax6.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## seventh element
dataX = dataDict[6]
dataY = dataDict[25]
ax7.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax7.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax7.text(.9,.9,'7', horizontalalignment='right', verticalalignment='top',transform=ax7.transAxes, color='red')
ax7.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## eigth element
dataX = dataDict[7]
dataY = dataDict[26]
ax8.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax8.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax8.text(.9,.9,'8', horizontalalignment='right', verticalalignment='top',transform=ax8.transAxes, color='red')
ax8.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## ninth element
dataX = dataDict[8]
dataY = dataDict[27]
ax9.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax9.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax9.set_ylabel('Normalized Power')
ax9.text(.9,.9,'9', horizontalalignment='right', verticalalignment='top',transform=ax9.transAxes, color='red')
ax9.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## tenth element
dataX = dataDict[9]
dataY = dataDict[28]
ax10.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax10.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax10.text(.9,.9,'10', horizontalalignment='right', verticalalignment='top',transform=ax10.transAxes, color='red')
ax10.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## eleventh element
dataX = dataDict[10]
dataY = dataDict[29]
ax11.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax11.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax11.text(.9,.9,'11', horizontalalignment='right', verticalalignment='top',transform=ax11.transAxes, color='red')
ax11.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## twelveth element
dataX = dataDict[11]
dataY = dataDict[30]
ax12.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax12.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax12.text(.9,.9,'12', horizontalalignment='right', verticalalignment='top',transform=ax12.transAxes, color='red')
ax12.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## thirteenth element
dataX = dataDict[12]
dataY = dataDict[31]
ax13.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax13.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax13.set_ylabel('Normalized Power')
ax13.text(.9,.9,'13', horizontalalignment='right', verticalalignment='top',transform=ax13.transAxes, color='red')
ax13.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## fourteenth element
dataX = dataDict[13]
dataY = dataDict[32]
ax14.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax14.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax14.text(.9,.9,'14', horizontalalignment='right', verticalalignment='top',transform=ax14.transAxes, color='red')
ax14.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## fifteenth element
dataX = dataDict[14]
dataY = dataDict[33]
ax15.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax15.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax15.text(.9,.9,'15', horizontalalignment='right', verticalalignment='top',transform=ax15.transAxes, color='red')
ax15.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## sixteenth element
dataX = dataDict[15]
dataY = dataDict[34]
ax16.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax16.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax16.text(.9,.9,'16', horizontalalignment='right', verticalalignment='top',transform=ax16.transAxes, color='red')
ax16.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## seventeenth element
dataX = dataDict[16]
dataY = dataDict[35]
ax17.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax17.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax17.set_ylabel('Normalized Power')
ax17.set_xlabel('Scan Time [sec]')
ax17.text(.9,.9,'17', horizontalalignment='right', verticalalignment='top',transform=ax17.transAxes, color='red')
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## eighteen element
dataX = dataDict[17]
dataY = dataDict[36]
ax18.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax18.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax18.set_xlabel('Scan Time [sec]')
ax18.text(.9,.9,'18', horizontalalignment='right', verticalalignment='top',transform=ax18.transAxes, color='red')
ax18.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## nineteenth element
dataX = dataDict[18]
dataY = dataDict[37]
ax19.plot(timeAxis[5:], dataX[5:], linewidth=2, color = tableau20[2])
ax19.plot(timeAxis[5:], dataY[5:], linewidth=2, color = tableau20[0])
ax19.set_xlabel('Scan Time [sec]')
ax19.text(.9,.9,'19', horizontalalignment='right', verticalalignment='top',transform=ax19.transAxes, color='red')
ax19.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

## put in labels for pols
blue_patch = mpatches.Patch(color = tableau20[2], label='XX-Pol')
green_patch = mpatches.Patch(color = tableau20[0], label='YY-Pol')
ax20.legend((blue_patch,green_patch), ('XX-Pol', 'YY-Pol'))
ax20.set_xlabel('Scan Time [sec]')

#pyplot.savefig('Example.png')
pyplot.show()
