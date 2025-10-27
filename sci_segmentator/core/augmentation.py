import numpy as np
import albumentations as A

class DataAugmentation:

    def __init__(self, transform : list):

        self.transform = A.Compose(transform)


    def __call__(self, image, mask):

        X = []
        y = []

        for im, ms in zip(image, mask):

            sample = self.transform(image=im, mask=ms)
            X.append(sample['image'])
            y.append(sample['mask'])

        return np.asarray(X), np.asarray(y)
