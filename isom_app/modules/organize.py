from minisom import MiniSom
import os
import re
import pickle
from constants import *
from modules.vectorize import * 

n_iters = 20000
m = 20 # matrix size num cols
n = 10 # matrix size num rows
p = 0  # number of inputs


def init_som(m=m,n=n,p=p):
    som = MiniSom(m, n, p, 
              sigma=1.5, learning_rate=.7, 
              activation_distance='euclidean',
              topology='hexagonal', 
              neighborhood_function='gaussian', 
              random_seed=RANDOM_STATE
             )

    return som

def train_som(data, 
              m=m, n=n, p=p, 
              n_iters=n_iters):
    som = init_som(m,n,p)
    #som.pca_weights_init(data)
    som.random_weights_init(data)
    som.train_batch(data, n_iters, verbose=True)
    return som

def get_bmu_byrow(data, som):
    bmu_list = []
    p_ = som.get_weights().shape[2]
    mn = som.get_weights().shape[:2]
    

    for row in data:
        wx, wy = som.winner(row)
        bmu_list.append(np.ravel_multi_index((wx,wy), mn ) )
    return pd.Series(bmu_list, name='bmu')

def setup_pretrained():
    vec_path = os.path.join(ROOT_PATH, os.path.relpath(os.path.join('.', 'internal', 'data', '_processed', 'vec_df.csv')))
    pickle_path = os.path.join(ROOT_PATH, os.path.relpath(os.path.join('.', 'internal', 'models', 'som', 'som.p')))

    print(pickle_path)
    with open(pickle_path, 'rb') as infile:
        som = pickle.load(infile)
    
    vec_df = pd.read_csv(vec_path)
    vec_vals = vec_df.iloc[:,:som.get_weights().shape[2]].values

    return vec_vals, vec_df, som 

def setup_new(somparams=DEFAULT_SOMPARAMS, 
                dbpath=None, 
                save_vec_where=None,
                save=False, 
                save_som_where=None,
                vectorizer='sbert'):
    
    df_all = db_to_df(dbpath)
    df = filter_br(df_all)


    #if (vectorizer=='sbert'):
    vec_vals, vec_df, le = vectorize_sbert(df)

    som = train_som(vec_vals, 
                somparams['m'], 
                somparams['n'], 
                vec_vals.shape[1], 
                somparams['n_iters'])
    
    vec_df['bmu'] = get_bmu_byrow(vec_vals, som)

    if save==True:
        save_trained_som(som, save_som_where)

        if save_vec_where == None:
            vec_path = os.path.join(ROOT_PATH, os.path.relpath(os.path.join('.', 'internal', 'data', '_processed', 'vec_df.csv')))
        else:
            vec_path = save_vec_where
        vec_df.to_csv(vec_path, index=False)
    
    return vec_vals, vec_df, som 


def save_trained_som(som, where=None):
    if where==None:
        pickle_path = os.path.join(ROOT_PATH, os.path.relpath(os.path.join('.', 'internal', 'models', 'som', 'som.p')))
    else:
        pickle_path = where
    
        
    with open(pickle_path, 'wb') as outfile:
        pickle.dump(som, outfile)
        print('Pickling SOM to', pickle_path)

    return 

def load_trained_som():

    summary_embeddings_df_path = os.path.join(ROOT_PATH, 
                                 os.path.relpath('internal/data/processed/summary_embeddings_df_bmu.csv'))
                                 #os.path.relpath('..', '..', 'internal', 'data', 'processed', 'summary_embeddings_df_bmu.csv')))
    
    #pickle_path = os.path.join(ROOT_PATH, os.path.relpath('./internal/models/som/som.p'))
    pickle_path = os.path.join(ROOT_PATH, os.path.relpath(os.path.join('.', 'internal', 'models', 'som', 'som.p')))


    with open(pickle_path, 'rb') as infile:
        som = pickle.load(infile)

    summary_embeddings_df = pd.read_csv(summary_embeddings_df_path)
    summary_embeddings_df.bmu = summary_embeddings_df.bmu.astype(int)

    return summary_embeddings_df, som

def get_node_errors(codebook_long, data, win_map, s):
    mse = [-1 for i in range(s)]
    for i in win_map:
        mse_i = []
        for j in win_map[i]:
            A = data[j]
            B = codebook_long[i]
            mse_i.append(np.linalg.norm(A-B))
        mse[i] = np.mean(mse_i)
        
    return mse