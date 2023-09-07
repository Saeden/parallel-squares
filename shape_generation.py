import shapes.shapes as shapes
from model.configuration import Configuration
import json
import random
import os


def serialize(config: Configuration, num_blocks: int, seed: int, start: bool):
    directory = f"results/shapes/{num_blocks}"
    if start:
        file_name = f"shape_{seed+1}_size_{num_blocks}_start.json"
    else:
        file_name = f"shape_{seed+1}_size_{num_blocks}_target.json"

    if not os.path.exists(directory):
        os.makedirs(directory)

    path = os.path.join(directory, file_name)

    blocks = []
    for block in config.blocks:
        if block:
            block_data = {'x': block.p[0], 'y': block.p[1], 'color': [None, None, None]}
            blocks.append(block_data)
        
    obj = {'_version': 1, 'dimensions': config.boundary, 'cubes': blocks}
        
    with open(path, "w") as json_file:
        json.dump(obj, json_file)


def generate_XYmonotone_files():
    number_of_blocks = [500]

    seed_list = range(1)

    for block_num in number_of_blocks:
        for seed in seed_list:
            random.seed(seed)
            max_x = int(block_num/2)

            start: Configuration = shapes.xy_monotone_new(blocks=block_num,x=random.randint(2, max_x), seed=seed)
            target: Configuration = shapes.xy_monotone_new(blocks=block_num,x=random.randint(2, max_x), seed=seed)

            serialize(config=start, num_blocks=block_num, seed=seed, start=True)
            serialize(config=target, num_blocks=block_num, seed=seed, start=False)

if __name__ == "__main__":
    generate_XYmonotone_files()