import sys
import copy
import itertools


cube1 = {'-Y' : 'green', '+Z' : 'green', '+Y' : 'green', '-Z' : 'red'  , '-X' : 'white', '+X' : 'blue' }
cube2 = {'-Y' : 'red'  , '+Z' : 'white', '+Y' : 'red'  , '-Z' : 'blue' , '-X' : 'blue' , '+X' : 'green'}
cube3 = {'-Y' : 'green', '+Z' : 'blue' , '+Y' : 'white', '-Z' : 'green', '-X' : 'red'  , '+X' : 'white'}
cube4 = {'-Y' : 'white', '+Z' : 'red'  , '+Y' : 'blue' , '-Z' : 'white', '-X' : 'green', '+X' : 'red'  }

color_code = {'red' : [0, 0], 'white' : [0, 1], 'blue' : [1, 0], 'green' : [1, 1]}


def rotation_by_pi_over_2_around_x(cube):
    color_A = cube['+Y']
    color_B = cube['+Z']
    color_C = cube['-Y']
    color_D = cube['-Z']
    cube['+Y'] = color_D
    cube['+Z'] = color_A
    cube['-Y'] = color_B
    cube['-Z'] = color_C


def rotation_by_pi_around_x(cube):
    rotation_by_pi_over_2_around_x(cube)
    rotation_by_pi_over_2_around_x(cube)


def rotation_by_pi_over_2_around_z(cube):
    color_A = cube['+X']
    color_B = cube['+Y']
    color_C = cube['-X']
    color_D = cube['-Y']
    cube['+X'] = color_D
    cube['+Y'] = color_A
    cube['-X'] = color_B
    cube['-Y'] = color_C


def rotation_by_pi_around_z(cube):
    rotation_by_pi_over_2_around_z(cube)
    rotation_by_pi_over_2_around_z(cube)


def apply_switches(cube, switches):
    if switches[0]:
        rotation_by_pi_over_2_around_z(cube)
    if switches[1]:
        rotation_by_pi_around_x(cube)
    if switches[2]:
        rotation_by_pi_over_2_around_x(cube)
    if switches[3]:
        rotation_by_pi_around_z(cube)
    if switches[4]:
        rotation_by_pi_over_2_around_z(cube)


def generate_valid_states(cube):
    V = set()
    for s in itertools.product([True, False], repeat=5):
        cube_copy = copy.copy(cube)
        apply_switches(cube_copy, s)
        valid_state = []
        valid_state += color_code[cube_copy['+X']]
        valid_state += color_code[cube_copy['+Z']]
        valid_state += color_code[cube_copy['-X']]
        valid_state += color_code[cube_copy['-Z']]
        V.add(tuple(valid_state))
    return V


def cube_configurations(ci):
    cube_names = 'ABCD'
    
    variable_name_tuple = [cube_names[ci-1] + '_' + face + '_' + bit for face in 'fubd' for bit in ['hi', 'lo']]

    if ci == 1:
        cube = cube1
    elif ci == 2:
        cube = cube2
    elif ci == 3:
        cube = cube3
    elif ci == 4:
        cube = cube4
    else:
        print('cube must be 1, 2, 3 or 4')
        quit()

    return variable_name_tuple, (generate_valid_states(cube))


def face_configurations(face):
    variable_name_tuple = [cube + '_' + face + '_' + bit for cube in 'ABCD' for bit in ['hi', 'lo']]
    valid_states = set()
    for t in itertools.product([0,1], repeat=8):
        L = [t[0] + 2*t[1], t[2] + 2*t[3], t[4] + 2*t[5], t[6] + 2*t[7]]
        L.sort()
        if L == [0, 1, 2, 3]:
            valid_states.add(t)
    return variable_name_tuple, valid_states


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ci = int(sys.argv[1])
        bc = boolean_configurations(ci)
        for valid_configuration in bc:
            print(valid_configuration)
    else:
        print('Usage: cubes.py {1|2|3|4}')
        sys.exit(1)
