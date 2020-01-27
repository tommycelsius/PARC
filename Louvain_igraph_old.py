from sklearn.cluster import DBSCAN
import phenograph
import os
import sys
import LargeVis
import copy
import numpy as np
import time
from sklearn.cluster import DBSCAN, KMeans
from MulticoreTSNE import MulticoreTSNE as multicore_tsne
import scipy.io
import pandas as pd
from pandas import ExcelWriter
import hnswlib
from scipy.sparse import csr_matrix
import igraph as ig
import louvain
import matplotlib.pyplot as plt
# from mst_clustering import MSTClustering
from MST_clustering_mergetooclose import MSTClustering
import time
from sklearn import metrics
from sklearn.neighbors import KernelDensity
from scipy import stats
from pandas import ExcelWriter


# 0: no fluor
# 1: only fluor
# 2: all features (fluor + non-fluor)

def get_data(cancer_type, benign_type, n_cancer, ratio, fluor, dataset_number, new_folder_name, method, randomseedval):
    print('randomseed val ', randomseedval)
    n_pbmc = int(n_cancer * ratio)
    n_total = int(n_pbmc + n_cancer)
    new_file_name = new_file_name_title = 'N' + str(n_total) + '_r{:.2f}'.format(ratio) + cancer_type + '_pbmc_gated_d' + str(
        dataset_number)
    if method == 'bh':
        label_file_name = '/home/shobi/Thesis/BarnesHutMC_data/' + new_folder_name + '/BH_label_' + new_file_name + '.txt'
        tag_file_name = '/home/shobi/Thesis/BarnesHutMC_data/' + new_folder_name + '/BH_tag_' + new_file_name + '.txt'
        data_file_name = '/home/shobi/Thesis/BarnesHutMC_data/' + new_folder_name + '/BH_data_' + new_file_name + '.txt'
    if method == 'lv':
        label_file_name = '/home/shobi/Thesis/LV_data/' + new_folder_name + '/LV_label_' + new_file_name + '.txt'
        tag_file_name = '/home/shobi/Thesis/LV_data/' + new_folder_name + '/LV_tag_' + new_file_name + '.txt'
        data_file_name = '/home/shobi/Thesis/LV_data/' + new_folder_name + '/LV_data_' + new_file_name + '.txt'

    # KELVINS K562 AND ACC220 DONT HAVE columns for FLUOR DATA
    featureName_k562_acc220 = ['File ID', 'Cell ID', 'Area', 'Volume', 'Circularity', 'Attenuation density',
                               'Amplitude var', 'Amplitude skewness', 'Amplitude kurtosis', 'Focus factor 1',
                               'Focus factor 2', 'Dry mass', 'Dry mass density', 'Dry mass var', 'Dry mass skewness',
                               'Peak phase', 'Phase var', 'Phase skewness', 'Phase kurtosis', 'DMD contrast 1',
                               'DMD contrast 2', 'DMD contrast 3', 'DMD contrast 4', 'Mean phase arrangement',
                               'Phase arrangement var', 'Phase arrangement skewness', 'Phase orientation var',
                               'Phase orientation kurtosis']
    # DICKSON'S NSCLC HAVE FLUOR DATA. FOCUS FACTOR IS NOT THE FINAL FEATURE
    featureName_fluor = ['File ID', 'Cell ID', 'Area', 'Volume', 'Circularity', 'Attenuation density', 'Amplitude var',
                         'Amplitude skewness', 'Amplitude kurtosis', 'Focus factor 1', 'Focus factor 2', 'Dry mass',
                         'Dry mass density', 'Dry mass var', 'Dry mass skewness', 'Peak phase', 'Phase var',
                         'Phase skewness', 'Phase kurtosis', 'DMD contrast 1', 'DMD contrast 2', 'DMD contrast 3',
                         'DMD contrast 4', 'Mean phase arrangement', 'Phase arrangement var',
                         'Phase arrangement skewness', 'Phase orientation var', 'Phase orientation kurtosis',
                         'Fluorescence (Peak)', 'Fluorescence (Area)', 'Fluorescence density',
                         'Fluorescence-Phase correlation']
    # KELVINS PBMC AND THP1 HAVE EMPTY COLUMNS FOR FLUOR WHICH WE WILL DROP LATER. THE FOCUS FACTOR FEATURE IS THE FINAL FEATURE
    featureName = ['File ID', 'Cell ID', 'Area', 'Volume', 'Circularity', 'Attenuation density', 'Amplitude var',
                   'Amplitude skewness', 'Amplitude kurtosis', 'Dry mass', 'Dry mass density', 'Dry mass var',
                   'Dry mass skewness', 'Peak phase', 'Phase var', 'Phase skewness', 'Phase kurtosis', 'DMD contrast 1',
                   'DMD contrast 2', 'DMD contrast 3', 'DMD contrast 4', 'Mean phase arrangement',
                   'Phase arrangement var', 'Phase arrangement skewness', 'Phase orientation var',
                   'Phase orientation kurtosis', 'Fluorescence (Peak)', 'Fluorescence (Area)', 'Fluorescence density',
                   'Fluorescence-Phase correlation', 'Focus factor 1', 'Focus factor 2']
    # ALL FEATURES EXCLUDING FILE AND CELL ID:
    feat_cols = ['Area', 'Volume', 'Circularity', 'Attenuation density', 'Amplitude var', 'Amplitude skewness',
                 'Amplitude kurtosis', 'Dry mass', 'Dry mass density', 'Dry mass var', 'Dry mass skewness',
                 'Peak phase', 'Phase var', 'Phase skewness', 'Phase kurtosis', 'DMD contrast 1', 'DMD contrast 2',
                 'DMD contrast 3', 'DMD contrast 4', 'Mean phase arrangement', 'Phase arrangement var',
                 'Phase arrangement skewness', 'Phase orientation var', 'Phase orientation kurtosis', 'Focus factor 1',
                 'Focus factor 2']
    feat_cols_includefluor = ['Area', 'Volume', 'Circularity', 'Attenuation density', 'Amplitude var',
                              'Amplitude skewness', 'Amplitude kurtosis', 'Dry mass', 'Dry mass density',
                              'Dry mass var', 'Dry mass skewness', 'Peak phase', 'Phase var', 'Phase skewness',
                              'Phase kurtosis', 'DMD contrast 1', 'DMD contrast 2', 'DMD contrast 3', 'DMD contrast 4',
                              'Mean phase arrangement', 'Phase arrangement var', 'Phase arrangement skewness',
                              'Phase orientation var', 'Phase orientation kurtosis', 'Focus factor 1', 'Focus factor 2',
                              'Fluorescence (Peak)', 'Fluorescence (Area)', 'Fluorescence density',
                              'Fluorescence-Phase correlation']
    feat_cols_fluor_only = ['Fluorescence (Peak)', 'Fluorescence (Area)', 'Fluorescence density',
                            'Fluorescence-Phase correlation']
    feat_cols1 = ['Area', 'Volume', 'Circularity', 'Attenuation density', 'Amplitude var']

    #print('loaded pbmc')
    # MCF7_Raw = scipy.io.loadmat('/home/shobi/Thesis/Data/MCF7_clean_real.mat') #32 x 306,968

    if benign_type == 'pbmc':
        #print('constructing dataframe for ', benign_type)
        PBMC_Raw = scipy.io.loadmat(
            '/home/shobi/Thesis/Data/ShobiGatedData/pbmc2017Nov22_gatedPbmc.mat')  # 28 x 466,266
        pbmc_struct = PBMC_Raw['pbmc2017Nov22_gatedPbmc']
        df_pbmc = pd.DataFrame(pbmc_struct[0, 0]['cellparam'].transpose().real)
        pbmc_fileidx = pbmc_struct[0, 0]['gated_idx'][0].tolist()
        pbmc_features = pbmc_struct[0, 0]['cellparam_label'][0].tolist()
        flist = []
        idxlist = []
        for element in pbmc_features:
            flist.append(element[0])
        df_pbmc.columns = flist
        pbmc_fileidx = pd.DataFrame(pbmc_struct[0, 0]['gated_idx'].transpose())
        pbmc_fileidx.columns = ['filename', 'matlabindex']
        #print('shape of fileidx', pbmc_fileidx.shape)
        df_pbmc['cell_filename'] = 'pbmc2017Nov22_' + pbmc_fileidx["filename"].map(int).map(str)
        df_pbmc['cell_idx_inmatfile'] = pbmc_fileidx["matlabindex"].map(int).map(str)
        df_pbmc['cell_tag']='pbmc2017Nov22_' + pbmc_fileidx["filename"].map(int).map(str)+'midx'+pbmc_fileidx["matlabindex"].map(int).map(str)
        df_pbmc['label'] = 'PBMC'
        df_pbmc['class'] = 0
        df_benign = df_pbmc.sample(frac=1,random_state = randomseedval).reset_index(drop=False)[0:n_pbmc]
        # print(df_benign.head(5))
        #print(df_benign.shape)

    # pbmc_fluor_raw = scipy.io.loadmat('/home/shobi/Thesis/Data/pbmc_fluor_clean_real.mat') #42,308 x 32
    # nsclc_fluor_raw = scipy.io.loadmat('/home/shobi/Thesis/Data/nsclc_fluor_clean_real.mat') #1,031 x 32
    if cancer_type == 'acc220':
        #print('constructing dataframe for ', cancer_type)
        acc220_Raw = scipy.io.loadmat(
            '/home/shobi/Thesis/Data/ShobiGatedData/acc2202017Nov22_gatedAcc220.mat')  # 28 x 416,421
        acc220_struct = acc220_Raw['acc2202017Nov22_gatedAcc220']
        df_acc220 = pd.DataFrame(acc220_struct[0, 0]['cellparam'].transpose().real)
        acc220_fileidx = acc220_struct[0, 0]['gated_idx'][0].tolist()
        acc220_features = acc220_struct[0, 0]['cellparam_label'][0].tolist()
        flist = []
        for element in acc220_features:
            flist.append(element[0])
        df_acc220.columns = flist
        acc220_fileidx = pd.DataFrame(acc220_struct[0, 0]['gated_idx'].transpose())
        acc220_fileidx.columns = ['filename', 'matlabindex']
        #print('shape of fileidx', acc220_fileidx.shape)
        df_acc220['cell_filename'] = 'acc2202017Nov22_' + acc220_fileidx["filename"].map(int).map(str)
        df_acc220['cell_idx_inmatfile'] = acc220_fileidx["matlabindex"].map(int).map(
            str)  # should be same number as image number within that folder
        df_acc220['cell_tag'] = 'acc2202017Nov22_' + acc220_fileidx["filename"].map(int).map(str) + 'midx' + acc220_fileidx[
            "matlabindex"].map(int).map(str)
        df_acc220['label'] = 'acc220'
        df_acc220['class'] = 1
        df_cancer = df_acc220.sample(frac=1,random_state = randomseedval).reset_index(drop=False)[0:n_cancer]
        #print(df_cancer.shape)

    if cancer_type == 'k562':
        #print('constructing dataframe for ', cancer_type)
        K562_Raw = scipy.io.loadmat('/home/shobi/Thesis/Data/ShobiGatedData/k5622017Nov08_gatedK562.mat')
        k562_struct = K562_Raw['k5622017Nov08_gatedK562']
        df_k562 = pd.DataFrame(k562_struct[0, 0]['cellparam'].transpose().real)
        k562_features = k562_struct[0, 0]['cellparam_label'][0].tolist()
        flist = []
        for element in k562_features:
            flist.append(element[0])
        df_k562.columns = flist
        k562_fileidx = pd.DataFrame(k562_struct[0, 0]['gated_idx'].transpose())
        k562_fileidx.columns = ['filename', 'matlabindex']
        #print('shape of fileidx', k562_fileidx.shape)
        df_k562['cell_filename'] = 'k5622017Nov08_' + k562_fileidx["filename"].map(int).map(str)
        df_k562['cell_idx_inmatfile'] =  k562_fileidx["matlabindex"].map(int).map(str) #should be same number as image number within that folder
        df_k562['cell_tag'] = 'k5622017Nov08_' + k562_fileidx["filename"].map(int).map(str) + 'midx' + k562_fileidx[
            "matlabindex"].map(int).map(str)
        df_k562['label'] = 'K562'
        df_k562['class'] = 1
        df_cancer = df_k562.sample(frac=1,random_state = randomseedval).reset_index(drop=False)[0:n_cancer]
        #print(df_cancer.shape)

    if cancer_type == 'thp1':
        #print('constructing dataframe for ', cancer_type)
        THP1_Raw = scipy.io.loadmat(
            '/home/shobi/Thesis/Data/ShobiGatedData/thp12017Nov22_gatedThp1.mat')  # 28 x 307,339
        thp1_struct = THP1_Raw['thp12017Nov22_gatedThp1']
        df_thp1 = pd.DataFrame(thp1_struct[0, 0]['cellparam'].transpose())
        thp1_fileidx = thp1_struct[0, 0]['gated_idx'][0].tolist()
        thp1_features = thp1_struct[0, 0]['cellparam_label'][0].tolist()
        flist = []
        idxlist = []
        for element in thp1_features:
            flist.append(element[0])
        df_thp1.columns = flist

        thp1_fileidx = pd.DataFrame(thp1_struct[0, 0]['gated_idx'].transpose())
        thp1_fileidx.columns = ['filename', 'matlabindex']
        #print('shape of fileidx', thp1_fileidx.shape)
        df_thp1['cell_filename'] = 'thp12017Nov22_' + thp1_fileidx["filename"].map(int).map(str)
        df_thp1['cell_idx_inmatfile'] = thp1_fileidx["matlabindex"].map(int).map(
            str)  # should be same number as image number within that folder
        df_thp1['cell_tag'] = 'thp12017Nov022_' + thp1_fileidx["filename"].map(int).map(str) + 'midx' + thp1_fileidx[
            "matlabindex"].map(int).map(str)
        df_thp1['label'] = 'thp1'
        df_thp1['class'] = 1
        df_cancer = df_thp1.sample(frac=1,random_state = randomseedval).reset_index(drop=False)[0:n_cancer]
        #print(df_cancer.shape)


    # frames = [df_pbmc_fluor,df_nsclc_fluor]
    frames = [df_benign, df_cancer]
    df_all = pd.concat(frames, ignore_index=True)

    # EXCLUDE FLUOR FEATURES
    if fluor == 0:
        df_all[feat_cols] = (df_all[feat_cols] - df_all[feat_cols].mean()) / df_all[feat_cols].std()
        X_txt = df_all[feat_cols].values
        #print('size of data matrix:', X_txt.shape)
    # ONLY USE FLUOR FEATURES
    if fluor == 1:
        df_all[feat_cols_fluor_only] = (df_all[feat_cols_fluor_only] - df_all[feat_cols_fluor_only].mean()) / df_all[
            feat_cols_fluor_only].std()
        X_txt = df_all[feat_cols_fluor_only].values
        print('size of data matrix:', X_txt.shape)
    if fluor == 2:  # all features including fluor when a dataset has incorporated a fluo marker
        df_all[feat_cols_includefluor] = (df_all[feat_cols_includefluor] - df_all[feat_cols_includefluor].mean()) / \
                                         df_all[feat_cols_includefluor].std()
        X_txt = df_all[feat_cols_includefluor].values

    label_txt = df_all['class'].values
    tag_txt = df_all['cell_filename'].values
    print(X_txt.size, label_txt.size)
    true_label = np.asarray(label_txt)
    #true_label = np.reshape(true_label, (true_label.shape[0], 1))
    print('true label shape:', true_label.shape)
    true_label = true_label.astype(int)
    tag = np.asarray(tag_txt)
    tag = np.reshape(tag, (tag.shape[0], 1))
    index_list = list(df_all['index'].values)
    # index_list = np.reshape(index_list,(index_list.shape[0],1))
    # print('index list', index_list)
    #np.savetxt(data_file_name, X_txt, comments='', header=str(n_total) + ' ' + str(int(X_txt.shape[1])), fmt="%f",  delimiter=" ")
    #np.savetxt(label_file_name, label_txt, fmt="%i", delimiter="")
    #np.savetxt(tag_file_name, tag_txt, fmt="%s", delimiter="")
    return true_label, tag, X_txt, new_file_name, df_all, index_list,flist

