import numpy as np
import nibabel as nib
import tensorflow as tf


def read_nifti(path):
    scan = nib.load(path)

    return np.flip(np.rot90(scan.get_fdata()))

class ImageFeeder(tf.keras.utils.Sequence):

    def __init__(self,
                 flr_paths,
                 tar_paths,
                 t1w_paths=None,
                 batch_size=8,
                 shuffle=True,
                 preprocessing=None,
                 augmentation=None):

        #check that the same number of path for input images and targets is provided
        assert len(flr_paths) == len(tar_paths)

        # check that the nuber of input images is greater than the required number of image for each batch
        assert  batch_size <= len(flr_paths)

        if t1w_paths is not None:
            assert len(t1w_paths) == len(flr_paths)

        self.flr_paths = flr_paths
        self.tar_paths = tar_paths
        self.t1w_paths = t1w_paths
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.preprocessing = preprocessing
        self.augmentation = augmentation
        self.indexes = np.arange(0, len(flr_paths), 1)

        self.on_epoch_end()

    def __len__(self):
        '''
        Get the total number of step for each epoch
        '''
        return len(self.indexes) // self.batch_size

    def __getitem__(self, idx):

        idxs = self.indexes[idx * self.batch_size : (1 + idx) * self.batch_size]

        # load the required images

        X = np.asarray([read_nifti(self.flr_paths[i]) for i in idxs])[..., np.newaxis]
        y = np.asarray([read_nifti(self.tar_paths[i]) for i in idxs])[..., np.newaxis]

        if self.t1w_paths is not None:
            Xt =  np.asarray([read_nifti(self.t1w_paths[i]) for i in idxs])[..., np.newaxis]
            X = np.concatenate([X, Xt], axis=3)
        X = X.astype(np.float32)
        y = y.astype(np.float32)

        if self.augmentation is not None:
            X, y = self.augmentation(X, y)
        if self.preprocessing is not None:
            X, y = self.preprocessing(X, y)

        return X, y

    def on_epoch_end(self):
        '''
        Shuffle the indexes at the end of each epoch
        '''
        if self.shuffle:
            np.random.shuffle(self.indexes)