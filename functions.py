import lcdata
import matplotlib.pyplot as plt
import xrb
import kepdump
import numpy as np
import os
import re
from PIL import Image


def plot_lc(folder):
    l = lcdata.load(folder + '/h3.lc')

    plt.plot(l.time, l.xlum)
    plt.ylim(-0.5e38, 1e39)
    #plt.plot(l_adelle.time, l_adelle.xlum)

    plt.savefig(folder +"/light_curve.png")
    plt.show()


def replace_gen(gen_file, newh1, newhe4, newn14, newaccrate, b_heat, nstop, increment, diff_met=False, newC12=None, newO15=None):
    with open(gen_file, 'r') as file:
        lines = file.readlines()
    line = lines[81].split()
    line[2] = str(newh1)
    line[4] = str(newhe4)
    line[6] = str(newn14)
    if diff_met == True:
        line[9] = 'c12'
        line[8] = str(newC12)
        line[11] = 'o15'
        line[10] = str(newO15)
    lines[81] = ' '.join(line) + '\n'
    line2 = lines[157].split()
    line2[2] = str(increment)
    lines[157] = ' '.join(line2) + '\n'
    line3 = lines[873].split()
    line3[2] = str(newaccrate)
    lines[873] = ' '.join(line3) + '\n'
    line4 = lines[717].split()
    line4[2] = str(nstop)
    lines[717] = ' '.join(line4) + '\n'
    line5 = lines[867].split()
    line5[2] = str(b_heat)
    lines[867] = ' '.join(line5) + '\n'
    line6 = lines[885].split()
    line6[2] = str(nstop)
    lines[885] = ' '.join(line6) + '\n'
    with open(gen_file, 'w') as file:
        file.writelines(lines)
    
def replace_burn(burn_file, newh1, newhe4, newn14, diff_met=False, newC12=None, newO15=None):
    with open(burn_file, 'r') as file:
        lines = file.readlines()
    line = lines[28].split()
    line[2] = str(newh1)
    line[4] = str(newhe4)
    line[6] = str(newn14)
    if diff_met == True:
        line[9] = 'c12'
        line[8] = str(newC12)
        line[11] = 'o15'
        line[10] = str(newO15)
    lines[28] = ' '.join(line) + '\n'
    with open(burn_file, 'w') as file:
        file.writelines(lines)

def card_update(folder, newh1, newhe4, newn14, newaccrate, b_heat,nstop, increment,diff_met=False, newC12=None, newO15=None):
    gen_file = folder + '/h3g'
    burn_file = folder + '/rpabg'
    replace_gen(gen_file, newh1, newhe4, newn14, newaccrate, b_heat, nstop, increment,diff_met=False, newC12=None, newO15=None)
    replace_burn(burn_file, newh1, newhe4, newn14,diff_met=False, newC12=None, newO15=None)


def list_files_with_prefix(directory, prefix):
    files = os.listdir(directory)
    filtered_files = [file for file in files if file.startswith(prefix)]
    # Extract the number following the prefix for sorting
    def extract_number(file_name):
        match = re.match(rf'{re.escape(prefix)}(\d+)', file_name)
        return int(match.group(1)) if match else float('inf')
    
    # Sort the files based on the extracted number
    filtered_files.sort(key=extract_number)
    
    return filtered_files

def all_dumps(dump_folder):
    list1 = list_files_with_prefix(dump_folder, 'h3#')
    print('sorted')
    dumps = []

    for item in list1:
        dumps.append(dump_folder + '/' + item)
        # if i%100==0:
        #     print('listing dumps')

    return dumps

