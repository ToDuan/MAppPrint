# MAppPrint_CCS2026_Submission



Datasets and code implementation for paper:  ''MAppPrint: Fast and Robust Mobile App Fingerprinting via Traffic Behavior Causal Graphs''.

This repository contains:

- (1) **Code of MAppPrint** (in folder `./MAppPrint`);
- (2) **Code of Mobile App Traffic Triggering and Labeling System** (in folder `./AndroidTrafficSniff`);
- (3) **Public and Self-collected Datasets** (in folder `./Datasets`).



# Environment Setup

python==3.8.0

torch==1.11.0+cu113
torchvision==0.12.0+cu113
torchsummary==1.5.1
torchaudio==0.11.0

dgl-cu113==0.9.1.post1
numpy==1.24.4
pandas==2.0.3
scikit-learn==1.3.2

**You can directly clone the conda environment using the `MAppPrint_conda_env.yml' file:**

conda env create -f MAppPrint_conda_env.yml

# Toy Example

https://drive.google.com/drive/folders/1wvZwYn3XJOlc0WfeINMJsCVwIUfr-_8f?usp=drive_link

run: nohup sh train.sh > /dev/null 2>&1

You can obtain the results of MAppPrint on the SIM-APP dataset with a 5-second time window


# Use MAppPrint/MAppPrint-MC

#### 1. TBCG Construction

###### Traffic Trace pre-processing: 

- Parse the pcap traffic traces, extract per-packet features, and convert them into CSV files.

  -- run: `./MAppPrint/tbcg_construction/pcap2csv.py`

- Segment the traffic traces into samples based on the specified time window size (i.e., 5s, 10s, 20s, 30s, or 60s).

  -- run: `./MAppPrint/tbcg_construction/traces_segment.py`

- Split the training and testing datasets.

  -- run:  `./MAppPrint/tbcg_construction/datasets_split.py`

###### Construct a Traffic Behavior Causal Graph (TBCG): Transform each traffic trace into a TBCG.

-- run: `./MAppPrint/tbcg_construction/graph_construction.py`

#### 2. TBCG Compression

###### Anchor Nodes Mining: Extract high-frequency unit traffic behaviors from the training set as anchor nodes.

-- run: `./MAppPrint/tbcg_compression/anchors_mining.py`

###### TCBG Compression: Compare the similarity between TCBG nodes and anchor nodes, and aggregate similar nodes.

-- run: `./MAppPrint/tbcg_compression/graph_compress.py`

#### 3. Mobile App Identification

###### MAppPrint:

- Single-/Multi-App Running Modes Differentiation

  --run: `./App_RunModel_different.py`

- Multi-App TBCG Separation  

  --run: `./multiapp_separate.py`

- App idetification

  --run: `./singleApp_Classifier_train.py`


