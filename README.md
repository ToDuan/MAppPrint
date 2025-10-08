# MAppPrint_WWW26_Submission



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

**You can directly clone the conda environment using the `./MAppPrint_conda_env.yml` file:**

`conda env create -f MAppPrint_conda_env.yml`

# Toy Example

 **Download** processed dataset from https://drive.google.com/drive/folders/1j2l9rYI6_bNES6UTYU4qqIGFL4qEfMuU?usp=sharing to folder `./Datasets/TBCGs/FOAP/5/`, 
and then **Run**: `nohup sh ./MAppPrint/train.sh > /dev/null 2>&1`

You can obtain the following results (i.e., the performance of MAppPrint-MC on the FOAP dataset with a 5-second time window):

<img src="figers/MAppPrintMC_FOAP_5s.png" alt="MAppPrintMC_FOAP_5s" style="zoom: 50%;" />

# Use MAppPrint&MAppPrint-MC

#### 1. TBCG Construction

**Traffic Trace Pre-processing:** 

- Parse the pcap traffic traces, extract per-packet features, and convert them into CSV files.

  -- Run: `./MAppPrint/tbcg_construction/pcap2csv.py`

- Segment the traffic traces into samples based on the specified time window size (i.e., 5s, 10s, 20s, 30s, or 60s).

  -- Run: `./MAppPrint/tbcg_construction/traces_segment.py`

- Split the training and testing datasets.

  -- Run: `./MAppPrint/tbcg_construction/datasets_split.py`

**Construct a Traffic Behavior Causal Graph (TBCG): Transform each traffic trace into a TBCG.**

-- Run: `./MAppPrint/tbcg_construction/graph_construction.py`

#### 2. TBCG Compression

**Anchor Nodes Mining: Extract high-frequency unit traffic behaviors from the training set as anchor nodes.**

-- Run: `./MAppPrint/tbcg_compression/anchors_mining.py`

**TCBG Compression: Compare the similarity between TCBG nodes and anchor nodes, and aggregate similar nodes.**

-- Run: `./MAppPrint/tbcg_compression/graph_compress.py`

#### 3. Mobile App Identification

**Train GNN-based classifier** 

--Run: `./MAppPrint/train.py`

# Notes

The training logs, results, and model parameters are saved in the `./MAppPrint/train_log`, `./MAppPrint/train_result`, and `./MAppPrint/trained_model` folders, respectively.