def obtain_dumps(lc_path, dump_folder, ignore:bool, dump_gap):
    # read in light curve data:
    lc = lcdata.load(lc_path)
    dumps = all_dumps(dump_folder)
    #print('done listing')
    # locate start of burst from temperature threshold:    
    threshold = 10**(37)
    # lc = lcdata.load(lc_path)    
    dumptime = []
    for item2 in dumps:
        dump = kepdump.load(item2)
        dumptime.append(dump.time)
    dumptime = np.array(dumptime)    
    print('before threshold check')
    thresh_index = np.array(np.where(lc.xlum > threshold)[0])
    print('after threshold check')
    filler = np.array([0,1,2,3,4,5])
    thresh_time = np.append(filler,lc.time[thresh_index])
    threshdt = np.diff(thresh_time)
    burst_iend = np.array(np.where(threshdt > 50)[0])
 
    burst_time_end = thresh_time[burst_iend+1] + 600
    burst_time_start = thresh_time[burst_iend+1] - 150
    # This step excludes first and last burst
    if ignore==True:
        burst_time_end = burst_time_end[1:-1]
        burst_time_start = burst_time_start[1:-1]    
    
    
    # Find dump number and time of dump closest to identified burst times using np.searchsorted:
    print('before search')
    dump_indexs = np.searchsorted(dumptime,burst_time_start)
    dump_indexe = np.searchsorted(dumptime,burst_time_end)   
    print('after search')

   
    burst_dumps = []    
    burst_dumpst_index = dump_indexs * dump_gap
    burst_dumpse_index = dump_indexe * dump_gap
    print(burst_time_start)
    print(burst_time_end)
    print(burst_dumpst_index)
    print(burst_dumpse_index)
    #     f = plt.figure()
    #     plt.plot(lc.time,(lc.xlum), color='black')
    #     for i in burst_time_start:
    #         plt.axvline(i, color='cyan')
    #     for i in burst_time_end:
    #         plt.axvline(i, color='magenta')
    #     for i in dump_indexs:
    #         plt.axvline(dumptime[i-1],color='grey')
    #     plt.xlabel('time (s)')
    #     plt.ylabel('xlum')
    #     plt.savefig('burst_dumps_lc_{}.pdf'.format(output_name))
    #     plt.close('f') 
    lc_index_s = []
    lc_index_e = []   
    # while dump_indexe[-1] == len(dumptime):
    #     dump_ind = []    
    #     print('done)')
    for i in range(0,len(dump_indexs)):        
        for h in range(len(lc.time)):            
            # print((h,i))
            # print(len(dumptime))
            # print(dump_indexe[i])
            if lc.time[h] == dumptime[dump_indexs[i]]:                
                lc_index_s.append(h+1)            
            if lc.time[h] == dumptime[dump_indexe[i]]:                
                lc_index_e.append(h+1)
    print('obtained')
    return lc_index_s,lc_index_e

def index_to_time(outList,dump_folder):
    start_list = outList[0]
    end_list = outList[1]
    start_time = []
    end_time = []
    for item in start_list:
        dumpname = dump_folder + '/' + f'h3#{item}'
        dump = kepdump.load(dumpname)
        time = dump.time
        start_time.append(time)
    for item in end_list:
        dumpname = dump_folder + '/' + f'h3#{item}'
        dump = kepdump.load(dumpname)
        time2 = dump.time
        end_time.append(time2)
    return np.array(start_time),np.array(end_time)

def round_to_nearest_multiple(value, multiple):
    return round(value / multiple) * multiple

def flat_indices(dumpList,dump_gap):
    startList = dumpList[0]
    endList = dumpList[1]
    flatList = []
    print(startList)
    print(endList)
    for i in range(1,len(startList)):
        flat_start = endList[i-1]
        flat_end = startList[i]
        flat_index = (flat_start + flat_end)/2
        flat_index = round_to_nearest_multiple(flat_index,dump_gap)
        flatList.append(flat_index)
    print(flatList)
    return flatList

def create_subplots(dump_folder, dump_gap):
    dumpList = obtain_dumps(dump_folder+'/h3.lc',dump_folder, True, dump_gap)
    
    if len(dumpList[0]) < 6:
        short = True
    else:
        short = False
    if short == False:
        flat_list = flat_indices(dumpList,dump_gap)
        for dumpnum in flat_list:
            abu_plot(dumpnum,dump_folder)
    else:
        dumps = all_dumps(dump_folder)
        num = len(dumps)
        i = 0
        for i in range(0,num):
            if i%(np.round(num/30))==0:
                abu_plot(dumps[i], dump_folder)
            i += 1