def run_lv(perplexity, lr, graph_array_name):
    outdim = 2
    threads = 8
    samples = -1
    prop = -1
    alpha = lr
    trees = -1
    neg = -1
    neigh = -1
    gamma = -1
    perp = perplexity
    fea = 1
    #alpha is the initial learning rate
    time_start = time.time()
    print('starting largevis', time.ctime())
    LargeVis.loadgraph(graph_array_name)
    X_embedded_LV=LargeVis.run(outdim, threads, samples, prop, alpha, trees, neg, neigh, gamma, perp)
    X_embedded = np.array(X_embedded_LV)
    print('X_embedded shape: ',X_embedded.shape)
    time_elapsed = time.time() - time_start
    return X_embedded
def func_mode(ll):  # return MODE of list
    # If multiple items are maximal, the function returns the first one encountered.
    return max(set(ll), key=ll.count)

def func_counter(ll):
    c_0 = ll.count(0)
    c_1 = ll.count(1)
    if c_0 > c_1: return 0
    if c_0 < c_1: return 1
    if c_0 == c_1: return 999
def make_knn_struct(X_data, ef=200):
    num_dims = X_data.shape[1]
    n_elements = X_data.shape[0]
    p = hnswlib.Index(space='l2', dim=num_dims)
    p.init_index(max_elements=n_elements, ef_construction=300, M=30)
    time_start_knn = time.time()
    # Element insertion (can be called several times):
    p.add_items(X_data)
    p.set_ef(ef)  # ef should always be > k
    p.save_index('/home/shobi/Thesis/Louvain_data/test_knnindex.txt')
    return p

