# Reads and tokenizes labelled training files with reviews.
from textcleaner import *
import os
import gensim
import smart_open
import pickle

"""
    Retrieves the sentiment, +1 or -1, from the review.

    return - tuple(str, str)
"""
def splitSentimentAndReview(review):
    tag = review[0:2] # get sentiment +1 or -1 from first two characters
    sentiment =  'pos' if tag == '+1' else 'neg'
    review = review[2:] # get the rest of the review
    return sentiment, review

"""
    Reads, tokenizes, and filters each review in the test/training file.

    Implementation based on gensim tutorial
        - https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb

    return - tokenized reviews
"""
def tokenizeReviews(fileName, isTrainingFile=False):
    tokens = []
    cnt = 0
    # read training file in utf-8 encoding
    for i, review in enumerate(smart_open.smart_open(fileName, encoding="utf-8")):
        if cnt == 5010: break
        sentiment, review = splitSentimentAndReview(review)
        tokenizedReview = tokenizeDocument(review)
        # tag training documents
        if(isTrainingFile):
            id = '{}_{}'.format(sentiment, i)
            tokens.append(gensim.models.doc2vec.TaggedDocument(tokenizedReview, [id]))
        else:
            tokens.append(tokenizedReview)
        cnt += 1
    return tokens

"""
    Read reviews from raw training/test file OR load a pickled file to
    deserialize the object. Pickled files assume that the training/test file
    has already been read and checkpointed. Raw training/test files will be
    tokenized and pickled.

    return - tokenized reviews as a generator
"""
def readReviews(fileName, pickleFileExists=False, isTrainingFile=False):
    pickleFileName = renameFileExtension(fileName, 'data', 'pkl')

    if(pickleFileExists):
        # deserialize object if .pkl file already exists
        with smart_open.smart_open(pickleFileName, "rb") as f:
            yield pickle.load(f, encoding="utf-8")
    else:
        # serialize and pickle the object to a file with .pkl extension
        tokens = tokenizeReviews(fileName, isTrainingFile) # grab filtered tokens
        serializeObject(pickleFileName, tokens) # write pickle file
        yield tokens


"""
    Serializes the object into a file.
"""
def serializeObject(fileName, obj):
    with smart_open.smart_open(fileName, "wb") as f:
        pickle.dump(obj, f)

def fileExists(fileName):
    return os.path.exists(fileName)

def renameFileExtension(fileName, oldExt, newExt):
    fileExtensionIdx = fileName.rfind(oldExt)
    newFileName = fileName[:fileExtensionIdx] + newExt
    return newFileName
