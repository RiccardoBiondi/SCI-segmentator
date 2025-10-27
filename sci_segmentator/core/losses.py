import tensorflow as tf


@tf.function
def tversky_loss(y_true, y_pred, alpha=.5, beta=.5, smooth=1e-6, dim_ordering='tf'):

    if dim_ordering != 'tf':
        y_true = K.permute_dimensions(y_true, (3, 0, 1, 2))
        y_pred = K.permute_dimensions(y_pred, (3, 0, 1, 2))
    beta = 1. - alpha
    y_true = K.cast(y_true, 'float32')
    y_pred = K.cast(y_pred, 'float32')

    # clip to prevent NaN's and Inf's
    y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())

    y_true = y_true[..., 0] # assumption: I have a single channel image
    y_pred = y_pred[..., 0] # assumption: I have a single channel image

    y_true = K.flatten(y_true)
    y_pred = K.flatten(y_pred)

    # now compute the required quantities for the loss
    TP = K.sum((y_true * y_pred))
    FP = K.sum((1 - y_true) * y_pred)
    FN = K.sum(y_true * (1 - y_pred))

    tversky = (TP + smooth) / (TP + alpha * FP + beta*FN + smooth)

    return 1 - tversky

def dice_coeff(y_true, y_pred, smooth=1e-6):
    '''
    dice coefficient =2*sum(|y_true*y_pred|)/(sum(y_true^2)+sum(y_pred^2))
    
    Args:
      ->ground truth label
      ->predicted label
      -smooth:default is 1
      
    '''
    y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
    y_pred = K.cast(y_pred > .5, 'uint8')
    y_pred = K.cast(y_pred, 'float32')

    TP = K.sum((y_true * y_pred))
    FP = K.sum((1 - y_true) * y_pred)
    FN = K.sum(y_true * (1 - y_pred))

    dice = (2 * TP + smooth) / (2 * TP + FP + FN + smooth)

    return dice

def volume_similarity(y_true, y_pred):

    y_pred = K.cast(y_pred > .5, 'uint8')
    y_pred = K.cast(y_pred, 'float32')

    pred_volume = K.sum(y_pred)
    gt_volume = K.sum(y_true)

    num = K.abs(pred_volume - gt_volume)
    den = pred_volume + gt_volume

    return num / den

@tf.function
def dice_loss(y_true, y_pred):
    loss = 1. - dice_coeff(y_true, y_pred)
    return loss