import glob
import subprocess
from sty import fg, bg, rs


def main():
    # o = subprocess.run(['./compile_vhdl.sh'], capture_output=True)
    # print(o.stdout.decode())
    # print(o.stderr.decode())
    # print(o.stdout)
    # print(o.stderr)

    for filename in glob.glob('../vhdl_work_dir/build/*.tcl'):
        fu = filename.split('/')[-1]
        fu = fu.split('.')[0]
        o = subprocess.run(['./run_xsim.sh', fu], capture_output=True)
        print('\nOUTPUT FROM FU: ' + fu)
        expected = []
        with open('../out/' + fu + '.out') as f:
            lines = iter(f)
            next(lines)
            for line in lines:
                l = line.split(',')
                expected.append(int(l[0]))

        outputs = []
        with open('../vhdl_work_dir/build/' + fu + '.log') as f:
            for line in f:
                l = line.lstrip('0')
                if 'XX' in l:
                    l = None
                    outputs.append(l)
                    continue
                if l == '\n':
                    l = '0'
                outputs.append(int(l, 16))

        passed = True
        if len(outputs) == len(expected):
            for i, val in enumerate(expected):
                tmp = outputs[i]
                if tmp != None:
                    print('{} == {}? '.format(val, outputs[i]), end='')
                    if val != outputs[i]:
                        print(bg.da_red + 'FAIL' + rs.bg)
                        passed = False
                    else:
                        print(bg.da_green + 'PASS' + rs.bg)
                if tmp is None:
                    print('{} == None? '.format(val), end='')
                    print(bg.da_red + 'FAIL' + rs.bg)
                    passed = False
        else:
            print(bg.da_red + 'FAILED, not the same number of outpus as expected outputs!' + rs.bg)
            passed = False

        if passed:
            print(bg.green + fg.black + 'PASSED' + rs.bg + fg.rs)
        else:
            print(bg.red + 'FAILED' + rs.bg)
            print('EXPECTED:')
            for i in expected:
                print(str(i) + ', ', end='')
            print()
            print('OUTPUTS:')
            for i in outputs:
                print(str(i) + ', ', end='')
            print()

    #     print("RUNNING SIM FOR: {}".format(fu))
    #     print(o.stdout.decode())
    #     print(o.stderr.decode())
    #     break


if __name__ == '__main__':
    main()
