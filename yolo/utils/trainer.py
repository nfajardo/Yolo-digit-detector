# -*- coding: utf-8 -*-
import os

from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard


def train_yolo(model,
               loss_func,
               train_batch_gen,
               valid_batch_gen,
               learning_rate = 1e-4,
               nb_epoch = 300,
               train_times = 1,
               valid_times = 1,
               saved_weights_name = 'best_weights.h5',
               ):
    """A function that performs training on a general keras model.

    # Args
        model : keras.models.Model instance
        loss_func : function
            refer to https://keras.io/losses/

        train_batch_gen : keras.utils.Sequence instance
        valid_batch_gen : keras.utils.Sequence instance
        learning_rate : float
        train_times : int
        valid_times : int
        saved_weights_name : str
    """
    # 1. create optimizer
    optimizer = Adam(lr=learning_rate, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    
    # 2. create loss function
    model.compile(loss=loss_func,
                  optimizer=optimizer)

    # 4. training
    model.fit_generator(generator = train_batch_gen,
                        steps_per_epoch  = len(train_batch_gen) * train_times, 
                        epochs           = nb_epoch, 
                        verbose          = 1,
                        validation_data  = valid_batch_gen,
                        validation_steps = len(valid_batch_gen) * valid_times,
                        callbacks        = _create_callbacks(saved_weights_name), 
                        workers          = 3,
                        max_queue_size   = 8)

def _create_callbacks(saved_weights_name):
    # Make a few callbacks
    early_stop = EarlyStopping(monitor='val_loss', 
                       min_delta=0.001, 
                       patience=3, 
                       mode='min', 
                       verbose=1)
    checkpoint = ModelCheckpoint(saved_weights_name, 
                                 monitor='val_loss', 
                                 verbose=1, 
                                 save_best_only=True, 
                                 mode='min', 
                                 period=1)
    tb_counter  = len([log for log in os.listdir(os.path.expanduser('~/logs/')) if 'yolo' in log]) + 1
    tensorboard = TensorBoard(log_dir=os.path.expanduser('~/logs/') + 'yolo' + '_' + str(tb_counter), 
                              histogram_freq=0, 
                              write_graph=True, 
                              write_images=False)
    callbacks = [early_stop, checkpoint, tensorboard]
    return callbacks