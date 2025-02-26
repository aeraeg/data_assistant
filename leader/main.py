'''
this model based on Character-Level LSTM in PyTorch form udacity
recurrent-neural-networks/char-rnn
we also use word2vec-embeddings 
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import torch
from torch import nn
import torch.nn.functional as F
#from local library
from .network import TextRnn as Model

class Ai_thinking():    
    def __init__(self,folder,readfile,readsheet,column1,column2,writefile):
        #self.folder=folder
        self.folder=folder
        self.readfile=readfile
        self.readsheet=readsheet
        self.column1=column1
        self.column2=column2
        self.writefile=writefile        
    def show_data(self):
        os.chdir(self.folder)
        from .utiliy import get_batches
        #Load and prepare the data

        reader=pd.read_excel(self.readfile,self.readsheet)
        reader_filter=reader[reader["category"]=="products_items"]
        reader_item=reader_filter[[self.column1 , self.column2]]
        #reader_item["id_inside_cagegory"]=reader_item[self.column2]
        #https://towardsdatascience.com/multi-class-text-classification-with-lstm-1590bee1bd17
        print("Info",reader_item.info())
        print("reader_item",reader_item[:10])
        print("reader_item[""names]",reader_item["names"][:10])

        print("reader_item.id_inside_cagegory",reader_item.id_inside_cagegory[:10])
       
        ## split by new lines and spaces
        #reviews_split = all_text.split('\n')
        #all_text = ' '.join(reviews_split)

        ## create a list of words
        #words = all_text.split()

        reader_names=reader_item.names.value_counts()
        print("______names categories________",reader_names[5])

        reader_id=reader_item.id_inside_cagegory.value_counts()
        print("______id categories________",reader_id)

        #reader_inside_category=reader_item.reader_inside_category.value_counts()
        # encode the text and map each character to an integer and vice versa

        # we create two dictionaries:
            #first deictionaries for id
        chars_id = tuple(set(reader_id))
        int2char = dict(enumerate(chars_id))
        char2int = {ch: ii for ii, ch in int2char.items()}
        
        ## encode the text
        encoded_id = np.array([char2int[ch] for ch in reader_id])
        
        #========================================

        print("encoded_id categories",encoded_id[:100])
        #data pre-process for names
        chars_names = tuple(set(reader_names))
        int2char_id = dict(enumerate(chars_id))
        char2int_id = {ch: ii for ii, ch in int2char.items()}
        print("____________ reader_name categories",reader_names[5])
        ## encode the text
        encoded_names= np.array([char2int[ch] for ch in reader_names])
        print("encoded_name categories",encoded_names[:100])
           #second deictionaries for name
        #filter names by id
        #list_id=list(reader_item["id_inside_cagegory"])
        print("reader_id",reader_names.value_counts())
        names=[]
        for id in reader_id.value_counts():
            reader_item_filter=reader_item[reader_item["id_inside_cagegory"]==id]
            names_items=[]
            for i in reader_item_filter.names:
                names_items.append(reader_item_filter.names)
                names.append(names_items)
            #return names
        print("names",names[:5])
        writer = pd.ExcelWriter(self.writefile)
        names_df=pd.DataFrame(names)
        names_df.to_excel(writer,"data")
        
        writer.save()

        chars_id = tuple(set(reader_names))
        int2char_name = dict(enumerate(chars_id))
        char2int_name = {ch: ii for ii, ch in int2char_name.items()}
        
        
        ## encode the text
        encoded_id = np.array([char2int_name[ch] for ch in reader_names])
        print("encoded_id categories",encoded_id)

        #Pre-processing the data¶
        def one_hot_encode(self,arr, n_labels):
            '''
             LSTM expects an input that is one-hot encoded_id meaning that each character 
             is converted into an integer (via our created dictionary) 
             and then converted into a column vector where only it's corresponding integer index will have the value of 1 and the rest of the vector will be filled with 0's. Since we're one-hot encoding the data
            '''
            # Initialize the the encoded_id array
            one_hot = np.zeros((np.multiply(*arr.shape), n_labels), dtype=np.float32)
            
            # Fill the appropriate elements with ones
            one_hot[np.arange(one_hot.shape[0]), arr.flatten()] = 1.
            
            # Finally reshape it to get back to the original array
            one_hot = one_hot.reshape((*arr.shape, n_labels))
            
            return one_hot
        # check that the function works as expected
        test_seq = np.array([[3, 5, 1]])
        one_hot = one_hot_encode(self,test_seq, 8)

        print("____one_hot____",one_hot)
        
        #to switch between id and name
        #encoded=encoded_id
        encoded=encoded_names
        
        self.batches = get_batches(encoded, 8, 50)
        
        self.x, self.y = next(self.batches)
        # printing out the first 10 items in a sequence
        print('x\n', self.x[:10, :10])
        print('\ny\n', self.y[:10, :10])

        # check if GPU is available
        train_on_gpu = torch.cuda.is_available()
        if(train_on_gpu):
            print('Training on GPU!')
        else: 
            print('No GPU available, training on CPU; consider making n_epochs very small.')
        ## : set you model hyperparameters
        # define and print the net
        n_hidden=512
        n_layers=2
    
        #net = Model(chars_names, n_hidden, n_layers)
        #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        #net = Model(chars_id, n_hidden, n_layers).to(device)
        net = Model(chars_id, n_hidden, n_layers)
        #optimizer = optim.Adam(model.parameters())
        #loss_fn = torch.nn.BCELoss()

        print(net)
        batch_size = 128
        seq_length = 100
        n_epochs =  20 # start small if you are just testing initial behavior

        # train the model
##_________________________________________
        def train(net, data, epochs, batch_size, seq_length, lr=0.001, clip=5, val_frac=0.1, print_every=10):
            ''' Training a network 
            
                Arguments
                ---------
                
                net: CharRNN network
                data: text data to train the network
                epochs: Number of epochs to train
                batch_size: Number of mini-sequences per mini-batch, aka batch size
                seq_length: Number of character steps per mini-batch
                lr: learning rate
                clip: gradient clipping
                val_frac: Fraction of data to hold out for validation
                print_every: Number of steps for printing training and validation loss            
            '''
            net.train()
            
            opt = torch.optim.Adam(net.parameters(), lr=lr)
            criterion = nn.CrossEntropyLoss()
            
            # create training and validation data
            val_idx = int(len(data)*(1-val_frac))
            data, val_data = data[:val_idx], data[val_idx:]
            train_on_gpu = torch.cuda.is_available()
            if(train_on_gpu):
                net.cuda()
            
            counter = 0
            n_chars = len(net.chars)
            print("get_batches",get_batches(data, batch_size, seq_length))
            for e in range(epochs):
                # initialize hidden state
                h = net.init_hidden(batch_size)
                for x, y in get_batches(data, batch_size, seq_length):
                    counter += 1
                    print("i am on train")

                    # One-hot encode our data and make them Torch tensors
                    x = one_hot_encode(self,x, n_chars)
                    inputs, targets = torch.from_numpy(x), torch.from_numpy(y)
                    if(train_on_gpu):
                        inputs, targets = inputs.cuda(), targets.cuda()

                    # Creating new variables for the hidden state, otherwise
                    # we'd backprop through the entire training history
                    h = tuple([each.data for each in h])
                    

                    # zero accumulated gradients
                    net.zero_grad()
                    # get the output from the model
                    output, h = net(inputs, h)
                    

                    # calculate the loss and perform backprop
                    loss = criterion(output, targets.view(batch_size*seq_length))
                    loss.backward()
                    # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
                    nn.utils.clip_grad_norm_(net.parameters(), clip)
                    opt.step()
                    
                    

                    # loss stats
                    if counter % print_every == 0:
                        # Get validation loss
                        val_h = net.init_hidden(batch_size)
                        val_losses = []
                        net.eval()
                        for x, y in get_batches(val_data, batch_size, seq_length):
                            # One-hot encode our data and make them Torch tensors
                            x = one_hot_encode(x, n_chars)
                            x, y = torch.from_numpy(x), torch.from_numpy(y)
                            
                            # Creating new variables for the hidden state, otherwise
                            # we'd backprop through the entire training history
                            val_h = tuple([each.data for each in val_h])
                            
                            inputs, targets = x, y
                            if(train_on_gpu):
                                inputs, targets = inputs.cuda(), targets.cuda()

                            output, val_h = net(inputs, val_h)
                            val_loss = criterion(output, targets.view(batch_size*seq_length))
                        
                            val_losses.append(val_loss.item())
                        
                        net.train() # reset to train mode after iterationg through validation data
                        print("Epoch: {}/{}...".format(e+1, epochs),
                            "Step: {}...".format(counter),
                            "Loss: {:.4f}...".format(loss.item()),
                            "Val Loss: {:.4f}".format(np.mean(val_losses)))
#_________________________________________
        train(net, encoded, epochs=n_epochs, batch_size=batch_size, seq_length=seq_length, lr=0.001, print_every=10)

        ## change the name, for saving multiple files

        model_name = 'rnn_x_epoch.net'

        checkpoint = {'n_hidden': net.n_hidden,
                    'n_layers': net.n_layers,
                    'state_dict': net.state_dict(),
                    'tokens': net.chars}

        with open(model_name, 'wb') as f:
            torch.save(checkpoint, f)
        # change the name, for saving multiple files
        
        model_name = 'rnn_x_epoch.net'

        checkpoint = {'n_hidden': net.n_hidden,
                    'n_layers': net.n_layers,
                    'state_dict': net.state_dict(),
                    'tokens': net.chars}

        with open(model_name, 'wb') as f:
            torch.save(checkpoint, f)