def abu_plot(dumpnum, dump_folder):
    if type(dumpnum) != int:
        filename = os.path.basename(dumpnum)
        # Extract just the numbers from the filename
        numbers = re.findall(r'\d+', filename)
        # Join the list of numbers into a single string
        dumpnum = ''.join(numbers)
    dumpname = 'h3#'+str(dumpnum)
    dump = kepdump.load(dump_folder + '/' + dumpname)
    ions = []
    for item in dump.abub.ions:
        ions.append(str(item))
    ions = np.array(ions)
    y = dump.y
    y = np.nan_to_num(y)
    abus = dump.abub.X.T
    index_c12 = int(np.where(ions == 'C12')[0][0])
    index_H1 = int(np.where(ions == 'H1')[0][0])
    index_He4 = int(np.where(ions == 'He4')[0][0])
    iso_list = ['C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'N11', 'N12', 'N13','N14', 'N15', 'N16', 'N17', 'N18','N19','N20','O13','O14','O15','O16','O17','O18','O19','O20','O21']
    abu_CNO = np.zeros(np.shape(abus[index_c12]))
    for iso in iso_list:
        if iso in ions:
            index = int(np.where(ions == iso)[0][0])
            abu_CNO = abu_CNO + np.nan_to_num(abus[index])
    abu_C12 = abus[index_c12]
    abu_H1 = abus[index_H1]
    abu_He4 = abus[index_He4]
    plt.figure(figsize=(10,8))
    plt.suptitle(f'Dump: {dumpnum}')
    plt.subplot(2,1,1)
    temps = dump.tn
    plt.plot(y,temps,label='T', color = 'black', linestyle = '-')
    plt.ylabel('Temperature (K)')
    plt.xscale('log')
    plt.yscale('log')
    plt.subplot(2,1,2)
    plt.plot(y,abu_CNO,linestyle = ':',label='CNO', color = 'green')
    plt.plot(y,abu_H1,linestyle = '-',label='H1', color = 'black')
    plt.plot(y,abu_C12,linestyle = '-.',label='C12', color = 'red')
    plt.plot(y,abu_He4,linestyle = '--',label='He4', color = 'blue')
    plt.xlabel(r'Column depth (g cm$^{-2}$)')
    plt.ylabel('Mass fraction ')
    plt.yscale('log')
    plt.xscale('log')
    plt.ylim(1e-10,1)
    plt.legend()
    #plt.show()

    plt.savefig(dump_folder+ f'/images/subplots/{dumpnum}')
    plt.close()


def plot(dumpname,dump_folder):
    dump:kepdump = kepdump.load(dump_folder + '/' + dumpname)
    labels = dump.abub.ions
    old_labels = dump.ions
    offset = 1
    depths = dump.y + offset
    depths = np.array(depths)  # Assuming depth_values is your array of depth values
    cell_arr = []
    for i in range(0,len(depths)):
        cell_arr.append(i)
    cell_arr = np.array(cell_arr)
    offset = 1e-10
    ions = []
    for item in dump.abub.ions:
        ions.append(str(item))
    ions = np.array(ions)
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(np.log10(depths), ions, np.log10((dump.abub.X).T+offset), cmap='plasma', vmin=-12)
    plt.ylim(0,80)
    plt.colorbar(label='Abundance')
    plt.xlabel('log10(depth)')
    plt.ylabel('Mass Number')
    plt.title('Abundance Heatmap')

    # Show plot
    #plt.show()

    plt.savefig(dump_folder + '/images/' + dumpname)


def extend_list(list):
    startList = list[0]
    endList = list[1]
    fullList = np.sort(np.append(startList,endList))
    print('extended')
    return fullList

def create_plots(index_list, dump_folder):
    nameList = []
    print(nameList)
    for item in index_list:
        nameList.append(f'h3#{item}')
    for item2 in nameList:
        plot(item2, dump_folder)
    

import os
from PIL import Image

def create_gif_from_images(folder_path, output_filename='output.gif', duration=750):
    # Get all image files from the folder, assuming they are sorted by name
    images = [img for img in os.listdir(folder_path) if img.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    images.sort()  # Sort images by filename

    # Load images
    frames = [Image.open(os.path.join(folder_path, img)) for img in images]

    # Save as GIF
    if frames:
        output_path = os.path.join(folder_path, output_filename)
        frames[0].save(output_path, format='GIF', append_images=frames[1:], save_all=True, duration=duration, loop=0)
        print(f"GIF saved as {output_path}")
    else:
        print("No images found in the folder.")

# Example usage
#create_plots(extend_list(obtain_dumps('h_0/acc_0.3/h3.lc','h_0/acc_0.3')),'h_0/acc_0.3')

# folder_path = 'h_0/acc_0.15/images'  # Replace with your folder path
# create_gif_from_images(folder_path)

# plot_lc('h_0.73/acc_0.15/h3.lc')

# print(dumpList)
# startList = dumpList[0]
# endList = dumpList[1]
# print(dumpList)
# carbon_abu(extend_list(dumpList),0,0.15, True)

    

#print(len(index_to_time(obtain_dumps('h.lc', 68733)))/2)
#plot_lc('Q_0.3/h_0.05/acc_0.075')
#abu_plot('66000','Q_0.3/h_0.05/acc_0.075')
card_update('Q_0.1/h_0/CNO_0.01_each/acc_0.11', 0.0, 0.97, 0.01, 0.11, 0.1, 150000, 10, True, 0.01, 0.01)
#obtain_dumps('h_0.73/acc_0.15/h3.lc','h_0.73/acc_0.15')
#print(index_to_time(obtain_dumps('h_0.73/acc_0.15/h3.lc','h_0.73/acc_0.15'), 'h_0.73/acc_0.15'))
#create_plots(extend_list(obtain_dumps('Q_0.3/h_0.05/acc_0.075/h3.lc','Q_0.3/h_0.05/acc_0.075', True, 10)),'Q_0.3/h_0.05/acc_0.075')
#create_gif_from_images('Q_0.3/h_0.05/acc_0.075/images')

#create_subplots('Q_0.3/h_0.05/acc_0.075', 10)
#create_gif_from_images('Q_0.3/h_0.05/acc_0.075/images/subplots')