def make_csrmatrix_noselfloop(neighbor_array, distance_array):
    row_list = []
    col_list = []
    weight_list = []
    neighbor_array = neighbor_array
    distance_array = distance_array
    n_neighbors = neighbor_array.shape[1]
    n_cells =  neighbor_array.shape[0]
    rowi = 0
    for row in neighbor_array:
        distlist =distance_array[rowi, :]
        #print(distlist)
        to_keep = np.where(distlist < np.mean(distlist)+0*np.std(distlist))[0]
        #print('to_keep', to_keep)
        updated_nn_ind = row[np.ix_(to_keep)]
        updated_nn_weights = distlist[np.ix_(to_keep)]
        #print('distlist update', updated_nn_weights)
        #print('nn update', updated_nn_ind)
        for ik in range(len(updated_nn_ind)):
            if rowi != row[ik]:  # remove self-loops
                row_list.append(rowi)
                #col_list.append(row[ik])
                col_list.append(updated_nn_ind[ik])
                dist = np.sqrt(updated_nn_weights[ik])
                #dist = np.sqrt(updated_nn_weights[rowi, ik])# making it the same as the minkowski distance
                if dist ==0:
                    print('rowi and row[ik] are ', rowi, row[ik], 'and are 0 dist apart')
                    dist = 0.000001
                weight_list.append(1 / dist)
                #if rowi%100000==0: print('distances to 1st and last neighbor:', dist)
        rowi = rowi + 1
    #print('average distances of neighbors', np.mean(dist_list))
    csr_graph = csr_matrix((np.array(weight_list), (np.array(row_list), np.array(col_list))), shape=(n_cells, n_cells))
    undirected_graph_array = None
    if n_neighbors >= 10:
        neighbor_array_noself = np.vstack((np.array(row_list),np.array(col_list))).T
        reverse_neighbor_array_noself =np.fliplr(neighbor_array_noself)
        undirected_neighbor_array = np.concatenate((neighbor_array_noself,reverse_neighbor_array_noself))
        print('undirec neigh array', undirected_neighbor_array.shape )
        weight_array = np.array(weight_list)
        weight_array = np.concatenate((weight_array,weight_array))
        weight_array = np.reshape(weight_array,(weight_array.shape[0],1))
        print('weight array shape', weight_array.shape)
        undirected_graph_array = np.hstack((undirected_neighbor_array,weight_array))

    return csr_graph, undirected_graph_array
