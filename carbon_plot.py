import kepdump
import numpy as np
import os
import re
import matplotlib.pyplot as plt
from functions import obtain_dumps
from functions import extend_list
from functions import all_dumps
from functions import index_to_time
import time
from functions import create_subplots

# def iso_frac(isotope:str, dump:kepdump):
#     ions = []
#     for item in dump.abub.ions:
#         ions.append(str(item))
#     ions = np.array(ions)
#     mass = dump.xm
    
#     index_iso = int(np.where(ions == isotope)[0][0])
#     total_mass = 0
#     abu_arr = (dump.abub.X).T[index_iso]
#     abu_arr = np.nan_to_num(abu_arr, nan=0.0)
   
#     iso_mass = np.sum([abu_arr[i]*mass[i] for i in range(0,len(mass))])
#     for i in range(0,np.shape(dump.abub.X.T)[0]):
#         abu_arr2 = dump.abub.X.T[i]
#         abu_arr2 = np.nan_to_num(abu_arr2, nan=0.0)
#         for ii in range(0,len(abu_arr2)):
#             total_mass += abu_arr2[ii] * mass[ii]
#     frac_abu = iso_mass/total_mass
#     return frac_abu

def iso_frac(isotope: str, dump: kepdump):
    # Convert ion names to a NumPy array
    ions = np.array([str(item) for item in dump.abub.ions])
    
    # Get the index of the isotope
    index_iso = np.where(ions == isotope)[0][0]
    
    # Mass and abundance arrays
    mass = np.array(dump.xm)
    abu_data = np.nan_to_num(dump.abub.X, nan=0.0)  # Handle NaNs

    # Isotope mass calculation
    abu_arr = abu_data.T[index_iso]
    iso_mass = np.dot(abu_arr, mass)
    
    # Total mass calculation
    total_mass = np.dot(abu_data.T, mass).sum()
    
    # Calculate the fraction
    frac_abu = iso_mass / total_mass
    return frac_abu


def iso_vs_time(dump_folder,iso_name:str):
    dumps = []
    dList = obtain_dumps(dump_folder+'/h3.lc',dump_folder, True, 10)
    starts = dList[0]
    ends = dList[1]
    dumps = extend_list(dList)
    dList=None
    if len(dumps) < 6:
        short = True
        dumps = all_dumps(dump_folder)
    else:
        short = False
    times = []
    abus = []
    i = 0
    print("Loading dumps:")
    for item in dumps:
        if short == False:
            dump = kepdump.load(dump_folder+f'/h3#{item}')
            times.append(dump.time)
            abu = iso_frac(iso_name, dump)
            print(abu)
            abus.append(abu)
        else:
            num = len(dumps)
            if i%(np.round(num/30))==0:
                dump = kepdump.load(item)
                times.append(dump.time)
                abus.append(iso_frac(iso_name, dump))
            i += 1
    times = np.array(times)
    abus = np.array(abus)
    plt.plot(times,abus)
    plt.xlabel("Time")
    plt.ylabel(f'Fractional abundance of {iso_name}')
    if short == False:
        for dump in starts:
            dump = kepdump.load(dump_folder + f'/h3#{dump}')
            time = dump.time
            plt.axvline(x=int(time), color='g', linestyle='--', linewidth=0.7)
    plt.savefig(dump_folder + f'/images/{iso_name}_fraction.png')
    with open(dump_folder +f'/images/{iso_name}_data.txt', 'w') as f:
        for i in range(0, len(abus)):
            f.write(f"{abus[i]}\n")  # Write each item followed by a newline
    #plt.show()
    plt.close()


def list_subfolders_second_level(directory):
    subfolders = []
    
    # Walk through the directory tree
    for root, dirs, _ in os.walk(directory):
        # Calculate the current depth by comparing root to the original directory
        depth = root[len(directory):].count(os.sep)
        
        # Only include directories at depth 1 (second level)
        if depth == 1:
            for dir_name in dirs:
                subfolders.append(os.path.join(root, dir_name))
    
    return subfolders

#Example usage to list subfolders only at the second level in the current working directory
# current_directory = 'keplerrun/Q_0.1'
# second_level_subfolders = list_subfolders_second_level(current_directory)
# print(second_level_subfolders)
# final_abus = []
# for item in second_level_subfolders:
#     #create_subplots(item, 10)
#     #iso_vs_time(item, 'C12')
#     text_file = item + '/images/C12_data.txt'
#     with open(text_file, 'r') as f:
#         lines = f.readlines()  # Read all lines into a list
    
#     # Extract the last two lines and convert them to integers (or float, if needed)
#     last_two = [float(line.strip()) for line in lines[-2:]]
#     final_abus.append(max(last_two))


# current_directory = 'keplerrun/Q_0.3'
# second_level_subfolders2 = list_subfolders_second_level(current_directory)


# for item in second_level_subfolders2:
#     #create_subplots(item,10)
#     #iso_vs_time(item, 'C12')
#     text_file = item + '/images/C12_data.txt'
#     with open(text_file, 'r') as f:
#         lines = f.readlines()  # Read all lines into a list
    
#     # Extract the last two lines and convert them to integers (or float, if needed)
#     last_two = [float(line.strip()) for line in lines[-2:]]
#     final_abus.append(max(last_two))

#print(second_level_subfolders)
#print(second_level_subfolders2)
#print(final_abus)
# start_time = time.time() 
#iso_vs_time('Q_0.3/h_0.05/acc_0.075', 'C12')
# end_time = time.time()
# #dump = kepdump.load('Q_0.3/h_0.73/acc_0.11/h3#23000')

# #print(iso_frac('H1',dump)) # Replace with your function call

# execution_time1 = end_time - start_time

# print(execution_time1)
# dump = kepdump.load('Q_0.3/h_0/acc_0.25/h3#100000')
# num = np.max(np.nan_to_num(dump.abub.X[-150:-20]))
# index = np.where(dump.abub.X == num)
# print(index)
# ions = []
# for item in dump.abub.ions:
#     ions.append(str(item))
# ions = np.array(ions)
# print(ions[100])
# print(num)
#dump = kepdump.load('Q_0.3/h_0.05/acc_0.075/h3#60000')
#print(iso_frac('C12', dump))