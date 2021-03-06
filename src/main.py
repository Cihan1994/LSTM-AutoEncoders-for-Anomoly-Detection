import os

import torch
import data_representation as data
import model as m
import utils


def run_pipeline(args: dict):

    # return the dataset, perform the usual imputation
    # standardization, scaling etc
    dataset = data.return_dataset(args=args)

    if args['model']['train_model']:
        # implementation of a LSTM auto-encoder
        rnn_ae = m.RecurrentAutoencoder(
            seq_len=dataset['seq_len'],
            n_features=dataset['n_features'],
            embedding_dim=16
        )

        rnn_ae, performance = utils.train_model(
            model=rnn_ae,
            train_data=dataset['train'],
            val_data=dataset['valid'],
            n_epochs=200
        )

        # plot and save the performance
        utils.plot_training_performance(
            data=performance
        )

        # save the model
        utils.save_model(
            model=rnn_ae,
            save_dir=os.path.join(os.path.dirname(os.getcwd()), 'model', 'model.wt')
        )

    else:
        rnn_ae = torch.load(
            os.path.join(os.path.dirname(os.getcwd()), 'model', 'model.wt')
        )


    # gather the reconstruction loss so to set a threshold for
    # anomoly detection
    _, anom_losses = utils.predict(model=rnn_ae, dataset=dataset['train'])

    utils.plot_reconstruction_loss(
        data=anom_losses,
        title="Distribution of Training Reconstruction Loss",
        fname='train_reconstruction_loss.png',
        xlim=[0, 0.4]
    )

    # threshold set via manual inspection of the distribution plot above
    anomoly_threshold = 0.07

    # test on the anomoly dataset
    _, losses = utils.predict(model=rnn_ae, dataset=dataset['anomoly'])

    utils.plot_reconstruction_loss(
        data=losses,
        title="Distribution of Anomoly Reconstruction Loss",
        fname="anomoly_reconstruction_loss.png",
        xlim=[0, 0.5]
    )

    _,te_losses = utils.predict(model=rnn_ae, dataset=dataset['test'])

    utils.plot_reconstruction_loss(
        data=te_losses,
        title="Distribution of Test Reconstruction Loss",
        fname="test_reconstruction_loss.png",
        xlim=[0, 0.5]
    )

    f1 = utils.evaluate_model(
        te_loss=te_losses,
        anom_loss=anom_losses,
        threshold=anomoly_threshold,
    )

    print(f'FINAL MODEL PERFORMANCE.. {f1}')



if __name__=="__main__":

    args = {
        'task': 'time-series',
        'data': {
            'labels': 'eighthr.names',
            'values': 'eighthr.data',
        },
        'model': {
            'train_model': True
        }
    }

    run_pipeline(args)