def make_csrmatrix_withselfloop(neighbor_array, distance_array):
    row_list = []
    col_list = []
    dist_list = []
    neighbor_array = neighbor_array
    distance_array = distance_array
    n_neighbors = neighbor_array.shape[1]
    n_cells =  neighbor_array.shape[0]
    rowi = 0
    for row in neighbor_array:
        # print(row)
        for ik in range(n_neighbors):
            row_list.append(rowi)
            col_list.append(row[ik])
            if rowi == row[ik]:dist = 0.00001
            else: dist = np.sqrt(distance_array[rowi, ik])# making it the same as the minkowski distance
            dist_list.append(1 / dist)
            #if rowi%100000==0: print('distances:', dist)
            #if rowi ==row[ik]:
                #print('first neighbor is itself with dist:', dist)
             #
            #if dist ==0: dist = 0.001
            #dist_list.append(1/dist)
        rowi = rowi + 1
    #print('average distances of neighbors', np.mean(dist_list))
    csr_graph = csr_matrix((np.array(dist_list), (np.array(row_list), np.array(col_list))), shape=(n_cells, n_cells))
    return csr_graph
def run_toobig_sublouvain(X_data, knn_struct,k_nn,self_loop = False):
    n_elements = X_data.shape[0]
    time_start_knn = time.time()
    X_data_copy = copy.deepcopy(X_data)

    print('number of k-nn is', k_nn)
    neighbor_array, distance_array = knn_struct.knn_query(X_data_copy, k=k_nn)
    # print(neighbor_array, distance_array)

    # print('time elapsed {} seconds'.format(time.time() - time_start_knn))
    # print(neighbor_array.shape, distance_array.shape)
    undirected_graph_array_forLV = None
    if self_loop == False:
        csr_array, undirected_graph_array_forLV = make_csrmatrix_noselfloop(neighbor_array, distance_array)
        print(undirected_graph_array_forLV)

    if self_loop == True:
        csr_array = make_csrmatrix_withselfloop(neighbor_array, distance_array)
    time_start_nx = time.time()

    sources, targets = csr_array.nonzero()
    # print(len(sources),len(targets))
    mask = np.zeros(len(sources), dtype=bool)
    mask |= (csr_array.data < (np.mean(csr_array.data) - np.std(csr_array.data) * 5))
    print('sum of mask', sum(mask))
    csr_array.data[mask] = 0
    csr_array.eliminate_zeros()
    sources, targets = csr_array.nonzero()
    edgelist = list(zip(sources.tolist(), targets.tolist()))
    edgelist_copy = edgelist.copy()
    G = ig.Graph(edgelist, edge_attrs={'weight': csr_array.data.tolist()})
    sim_list = G.similarity_jaccard(pairs=edgelist_copy)
    G_sim = ig.Graph(list(edgelist), edge_attrs={'weight': sim_list})
    print('average degree of graph is ', np.mean(G_sim.degree()))
    G_sim.simplify(combine_edges='first')
    print('average degree of SIMPLE graph is ', np.mean(G_sim.degree()), G_sim.degree)
    time_start_louvain = time.time()
    print('starting Louvain clustering at', time.ctime())
    partition = louvain.find_partition(G_sim, louvain.ModularityVertexPartition)
    louvain_labels = np.empty((n_elements, 1))
    small_pop_list = []
    for key in range(len(partition)):
        population = len(partition[key])
        for cell in partition[key]:
            louvain_labels[cell] = key

    return louvain_labels

