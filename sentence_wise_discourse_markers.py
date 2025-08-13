
import os
import csv
from conllu import parse
import networkx as nx

def statistics_corpus(file_in, file_out):
    file_out = os.path.join(file_out, "Sentence_Wise_Discourse_markers.csv") 
    with open(file_out, "w",encoding="utf-8", newline='',) as csvfile: 
    
        csvwriter = csv.writer(csvfile, delimiter = ',')   
        csvwriter.writerow(["Phase", "File", "Sent Id", "Sentence Length","Discourse Marker","Part of Speech"])
        dirs = sorted(os.listdir(file_in))       # Creating sorted list of directories from given path
        print('dir',dirs)
        # for every file in the directory
        count_sent_na = 0
        count_sent_to = 0
        count_sent_hi = 0 
        count_sent_bhi = 0
        for file in dirs:
            print('file',file)
            if not os.path.isfile((file_in+str(file))):         # Ignoring the files and only considering folders in given path  

                phase_dir = sorted(os.listdir(file_in+str(file)))
                # print("p_dir",phase_dir)
                Phase = file[-1]                                  # Considering the phase of output files

                for phases in phase_dir:
                    if not os.path.isfile((file_in+str(file)+"/"+str(phases))):
                        outputfiles_dir = sorted(os.listdir(file_in+str(file)+"/"+str(phases)))   # Accessing output files folder in each phase
                        # print("output",outputfiles_dir)
                        for output_file in outputfiles_dir:
                            filename = file_in+str(file)+"/"+str(phases)+"/"+str(output_file)    # Looping over each output file in output files folder
                            print("filename",filename)
                            if filename.endswith(".conllu"):#filename.endswith(".txt"):
                                filename_in = filename

                                data_file = open(str(filename_in),'r',encoding='utf-8').read()
                                file1 = parse(data_file)       # Loading CoNLL output file using pyconll module

                                # count_sent = 0   
                                token_sent = 0
                                for sentence in file1:
                                    # count_sent+=1             # Counting number of sentences in each output file
                                    # print(count_sent)
                                    sentence_length=0
                                    # print(sentence.metadata['sent_id'])
                                    
                                    tree = nx.DiGraph()                              # An empty directed graph (i.e., edges are uni-directional)
                                    for nodeinfo in sentence[0:]:                    # retrieves information of each node from dependency tree in UD format
                                        entry=list(nodeinfo.items())
                                        tree.add_node(entry[0][1], form=entry[1][1], lemma=entry[2][1], upostag=entry[3][1], xpostag=entry[4][1], feats=entry[5][1], head=entry[6][1], deprel=entry[7][1], deps=entry[8][1], misc=entry[9][1])                #adds node to the directed graph
                                    ROOT=0
                                    tree.add_node(ROOT)                            # adds an abstract root node to the directed graph

                                    for nodex in tree.nodes:
                                        if not nodex==0:
                                            if tree.has_node(tree.nodes[nodex]['head']):                                         # to handle disjoint trees
                                                tree.add_edge(tree.nodes[nodex]['head'],nodex,drel=tree.nodes[nodex]['deprel'])       # adds edges as relation between nodes

                                    n=len(tree.edges) #length of sentence 
                                    dd=[]
                                    for edgex in tree.edges:
                                        if not edgex[0]==ROOT:
                                            dd_temp=dependency_distance(tree, ROOT,edgex)
                                            dd.append(dd_temp)
                                    if dd == []:
                                        dd=[1]
                                    # print(dd)
                                    sentence_str = (sentence.metadata['Sentence'])
                                    if " ना " in sentence_str or " तो " in sentence_str or " ही " in sentence_str or " भी " in sentence_str:
                                        d_m=""
                                        # print(count_sent, sentence_str)
                                        if " ना " in sentence_str:
                                            d_m="na"
                                            count_sent_na+=1 
                                        if " तो " in sentence_str:
                                            d_m="to"
                                            count_sent_to+=1 
                                        if " ही " in sentence_str:
                                            d_m="hi"
                                            count_sent_hi+=1
                                        if " भी " in sentence_str:
                                            d_m="bhi"
                                            count_sent_bhi+=1
                                        for token in sentence:       #counting number of token in each sentence
                                            token_sent+=1 
                                            if token["form"]=="ना":
                                                pos=token["upos"]
                                            if "_" not in token["form"]: #if its not a chunk
                                                sentence_length+=1
                                            else:
                                                if token["misc"]!= None:
                                                    for i in token["misc"].keys():#miscellaneous column
                                                        if i == 'CodeSwitch' or i == "Quote" or i=="Expletive":
                                                            chunk_split=token["form"].split("_")
                                                            sentence_length+=len(chunk_split)
                                        csvwriter.writerow([Phase, output_file.replace("_output", ""), sentence.metadata['sent_id'], sentence_length, d_m, pos])
        print(count_sent_na, count_sent_to, count_sent_hi, count_sent_bhi)

def dependency_distance(tree, root, edge):        # Computes the dependency length i.e., no. of nodes between head and its dependent 
    dd=0
    if edge[0]>edge[1]:                      
        for nodex in nx.descendants(tree, root):        
            if edge[1]<=nodex<edge[0]:                             # all the nodes that lies linearly between dependent and head   
                dd+=1
    else:
        for nodex in nx.descendants(tree, root):
            if edge[0]<=nodex<edge[1]:
                dd+=1
    return dd
file_in ="C:/Users/meghn/OneDrive/Documents/Psycholing/Dialouge_Corpus DataAnalysis/data_files/parse_gold/"
file_out ="C:/Users/meghn/OneDrive/Documents/Phd - work/doweny lab/Discourse Analysis/"
statistics_corpus(file_in, file_out)
         