import os
import json
import random
import warnings
warnings.filterwarnings('ignore')

params = [(5,0)]
train_size = 0.8

# FOAP
target_app =  ['com.discord', 'com.azure.authenticator', 'com.shopify.arrive', 'com.bamnetworks.mobile.android.gameday.atbat',
        'com.lingodeer','com.snapchat.android', 'com.northghost.touchvpn', 'com.skype.raider', 'ca.crea.app.consumer',
        'com.phenix.cajou', 'com.mobilemedia.tanuki', 'com.yahoo.mobile.client.android.mail', 'com.proan.bestmart360',
        'com.dywx.larkplayer', 'tw.com.youbike.plus', 'com.pratilipi.comics', 'com.lemon.lvoverseas',
        'com.dailywire.thedailywire', 'com.viamichelin.android.viamichelinmobile', 'com.bbc.sounds', 'video.reface.app',
        'org.aastudio.games.longnards', 'com.saramart.android', 'ru.labirint.android']

def get_train_test(filenames, train_size):
  """
  Parameters
  ----------
  filenames : a files name list : ['app1_1.csv','app1_2.csv',...'app1_n.csv']
  train_size

  Returns : two files name list : train_files_name:[...] ; test_files_name:[...]
  -------
  """
  train_idx = random.sample(range(len(filenames)), int(len(filenames)*train_size))  # random
  train_filenames = [filenames[i] for i in train_idx]

  test_filenames = list(set(filenames) - set(train_filenames))

  return (train_filenames, test_filenames)

save_dir = '../Datasets/TBCGs/FOAP/5/'
for duration, overlap in params:
  param_folder = os.path.join(save_dir, 'split_chunks','%d_%d'%(duration, overlap))
  samples_folder = os.path.join(param_folder, 'samples')

  train_test_info = dict()
  for app in target_app:
    app_folder = os.path.join(samples_folder, app)
    filenames = os.listdir(app_folder)
    train_test_info[app] = get_train_test(filenames, train_size)

  # save train_test_info as json file
  saved_path = os.path.join(param_folder, 'train_test_info.json')
  with open(saved_path, 'w') as f:
    json.dump(train_test_info, f)
