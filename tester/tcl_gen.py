import glob


def main():
    for filename in glob.glob('../out/*.out'):
        fu = filename.split('/')
        fu = fu[-1].split('.')[0]
        with open(filename) as file:
            waits = int(file.readline())
            curr_cycle = 0
            out = ''
            for line in file:
                l = line.split(',')
                val = l[0]
                cycle = int(l[1])
                w = cycle - curr_cycle
                curr_cycle = cycle
                out += 'run {} ns\n'.format(w * 50)
                out += 'puts $chan [get_value /{}/w_o_FU]\n'.format(fu + '_tb')

        with open('../vhdl_work_dir/build/' + fu + '.tcl', 'w') as file:
            file.write('set chan [open ' + fu + '.log w]\n')
            file.write('add_wave {{/' + fu + '_tb/UUT}}\n')
            file.write('run {} ns\n'.format(waits))
            file.write(out)
            file.write('exit')


if __name__ == '__main__':
    main()
