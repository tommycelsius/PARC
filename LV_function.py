'''
Created on 5 May, 2018

@author: shobi
'''

import os
import sys
import LargeVis
import numpy as np
import time
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

import scipy.io
import pandas as pd
import matplotlib.pyplot as plt
# from mst_clustering import MSTClustering
from MST_clustering_mergetooclose import MSTClustering
import time
from sklearn import metrics
from scipy import stats
from MulticoreTSNE import MulticoreTSNE as multicore_tsne

# 0: no fluor
# 1: only fluor
# 2: all features (fluor + non-fluor)

def get_data(cancer_type, benign_type, n_cancer, ratio, fluor, dataset_number, new_folder_name):
    n_pbmc = int(n_cancer * ratio)
    n_total = int(n_pbmc + n_cancer)
    new_file_name = new_file_name_title = 'N' + str(n_total) + '_r' + str(ratio) + cancer_type + '_pbmc_gated_d' + str(
        dataset_number)

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

    print('loaded pbmc')
    # MCF7_Raw = scipy.io.loadmat('/home/shobi/Thesis/Data/MCF7_clean_real.mat') #32 x 306,968

    if benign_type == 'pbmc':
        print('constructing dataframe for ', benign_type)
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
        print('shape of fileidx', pbmc_fileidx.shape)
        df_pbmc['cell_tag'] = 'pbmc2017Nov22_' + pbmc_fileidx["filename"].map(int).map(str) + '_' + pbmc_fileidx[
            "matlabindex"].map(int).map(str)
        df_pbmc['label'] = 'PBMC'
        df_pbmc['class'] = 0
        df_benign = df_pbmc.sample(frac=1).reset_index(drop=False)[0:n_pbmc]
        # print(df_benign.head(5))
        print(df_benign.shape)

    # pbmc_fluor_raw = scipy.io.loadmat('/home/shobi/Thesis/Data/pbmc_fluor_clean_real.mat') #42,308 x 32
    # nsclc_fluor_raw = scipy.io.loadmat('/home/shobi/Thesis/Data/nsclc_fluor_clean_real.mat') #1,031 x 32
    if cancer_type == 'acc220':
        print('constructing dataframe for ', cancer_type)
        acc220_Raw = scipy.io.loadmat(
            '/home/shobi/Thesis/Data/ShobiGatedData/acc2202017Nov22_gatedAcc220.mat')  # 28 x 416,421
        acc220_struct = acc220_Raw['acc2202017Nov22_gatedAcc220']
        df_acc220 = pd.DataFrame(acc220_struct[0, 0]['cellparam'].transpose().real)
        acc220_fileidx = acc220_struct[0, 0]['gated_idx'][0].tolist()
        acc220_features = acc220_struct[0, 0]['cellparam_label'][0].tolist()
        flist = []
        idxlist = []
        for element in acc220_features:
            flist.append(element[0])
        df_acc220.columns = flist

        for ielement in acc220_fileidx:
            idxlist.append(ielement[0])
        df_acc220['cell_tag'] = idxlist
        df_acc220['label'] = 'ACC220'
        df_acc220['class'] = 1
        df_cancer = df_acc220.sample(frac=1).reset_index(drop=False)[0:n_cancer]
        # print(df_cancer.head(5))
        print('cancer df shape', df_cancer.shape)  # , df_cancer['cell_tag'][0:10])

    if cancer_type == 'k562':
        print('constructing dataframe for ', cancer_type)
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
        print('shape of fileidx', k562_fileidx.shape)
        df_k562['cell_tag'] = 'k5622017Nov08_' + k562_fileidx["filename"].map(int).map(str) + '_' + k562_fileidx[
            "matlabindex"].map(int).map(str)
        df_k562['label'] = 'K562'
        df_k562['class'] = 1
        df_cancer = df_k562.sample(frac=1).reset_index(drop=False)[0:n_cancer]
        print(df_cancer.shape)

    if cancer_type == 'thp1':
        print('constructing dataframe for ', cancer_type)
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

        for ielement in thp1_fileidx:
            idxlist.append(ielement[0])
        df_thp1['cell_tag'] = idxlist
        df_thp1['label'] = 'THP1'
        df_thp1['class'] = 1
        df_cancer = df_thp1.sample(frac=1).reset_index(drop=False)[0:n_cancer]
        # print(df_cancer.head(5))
        print('cancer df shape', df_cancer.shape)  # , df_cancer['cell_tag'][0:10])

    '''
    df_pbmc['subtype'] = ['lym' if (x <=110) & (x>=30) else 'u' for x in df_pbmc['Area']]
    df_pbmc['subtype'] = ['mon' if x >=150 else str(s) for x,s in zip(df_pbmc['Area'],df_pbmc['subtype'])]
    print(df_pbmc['subtype'].value_counts() )
    df_pbmc['cell_tag'] = 'P'+df_pbmc['subtype']+'_'+ df_pbmc['cell_tag'].map(str)
    print('subtype check complete')
    '''
    '''
    df_pbmc_fluor = pd.DataFrame(pbmc_fluor_raw['pbmc_fluor_clean_real'])
    df_pbmc_fluor = df_pbmc_fluor.replace('inf', 0)
    df_pbmc_fluor.columns = featureName_fluor
    df_pbmc_fluor['label'] = 'PBMC'
    df_pbmc_fluor['cell_tag'] = df_pbmc_fluor.index
    df_pbmc_fluor['cell_tag'] = 'P'+df_pbmc_fluor['cell_tag'].map(str)+'_'+df_pbmc_fluor["File ID"].map(int).map(str) + '_' + df_pbmc_fluor["Cell ID"].map(int).map(str)
    df_pbmc_fluor['class'] = 0
    df_pbmc_fluor = df_pbmc_fluor.sample(frac=1).reset_index(drop=True)[0:n_pbmc]
    print(df_pbmc_fluor.shape)

    df_nsclc_fluor = pd.DataFrame(nsclc_fluor_raw['nsclc_fluor_clean_real'])
    df_nsclc_fluor = df_nsclc_fluor.replace('inf', 0)
    df_nsclc_fluor.columns = featureName_fluor
    df_nsclc_fluor['label'] = 'nsclc'
    df_nsclc_fluor['cell_tag'] = df_nsclc_fluor.index
    df_nsclc_fluor['cell_tag'] = 'N'+df_nsclc_fluor['cell_tag'].map(str)+'_'+df_nsclc_fluor["File ID"].map(int).map(str) + '_' + df_nsclc_fluor["Cell ID"].map(int).map(str)
    df_nsclc_fluor['class'] = 1
    df_nsclc_fluor = df_nsclc_fluor.sample(frac=1).reset_index(drop=True)[0:n_cancer]
    print(df_pbmc_fluor.shape)
    '''
    # frames = [df_pbmc_fluor,df_nsclc_fluor]
    frames = [df_benign, df_cancer]
    df_all = pd.concat(frames, ignore_index=True)

    # EXCLUDE FLUOR FEATURES
    if fluor == 0:
        df_all[feat_cols] = (df_all[feat_cols] - df_all[feat_cols].mean()) / df_all[feat_cols].std()
        X_txt = df_all[feat_cols].values
        print('size of data matrix:', X_txt.shape)
    # ONLY USE FLUOR FEATURES
    if fluor == 1:
        df_all[feat_cols_fluor_only] = (df_all[feat_cols_fluor_only] - df_all[feat_cols_fluor_only].mean()) / df_all[
            feat_cols_fluor_only].std()
        X_txt = df_all[feat_cols_fluor_only].values
        print('size of data matrix:', X_txt.shape)
    if fluor == 2:  # all features including fluor
        df_all[feat_cols_includefluor] = (df_all[feat_cols_includefluor] - df_all[feat_cols_includefluor].mean()) / \
                                         df_all[feat_cols_includefluor].std()
        X_txt = df_all[feat_cols_includefluor].values

    label_txt = df_all['class'].values
    tag_txt = df_all['cell_tag'].values
    print(X_txt.size, label_txt.size)
    true_label = np.asarray(label_txt)
    true_label = np.reshape(true_label, (true_label.shape[0], 1))
    print('true label shape:', true_label.shape)
    true_label = true_label.astype(int)
    tag = np.asarray(tag_txt)
    tag = np.reshape(tag, (tag.shape[0], 1))
    index_list = list(df_all['index'].values)
    # index_list = np.reshape(index_list,(index_list.shape[0],1))
    # print('index list', index_list)
    np.savetxt(data_file_name, X_txt, comments='', header=str(n_total) + ' ' + str(int(X_txt.shape[1])), fmt="%f",
               delimiter=" ")
    np.savetxt(label_file_name, label_txt, fmt="%i", delimiter="")
    np.savetxt(tag_file_name, tag_txt, fmt="%s", delimiter="")
    return true_label, tag, X_txt, new_file_name, df_all, index_list


