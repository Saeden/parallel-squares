from model.world import World


def deserialize(path: String, dim: int, fill: int) -> World:
    data = 
    let obj = JSON.parse(data);
        if (obj['_version'] > 1) {
            throw new Error('Save file with incorrect version');
        }
        let cubes = obj['cubes'];
        cubes.forEach((cube) => {
            let color = cube_1.Color.BLUE;
            if (cube.hasOwnProperty('color')) {
                color = new cube_1.Color(cube['color'][0], cube['color'][1], cube['color'][2]);
            }
            this.addCube([cube['x'], cube['y']], color);
        });