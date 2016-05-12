import csv
import os
import math
from datetime import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import string

csvfiles = [os.path.join(root, name) for root, dirs, files in os.walk("./") for name in files if name.endswith((".csv")) and name[-12:] != "template.csv"]


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

charts = {}
for item in data:
    if data[item][16] not in charts:
        charts[data[item][16]] = [data[item]]
    else:
        charts[data[item][16]].append(data[item])

datatoplot = {}
for date in charts:
    datatoplot[date] = []
    for setofdata in charts[date]:
        energy = setofdata[9]
        end = datetime(setofdata[4], setofdata[5], setofdata[6])
        start = datetime(setofdata[1], setofdata[2], setofdata[3])
        difference = end - start
        time = (difference.days + difference.seconds/86400)/365.2425
        activity = setofdata[7]*math.e**(-math.log(2)*time/setofdata[8])
        s = setofdata[11]
        r = setofdata[12]
        solidangle = s**2 / (4 * math.pi * r**2)
        expectation = 37000 * activity * setofdata[10] * setofdata[13] * solidangle
        experimental = setofdata[14]
        efficiency = experimental / expectation
        datatoplot[date].append((energy, efficiency))

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

        plt.title(str(plotting[i]))
        pdf.savefig()  # saves the current figure into a pdf page
        plt.close()