def simple_accuracy(predicted_labels, true_labels, data_version, index_list, df_all):
    # index list: the list of the original index in the original dataframe
    n_tot = true_labels.shape[0]
    n_cancer = list(true_labels).count(1)
    n_pbmc = list(true_labels).count(0)
    predicted_labels = predicted_labels.transpose()
    tn = fn = tp = fp = 0
    precision = 0
    recall = 0
    f1_score = 0
    fn_tag_list = []
    fp_tag_list = []
    fn_index_list = []
    # print(predicted_labels)
    # print(true_labels)
    for k in range(n_tot):
        if predicted_labels[k] == 0 and true_labels[k] == 0:
            tn = tn + 1
        if (predicted_labels[k] == 0) and (true_labels[k] == 1):
            fn = fn + 1
            fn_tag_list.append([df_all.loc[k, 'index'], df_all.loc[k, 'cell_tag']])
            fn_index_list.append(index_list[k])
        if (predicted_labels[k] == 1) and (true_labels[k] == 0):
            fp = fp + 1
            fp_tag_list.append([df_all.loc[k, 'index'], df_all.loc[k, 'cell_tag']])
        if (predicted_labels[k] == 1) and (true_labels[k] == 1):
            tp = tp + 1
    error_rate = (fp + fn) / n_tot
    comp_n_cancer = tp + fp
    comp_n_pbmc = fn + tn
    tnr = tn / n_pbmc
    fnr = fn / n_cancer
    tpr = tp / n_cancer
    fpr = fp / n_pbmc
    recall = tp / (tp + fn)  # ability to find all positives
    if comp_n_cancer != 0:
        computed_ratio = comp_n_pbmc / comp_n_cancer
        precision = tp / (tp + fp)  # ability to not misclassify negatives as positives
        if tp != 0: f1_score = precision * recall * 2 / (precision + recall)
    # print('fn tags:',fn_tag_list)
    # print('fn index', fn_index_list)
    # print('fp tags:',fp_tag_list)
    summary_simple_acc = [data_version, f1_score, tnr, fnr, tpr, fpr, precision, recall, error_rate, computed_ratio]
    return summary_simple_acc, fp_tag_list, fn_tag_list


