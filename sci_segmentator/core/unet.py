import tensorflow.keras as keras
from tensorflow.keras import layers as L
from tensorflow.keras.models import Model

def get_crop_shape(target, refer):
    '''
    '''
    cw = target.shape[2] - refer.shape[2]
    
    assert (cw >= 0)
    if cw % 2 != 0:
        cw1, cw2 = int(cw/2), int(cw/2) + 1
    else:
        cw1, cw2 = int(cw/2), int(cw/2)
    # height, the 2nd dimension
    ch = target.shape[1] - refer.shape[1]

    assert (ch >= 0)
    if ch % 2 != 0:
        ch1, ch2 = int(ch/2), int(ch/2) + 1
    else:
        ch1, ch2 = int(ch/2), int(ch/2)

    return (ch1, ch2), (cw1, cw2)


def get_unet(inputs):

    #inputs = L.Input(shape=image_shape)

    conv1 = L.Conv2D(filters=64, kernel_size=5, strides=1, activation='relu', padding='same', data_format='channels_last')(inputs)
    conv1 = L.Conv2D(filters=64, kernel_size=5, strides=1, activation='relu', padding='same', data_format='channels_last')(conv1)
    pool1 = L.MaxPooling2D(pool_size=(2, 2), data_format='channels_last')(conv1)

    conv2 = L.Conv2D(96, 3, 1, activation='relu', padding='same',  data_format='channels_last')(pool1)
    conv2 = L.Conv2D(96, 3, 1, activation='relu', padding='same',  data_format='channels_last')(conv2)
    pool2 = L.MaxPooling2D(pool_size=(2, 2),  data_format='channels_last')(conv2)

    conv3 = L.Conv2D(128, 3, 1, activation='relu', padding='same', data_format='channels_last')(pool2)
    conv3 = L.Conv2D(128, 3, 1, activation='relu', padding='same', data_format='channels_last')(conv3)
    pool3 = L.MaxPooling2D(pool_size=(2, 2), data_format='channels_last')(conv3)

    conv4 = L.Conv2D(256, 3, 1, activation='relu', padding='same', data_format='channels_last')(pool3)
    conv4 = L.Conv2D(256, 4, 1, activation='relu', padding='same', data_format='channels_last')(conv4)
    pool4 = L.MaxPooling2D(pool_size=(2, 2), data_format='channels_last')(conv4)

    conv5 = L.Conv2D(512, 3, 1, activation='relu', padding='same', data_format='channels_last')(pool4)
    conv5 = L.Conv2D(512, 3, 1, activation='relu', padding='same', data_format='channels_last')(conv5)

    up_conv5 = L.UpSampling2D(size=(2, 2), data_format='channels_last')(conv5)
 
    ch, cw = get_crop_shape(conv4, up_conv5)
    crop_conv4 = L.Cropping2D(cropping=(ch,cw), data_format='channels_last')(conv4)
    up6 = L.Concatenate(axis=-1)([up_conv5, crop_conv4])
    conv6 = L.Conv2D(256, 3, 1, activation='relu', padding='same', data_format='channels_last')(up6)
    conv6 = L.Conv2D(256, 3, 1, activation='relu', padding='same', data_format='channels_last')(conv6)

    up_conv6 = L.UpSampling2D(size=(2, 2), data_format='channels_last')(conv6)
    ch, cw = get_crop_shape(conv3, up_conv6)
    crop_conv3 = L.Cropping2D(cropping=(ch,cw), data_format='channels_last')(conv3)
    up7 = L.Concatenate(axis=-1)([up_conv6, crop_conv3])
    conv7 = L.Conv2D(128, 3, 1, activation='relu', padding='same', data_format='channels_last')(up7)
    conv7 = L.Conv2D(128, 3, 1, activation='relu', padding='same', data_format='channels_last')(conv7)


    up_conv7 = L.UpSampling2D(size=(2, 2), data_format='channels_last')(conv7)
    ch, cw = get_crop_shape(conv2, up_conv7)
    crop_conv2 = L.Cropping2D(cropping=(ch,cw), data_format='channels_last')(conv2)
    up8 = L.Concatenate(axis=-1)([up_conv7, crop_conv2])
    conv8 = L.Conv2D(96, 3, 1, activation='relu', padding='same', data_format='channels_last')(up8)
    conv8 = L.Conv2D(96, 3, 1, activation='relu', padding='same', data_format='channels_last')(conv8)

    up_conv8 = L.UpSampling2D(size=(2, 2), data_format='channels_last')(conv8)
    ch, cw = get_crop_shape(conv1, up_conv8)
    crop_conv1 = L.Cropping2D(cropping=(ch,cw), data_format='channels_last')(conv1)
    up9 = L.Concatenate(axis=-1)([up_conv8, crop_conv1])
    conv9 = L.Conv2D(64, 3, 1, activation='relu', padding='same', data_format='channels_last')(up9)
    conv9 = L.Conv2D(64, 3, 1, activation='relu', padding='same', data_format='channels_last')(conv9)

    ch, cw = get_crop_shape(inputs, conv9)
    conv9 = L.ZeroPadding2D(padding=(ch, cw), data_format='channels_last')(conv9)
    conv10 = L.Conv2D(1, 1, 1, activation='sigmoid', data_format='channels_last')(conv9)

    
    
    return conv10


def get_base_model(image_shape, wpath=None, training=False):
    
    inputs = L.Input(shape=image_shape)
    output = get_unet(inputs)
    model = Model(inputs, output)

    if wpath is not None:
        _ = model.load_weights(wpath)
        model.trainable = training

    return model
