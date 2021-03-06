import torch
import torch.nn.functional as F
import numpy as np
import logging
import random
# import tensorflow as tf
import torch.nn as tf

from typing import Tuple

import torch
from torch import nn, Tensor


'''
class TripletLoss(nn.Module):
    """Triplet loss with hard positive/negative mining.
    
    Reference:
        Hermans et al. In Defense of the Triplet Loss for Person Re-Identification. arXiv:1703.07737.
    
    Imported from `<https://github.com/Cysu/open-reid/blob/master/reid/loss/triplet.py>`_.
    
    Args:
        margin (float, optional): margin for triplet. Default is 0.3.
    """
    
    def __init__(self, margin, global_feat, labels):
        super(TripletLoss, self).__init__()
        self.margin = margin
        self.ranking_loss = nn.MarginRankingLoss(margin=margin)
    def forward(self, inputs, targets):
        """
        Args:
            inputs (torch.Tensor): feature matrix with shape (batch_size, feat_dim).
            targets (torch.LongTensor): ground truth labels with shape (num_classes).
        """
        n = inputs.size(0)
        
        # Compute pairwise distance, replace by the official when merged
        dist = torch.pow(inputs, 2).sum(dim=1, keepdim=True).expand(n, n)
        dist = dist + dist.t()
        dist.addmm_(1, -2, inputs, inputs.t())
        dist = dist.clamp(min=1e-12).sqrt()  # for numerical stability
        
        # For each anchor, find the hardest positive and negative
        mask = targets.expand(n, n).eq(targets.expand(n, n).t())
        dist_ap, dist_an = [], []
        for i in range(n):
            dist_ap.append(dist[i][mask[i]].max().unsqueeze(0))
            dist_an.append(dist[i][mask[i] == 0].min().unsqueeze(0))
        dist_ap = torch.cat(dist_ap)
        dist_an = torch.cat(dist_an)
        
        # Compute ranking hinge loss
        y = torch.ones_like(dist_an)
        print(dist_ap,dist_an,y,'333333333')
        return self.ranking_loss(dist_an, dist_ap, y)
'''



def test(step, dataset_test, filename, n_share, unk_class, G, C1, threshold):
    G.eval()
    C1.eval()
    correct = 0
    correct_close = 0
    size = 0
    class_list = [i for i in range(n_share)]
    class_list.append(unk_class)
    per_class_num = np.zeros((n_share + 1))
    per_class_correct = np.zeros((n_share + 1)).astype(np.float32)
    per_class_correct_cls = np.zeros((n_share + 1)).astype(np.float32)
    all_pred = []
    all_gt = []

    label_tt = []
    all_entr = []
    Tfeat = []
    Tpre = []



    for batch_idx, data in enumerate(dataset_test):
        with torch.no_grad():
            img_t, label_t, path_t = data[0], data[1], data[2]
            img_t, label_t = img_t.cuda(), label_t.cuda()

            #print(img_t, label_t, path_t,'01230000  ')

            feat = G(img_t)
#########################################################################################
            #feat1 = feat.cpu().numpy()
            #Tfeat = []
            Tfeat += list(feat) 
            #Tfeat1 = np.array(Tfeat) 
            #print(Tfeat1,'00001230  ')
            #print(Tfeat,'00001231  ') #######
            #print(feat,'00001232  ')
            #print(Tfeat1[1],Tfeat1[1][1],'00001233  ')
            #print(Tfeat[1],Tfeat[1][1],'00001234  ')
########################################################################################
            out_t = C1(feat)

            #print(out_t,'9999999   ')

            out_t = F.softmax(out_t)
            #print(out_t,'000000000')
            #print(out_t[1][0],out_t[1][1],'000000000')
#####################################################################################
            i = 0
            #out_t1 = out_t.cpu().numpy()
            #print(out_t[1][0],out_t[1][1],'000000000')
            e = int(np.size(out_t,axis=0))
            x = np.zeros(np.size(out_t,axis=0))
            for i in range(e):
                
                if out_t[i][0] > out_t[i][1]:
                    ma = out_t[i][0]
                else:
                    ma = out_t[i][1]
                x[i] = ma
                #i = i+1
            #Tpre = []
            Tpre += list(x) 

            #a = 'sssssssssss'
            #print(Tpre,a)#???????????????????????????????????????
#########################################################################################

            entr = -torch.sum(out_t * torch.log(out_t), 1).data.cpu().numpy()
            pred = out_t.data.max(1)[1]
            all_entr += list(entr)
            #b = '1111111111'
            #pred1 = pred.cpu().numpy()
            #print(entr,b)           #########
            #print(np.size(pred1))

            k = label_t.data.size()[0]
            pred_cls = pred.cpu().numpy()
            pred = pred.cpu().numpy()

            #c = '2222222222'
            #print(pred,c)           #?????????####

            pred_unk = np.where(entr > threshold)

            #print(pred_unk,'777777   ')

            pred[pred_unk[0]] = unk_class

            #print(pred,'555555   ')
            #print(np.size(pred))

            all_gt += list(label_t.data.cpu().numpy())
            all_pred += list(pred)
            #list() ???????????????????????????????????????
            #data.cpu().numpy()???tensor?????????numpy?????????

            #print(all_gt,'444444   ')
            #print(np.size(all_gt),np.size(all_pred))


            for i, t in enumerate(class_list):
                t_ind = np.where(label_t.data.cpu().numpy() == t)
                correct_ind = np.where(pred[t_ind[0]] == t)
                correct_ind_close = np.where(pred_cls[t_ind[0]] == i)
                per_class_correct[i] += float(len(correct_ind[0]))
                per_class_correct_cls[i] += float(len(correct_ind_close[0]))
                per_class_num[i] += float(len(t_ind[0]))
                correct += float(len(correct_ind[0]))
                correct_close += float(len(correct_ind_close[0]))

                #print(t_ind,t_ind[0],pred[t_ind[0]],correct_ind,correct_ind[0],correct_ind_close[0],'333333   ')
                
            label_tt = list(label_tt) + list(label_t.data.cpu().numpy())

            size += k

            #print(size,k,'666666    ')

