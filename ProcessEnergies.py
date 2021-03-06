import csv
import os
import math
from datetime import datetime
import string
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from scipy.stats import linregress


#creates a list of all the csv files in the directory excluding the template
csvfiles = [os.path.join(root, name) for root, dirs, files in os.walk("./") for name in files if name.endswith((".csv")) and name[-12:] != "template.csv"]


#creates a dictionary associating each file with a list of its data
data = {}
for file in csvfiles:
    data[file] = []
    with open(file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            data[file].append(row[0])
        for i in range(1,7):
            data[file][i] = int(data[file][i])
        for i in range(7,16):
            data[file][i] = float(filter(lambda x: x in string.printable, data[file][i]))


#combines the data into a dictionary keyed with names representing a chart
# with a value as a list of lists of the data for a particular graph
charts = {}
for item in data:
    if data[item][16] not in charts:
        charts[data[item][16]] = [data[item]]
    else:
        charts[data[item][16]].append(data[item])


# processes the data and calculations outputting tuples (pairs) of results to plot
datatoplot = {}
for date in charts:
    datatoplot[date] = []
    #memoize some of the processing
    processed = {}
    def findexpectation(setofdata,processed):
        activity = setofdata[7] * math.e ** (-math.log(2) * time / setofdata[8])
        s = setofdata[11]
        r = setofdata[12]
        solidangle = s ** 2 / (4 * math.pi * r ** 2)
        expec = 37000 * activity * setofdata[10] * setofdata[13] * solidangle
        processed[(time, setofdata[10], setofdata[13], setofdata[11], setofdata[12])] = expec
        return expec

    for setofdata in charts[date]:
        end = datetime(setofdata[4], setofdata[5], setofdata[6])
        start = datetime(setofdata[1], setofdata[2], setofdata[3])
        difference = end - start
        time = (difference.days + difference.seconds / 86400) / 365.2425
        energy = setofdata[9]
        #check memoized data
        if (time, setofdata[10], setofdata[13], setofdata[11], setofdata[12]) in processed:
            expectation = processed[(time, setofdata[10], setofdata[13], setofdata[11], setofdata[12])]
        #in case not already calculated, then calculate
        else:
            expectation = findexpectation(setofdata, processed)
        experimental = setofdata[14]
        efficiency = experimental / expectation
        datatoplot[date].append((energy, efficiency))



#outputs data and graphs onto a pdf
with PdfPages('data.pdf') as pdf:
    plotting = sorted(datatoplot)

    for i in range(len(datatoplot)):
        x = []
        y = []
        for tup in datatoplot[plotting[i]]:
            x.append(tup[0])
            y.append(tup[1])

        # make the scatter plot
        plt.scatter(x, y, s=10, alpha=.5, marker='o')
        # determine best fit line
        par = np.polyfit(x, y, 1, full=True)
        slope=par[0][0]
        intercept=par[0][1]
        xl = [min(x), max(x)]
        yl = [slope*xx + intercept for xx in xl]
        plt.plot(xl, yl, '-r')

        #analyze data
        slope, intercept, rcorrelation, pcorrelation, stderr = linregress(x, y)
        #output y=mx+b and r^2 onto graph pdf
        plt.text(0, .95, "y = " + str(slope) + "x + " + str(intercept) + ", r squared = " + str(rcorrelation))

        #output data points as text (ordered pairs) onto graph
        texts = {}
        for j in range(len(datatoplot[plotting[i]])):
            plt.text(0, .85 - j*.1 , datatoplot[plotting[i]][j])

        #label axes
        plt.xlabel('energy')
        plt.ylabel('efficiency')
        
        #set limits of x and y axes
        plt.ylim([0, 1])
        plt.xlim([0, 1400])

        #plot title
        plt.title(str(plotting[i]))

        pdf.savefig()  # saves the current figure into a pdf page
        plt.close()








