import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


root_path = '../Dataset/Traces_CSV/FOAP'
params = [(5,0)]


# APP Name List
target_app = ['app_a','app_b',...]

sources_folder = root_path

save_dir = '../Datasets/TBCGs/FOAP/5/'

for duration, overlap in params:
  param_folder = os.path.join(save_dir, 'split_chunks','%d_%d'%(duration, overlap))

  if not os.path.exists(param_folder):
    os.mkdir(param_folder)

    samples_folder = os.path.join(param_folder, 'samples')
    os.mkdir(samples_folder)

    for app in target_app:
      print('App: ', app)
      app_sources_folder = os.path.join(sources_folder, app)
      app_samples_folder = os.path.join(samples_folder, app)
      if not os.path.exists(app_samples_folder):
        os.mkdir(app_samples_folder)

      for filename in os.listdir(app_sources_folder):
        if '.csv' not in filename:continue
        print('Processing %s ...' % filename)
        index = 1

        file_path = os.path.join(app_sources_folder, filename)
        df = pd.read_csv(file_path, index_col=0)
        if df.shape[0]<50:
            print("Empty Pcap File...")
            continue
        base = df['time'].iloc[0]
        end = df['time'].iloc[-1]
      
        while ((index - 1)*(duration - overlap) + duration) + base < end:
          start_time = base + (index-1)*(duration - overlap)
          end_time = start_time + duration
          df_ = df[(df['time'] >= start_time) & (df['time'] <= end_time)].reset_index(drop=True) # each time window

          #FOAPData:
          sample_filename = filename.split('.csv')[0] + '_' + str(index) + '.csv'

          sample_path = os.path.join(app_samples_folder, sample_filename)
          df_.to_csv(sample_path, index=True)

          index += 1
    
      print('...................................................')

