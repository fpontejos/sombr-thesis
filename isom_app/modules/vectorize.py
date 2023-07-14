import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder
from sentence_transformers import SentenceTransformer

from nltk.tokenize import word_tokenize

import os
import re
from constants import *

##################################################################
## Load data
##################################################################


def db_to_df(dbpath = None, 
                  query=BR_QUERY
                  ):

    """
    Loads sqlite db into a df
    """

    if dbpath == None:
        _br_csv = os.path.join(ROOT_PATH, os.path.join('internal', 'data', '_processed', 'spark-bugreports.csv'))
        return pd.read_csv(_br_csv)
    else:
        con = sqlite3.connect(dbpath)
        cur = con.cursor()
        df = pd.read_sql_query(query, con)
        return df


def filter_br(df, 
              keep_status=KEEP_STATUS, 
              keep_resolution=KEEP_RESOLUTION,
              keep_type=KEEP_TYPE,
              prevent_nan=PREVENT_NAN
             ):
    
    df_star = df.copy()

    df_star.sort_values(by='resolved_date', inplace=True)
        
    df_star['isbug']          = df_star.apply(lambda row: (1 if (row['type'] in keep_type) else 0), axis=1 )
    df_star['statusdone']     = df_star.apply(lambda row: (1 if (row['status'] in keep_status) else 0), axis=1 )
    df_star['resolutiondone'] = df_star.apply(lambda row: (1 if (row['resolution'] in keep_resolution) else 0), axis=1 )
    df_star['hasassigned']    = (~df_star['assignee_username'].isna()).astype(int)
    
    df_filt = df_star[(df_star['isbug']==1) & 
            (df_star['statusdone']==1) &
            (df_star['resolutiondone']==1) & 
            (df_star['hasassigned']==1)
            ]
    
    df_trunc = df_filt.copy()
    df_trunc['summary_original'] = df_trunc['summary'].copy()
    df_trunc['summary'] = df_trunc['summary'].apply(lambda x: baseline_prep(x))
    df_trunc.replace('',np.nan, inplace=True)
    
    for p in prevent_nan:
        df_trunc = df_trunc.loc[~df[p].isna()]

    df_trunc = df_trunc.loc[:,KEEP_ISSUE_COLS+['summary_original']]
    
    df_trunc.reset_index(inplace=True)
    
    return df_trunc


##################################################################
## Vectorize text
##################################################################


def get_transformer(modelname='all-MiniLM-L6-v2'):
    """
    Use pre-downloaded model if it exists, 
    otherwise download this model and save it locally.
    """
    #models_path# = './../isom_app/internal/models/{}/'.format(modelname)
    models_path = os.path.join(ROOT_PATH, os.path.join('internal', 'models', modelname))
    
    if os.path.exists(models_path):
        print('Using pre-loaded model:', modelname)
        return SentenceTransformer(models_path)
    else:
        print('Downloading transformer model', modelname)
        transformer = SentenceTransformer(modelname)
        transformer.save(models_path)
        return transformer

def get_vector_values(encoder, d):
    """
    Returns the vectors of 
    @param d (data) using 
    @param encoder 
    example use:
    get_embedding_values(transformer.encode, df['summary'])
    """
    
    return encoder(d)

def get_vector_df(vec, df, cols):
    """
    Returns a df combining the vector values 
    with metadata attributes from df[cols] appended; 
    
    
    sample use:
    
    get_embedding_df(sbert_embeddings, # embedding vectors
                    df,                # df containing original data
                    ['assignee_username', 'resolution', 'issue_id', 'summary'], # columns in df to copy
                    )
    """
    e_df = pd.DataFrame(vec, index=df.index)
    
    
    ## copy additional attributes from original data to embedding df
    for c in cols:
        e_df[c] = df[c]

    return e_df

def prep_labels(df, label_params, rename=False, le=None):

    """
    LabelEncode columns OR rename columns. 
    Can be passed a fitted LabelEncoder, otherwise will be fitted here.
    Returns the modified df and the fitted LE.

    Example input:
    label_params = {
        'label_encode_col':'assignee_username',   # column to use LabelEncoder on
        'label_prefix':'user_',                   # prefix to use for label
        'rename':{'assignee_username': 'target'}  # what to rename columns if rename=True
    }
    """
    le_ = OrdinalEncoder(handle_unknown='use_encoded_value',
                        unknown_value=-1)
    le_.fit(df[[label_params['label_encode_col']]])
        
    
    if label_params['label_encode_col'] != False:
        labels = None
        if le == None: # unfitted LabelEncoder
            labels = le_.transform(df[[label_params['label_encode_col']]])
            le = le_
        else:
            labels = le.transform(df[[label_params['label_encode_col']]])
            
        df[[label_params['label_encode_col']]] = np.char.mod('{}%d'.format(label_params['label_prefix']), labels)

    if rename == True:
        df = df.rename(columns=label_params['rename'])

    return df, le

##################################################################
## Preprocessing helpers
##################################################################

def remove_digits(t):
    t = re.sub(r'\d+', '', t)
    t = re.sub(' +', ' ', t)
    return t.strip()

def replace_symbols(t):    
    t = ''.join([re.sub(r'[^A-Za-z0-9 ]+',' ',t)])
    t = re.sub(' +', ' ', t)
    return t.strip()

def truncate_sentence(s, l=300):
    ts = " ".join(s.split(" ")[:l])    
    return ts

def baseline_prep(t):
    
    tokens = " ".join(word_tokenize(t))    
    tokens = remove_digits(tokens)
    tokens = replace_symbols(tokens)
    tokens = truncate_sentence(tokens)
    tokens = re.sub(' +', ' ', tokens)
    
    return tokens.strip()

##################################################################
## Vectorize texts
##################################################################

def vectorize_sbert(df, encode_col="summary", cols=[], le=None, lp=None):
    sbert_model = 'all-MiniLM-L6-v2'
    sbert_transformer = get_transformer(sbert_model)

    if len(cols) == 0:
        cols = ['assignee_username', 'resolution', 'issue_id', 'summary', 'summary_original']

    label_params = {
        'label_encode_col':'assignee_username',   # column to use LabelEncoder on
        'label_prefix':'user_',                   # prefix to use for label
        'rename':{'assignee_username': 'target'}  # rename columns
    }

    if lp == None:
        lp = label_params
    
    sbert_vec = sbert_transformer.encode(df['summary'].values)
    sbert_df = get_vector_df(sbert_vec, df, cols)
    sbert_df, spark_le = prep_labels(sbert_df, lp, rename=True, le=le)

    return sbert_vec, sbert_df, spark_le