def run_mctsne(version, input_data, perplexity, lr, new_file_name, new_folder_name):
    outdim = 2
    threads = 8
    samples = -1
    prop = -1
    alpha = -1
    trees = -1
    neg = -1
    neigh = -1
    gamma = -1
    perp = perplexity
    fea = 1
    #alpha is the initial learning rate
    time_start = time.time()
    print('starting largevis', time.ctime())
    embedding_filename = '/home/shobi/Thesis/LV_data/' + new_folder_name + '/LV_embedding' + new_file_name + '_lr' + str(
        lr) + '_lv' + str(version) + '.txt'
    LV_input_data = input_data.tolist() # will make a list of lists. required for parsing LV input
    LargeVis.loaddata(LV_input_data)
    X_embedded_LV=LargeVis.run(outdim, threads, samples, prop, lr, trees, neg, neigh, gamma, perp)
    X_embedded = np.array(X_embedded_LV)
    print(X_embedded.shape)
    time_elapsed = time.time() - time_start
    print(embedding_filename, ' LV done! Time elapsed: {} seconds'.format(time_elapsed))
    np.savetxt(embedding_filename, X_embedded, comments='',
               header=str(int(X_embedded.shape[0])) + ' ' + str(int(X_embedded.shape[1])), fmt="%f", delimiter=" ")
    return X_embedded, embedding_filename, time_elapsed

def run_dbscan(X_embedded, n_cancer, true_label, data_version, tsne_version, embedding_filename, tsne_runtime):
    list_roc = []
    sigma_list = [0.5]
    if n_cancer > 1000:
        cluster_size_list = [20]
    else:
        cluster_size_list = [15]
    iclus = 0
    for i_sigma in sigma_list:
        for i_cluster_size in cluster_size_list:
            print('Starting DBSCAN', time.ctime())
            model = DBSCAN(eps = i_sigma, min_samples = i_cluster_size).fit(X_embedded)
            time_start = time.time()
            mst_runtime = time.time() - time_start
            print('DBSCAN Done! Time elapsed: {:.2f} seconds'.format(mst_runtime),
                  'tsne version {}'.format(tsne_version), 'data version {}'.format(data_version),
                  'sigma {}'.format(i_sigma), 'and min cluster {}'.format(i_cluster_size))
            vals_roc, predict_class_array = accuracy_mst(i_sigma, i_cluster_size, model, true_label[:, 0], X_embedded,
                                                         embedding_filename, merge=1)
            list_roc.append(vals_roc + [tsne_runtime])

            if iclus == 0:
                predict_class_aggregate = np.array(predict_class_array)
            else:
                predict_class_aggregate = np.vstack((predict_class_aggregate, predict_class_array))

            iclus = 1
    df_accuracy = pd.DataFrame(list_roc,
                               columns=['embedding filename', 'eps', 'min cluster size', 'f1-score', 'tnr', 'fnr',
                                        'tpr', 'fpr', 'precision', 'recall', 'num_groups', 'clustering runtime',
                                        'tsne runtime'])

    sigma_opt = df_accuracy['sigma'][df_accuracy['f1-score'].idxmax()]
    min_cluster_size_opt = df_accuracy['min cluster size'][df_accuracy['f1-score'].idxmax()]
    return predict_class_aggregate, df_accuracy, sigma_opt, min_cluster_size_opt