def run_sublouvain(X_data, knn_struct,k_nn,self_loop = False):
    n_elements = X_data.shape[0]
    time_start_knn = time.time()
    X_data_copy = copy.deepcopy(X_data)

    print('number of k-nn is', k_nn)
    neighbor_array, distance_array = knn_struct.knn_query(X_data_copy, k=k_nn)
    #print(neighbor_array, distance_array)

    #print('time elapsed {} seconds'.format(time.time() - time_start_knn))
    #print(neighbor_array.shape, distance_array.shape)
    undirected_graph_array_forLV = None
    if self_loop == False:
        csr_array, undirected_graph_array_forLV = make_csrmatrix_noselfloop(neighbor_array, distance_array)
        print(undirected_graph_array_forLV)

    if self_loop == True:
        csr_array = make_csrmatrix_withselfloop(neighbor_array, distance_array)
    time_start_nx = time.time()

    sources, targets = csr_array.nonzero()
    #print(len(sources),len(targets))
    mask = np.zeros(len(sources), dtype=bool)
    mask |= (csr_array.data < (np.mean(csr_array.data) - np.std(csr_array.data)*5))
    print('sum of mask', sum(mask))
    csr_array.data[mask] = 0
    csr_array.eliminate_zeros()
    sources, targets = csr_array.nonzero()
    edgelist = list(zip(sources.tolist(), targets.tolist()))
    #print('EDGELIST', edgelist)
    edgelist_copy = edgelist.copy()
    #print('EDGELIST',edgelist)
    #print('making iGraph')
    G = ig.Graph(edgelist, edge_attrs={'weight': csr_array.data.tolist()})
    #print('edgelist_copy:', edgelist_copy)
    sim_list = G.similarity_jaccard(pairs = edgelist_copy)
    #print('edgelist:', edgelist_copy)
    #print('simlist:',sim_list)
    G_sim = ig.Graph(list(edgelist), edge_attrs={'weight': sim_list})
    #layout = G.layout("rt",2)
    #ig.plot(G)
    print('average degree of graph is ', np.mean(G_sim.degree()))
    G_sim.simplify(combine_edges='first')
    print('average degree of SIMPLE graph is ', np.mean(G_sim.degree()), G_sim.degree)
    #print('vertices', G.vcount())
    #print('time elapsed {} seconds'.format(time.time() - time_start_nx))
    # first compute the best partition. A length n_total dictionary where each dictionary key is a group, and the members of dict[key] are the member cells
    time_start_louvain = time.time()
    print('starting Louvain clustering at', time.ctime())
    partition = louvain.find_partition(G_sim, louvain.ModularityVertexPartition)
    louvain_labels = np.empty((n_elements, 1))
    #print(partition,'partition dict')
    small_pop_list = []
    for key in range(len(partition)):
        population = len(partition[key])
        if population < 10:
            print(key, ' has population less than 10: of ', population, )
            small_pop_list.append([t for t in partition[key]])
        for cell in partition[key]:
            louvain_labels[cell] = key
    print(small_pop_list)
    for small_cluster in small_pop_list:
        for single_cell in small_cluster:
            print('single cell')
            print('dim neigh array', neighbor_array.shape)
            old_neighbors = neighbor_array[single_cell,:]
            #print(old_neighbors, 'old neighbors')
            group_of_old_neighbors = louvain_labels[old_neighbors]
            group_of_old_neighbors = list(group_of_old_neighbors.flatten())

            #print('single cell', single_cell, 'has this group_of_old_neighbors', group_of_old_neighbors)
            from statistics import mode
            best_group =max(set(group_of_old_neighbors), key=group_of_old_neighbors.count)
            #print(best_group)
            louvain_labels[single_cell] = best_group
    louvain_labels_0 = louvain_labels
    too_big = False
    print(set(list(louvain_labels.T)[0]))
    set_louvain_labels = set(list(louvain_labels.T)[0])
    print(set_louvain_labels)
    for cluster_i in set_louvain_labels:
        cluster_i_loc = np.where(louvain_labels == cluster_i)[0]
        pop_i = len(cluster_i_loc)
        if pop_i > 0.4*n_elements:
            too_big = True
            cluster_big_loc  = cluster_i_loc
    while too_big == True:
        print('removing too big')
        X_data_big = X_data[cluster_big_loc,:]
        knn_struct_big = make_knn_struct(X_data_big)
        print(X_data_big.shape)
        louvain_labels_big = run_toobig_sublouvain(X_data_big, knn_struct_big, k_nn=200, self_loop=False)
        print('set of new big labels ',set(list(louvain_labels_big.flatten())))
        louvain_labels_big = louvain_labels_big+1000#len(set_louvain_labels)
        print('set of new big labels +1000 ', set(list(louvain_labels_big.flatten())))
        pop_list = []
        for item in set(list(louvain_labels_big.flatten())):
            pop_list.append(list(louvain_labels_big.flatten()).count(item))
        print('pop of big list', pop_list)
        jj =0
        print('shape louvain_labels', louvain_labels.shape)
        for j in cluster_big_loc:
            louvain_labels[j] = louvain_labels_big[jj]
            jj=jj+1
        dummy, louvain_labels= np.unique(list(louvain_labels.flatten()), return_inverse=True)
        print('new set of labels ', set(louvain_labels))
        too_big = False
        set_louvain_labels =set(louvain_labels)
        louvain_labels = np.asarray(louvain_labels)
        for cluster_i in set_louvain_labels:
            print('asarray:', louvain_labels.shape)
            cluster_i_loc = np.where(louvain_labels == cluster_i)[0]
            pop_i = len(cluster_i_loc)
            if pop_i > 0.4 * n_elements:
                too_big = True
                print('cluster', cluster_i, 'is too big')
                cluster_big_loc = cluster_i_loc
    print('final shape before too_small allocation', set(list(louvain_labels.flatten())))
    small_pop_list= []
    small_pop_exist= False
    for cluster in set(list(louvain_labels.flatten())):
        population = len(np.where(louvain_labels==cluster)[0])
        if population < 50:
            small_pop_exist= True
            print(cluster, ' has small population of', population, )
            small_pop_list.append(np.where(louvain_labels==cluster)[0])
    while small_pop_exist ==True:
        for small_cluster in small_pop_list:
            for single_cell in small_cluster:
                #print('single cell')
                #print('dim neigh array', neighbor_array.shape)
                old_neighbors = neighbor_array[single_cell, :]
                #print(old_neighbors, 'old neighbors')
                group_of_old_neighbors = louvain_labels[old_neighbors]
                group_of_old_neighbors = list(group_of_old_neighbors.flatten())

                #print('single cell', single_cell, 'has this group_of_old_neighbors', group_of_old_neighbors)
                from statistics import mode
                best_group = max(set(group_of_old_neighbors), key=group_of_old_neighbors.count)
                #print(best_group)
                louvain_labels[single_cell] = best_group
        small_pop_exist = False
        for cluster in set(list(louvain_labels.flatten())):
            population = len(np.where(louvain_labels == cluster)[0])
            if population < 50:
                small_pop_exist = True
                print(cluster, ' has small population of', population, )
                small_pop_list.append(np.where(louvain_labels == cluster)[0])

    dummy, louvain_labels = np.unique(list(louvain_labels.flatten()), return_inverse=True)
    louvain_labels=np.asarray(louvain_labels)
    print('final labels allocation', set(list(louvain_labels.flatten())))
    pop_list=[]
    for item in set(list(louvain_labels.flatten())):
        pop_list.append(list(louvain_labels.flatten()).count(item))
    print('pop of big list', pop_list)

    return louvain_labels,undirected_graph_array_forLV

