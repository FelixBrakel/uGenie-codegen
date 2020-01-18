import glob
import subprocess
from sty import fg, bg, rs


def main():
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
                if l[0] == 'BUGGED':
                    expected.append(None)
                else:
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

        # Some serious spaghetti code here but to clean this up would be a lot of work and would prob require the .out
        # files to be redesigned.
        passed = True
        if len(outputs) == len(expected):
            for i, val in enumerate(expected):
                tmp = outputs[i]
                # If val is None then we are dealing with the DFG#2 edge-case in which case we classify this as a soft
                # fail.
                if val is None:
                    passed = 'Soft'
                    if tmp is None:
                        print('None == None? ', end='')
                    else:
                        print('None == {}? '.format(outputs[i]), end='')

                    print(bg.da_yellow + 'DFG#2' + rs.all)
                else:
                    if tmp is not None:
                        print('{} == {}? '.format(val, outputs[i]), end='')
                        if val != outputs[i]:
                            print(bg.da_red + 'FAIL' + rs.all)
                            passed = False
                        else:
                            print(bg.da_green + 'PASS' + rs.all)
                    # Handle an unknow output from the sim (represented as None) seperately.
                    if tmp is None:
                        print('{} == None? '.format(val), end='')
                        print(bg.da_red + 'FAIL' + rs.all)
                        passed = False
        else:
            print(bg.da_red + 'FAILED, not the same number of outpus as expected outputs!' + rs.all)
            passed = False

        if passed == 'Soft':
            print(bg.yellow + 'SOFT PASS' + rs.all)
        elif passed:
            print(bg.green + 'PASSED' + rs.all)
        else:
            print(bg.red + 'FAILED' + rs.all)
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