def run_mstclustering(X_embedded, n_cancer, true_label, data_version, tsne_version, embedding_filename, tsne_runtime):
    list_roc = []
    list_roc_nomerge = []
    sigma_list = np.arange(2, 4, 1)
    if n_cancer > 1000:
        cluster_size_list = [20]
    else:
        cluster_size_list = [15]
    iclus = 0
    for i_sigma in sigma_list:
        for i_cluster_size in cluster_size_list:
            min_cluster_size = min(i_cluster_size, 20)
            model = MSTClustering(cutoff_scale=0.3, approximate=True, min_cluster_size=min_cluster_size,
                                  sigma_factor=i_sigma)
            time_start = time.time()
            print('Starting Clustering', time.ctime())
            model.fit_predict(X_embedded)
            mst_runtime = time.time() - time_start
            print('Clustering Done! Time elapsed: {:.2f} seconds'.format(mst_runtime),
                  'tsne version {}'.format(tsne_version), 'data version {}'.format(data_version),
                  'sigma {}'.format(i_sigma), 'and min cluster {}'.format(min_cluster_size))
            vals_roc, predict_class_array = accuracy_mst(i_sigma, min_cluster_size, model, true_label[:, 0], X_embedded,
                                                         embedding_filename, merge=1)
            list_roc.append(vals_roc + [tsne_runtime])
            vals_roc_nomerge, predict_class_array_nomerge = accuracy_mst(i_sigma, min_cluster_size, model,
                                                                         true_label[:, 0], X_embedded,
                                                                         embedding_filename, merge=0)
            list_roc_nomerge.append(vals_roc_nomerge + [tsne_runtime])
            if iclus == 0:
                predict_class_aggregate = np.array(predict_class_array)
                predict_class_aggregate_nomerge = np.array(predict_class_array_nomerge)

            else:
                predict_class_aggregate = np.vstack((predict_class_aggregate, predict_class_array))

                predict_class_aggregate_nomerge = np.vstack(
                    (predict_class_aggregate_nomerge, predict_class_array_nomerge))
            iclus = 1
    df_accuracy = pd.DataFrame(list_roc,
                               columns=['embedding filename', 'sigma', 'min cluster size', 'f1-score', 'tnr', 'fnr',
                                        'tpr', 'fpr', 'precision', 'recall', 'num_groups', 'clustering runtime',
                                        'tsne runtime'])
    df_accuracy_nomerge = pd.DataFrame(list_roc_nomerge,
                                       columns=['embedding filename', 'sigma', 'min cluster size', 'f1-score', 'tnr',
                                                'fnr', 'tpr', 'fpr', 'precision', 'recall', 'num_groups',
                                                'clustering runtime', 'tsne runtime'])
    sigma_opt = df_accuracy['sigma'][df_accuracy['f1-score'].idxmax()]
    min_cluster_size_opt = df_accuracy['min cluster size'][df_accuracy['f1-score'].idxmax()]
    return predict_class_aggregate, predict_class_aggregate_nomerge, df_accuracy, df_accuracy_nomerge, sigma_opt, min_cluster_size_opt


def accuracy_mst(sigma_roc, min_cluster_size_roc, model, true_labels, embedding_filename, merge=1):
    X_dict = {}
    Index_dict = {}
    X = model.X_fit_
    print(X.shape)
    if merge == 1:
        mst_labels = list(model.labels_)

    if merge == 0:
        mst_labels = list(model.labels_nomerge_)

    N = len(mst_labels)
    n_cancer = list(true_labels).count(1)
    n_pbmc = list(true_labels).count(0)
    m = 999
    for k in range(N):
        x = X[k, 0]
        y = X[k, 1]
        X_dict.setdefault(mst_labels[k], []).append((x, y))
        Index_dict.setdefault(mst_labels[k], []).append(true_labels[k])
        # Index_dict_dbscan.setdefault(dbscan_labels[k], []).append(true_labels[k])
    # X_dict_dbscan.setdefault(dbscan_labels[k], []).append((x, y))
    num_groups = len(Index_dict)
    sorted_keys = list(sorted(X_dict.keys()))
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

    for kk in sorted_keys:
        vals = [t for t in Index_dict[kk]]
        majority_val = func_counter(vals)
        len_unknown = 0
        if (majority_val == 1) and (kk != -1):
            thp1_labels.append(kk)
            fp = fp + len([e for e in vals if e != majority_val])
            tp = tp + len([e for e in vals if e == majority_val])
            error_count.append(len([e for e in vals if e != majority_val]))
        if (majority_val == 0) and (kk != -1):
            pbmc_labels.append(kk)
            fn = fn + len([e for e in vals if e != majority_val])
            tn = tn + len([e for e in vals if e == majority_val])
            error_count.append(len([e for e in vals if e != majority_val]))
        if majority_val == 999:
            thp1_labels.append(kk)
            unknown_labels.append(kk)
            print(kk, ' has no majority, we are adding it to cancer_class')
            fp = fp + len([e for e in vals if e != majority_val])
            tp = tp + len([e for e in vals if e == majority_val])
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
    if precision != 0 or recall != 0: f1_score = precision * recall * 2 / (precision + recall)

    print('f1_score', 'fnr ', 'sigma', ' min cluster size', f1_score, fnr, sigma_roc, min_cluster_size_roc)
    mst_runtime = model.clustering_runtime_
    accuracy_val = [embedding_filename, sigma_roc, min_cluster_size_roc, f1_score, tnr, fnr, tpr, fpr, precision,
                    recall, num_groups, mst_runtime]
    return accuracy_val, predict_class_array