def run_mainlouvain(X_data,true_label, self_loop = False,LV_graphinput_file_name =None, LV_plot_file_name =None, pop_small = 50):
    list_roc = []
    k_nn_range = [60]#[30, 20, 10,5,3]#,30]#,15,20,30]
    ef = 50
    f1_temp = -1
    temp_best_labels = []
    iclus = 0
    for k_nn in k_nn_range:
        knn_struct = make_knn_struct(X_data)
        # Query dataset, k - number of closest elements (returns 2 numpy arrays)
        time_start_louvain = time.time()
        louvain_labels, undirected_graph_array_forLV = run_sublouvain(X_data, knn_struct, k_nn, self_loop=self_loop)
        if k_nn >=10 and LV_graphinput_file_name!=None:
            LV_graphinput_file_name = LV_graphinput_file_name
            np.savetxt(LV_graphinput_file_name,undirected_graph_array_forLV)
            time_start_lv = time.time()
            X_embedded = run_lv(perplexity=30,lr=1, graph_array_name= LV_graphinput_file_name)
            print('lv runtime', time.time()- time_start_lv)
        #print('number of communities is:', len(set(list(louvain_labels))))
        print('time elapsed {:.2f} seconds'.format(time.time() - time_start_louvain))
        run_time =time.time() - time_start_louvain
        print('current time is: ', time.ctime())
        targets = list(set(true_label))
        if len(targets) >=2: target_range = targets
        else: target_range = [1]
        N = len(list(true_label))
        f1_accumulated =0
        for onevsall_val in target_range:
            vals_roc, predict_class_array = accuracy_mst(list(louvain_labels.flatten()), true_label,
                                                             embedding_filename=None, clustering_algo='louvain', onevsall=onevsall_val)
            #list(louvain_labels.T)[0]
            f1_current = vals_roc[1]
            f1_accumulated = f1_accumulated+ f1_current*(list(true_label).count(onevsall_val))/N
            #print(f1_accumulated, f1_current, list(true_label).count(onevsall_val))
            if f1_current > f1_temp:
                f1_temp = f1_current
                temp_best_labels = list(louvain_labels.flatten())
                onevsall_opt = onevsall_val
                knn_opt = k_nn
                predict_class_array_opt = predict_class_array
            list_roc.append([ef, k_nn, onevsall_val]+vals_roc + [run_time])

            if iclus == 0:
                predict_class_aggregate = np.array(predict_class_array)
                iclus = 1
            else:
                predict_class_aggregate = np.vstack((predict_class_aggregate, predict_class_array))
    if LV_graphinput_file_name != None:
        import Performance_phenograph as pp
        fig, ax = plt.subplots(1, 2, figsize=(20, 10))
        pp.plot_mst_simple(ax[0], ax[1], temp_best_labels, true_label, None, None, None, None,
                       cancer_type='k562', clustering_method='louvain', X_embedded=X_embedded,
                       k_nn=knn_opt)
        plt.savefig(LV_plot_file_name, bbox_inches='tight')
    df_accuracy = pd.DataFrame(list_roc,
                               columns=['ef','knn', 'onevsall-target','error rate','f1-score', 'tnr', 'fnr',
                                        'tpr', 'fpr', 'precision', 'recall', 'num_groups', 'clustering runtime'])
    print('accumulated F1-score: ', f1_accumulated)
    #knn_opt = df_accuracy['knn'][df_accuracy['f1-score'].idxmax()]
    return predict_class_aggregate, df_accuracy, temp_best_labels,knn_opt, onevsall_opt

