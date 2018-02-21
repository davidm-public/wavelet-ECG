
# coding: utf-8

# In[1]:


import pyedflib
import numpy as np

from scipy import signal
import matplotlib.pyplot as plt
import csv
import pandas as pd
import itertools as iter


# In[2]:


#read dataset
csv_file = 'mros-visit1-dataset-0.3.0.csv'
df = pd.read_csv(csv_file, dtype={"nsrrid": str, "poordi4": int}, low_memory=False)
AHI = df[['nsrrid', 'poordi4']] #select only two columns

#select only 50 patients from each group (normal/abnormal)
n_data = 100
group1 = AHI[AHI.poordi4 < 5][0:n_data/2] #group1 : normal
group1['class'] = 0
group2 = AHI[AHI.poordi4 >= 30][0:n_data/2] #group2 : OSA patient
group2['class'] = 1
all_data = pd.concat([group1, group2])


# In[ ]:


## get ECGs ##

#set params
sampling_rate = 512 #number of samplings per second
second_hour_start = sampling_rate * 60 * 60
fifth_hour_end = sampling_rate * 60 * 60 * 5
length = fifth_hour_end-second_hour_start
ECGs = np.zeros(shape=(n_data, length))

for i, it in enumerate(iter.izip(all_data['nsrrid'], all_data['class'])):
    try:
        print 'round', i
        f_name = "../mros/polysomnography/edfs/visit1/mros-visit1-" + it[0].lower() + ".edf"
        f = pyedflib.EdfReader(f_name)

        '''
        #Uncomment to see shape of data
        if i == 0:
            n = f.signals_in_file
            signal_labels = f.getSignalLabels()
            print "This file includes", n, "signals :"
            print "(list of signal : number of samples in each channel)"
            for i, s in enumerate(signal_labels):
                print '\t', s, ':', f.getNSamples()[i]
        '''

        #select only ECG
        ecg_L = f.readSignal(9)

        #select only data from 2nd to 5th hours
        ecg_L_4hrs = ecg_L[second_hour_start : fifth_hour_end]
  
        '''
        #filter by notch digital filter 
        #from https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirnotch.html
        fs = sampling_rate  # Sample frequency (Hz)
        f0 = 60.0  # Frequency to be removed from signal (Hz) => because of the US electrical 
        Q = 30.0  # Quality factor
        w0 = f0/(fs/2)  # Normalized Frequency
        b, a = signal.iirnotch(w0, Q)
        w, h = signal.freqz(b, a)
        freq = w*fs/(2*np.pi)
        print len(w), len(h), len(freq)
        '''
        
        #add all patients' ECGs and class to numpy array
        ECGs[i] = ecg_L_4hrs + it[1]
        
        #write selected period of signal to file
        fw_name = "./ECGs/visit1/mros-visit1-" + it[0].lower() + "-4hours.edf"
        np.save(fw_name, np.array(ecg_L_4hrs))
        print "Select ECG data only from 2nd to 5th hours =", length, "samplings from all", len(ecg_L), "samplings."
    
    except Exception, e:
        print 'FAIL at', f_name, e
    finally:
        f._close()
    
print ECGs.shape


# In[ ]:


f._close()
fw.close()