def plot_mst_simple(model, true_labels, X_data_array, embedding_filename, sigma, min_cluster, cancer_type, merge=1):
    # http://nbviewer.jupyter.org/github/jakevdp/mst_clustering/blob/master/MSTClustering.ipynb

    X_dict = {}
    X_dict_dbscan = {}
    Index_dict = {}
    Index_dict_dbscan = {}
    X_plot = model.X_fit_
    if merge == 0:
        mst_labels = list(model.labels_nomerge_)
        num_groups = len(set(mst_labels))
    if merge == 1:
        mst_labels = list(model.labels_)
        num_groups = len(set(mst_labels))
    N = len(mst_labels)
    n_cancer = list(true_labels).count(1)
    n_pbmc = list(true_labels).count(0)
    m = 999
    for k in range(N):
        x = X_plot[k, 0]
        y = X_plot[k, 1]
        X_dict.setdefault(mst_labels[k], []).append((x, y))

        Index_dict.setdefault(mst_labels[k], []).append(true_labels[k])

    sorted_keys = list(sorted(X_dict.keys()))
    print('in plot: number of distinct groups:', len(sorted_keys))
    # sorted_keys_dbscan =list(sorted(X_dict_dbscan.keys()))
    print(sorted_keys, ' sorted keys')
    error_count = []
    pbmc_labels = []
    thp1_labels = []
    unknown_labels = []
    fp = 0
    fn = 0
    tp = 0
    tn = 0
    f1_score = 0
    precision = 0
    recall = 0
    f1_score = 0
    computed_ratio = 999

    for kk in sorted_keys:
        vals = [t for t in Index_dict[kk]]
        # print('kk ', kk, 'has length ', len(vals))
        majority_val = func_counter(vals)
        len_unknown = 0

        if (kk == -1):
            unknown_labels.append(kk)
            len_unknown = len(vals)
        if (majority_val == 1) and (kk != -1):
            thp1_labels.append(kk)
            # print(majority_val, 'is majority val')
            fp = fp + len([e for e in vals if e != majority_val])
            tp = tp + len([e for e in vals if e == majority_val])
            error_count.append(len([e for e in vals if e != majority_val]))
        if (majority_val == 0) and (kk != -1):
            pbmc_labels.append(kk)
            # print(majority_val, 'is majority val')
            fn = fn + len([e for e in vals if e != majority_val])
            tn = tn + len([e for e in vals if e == majority_val])
            error_count.append(len([e for e in vals if e != majority_val]))
        if majority_val == 999:
            thp1_labels.append(kk)
            unknown_labels.append(kk)
            print(kk, ' has no majority, we are adding it to cancer_class')
            fp = fp + len([e for e in vals if e != majority_val])
            tp = tp + len([e for e in vals if e == majority_val])
            error_count.append(len([e for e in vals if e != majority_val]))
            # print(kk,' has no majority')
    # print('thp1_labels:', thp1_labels)
    # print('pbmc_labels:', pbmc_labels)
    # print('error count for each group is: ', error_count)
    # print('len unknown', len_unknown)
    error_rate = sum(error_count) / N
    # print((sum(error_count)+len_unknown)*100/N, '%')
    comp_n_cancer = tp + fp
    comp_n_pbmc = fn + tn
    tnr = tn / n_pbmc
    fnr = fn / n_cancer
    print('fnr is', fnr)
    tpr = tp / n_cancer
    fpr = fp / n_pbmc
    if comp_n_cancer != 0:
        computed_ratio = comp_n_pbmc / comp_n_cancer
        # print('computed-ratio is:', computed_ratio, ':1' )
    if tp != 0 or fn != 0: recall = tp / (tp + fn)  # ability to find all positives
    if tp != 0 or fp != 0: precision = tp / (tp + fp)  # ability to not misclassify negatives as positives
    if precision != 0 or recall != 0:
        f1_score = precision * recall * 2 / (precision + recall)
        print('f1-score is', f1_score)
    if merge == 1:
        fig, ax = plt.subplots(1, 3, figsize=(36, 12), sharex=True, sharey=True)
        segments = model.get_graph_segments(full_graph=True)

        ax[0].scatter(X_plot[:, 0], X_plot[:, 1], c=true_labels, cmap='nipy_spectral_r', zorder=2, alpha=0.5, s=4)
        # idx = np.where(color_feature < 5* np.std(color_feature))
        # print(idx[0].shape)
        # print('ckeep shape', c_keep.shape)
        # X_keep = X_data_array[idx[0],:]
        # print('xkeep shape', X_keep.shape)
        # print(c_keep.min(), c_keep.max())
        # s= ax[2].scatter(X_keep[:,0], X_keep[:,1], c =c_keep[:,0], s=4, cmap = 'Reds')
        # cb = plt.colorbar(s)

        # lman = LassoManager(ax[0], data_lasso)
        # ax[0].text(0.95, 0.01, "blue: pbmc", transform=ax[1].transAxes, verticalalignment='bottom', horizontalalignment='right',color='green', fontsize=10)

        colors_pbmc = plt.cm.winter(np.linspace(0, 1, len(pbmc_labels)))
        colors_thp1 = plt.cm.autumn(np.linspace(0, 1, len(thp1_labels)))

        for color_p, ll_p in zip(colors_pbmc, pbmc_labels):
            x = [t[0] for t in X_dict[ll_p]]
            population = len(x)
            y = [t[1] for t in X_dict[ll_p]]
            ax[1].scatter(x, y, color=color_p, s=2, alpha=1, label='pbmc ' + str(ll_p) + ' Cellcount = ' + str(len(x)))
            ax[1].annotate(str(ll_p), xytext=(np.mean(x), np.mean(y)), xy=(np.mean(x), np.mean(y)), color='black',
                           weight='semibold')
            # ax[1].scatter(np.mean(x), np.mean(y),  color = color_p, s=population, alpha=1)
            ax[2].annotate(str(ll_p)+'_n'+str(len(x)), xytext=(np.mean(x), np.mean(y)), xy = (np.mean(x), np.mean(y)), color= 'black', weight = 'semibold')
            ax[2].scatter(np.mean(x), np.mean(y),  color = color_p, s=np.log(population), alpha=1,zorder = 2)
        for color_t, ll_t in zip(colors_thp1, thp1_labels):
            x = [t[0] for t in X_dict[ll_t]]
            population = len(x)
            y = [t[1] for t in X_dict[ll_t]]
            ax[1].scatter(x, y, color=color_t, s=4, alpha=1,
                          label=cancer_type + ' ' + str(ll_t) + ' Cellcount = ' + str(len(x)))
            ax[1].annotate(str(ll_t), xytext=(np.mean(x), np.mean(y)), xy=(np.mean(x), np.mean(y)), color='black',
                           weight='semibold')
            ax[2].annotate(str(ll_t) + '_n'+str(len(x)), xytext=(np.mean(x), np.mean(y)), xy = (np.mean(x), np.mean(y)), color= 'black', weight = 'semibold')
            ax[2].scatter(np.mean(x), np.mean(y),  color = color_t, s=np.log(population), alpha=1, zorder = 2)

        n_clusters = len(pbmc_labels) + len(thp1_labels)

        ax[2].plot(segments[0], segments[1], '-k',zorder=1, linewidth=1)
        ax[1].text(0.95, 0.01, "number of groups: " + " {:.0f}".format(num_groups) + " FP: " + " {:.2f}".format(
            fp * 100 / n_pbmc) + "%. FN of " + "{:.2f}".format(fn * 100 / (n_cancer)) + '%', transform=ax[1].transAxes,
                   verticalalignment='bottom', horizontalalignment='right', color='green', fontsize=10)
        for uu in unknown_labels:
            x = [t[0] for t in X_dict[uu]]
            y = [t[1] for t in X_dict[uu]]
            ax[1].scatter(x, y, color='gray', s=4, alpha=1, label=uu)
        ax[1].axis('tight')
        title_str0 = embedding_filename
        # title_str1 = 'MST: cutoff' + str(cutoff_scale) +' min_cluster:' +str(min_cluster_size)
        title_str1 = 'MST: mean + ' + str(sigma) + '-sigma cutoff and min cluster size of: ' + str(
            min_cluster) + '\n' + "error: " + " {:.2f}".format(error_rate * 100) + '%' + " FP: " + " {:.2f}".format(
            fp * 100 / n_pbmc) + "%. FN of " + "{:.2f}".format(
            fn * 100 / (n_cancer)) + '%' + '\n' + 'computed ratio:' + "{:.4f}".format(
            computed_ratio) + ' f1-score:' + "{:.4f}".format(f1_score)
        title_str2 = 'graph layout and cluster populations'
        #ax[2].set_title(graph_title_force, size=16)
        ax[1].set_title(title_str1, size=10)
        ax[0].set_title(title_str0, size=10)
        ax[2].set_title(title_str2, size=12)

        # Put a legend to the right of the current axis
        ##box = ax[1].get_position()
        ##ax[1].set_position([box.x0, box.y0, box.width *0.9, box.height])
        ##ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize = 6)
        plt.savefig(embedding_filename[:-4] + 'merge' + str(merge) + '.png', bbox_inches='tight')

    mst_runtime = model.clustering_runtime_
    roc_val = [embedding_filename, sigma, min_cluster, f1_score, tnr, fnr, tpr, fpr, precision, recall, num_groups,
               mst_runtime]
    # plt.show()
    return roc_val




