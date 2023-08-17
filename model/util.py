from model.configuration import Configuration
from model.block import Block
import json


def deserialize(path: str, dim: int) -> Configuration:
    config = Configuration((dim+2, dim+2))
    with open(path) as data:
        obj = json.load(data)
        if obj['_version'] > 1:
            raise Exception('Save file with incorrect version')
        cubes = obj['cubes']
        for id, cube in enumerate(cubes):
            coord = (cube['x'], cube['y'])
            config.add(Block(p=coord, id=id))
            
    return config



