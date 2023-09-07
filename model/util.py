from model.configuration import Configuration
from model.block import Block
import json


def deserialize(path: str, dim: int=None) -> Configuration:
    if dim:
        config = Configuration((dim+2, dim+2))
    else:
        config = None
    with open(path) as data:
        obj = json.load(data)
        if obj['_version'] > 1:
            raise Exception('Save file with incorrect version')
            
        if not config:
            dimensions = (obj['dimensions'][0]+2, obj['dimensions'][1]+2) 
            config = Configuration(dimensions)
        
        cubes = obj['cubes']
        for id, cube in enumerate(cubes):
            coord = (cube['x'], cube['y'])
            config.add(Block(p=coord, id=id))
            
    return config