def run_phenograph(X_data, true_label):
    list_roc = []
    iclus = 0
    time_pheno = time.time()
    print('phenograph started at time:', time.ctime())
    communities, graph, Q = phenograph.cluster(X_data)
    print('communities finished at time :', time.ctime())
    pheno_time = time.time() - time_pheno
    print('phenograph took ', pheno_time, 'seconds')
    f1_temp = -1
    targets = list(set(true_label))
    if len(targets) >2: target_range = targets
    else: target_range = [1]
    for onevsall_val in target_range:
        vals_roc, predict_class_array = accuracy_mst(list(communities), true_label,
                                                        None, 'phenograph',
                                                        onevsall=onevsall_val)

        list_roc.append([onevsall_val]+vals_roc + [pheno_time])
        if vals_roc[0] > f1_temp:
            f1_temp = vals_roc[0]
            temp_best_labels = list(communities)
            onevsall_opt = onevsall_val
        if iclus == 0:
            predict_class_aggregate = np.array(predict_class_array)
            iclus = 1
        else:
            predict_class_aggregate = np.vstack((predict_class_aggregate, predict_class_array))



    df_accuracy = pd.DataFrame(list_roc, columns=['onevsall-target','error rate','f1-score', 'tnr', 'fnr',
                                        'tpr', 'fpr', 'precision', 'recall', 'num_groups', 'clustering runtime'])

    return predict_class_aggregate, df_accuracy, list(communities), onevsall_opt

def accuracy_mst(model, true_labels, embedding_filename, clustering_algo,phenograph_time = None, onevsall=1):
    if clustering_algo =='dbscan':
        sigma = model.eps
        min_cluster_size =model.min_samples
        mergetooclosefactor = model.tooclose_factor
    elif clustering_algo =='mst':
        sigma = model.sigma_factor
        min_cluster_size = model.min_cluster_size
        mergetooclosefactor = model.tooclosefactor
    elif clustering_algo =='kmeans':
        sigma = None
        min_cluster_size = None
        mergetooclosefactor = None
    elif clustering_algo =='phenograph':
        sigma = None
        min_cluster_size = None
        mergetooclosefactor = None
    else:
        sigma = None
        min_cluster_size = None
        mergetooclosefactor = None

    X_dict = {}
    Index_dict = {}
    #if clustering_algo =='phenograph': X = X_embedded
    #else: X = model.X_fit_
    #print(X.shape)
    if clustering_algo=='phenograph': mst_labels = list(model)
    elif clustering_algo=='louvain' or clustering_algo =='multiclass mst':
        mst_labels = model
        #print('louvain labels',model)

    else: mst_labels = list(model.labels_)
    N = len(mst_labels)
    n_cancer = list(true_labels).count(onevsall)
    n_pbmc = N-n_cancer
    m = 999
    for k in range(N):
        #x = X[k, 0]
        #y = X[k, 1]
        #X_dict.setdefault(mst_labels[k], []).append((x, y))
        Index_dict.setdefault(mst_labels[k], []).append(true_labels[k])
        # Index_dict_dbscan.setdefault(dbscan_labels[k], []).append(true_labels[k])
    # X_dict_dbscan.setdefault(dbscan_labels[k], []).append((x, y))
    num_groups = len(Index_dict)
    sorted_keys = list(sorted(Index_dict.keys()))
    error_count = []
    pbmc_labels = []
    thp1_labels = []
    unknown_labels = []
    fp = 0
    fn = 0
    tp = 0
    tn = 0
    precision = 0
    recall = 0
    f1_score = 0
    small_pop_list = []
    for kk in sorted_keys:
        vals = [t for t in Index_dict[kk]]
        population = len(vals)
        #majority_val = func_counter(vals)
        majority_val = func_mode(vals)
        print(kk, 'is majority ', majority_val, 'with population ', len(vals))
        if kk==-1:
            len_unknown = len(vals)
            print('len unknown', len_unknown)
        if (majority_val == onevsall) and (kk != -1):
            thp1_labels.append(kk)
            fp = fp + len([e for e in vals if e != onevsall])
            tp = tp + len([e for e in vals if e == onevsall])
            error_count.append(len([e for e in vals if e != majority_val]))
        elif (majority_val != onevsall) and (kk != -1):
            pbmc_labels.append(kk)
            tn = tn + len([e for e in vals if e != onevsall])
            fn = fn + len([e for e in vals if e == onevsall])
            error_count.append(len([e for e in vals if e != majority_val]))
        if majority_val == 999:
            thp1_labels.append(kk)
            unknown_labels.append(kk)
            print(kk, ' has no majority, we are adding it to cancer_class')
            fp = fp + len([e for e in vals if e != onevsall])
            tp = tp + len([e for e in vals if e == onevsall])
            error_count.append(len([e for e in vals if e != majority_val]))
    predict_class_array = np.array(mst_labels)
    mst_labels_array = np.array(mst_labels)
    for cancer_class in thp1_labels:
        predict_class_array[mst_labels_array == cancer_class] = 1
    for benign_class in pbmc_labels:
        predict_class_array[mst_labels_array == benign_class] = 0
    predict_class_array.reshape((predict_class_array.shape[0], -1))
    error_rate = sum(error_count) / N
    comp_n_cancer = tp + fp
    comp_n_pbmc = fn + tn
    tnr = tn / n_pbmc
    fnr = fn / n_cancer
    tpr = tp / n_cancer
    fpr = fp / n_pbmc
    if comp_n_cancer != 0:
        computed_ratio = comp_n_pbmc / comp_n_cancer
        # print('computed-ratio is:', computed_ratio, ':1' )
    if tp != 0 or fn != 0: recall = tp / (tp + fn)  # ability to find all positives
    if tp != 0 or fp != 0: precision = tp / (tp + fp)  # ability to not misclassify negatives as positives
    if precision != 0 or recall != 0:
        f1_score = precision * recall * 2 / (precision + recall)

    print('num groups', 'error rate', 'onevsall', 'population', 'f1_score', 'fnr ', 'sigma', ' min cluster size', 'mergetooclose factor',
          len(sorted_keys), error_rate, onevsall, n_cancer, f1_score, fnr)
    #print('num groups','error rate','f1_score', 'fnr ', 'sigma', ' min cluster size', 'mergetooclose factor', len(sorted_keys), error_rate, f1_score, fnr, sigma, min_cluster_size, mergetooclosefactor)
    if clustering_algo=='phenograph': mst_runtime = phenograph_time
    elif clustering_algo =='multiclass mst' or clustering_algo== 'louvain': mst_runtime = None

    else: mst_runtime = model.clustering_runtime_
    if clustering_algo == 'louvain' or clustering_algo=='phenograph' or clustering_algo == 'multiclass mst' or clustering_algo =='kmeans': accuracy_val = [error_rate,f1_score, tnr, fnr, tpr, fpr, precision,
                    recall, num_groups]
    else: accuracy_val = [embedding_filename, sigma, min_cluster_size, mergetooclosefactor, error_rate, f1_score, tnr, fnr, tpr, fpr, precision,
                    recall, num_groups, mst_runtime]

    #print(accuracy_val)
    return accuracy_val, predict_class_array