def func_mode(ll):  # return MODE of list
    # If multiple items are maximal, the function returns the first one encountered.
    return max(set(ll), key=ll.count)


def func_counter(ll):
    c_0 = ll.count(0)
    c_1 = ll.count(1)
    if c_0 > c_1: return 0
    if c_0 < c_1: return 1
    if c_0 == c_1: return 999


def auc_accuracy(df_roc):
    fpr_list = df_roc['fpr'].values.tolist()
    tpr_list = df_roc['tpr'].values.tolist()
    fnr_list = df_roc['fnr'].values.tolist()
    tnr_list = df_roc['tnr'].values.tolist()
    precision_list = df_roc['precision'].values.tolist()
    recall_list = df_roc['recall'].values.tolist()
    fpr_list.append(1)
    tpr_list.append(1)
    tpr_list.insert(0, 0)
    fpr_list.insert(0, 0)
    fnr_list.append(1)
    tnr_list.append(1)
    fnr_list.insert(0, 0)
    tnr_list.insert(0, 0)
    precision_list.append(0)
    recall_list.append(1)
    precision_list.insert(0, 0)
    recall_list.insert(0, 1)
    auc_pr_val = metrics.auc(precision_list, recall_list, reorder=True)
    auc_roc_val = metrics.auc(fpr_list, tpr_list, reorder=True)
    print('precision-recall AUC:', auc_pr_val)
    print('ROC-AUC (fpr vs. tpr):', auc_roc_val)
    return auc_pr_val, auc_roc_val


