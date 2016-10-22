import json
import time
import sys
import subprocess


def get_limit_func(ml):
    # TODO: Java
    # if self.lang == 'Java':
    #     return None
    try:
        # works only for Unix
        # noinspection PyUnresolvedReferences
        import resource

        if ml != -1:
            ml *= 1024 ** 2
        hard_limit = resource.getrlimit(resource.RLIMIT_AS)[1]
        return lambda: resource.setrlimit(resource.RLIMIT_AS, (ml, hard_limit))
    except ImportError:
        return None


def main():
    s = input()
    # print('rh <-: {0}'.format(s), file=sys.stderr)
    helper_args = json.loads(s)

    while True:
        try:
            s = input()
        except EOFError:
            return

        # print('rh <-: {0}'.format(s), file=sys.stderr)
        args = json.loads(s)

        start_time = time.time()

        process = subprocess.Popen(helper_args['exec_cmd'].split(),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   preexec_fn=get_limit_func(helper_args['ml']),
                                   cwd=helper_args['work_dir'],
                                   universal_newlines=True)

        try:
            cout, cerr = process.communicate(input=args['input_data'], timeout=args['tl'])
        except subprocess.TimeoutExpired:
            process.kill()
            print(json.dumps({'exec_time': -1}))
            continue

        res = process.returncode

        end_time = time.time()
        exec_time = end_time - start_time

        # print('rh ->: {0}'.format(json.dumps({
        #     'returncode': res,
        #     'exec_time': exec_time,
        #     'stdout': cout,
        #     'stderr': cerr
        # })), file=sys.stderr)
        print(json.dumps({
            'returncode': res,
            'exec_time': exec_time,
            'stdout': cout,
            'stderr': cerr
        }))


if __name__ == '__main__':
    main()
