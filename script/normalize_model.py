if __name__ == '__main__':
    file_name = "rabbit_cym.obj"
    input_path = "../res/3d_model/%s" % file_name
    dot_position = input_path.rfind('.')
    output_filename = input_path[:dot_position] + '_normalizeed' + input_path[dot_position:]

    input_lines = open(input_path).read().split('\n')
    min_xyz = [2 ** 32] * 3
    max_xyz = [-2 ** 32] * 3

    for l in input_lines:
        l = l.strip()
        if len(l) == 0:
            continue
        tokens = l.split()
        if tokens[0] == 'v':
            xyz = [float(t) for t in tokens[1:]]
            min_xyz = [min(p) for p in zip(min_xyz, xyz)]
            max_xyz = [max(p) for p in zip(max_xyz, xyz)]

    print(min_xyz)
    print(max_xyz)


    # with open("../res/3d_model/rabbit_cym.obj"), open(output_filename) as input:
