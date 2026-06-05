from .sampleModel import SampleModel
MODELS = {
        'sample': SampleModel(),
    }


def getModel(key):
    return MODELS.get(key, None)
    