def run_main(cancer_type, n_cancer,n_benign, randomseedval=[1,2,3]):

    n_cancer = n_cancer
    n_benign = n_benign
    ratio = n_benign / n_cancer
    print('the ratio is {}'.format(ratio))
    print('ncancer, nbenign', n_cancer,n_benign)
    print(cancer_type ,' is the type of cancer')
    n_total = n_cancer + n_benign
    num_nn = 30
    cancer_type = cancer_type #'thp1'
    benign_type = 'pbmc'

    fluor = 0
    new_folder_name = cancer_type + '_r{:.2f}'.format(ratio) + '_n' + str(n_cancer)+'_NoJaccPrune_mask5s_101112'
    path_tocreate = '/home/shobi/Thesis/Louvain_data/' + new_folder_name
    os.mkdir(path_tocreate)
    num_dataset_versions = 1
    dataset_version_range = range(num_dataset_versions)

    for dataset_version in dataset_version_range:
        randomseed_singleval = randomseedval[dataset_version]
        excel_file_name = '/home/shobi/Thesis/Louvain_data/' + new_folder_name + '/Louvain_excel_' + cancer_type + '_data' + str(
            dataset_version) + '_r{:.2f}'.format(ratio) + '_ncancer' + str(n_cancer) + '.xlsx'
        LV_graphinput_file_name = '/home/shobi/Thesis/Louvain_data/' + new_folder_name + '/graphinput_' + cancer_type + '_data' + str(
            dataset_version) + '_r{:.2f}'.format(ratio) + '_ncancer' + str(n_cancer)+'.txt'
        LV_plot_file_name = '/home/shobi/Thesis/Louvain_data/' + new_folder_name + '/LV_Plot_' + cancer_type + '_data' + str(
            dataset_version) + '_r{:.2f}'.format(ratio) + '_ncancer' + str(n_cancer)+'.png'
        true_label, tag, X_data, new_file_name, df_all, index_list, flist = get_data(cancer_type, benign_type, n_cancer,
                                                                                     ratio,
                                                                                     fluor, dataset_version,
                                                                                 new_folder_name, method='louvain',randomseedval=randomseed_singleval)

        writer = ExcelWriter(excel_file_name)

        #model_dbscan = DBSCAN(0.02, 10, tooclose_factor=0).fit(X_data)
        #vals_roc, predict_class_array = accuracy_mst(model_dbscan, true_label,
                                                     #embedding_filename=None, clustering_algo='dbscan')
        predict_class_aggregate_louvain, df_accuracy_louvain, best_louvain_labels, knn_opt, onevsall_opt = run_mainlouvain(X_data,
                                                                                                             true_label, self_loop=False,LV_graphinput_file_name = None, LV_plot_file_name = LV_plot_file_name)


        #predict_class_aggregate_louvain, df_accuracy_louvain_selfloop, best_louvain_labels_selfloop, knn_opt_selfloop, onevsall_opt_selfloop = run_mainlouvain(X_data,
         #                                                                                                    true_label, self_loop=True)

        df_accuracy_louvain.to_excel(writer, 'louvain', index=False)
        #df_accuracy_louvain_selfloop.to_excel(writer, 'louvain self loop', index=False)

        writer.save()
        print('successfully saved excel files')
def main():

    #run_main('thp1', n_cancer=100, n_benign=466000)
    print('weighted graph with ef =50')
    run_main('k562', n_cancer=1000, n_benign=300000, randomseedval=[10,11,12])
    #run_main('acc220', n_cancer=100, n_benign=466000)
    ##run_main('thp1', n_cancer=50, n_benign=466000)
    #run_main('k562', n_cancer=50, n_benign=466000)
    #run_main('acc220', n_cancer=50, n_benign=466)
    #run_main('acc220', n_cancer=100, n_benign=466000)
    #run_main('acc220', n_cancer=200, n_benign=466000)

if __name__ == '__main__':
    main()