def main():
    perplexity = 30
    n_cancer = 1000
    ratio = 1
    n_total = n_cancer + (ratio * n_cancer)
    '''
    if n_total >= 250000: lr = 2000
    if n_total >=100000 and n_total < 250000: lr= 1500
    if n_total <100000: lr = 1000

    '''
    cancer_type = 'k562'
    benign_type = 'pbmc'
    fluor = 0
    num_dataset_versions = 4
    num_tsne_versions = 1
    dataset_version_range = range(num_dataset_versions)
    tsne_version_range = range(num_tsne_versions)
    list_accuracy_opt0 = []
    list_accuracy_opt1 = []
    list_accuracy_opt_dbscan = []
    fn_tag_list = []
    fp_tag_list = []
    pred_list = []
    pred_list_dbscan = []
    lr_range = [0.5, 1, 1.5, 2]

    new_folder_name = cancer_type + '_r' + str(ratio) + '_n' + str(n_cancer)
    path_tocreate = '/home/shobi/Thesis/LV_data/' + new_folder_name
    os.mkdir(path_tocreate)

    lr_file = lr_range[0]
    for dataset_version in dataset_version_range:
        true_label, tag, X_data, new_file_name, df_all, index_list = get_data(cancer_type, benign_type, n_cancer, ratio,
                                                                              fluor, dataset_version, new_folder_name)
        for lr in lr_range:
            print(lr, 'is lr')
            for tsne_version in tsne_version_range:
                new_folder_name = cancer_type + '_r' + str(ratio) + '_n' + str(n_cancer)
                print('dataset_version', dataset_version, 'tsne_version is', tsne_version)
                X_embedded, embedding_filename, tsne_runtime = run_mctsne(tsne_version, X_data, perplexity, lr,
                                                                          new_file_name, new_folder_name)
                predict_class_aggregate, predict_class_aggregate_nomerge, df_accuracy, df_accuracy_nomerge, sigma_opt, min_cluster_size_opt = run_mstclustering(
                    X_embedded, n_cancer, true_label, dataset_version, tsne_version, embedding_filename, tsne_runtime)
                predict_class_aggregate_dbscan, df_accuracy_dbscan, eps_opt, min_cluster_size_opt_dbscan = run_dbscan(
                    X_embedded, n_cancer, true_label, dataset_version, tsne_version, embedding_filename, tsne_runtime)

                auc_list = [auc_accuracy(df_accuracy), tsne_runtime]
                auc_list_nomerge = [auc_accuracy(df_accuracy_nomerge), tsne_runtime]
                auc_list_dbscan = [auc_accuracy(df_accuracy_dbscan), tsne_runtime]

                if tsne_version == 0:
                    print(tsne_version, 'agg')
                    predict_class_aggregate_all = predict_class_aggregate
                    print('shape of predict_class_aggregate', predict_class_aggregate_all.shape)
                    predict_class_aggregate_all_nomerge = predict_class_aggregate_nomerge
                    predict_class_aggregate_all_dbscan = predict_class_aggregate_dbscan

                # if dataset_version ==0 and tsne_version==0:
                if lr == lr_range[0] and tsne_version == 0:
                    df_all_merge = df_accuracy
                    df_all_nomerge = df_accuracy_nomerge
                    df_all_dbscan = df_accuracy_dbscan
                else:
                    df_all_merge = pd.concat([df_all_merge, df_accuracy], ignore_index=True)
                    df_all_nomerge = pd.concat([df_all_nomerge, df_accuracy_nomerge], ignore_index=True)
                    df_all_dbscan = pd.concat([df_all_dbscan, df_accuracy_dbscan], ignore_index=True)
                if tsne_version != 0:
                    predict_class_aggregate_all = np.vstack((predict_class_aggregate_all, predict_class_aggregate))
                    predict_class_aggregate_all_nomerge = np.concatenate(
                        (predict_class_aggregate_all_nomerge, predict_class_aggregate_nomerge), axis=0)
                    predict_class_aggregate_all_dbscan = np.vstack((predict_class_aggregate_all_dbscan, predict_class_aggregate_dbscan))
                    print(dataset_version, tsne_version, 'd and t version')

                model = MSTClustering(cutoff_scale=0.3, approximate=True, min_cluster_size=min_cluster_size_opt,
                                      sigma_factor=sigma_opt)
                model.fit_predict(X_embedded)
                model_dbscan = DBSCAN(X_embedded,eps_opt, min_cluster_size_opt_dbscan).fit(X_embedded)
                list_accuracy_opt1.append(
                    plot_mst_simple(model, true_label[:, 0], X_embedded, embedding_filename, sigma_opt,
                                    min_cluster_size_opt, cancer_type, merge=1) + auc_list)
                list_accuracy_opt0.append(
                    plot_mst_simple(model, true_label[:, 0], X_embedded, embedding_filename, sigma_opt,
                                    min_cluster_size_opt, cancer_type, merge=0) + auc_list_nomerge)
                list_accuracy_opt_dbscan.append(
                    plot_mst_simple(model_dbscan, true_label[:, 0], X_embedded, embedding_filename, eps_opt,
                                    min_cluster_size_opt_dbscan, cancer_type, merge=1) + auc_list_dbscan)
            print(predict_class_aggregate_all.shape, 'predict_agg_all shape')
            predict_class_final = stats.mode(predict_class_aggregate_all)[0]
            predict_class_final_dbscan = stats.mode(predict_class_aggregate_all_dbscan)[0]
            print('mode of predictions has shape ', predict_class_final.shape)
            summary_simple_acc, fp_tags, fn_tags = simple_accuracy(predict_class_final, true_label, dataset_version,
                                                                   index_list, df_all)
            summary_simple_acc_dbscan, fp_tags_dbscan, fn_tags_dbscan = simple_accuracy(predict_class_final_dbscan, true_label, dataset_version,
                                                                   index_list, df_all_dbscan)
            pred_list.append([lr] + summary_simple_acc)
            pred_list_dbscan.append([lr] + summary_simple_acc_dbscan)
            fp_tag_list.append(fp_tags)
            fn_tag_list.append(fn_tags)
        df_fp_tags = pd.DataFrame(fp_tag_list)
        df_fn_tags = pd.DataFrame(fn_tag_list)
        df_mode = pd.DataFrame(pred_list,
                               columns=['learning rate', 'data version', 'f1-score', 'tnr', 'fnr', 'tpr', 'fpr',
                                        'precision', 'recall', 'error_rate', 'computed_ratio'])
        df_mode_dbscan = pd.DataFrame(pred_list_dbscan,
                               columns=['learning rate', 'data version', 'f1-score', 'tnr', 'fnr', 'tpr', 'fpr',
                                        'precision', 'recall', 'error_rate', 'computed_ratio'])
        df_accuracy_opt1 = pd.DataFrame(list_accuracy_opt1,
                                        columns=['embedding filename', 'sigma', 'min cluster size', 'f1-score', 'tnr',
                                                 'fnr', 'tpr', 'fpr', 'precision', 'recall', 'num_groups',
                                                 'clustering runtime', 'auc prec', 'auc roc', 'tsne runtime'])
        df_accuracy_opt0 = pd.DataFrame(list_accuracy_opt0,
                                        columns=['embedding filename', 'sigma', 'min cluster size', 'f1-score', 'tnr',
                                                 'fnr', 'tpr', 'fpr', 'precision', 'recall', 'num_groups',
                                                 'clustering runtime', 'auc prec', 'auc roc', 'tsne runtime'])
        print('shape of excel dataframe', df_all_merge.shape)
        excel_file_name = '/home/shobi/Thesis/LV_data/' + new_folder_name + '/LV_excel_' + cancer_type + '_data' + str(
            dataset_version) + '_r' + str(ratio) + '_ncancer' + str(n_cancer) + '.xlsx'
        writer = pd.ExcelWriter(excel_file_name)
        df_all_merge.to_excel(writer, 'All')
        df_all_nomerge.to_excel(writer, 'All_nomerge')
        df_accuracy_opt1.to_excel(writer, 'merged_too_close') #best tsne run for each dataset (with merging)
        df_accuracy_opt0.to_excel(writer, 'no_merging')
        df_mode.to_excel(writer, 'Mode') #one mode per dataset run
        df_mode_dbscan.to_excel(writer, 'DBSCAN Mode')  # one mode per dataset run
        df_fn_tags.to_excel(writer, 'fn tags') #per mode
        df_fp_tags.to_excel(writer, 'fp tags')
        writer.save()


if __name__ == '__main__':
    main()