##########################################################################################################
    #print(all_entr,'444444   ')
    Tfeat_all = [[random.random() for _ in range(2052)]for _ in range(1031)]#np.zeros(np.size(Tfeat,axis=0),np.size(Tfeat,axis=1)+2)
    d = 0
    for i in range(np.size(all_pred)):
        with torch.no_grad():
            if all_pred[i] ==2:
                d = d+1
    i = 0
    #print(Tfeat[1030][2047],'bbbbbbbbb')
    for i in range(1031):#np.size(Tfeat,axis=0)-1):
        with torch.no_grad():   #??????Tfeat_all
            r = 0
            for r in range(2048):
                Tfeat_all[i][r] = Tfeat[i][r]
                r = r+1
            Tfeat_all[i][r] = all_pred[i]
            r = r+1
            Tfeat_all[i][r] = Tpre[i]
            r = r+1
            Tfeat_all[i][r] = i
            r = r+1
            Tfeat_all[i][r] = all_entr[i]
            i = i+1
    #print(Tfeat_all,'ffffffffffffff')
    #??????Tfeat_0???Tfeat_1???Tfeat_2
    i = 0
    Tfeat_0 = [[random.random() for _ in range(2052)]for _ in range(1031)]#np.zeros(np.size(Tfeat,axis=0),np.size(Tfeat,axis=1)+2)
    Tfeat_1 = [[random.random() for _ in range(2052)]for _ in range(1031)]#np.zeros(np.size(Tfeat,axis=0),np.size(Tfeat,axis=1)+2)
    Tfeat_2 = [[random.random() for _ in range(2052)]for _ in range(d)]#np.zeros(d+1,np.size(Tfeat,axis=1)+2)
    a = 0
    b = 0
    c = 0
    for i in range(np.size(Tfeat_all,axis=0)-1):
        with torch.no_grad():
            if Tfeat_all[i][2048] == 0:
                Tfeat_0[a] = Tfeat_all[i]
                a = a+1
            #a???Tfeat_0????????????
            if Tfeat_all[i][2048] == 1:
                Tfeat_1[b] = Tfeat_all[i]
                b = b+1
            if Tfeat_all[i][2048] == 2:
                Tfeat_2[c] = Tfeat_all[i]
                c = c+1   
    sorted(Tfeat_0, key=lambda s: s[2049], reverse=True)
    sorted(Tfeat_1, key=lambda s: s[2049], reverse=True)
    sorted(Tfeat_2, key=lambda s: s[2051], reverse=True)
    f = int(a*0.3)
    g = int(b*0.3) 
    #c = int(c*0.3)
    #print(Tfeat_0,'aaaaaaaaaaa')
    #print(Tfeat_1,'bbbbbbbbbbb')
    #print(Tfeat_2,'ccccccccccc')
    print(a)
    print(b)
    print(c,d,'rrrrrrrrrrr')
    #??????0.3?????????
    Tfeat_00 = [[random.random() for _ in range(2052)]for _ in range(a)]#np.zeros(a+1,np.size(Tfeat,axis=1)+2)
    Tfeat_11 = [[random.random() for _ in range(2052)]for _ in range(b)]#np.zeros(b+1,np.size(Tfeat,axis=1)+2)
    #Tfeat_22 = [[random.random() for _ in range(2051)]for _ in range(c)]#np.zeros(b+1,np.size(Tfeat,axis=1)+2)
    Tfeat_0f = [[random.random() for _ in range(2048)]for _ in range(a)]#np.zeros(a+1,np.size(Tfeat,axis=1))
    Tfeat_1f = [[random.random() for _ in range(2048)]for _ in range(b)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    Tfeat_2f = [[random.random() for _ in range(2048)]for _ in range(c)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    Tfeat_0t = [[random.random() for _ in range(2)]for _ in range(a)]#np.zeros(a+1,np.size(Tfeat,axis=1))
    Tfeat_1t = [[random.random() for _ in range(2)]for _ in range(b)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    
    Tfeat_0tt = [[random.random() for _ in range(2)]for _ in range(f)]#np.zeros(a+1,np.size(Tfeat,axis=1))
    Tfeat_1tt = [[random.random() for _ in range(2)]for _ in range(g)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    
    Tfeat_2t = [[random.random() for _ in range(2)]for _ in range(c)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    Tfeat_2e = [[random.random() for _ in range(3)]for _ in range(c)]

    Tfeat_0p = [[random.random() for _ in range(2)]for _ in range(a)]
    Tfeat_1p = [[random.random() for _ in range(2)]for _ in range(b)]
    Tfeat_pp = []

    label_0 = [0 for i in range(a)]
    label_1 = [1 for i in range(b)]
    label_2 = [2 for i in range(c)]
    labels = []
    Tfeatal = [[random.random() for _ in range(2)]for _ in range(a+b+c)]
    Tfeatall = [[random.random() for _ in range(2048)]for _ in range(a+b+c)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    embeddings = [[random.random() for _ in range(2048)]for _ in range(a+b+c)]#np.zeros(b+1,np.size(Tfeat,axis=1))
    #print(Tfeat_0[8][2048])
    #i = 0
    for i in range(a):
        with torch.no_grad():
            Tfeat_00[i] = Tfeat_0[i]
            Tfeat_0t[i][0] = Tfeat_0[i][2050]
            Tfeat_0t[i][1] = Tfeat_0[i][2048]

            Tfeat_0p[i][0] = Tfeat_0[i][2050]
            Tfeat_0p[i][1] = Tfeat_0[i][2049]
            j = 0
            for j in range(2048):
                Tfeat_0f[i][j] = Tfeat_0[i][j]
                Tfeat_0f[i][j] = Tfeat_0f[i][j].cpu().numpy()
                j = j+1
            #label_0 += list(Tfeat_0[i][2048])
            #i = i+1
    #i = 0
    for i in range(f):
        with torch.no_grad():
            #Tfeat_00[i] = Tfeat_0[i]
            Tfeat_0tt[i][0] = Tfeat_0[i][2050]
            Tfeat_0tt[i][1] = Tfeat_0[i][2048]
            ap = Tfeat_0[i][2049]
    
    for i in range(b):
        with torch.no_grad():
            Tfeat_11[i] = Tfeat_1[i]
            Tfeat_1t[i][0] = Tfeat_1[i][2050]
            Tfeat_1t[i][1] = Tfeat_1[i][2048]

            Tfeat_1p[i][0] = Tfeat_1[i][2050]
            Tfeat_1p[i][1] = Tfeat_1[i][2049]

            j = 0
            for j in range(2048):
                Tfeat_1f[i][j] = Tfeat_1[i][j]
                Tfeat_1f[i][j] = Tfeat_1f[i][j].cpu().numpy()
                j = j+1
            #label_1 += list(Tfeat_1[i][2048])
            #i = i+1
    #i = 0
    for i in range(g):
        with torch.no_grad():
            #Tfeat_11[i] = Tfeat_1[i]
            Tfeat_1tt[i][0] = Tfeat_1[i][2050]
            Tfeat_1tt[i][1] = Tfeat_1[i][2048]
            bp = Tfeat_1[i][2049]
    
    for i in range(c):
        with torch.no_grad():
            Tfeat_2t[i][0] = Tfeat_2[i][2050]
            Tfeat_2t[i][1] = Tfeat_2[i][2048]
            Tfeat_2e[i][0] = Tfeat_2[i][2050]
            Tfeat_2e[i][1] = Tfeat_2[i][2048]
            j = 0
            for j in range(2048):
                Tfeat_2f[i][j] = Tfeat_2[i][j]
                Tfeat_2f[i][j] = Tfeat_2f[i][j].cpu().numpy()
                j = j+1
            #label_2 += list(Tfeat_2[i][2048])
            #i = i+1
    #print(Tfeat_0t,'aaaaa000000000000')
    #print(Tfeat_1t,'bbbbb111111111111')
    #print(Tfeat_2t,'ddddd000000')
    #print(Tfeat_11,'eeeee111111')
    Tfeatall = list(Tfeat_0f) + list(Tfeat_1f) + list(Tfeat_2f)
    labels = list(label_0) + list(label_1) + list(label_2)
    Tfeatal = list(Tfeat_0t) + list(Tfeat_1t) + list(Tfeat_2t)
    Tfeat_pp = list(Tfeat_0p) + list(Tfeat_1p)
    '''
    with open("txt1/1.txt", "w") as output:
        i = 0
        for i in range(a+b+c):
            s = str(Tfeatal[i]).replace('[','').replace(']','')#??????[],???????????????????????????????????????
            s = s.replace("'",'')+'\n'  #??????????????????????????????????????????????????????  .replace(',','') 
            output.write(s)
    
    #text_save(txt1, Tfeatal)
    '''






    #print(Tfeatal,'hhhhhhhhh')
    #embeddings = Tfeatall
    #Tfeatall = np.array(Tfeatall)
    #labels = np.array(labels)
    #print(label_tt)
    labelss = label_tt#.cpu().numpy()
    #idd = Tfeatal
    #print(labelss,'eeeeeeeee')
    T = 10
    #i = 0
    #Ttfeat = np.array(Tfeatall)
    #Ttfeat = Ttfeat.cpu().numpy()
    for i in range(a+b+c):
        list_logit=[np.exp(Tfeatall[i])/T]    #Tfeatall[i]         for x in enumerate(logit_t_energy)Tfeat_2f[i]
    #logit_t_energy = Tfeat_2f .detach().cpu().numpy()
    #print(logit_t_energy) 
    #-E(X)???????????????????????????????????????????????????????????????????????????????????????????
    energy = [calculate(x) for x in enumerate(list_logit)]#Tfeat_2f[i]
    #rr = a+b+c
    energy = energy/np.log(80)#1031
    #energy = torch.Tensor(energy)
    #energy = energy.cpu()
    #print(energy) 
    #i = 0
    j = 0
    x = 0
    #lab = [0 for i in range(c+b+a)]
    lab = [[random.random() for _ in range(2)]for _ in range(c+b+a)]
    
    #i = 0
    for i in range(c+b+a):
        lab[i][0] = Tfeatal[i][0]
    for i in range(c+b+a):
        if energy[0][i] < -4.55:
            lab[i][1] = 2  #Tfeat_2e[i][2] = 2
            x = x + 1   #??????e, ??????
        else:
            lab[i][1] = 4

    e = 0
    #i = 0
    w = 0
    h = 0
    for i in range(a+b+c):
        if lab[i][1] == labelss[Tfeatal[i][0]]:
            e = e + 1 #??????e ?????????
            #print(lab[i][1],labelss[Tfeatal[i][0]],e)  
    print(e,x,'237')
    #i = 0
    for i in range(a+b+c):
        if lab[i][1] == 2:
            if Tfeatal[i][1] == 2:
                h = h + 1 #???e+s ??????
    print(h,'223377888')
    #i = 0
    for i in range(a+b+c):
        if lab[i][1] == labelss[Tfeatal[i][0]]:
            if Tfeatal[i][1] == labelss[Tfeatal[i][0]]:
                w = w + 1 #???e +s?????????
    print(w,'223377')
    lab1 = [[random.random() for _ in range(2)]for _ in range(h)]
    u = 0
    for i in range(a+b+c):
        if Tfeatal[i][1] == 2:
            if lab[i][1] == 2:
                lab1[u] = lab[i]
                u = u+1
            '''    
            else:
                if i < a:
                    if Tfeat_pp[i][1]>ap:
                        Tfeat_0tt.pop()
                        Tfeat_0tt.append(Tfeat_pp[i])
                else:
                    if Tfeat_pp[i][1]>bp:
                        Tfeat_1tt.pop()
                        Tfeat_1tt.append(Tfeat_pp[i])
            '''


                

    Tfeatalll = [[random.random() for _ in range(2)]for _ in range(f+g+h)]
    Tfeatalll = list(Tfeat_0tt) + list(Tfeat_1tt) + list(lab1)

    with open("txt1/1.txt", "w") as output:
        i = 0
        for i in range(f+g+h):
            s = str(Tfeatalll[i]).replace('[','').replace(']','')#??????[],???????????????????????????????????????
            s = s.replace("'",'')+'\n'  #??????????????????????????????????????????????????????  .replace(',','') 
            output.write(s)
    
    #text_save(txt1, Tfeatal)

    '''
        if Tfeat_2e[i][2] == 2 and Tfeat_2e[i][1] == 2:
            j = j + 1 #e???????????????
            Tfeat_2t[i][1] == 3
    i = 0
    e = 0
    w = 0
    for i in range(j):
        if (Tfeat_2t[i][1] - 1) == labelss[Tfeat_2t[i][0]]:
            e = e + 1 #e+s?????????
    i = 0
    for i in range(c):
        if Tfeat_2e[i][1] == labelss[Tfeat_2t[i][0]]:
            w = w + 1 # s?????????
            print(labelss[Tfeat_2t[i][0]],'999999')    
    print(j,e,w,'237')
    
    print(energy,'wwwwwwwwww')
    '''
    per_class_acc = per_class_correct / per_class_num
    close_p = float(per_class_correct_cls.sum() / per_class_num.sum())
    print(
        '\nTest set including unknown classes:  Accuracy: {}/{} ({:.0f}%)  '
        '({:.4f}%)\n'.format(
            correct, size,
            100. * correct / size, float(per_class_acc.mean())))
    output = [step, list(per_class_acc), 'per class mean acc %s'%float(per_class_acc.mean()),
              float(correct / size), 'closed acc %s'%float(close_p)]
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=filename, format="%(message)s")
    logger.setLevel(logging.INFO)
    print(output)
    logger.info(output)


    return Tfeatall,labels

    #y = batch_hard_triplet_loss(labels, embeddings, 0.3, False)
    #y = TripletLoss(0.3,Tfeatall,labels)
    #print(y,'222222')

#def text_save(filename, data):#filename?????????CSV??????????????????data????????????????????????.
    #file = open(filename,'a')
    #for i in range(len(data)):
        #s = str(data[i]).replace('[','').replace(']','')#??????[],???????????????????????????????????????
        #s = s.replace("'",'').replace(',','') +'\n'  #??????????????????????????????????????????????????????
        #file.write(s)
    #file.close()
    #print("??????????????????")

def calculate(list_val):
    total = 0
    T = 10
    for ele in range(0, len(list_val)):
        total = total + list_val[ele]
    return T*np.log(total)

'''
def _get_triplet_mask(labels):
    
       ????????????3D???mask [a, p, n], ??????triplet???a, p, n??????valid????????????True
       ----------------------------------
       Args:
          labels: ?????????????????????labels, shape = (batch_size,)
       
       Returns:
          mask: 3D,shape = (batch_size, batch_size, batch_size)
    
    
    
    # ????????????????????????????????????(i, j)???????????????1?????????indices_not_equal
    indices_equal = tf.cast(tf.eye(tf.shape(labels)[0]), tf.bool)
    indices_not_equal = tf.logical_not(indices_equal)
    # ????????????????????????3D???mask??????(i, j, k)??????????????????????????? i_not_equal_j ????????????????????????????????????(batch_size, batch_size, 1), ????????????
    i_not_equal_j = tf.expand_dims(indices_not_equal, 2) 
    i_not_equal_k = tf.expand_dims(indices_not_equal, 1)
    j_not_equal_k = tf.expand_dims(indices_not_equal, 0)
    # ?????????i!=j!=k, ???????????????and??????, ??????????????????????????????i, j, k?????????????????????True
    distinct_indices = tf.logical_and(tf.logical_and(i_not_equal_j, i_not_equal_k), j_not_equal_k)

    # ????????????labels????????????i=j, i!=k
    label_equal = tf.equal(tf.expand_dims(labels, 0), tf.expand_dims(labels, 1))
    i_equal_j = tf.expand_dims(label_equal, 2)
    i_equal_k = tf.expand_dims(label_equal, 1)
    valid_labels = tf.logical_and(i_equal_j, tf.logical_not(i_equal_k))
    # mask?????????????????????????????????????????????3D???and
    mask = tf.logical_and(distinct_indices, valid_labels)
    return mask 
'''
def test_get_triplet_mask(labels):
    '''
    valid ???i, j, k?????????
         - i, j, k ?????????
         - labels[i] == labels[j]  && labels[i] != labels[k]
    
    '''
    # ????????????????????????????????????(i, j)???????????????1?????????indices_not_equal    
    indices_equal = np.cast[np.bool](np.eye(np.shape(labels)[0], dtype=np.int32))
    indices_not_equal = np.logical_not(indices_equal)
    # ????????????????????????3D???mask??????(i, j, k)??????????????????????????? i_not_equal_j ????????????????????????????????????(batch_size, batch_size, 1), ????????????    
    i_not_equal_j = np.expand_dims(indices_not_equal, 2)
    i_not_equal_k = np.expand_dims(indices_not_equal, 1)
    j_not_equal_k = np.expand_dims(indices_not_equal, 0)
    # ?????????i!=j!=k, ???????????????and??????
    # ??????????????????
    '''array([[[False, False, False],
               [False, False,  True],
               [False,  True, False]],
              [[False, False,  True],
               [False, False, False],
               [ True, False, False]],
              [[False,  True, False],
              [ True, False, False],
              [False, False, False]]])'''
    # ????????????(i, j, k)??????????????????True
    distinct_indices = np.logical_and(np.logical_and(i_not_equal_j, i_not_equal_k), j_not_equal_k)
    
    # ????????????labels????????????i=j, i!=k
    label_equal = np.equal(np.expand_dims(labels, 0), np.expand_dims(labels, 1))
    i_equal_j = np.expand_dims(label_equal, 2)
    i_equal_k = np.expand_dims(label_equal, 1)
    valid_labels = np.logical_and(i_equal_j, np.logical_not(i_equal_k))
    
    # mask?????????????????????????????????????????????3D???and
    mask = np.logical_and(valid_labels, distinct_indices)
    return mask
    
'''
def test_batch_all_triplet_loss(margin):
    
    # ???????????????embeddings????????????????????????????????????????????????????????????batch_size, batch_size, batch_size????????????3D??????
    # ??????????????????valid ??? mask??????    
    labels = np.array([1, 0, 1])   # ??????1???3????????????2??????????????????????????????loss?????????16-8 = 8
    pairwise_distances = test_pairwise_distances()
    anchor_positive = np.expand_dims(pairwise_distances, axis=2)
    anchor_negative = np.expand_dims(pairwise_distances, axis=1)
    triplet_loss = anchor_positive - anchor_negative + margin
    
    mask = test_get_triplet_mask(labels)
    mask = np.cast[np.float32](mask)
    triplet_loss = np.multiply(mask, triplet_loss)
    triplet_loss = np.maximum(triplet_loss, 0.0)
    
    valid_triplet_loss = np.cast[np.float32](np.greater(triplet_loss, 1e-16))
    num_positive_triplet = np.sum(valid_triplet_loss)
    num_valid_triplet_loss = np.sum(mask)
    fraction_positive_triplet = num_positive_triplet / (num_valid_triplet_loss + 1e-16)
    
    triplet_loss = np.sum(triplet_loss) / (num_positive_triplet + 1e-16)
    return triplet_loss, fraction_positive_triplet
'''

def W_Entropy(input_,w_s):
    bs = input_.size(0)
    epsilon = 1e-5
    entropy = -input_ * torch.log(input_ + epsilon)
    entropy = torch.sum(entropy, dim=1)
    return entropy 
def _pairwise_distance(embeddings, squared=False):
    #squared=False
    '''
       ????????????embedding?????????
       ------------------------------------------
       Args???
          embedding: ??????????????? ?????????batch_size, vector_size???
          squared:   ???????????????????????????????????????
    
       Returns???
          distances: ??????embeddings???????????????????????? ???batch_size, batch_size???
    '''    
    # ????????????,?????????batch_size, batch_size??????????????????????????????|a-b|^2 = a^2 -2ab + b^2, 
    # ?????? ab ????????????????????????
    
    dot_product = np.dot(embeddings, np.transpose(embeddings))   
    # dot_product????????????????????? ??????embedding?????????
    square_norm = np.diag(dot_product)
    # |a-b|^2 = a^2 - 2ab + b^2
    # tf.expand_dims(square_norm, axis=1)??????batch_size, 1??????????????????????????? ???batch_size, batch_size?????????????????????????????????????????????
    distances = np.expand_dims(square_norm, axis=1) - 2.0 * dot_product + np.expand_dims(square_norm, axis=0)
    #distances = tf.maximum(distances, 0.0)   # ??????0???????????????0
    mask = np.float32(np.equal(distances, 0.0))
    if not squared:          # ????????????????????????????????????????????????0???????????????0??????????????? 1e*-16
        distances = distances + mask * 1e-16
        distances = np.sqrt(distances)
        distances = distances * (1.0 - mask)    # 0?????????????????????0
    #print(distances) 
    return distances


def batch_all_triplet_loss(labels, embeddings, margin, d, squared=False):
    #margin = 0.5
    '''
       triplet loss of a batch
       -------------------------------
       Args:
          labels:     ???????????????shape = ???batch_size,???
          embeddings: ???????????????????????? shape = (batch_size, vector_size)
          margin:     margin????????? scalar
          
       Returns:
          triplet_loss: scalar, ??????batch????????????
          fraction_postive_triplets : valid???triplets????????????
    '''
    d = d.cpu()
    d = d.detach().numpy()#np.array(d.cpu())
    #print(d,'d')
    d1 = [0 for _ in range(32)]
    for i in range(32):
        d1[i] = d[i][0]
        
        #print(d[i][0],'di')
    #print(d1,'d1')

    #dall = []
    #dall = torch.from_numpy(np.array(dall))

    #d1 = torch.from_numpy(np.array(d1))
    da1 = [[0 for _ in range(32)] for _ in range(32)]
    #d = torch.from_numpy(d)
    for i in range(32):
        da = d1[i] - d1
        for j in range(32):
            da1[i][j] = da[j]
        '''
        if i == 0:
            dall = da
            dall = torch.from_numpy(dall)
            print(dall,i)
        if i != 0:
            dall = torch.cat((dall, da.cpu()), 0)
            print(dall,i)
        '''
    #print(da1,'da1')

    dall1 = np.expand_dims(da1, axis=2)#.detach().numpy()
    dall2 = np.expand_dims(da1, axis=1)#.detach().numpy()
    dall0 = dall1 - dall2
    #print(dall0, np.size(dall0,0), np.size(dall0,1), np.size(dall0,2),'dall0')
    # ???????????????embeddings????????????????????????????????????????????????????????????batch_size, batch_size, batch_size????????????3D??????
    # ??????????????????valid ??? mask??????
    pairwise_distances = _pairwise_distance(embeddings, squared=squared)
    anchor_positive = np.expand_dims(pairwise_distances, axis=2)
    anchor_negative = np.expand_dims(pairwise_distances, axis=1)
    #print(anchor_positive,anchor_negative,'anchor_negative')
    triplet_loss = anchor_positive - anchor_negative + margin
    for i in range(32):
        for j in range(32):
            for k in range(32):
                #print(dall0[i][j][k])
                #print(triplet_loss[i][j][k])
                if dall0[i][j][k] > 0:
                    if triplet_loss[i][j][k] > 0:
                        triplet_loss[i][j][k] = 0 
            
    #print(triplet_loss, np.size(triplet_loss,0), np.size(triplet_loss,1),np.size(triplet_loss,2),'triplet_loss')
    #input()
    #anchor_positive_dist = tf.expand_dims(pairwise_dis, 2)
    #assert anchor_positive_dist.shape[2] == 1, "{}".format(anchor_positive_dist.shape)
    #anchor_negative_dist = tf.expand_dims(pairwise_dis, 1)
    #assert anchor_negative_dist.shape[1] == 1, "{}".format(anchor_negative_dist.shape)
    #triplet_loss = anchor_positive_dist - anchor_negative_dist + margin
    
    mask = test_get_triplet_mask(labels)
    mask = np.cast[np.float32](mask)
    #??????????????????
    triplet_loss = np.multiply(mask, triplet_loss)#??????
    triplet_loss = np.maximum(triplet_loss, 0.0)
    # ??????????????????x???y
    # x???y????????????????????????
    
    valid_triplet_loss = np.cast[np.float32](np.greater(triplet_loss, 1e-16))#??????x1????????????x2
    num_positive_triplet = np.sum(valid_triplet_loss)
    num_valid_triplet_loss = np.sum(mask)
    fraction_positive_triplet = num_positive_triplet / (num_valid_triplet_loss + 1e-16)
    
    triplet_loss = np.sum(triplet_loss) / (num_positive_triplet + 1e-16)
    return triplet_loss#, fraction_positive_triplet

    #mask = tf.to_float(mask)
    #triplet_loss = tf.multiply(mask, triplet_loss)
    #triplet_loss = tf.maximum(triplet_loss, 0.0)
    
    # ??????valid???triplet??????????????????????????????triplet loss?????????
    #valid_triplets = tf.to_float(tf.greater(triplet_loss, 1e-16))
    #num_positive_triplets = tf.reduce_sum(valid_triplets)
    #num_valid_triplets = tf.reduce_sum(mask)
    #fraction_postive_triplets = num_positive_triplets / (num_valid_triplets + 1e-16)
    
    #triplet_loss = tf.reduce_sum(triplet_loss) / (num_positive_triplets + 1e-16)
    #print(triplet_loss, fraction_postive_triplets) 
    #return triplet_loss#, fraction_postive_triplets


def _get_anchor_positive_triplet_mask(labels):
    ''' 
       ???????????????positive???mask??? ???2D????????????[a, p], a!=p and a???p??????labels
       ------------------------------------------------
       Args:
          labels: ???????????????shape = (batch_size, )
          
       Returns:
          mask: ?????????positive mask, shape = (batch_size, batch_size)
    '''
    indices_equal = np.cast[np.bool](np.eye(np.shape(labels)[0]))
    indices_not_equal = np.logical_not(indices_equal)               #i,j?????????
    labels_equal = np.equal(np.expand_dims(labels, 0), np.expand_dims(labels, 1))   #label??????
    mask = np.logical_and(indices_not_equal, labels_equal)           # ???and??????
    #print('111111') 
    #print(mask,'111111') 
    return mask

def _get_anchor_negative_triplet_mask(labels):
    '''
       ??????negative???2D mask, [a, n] ??????a, n?????????????????????labels
       ------------------------------------------------
       Args:
          labels: ???????????????shape = (batch_size, )
          
       Returns:
          mask: negative mask, shape = (batch_size, batch_size)
    '''
    labels_equal = np.equal(np.expand_dims(labels, 0), np.expand_dims(labels, 1))
    mask = np.logical_not(labels_equal)
    #print(mask,'22222222')
    #print('222222') 
    return mask


def batch_hard_triplet_loss(labels, embeddings, margin, squared=False):
    #margin = 0.3
    '''
       batch hard triplet loss of a batch??? ?????????????????????positive?????? - ?????????????????????negative??????
       ------------------------------------
       Args:
          labels:     ???????????????shape = ???batch_size,???
          embeddings: ???????????????????????? shape = (batch_size, vector_size)
          margin:     margin????????? scalar
          
       Returns:
          triplet_loss: scalar, ??????batch????????????
    '''
    pairwise_distances = _pairwise_distance(embeddings)
    mask_anchor_positive = _get_anchor_positive_triplet_mask(labels)
    mask_anchor_positive = np.cast[np.float](mask_anchor_positive)
    #mask_anchor_positive = tf.to_float(mask_anchor_positive)
    anchor_positive_dist = np.multiply(mask_anchor_positive, pairwise_distances)
    hardest_positive_dist = np.max(anchor_positive_dist, axis=1, keepdims=True)  # ????????????????????????????????????positive??????
    tf.summary.scalar("hardest_positive_dis", tf.reduce_mean(hardest_positive_dist))
    
    '''???????????????????????????????????????invalid [a, n]?????????0??? ????????????????????????????????????invalid??????????????????????????????????????????????????????????????????'''
    mask_anchor_negative = _get_anchor_negative_triplet_mask(labels)
    mask_anchor_negative = np.cast[np.float](mask_anchor_negative)
    #mask_anchor_negative = tf.to_float(mask_anchor_negative)
    max_anchor_negative_dist = np.max(pairwise_distances, axis=1, keepdims=True)   # ??????????????????
    anchor_negative_dist = pairwise_distances + max_anchor_negative_dist * (1.0 - mask_anchor_negative)  # (1.0 - mask_anchor_negative)??????invalid??????
    hardest_negative_dist = np.min(anchor_negative_dist, axis=1, keepdims=True)
    #hardest_negative_dist = tf.reduce_min(anchor_negative_dist, axis=1, keepdims=True)
    
    #tf.summary.scalar("hardest_negative_dist", tf.reduce_mean(hardest_negative_dist))
    
    #triplet_loss = tf.maximum(hardest_positive_dist - hardest_negative_dist + margin, 0.0)
    #triplet_loss = tf.reduce_mean(triplet_loss)

    triplet_loss = np.maximum(hardest_positive_dist - hardest_negative_dist + margin, 0.0)
    triplet_loss = np.mean(triplet_loss)
    #print('333333') 
    #print(triplet_loss,'3333333')
    return triplet_loss










def convert_label_to_similarity(normed_feature:Tensor, label:Tensor) -> Tuple[Tensor, Tensor]:
    similarity_matrix = normed_feature @ normed_feature.transpose(1, 0)
    label_matrix = label.unsqueeze(1) == label.unsqueeze(0)

    positive_matrix = label_matrix.triu(diagonal=1)
    negative_matrix = label_matrix.logical_not().triu(diagonal=1)

    similarity_matrix = similarity_matrix.view(-1)
    positive_matrix = positive_matrix.view(-1)
    negative_matrix = negative_matrix.view(-1)
    return similarity_matrix[positive_matrix], similarity_matrix[negative_matrix]


class CircleLoss(nn.Module):
    def __init__(self, m: float, gamma: float) -> None:
        super(CircleLoss, self).__init__()
        self.m = m
        self.gamma = gamma
        self.soft_plus = nn.Softplus()

    def forward(self, sp: Tensor, sn: Tensor) -> Tensor:
        ap = torch.clamp_min(- sp.detach() + 1 + self.m, min=0.)
        an = torch.clamp_min(sn.detach() + self.m, min=0.)

        delta_p = 1 - self.m
        delta_n = self.m

        logit_p = - ap * (sp - delta_p) * self.gamma
        logit_n = an * (sn - delta_n) * self.gamma

        loss = self.soft_plus(torch.logsumexp(logit_n, dim=0) + torch.logsumexp(logit_p, dim=0))

        return loss

'''
if __name__ == "__main__":
    feat = nn.functional.normalize(torch.rand(8, 64, requires_grad=True))
    lbl = torch.randint(high=10, size=(8,))

    inp_sp, inp_sn = convert_label_to_similarity(feat, lbl)

    criterion = CircleLoss(m=0.25, gamma=256)
    circle_loss = criterion(inp_sp, inp_sn)

    print(circle_loss)
'''






###########################################################################################################




def test_class_inc(step, dataset_test, name, num_class, G, C, known_class):
    G.eval()
    C.eval()
    ## Known Score Calculation.
    correct = 0
    size = 0
    per_class_num = np.zeros((num_class))
    per_class_correct = np.zeros((num_class)).astype(np.float32)
    class_list = [i for i in range(num_class)]
    for batch_idx, data in enumerate(dataset_test):
        with torch.no_grad():
            img_t, label_t, path_t = data[0], data[1], data[2]
            img_t, label_t = img_t.cuda(), label_t.cuda()
            feat = G(img_t)
            out_t = C(feat)
            out_t = F.softmax(out_t)
            pred = out_t.data.max(1)[1]
            correct += pred.eq(label_t.data).cpu().sum()
            pred = pred.cpu().numpy()
            k = label_t.data.size()[0]

            for i, t in enumerate(class_list):
                t_ind = np.where(label_t.data.cpu().numpy() == t)
                correct_ind = np.where(pred[t_ind[0]] == t)
                per_class_correct[i] += float(len(correct_ind[0]))
                per_class_num[i] += float(len(t_ind[0]))
            size += k
            label_t = label_t.data.cpu().numpy()
            if batch_idx == 0:
                label_all = label_t
                pred_all = out_t.data.cpu().numpy()
            else:
                pred_all = np.r_[pred_all, out_t.data.cpu().numpy()]
                label_all = np.r_[label_all, label_t]
    per_class_acc = per_class_correct / per_class_num
    print(
        '\nTest set including unknown classes:  Accuracy: {}/{} ({:.0f}%)  '
        '({:.4f}%)\n'.format(
            correct, size,
            100. * correct / size, float(per_class_acc.mean())))
    close_p = 100. * float(correct) / float(size)
    output = [step, "closed", list(per_class_acc), float(per_class_acc.mean()),
              "acc known %s"%float(per_class_acc[:known_class].mean()),
              "acc novel %s"%float(per_class_acc[known_class:].mean()), "acc %s"%float(close_p)]
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=name, format="%(message)s")
    logger.setLevel(logging.INFO)
    logger.info(output)
    print(output)
    return float(per_class_acc[:known_class].mean()), float(per_class_acc[known_class:].mean())


def feat_get(step, G, C1, dataset_source, dataset_target, save_path):
    G.eval()
    C1.eval()

    for batch_idx, data in enumerate(dataset_source):
        if batch_idx == 500:
            break
        with torch.no_grad():
            img_s = data[0]
            label_s = data[1]
            img_s, label_s = Variable(img_s.cuda()), \
                             Variable(label_s.cuda())
            feat_s = G(img_s)
            if batch_idx == 0:
                feat_all_s = feat_s.data.cpu().numpy()
                label_all_s = label_s.data.cpu().numpy()
            else:
                feat_s = feat_s.data.cpu().numpy()
                label_s = label_s.data.cpu().numpy()
                feat_all_s = np.r_[feat_all_s, feat_s]
                label_all_s = np.r_[label_all_s, label_s]
    for batch_idx, data in enumerate(dataset_target):
        if batch_idx == 500:
            break
        with torch.no_grad():
            img_t = data[0]
            label_t = data[1]
            img_t, label_t = Variable(img_t.cuda()), \
                             Variable(label_t.cuda())
            feat_t = G(img_t)
            if batch_idx == 0:
                feat_all = feat_t.data.cpu().numpy()
                label_all = label_t.data.cpu().numpy()
            else:
                feat_t = feat_t.data.cpu().numpy()
                label_t = label_t.data.cpu().numpy()
                feat_all = np.r_[feat_all, feat_t]
                label_all = np.r_[label_all, label_t]
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)
    np.save(os.path.join(save_path, "save_%s_target_feat.npy" % step), feat_all)
    np.save(os.path.join(save_path, "save_%s_source_feat.npy" % step), feat_all_s)
    np.save(os.path.join(save_path, "save_%s_target_label.npy" % step), label_all)
    np.save(os.path.join(save_path, "save_%s_source_label.npy" % step), label_all_s)
