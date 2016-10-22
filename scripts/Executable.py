
import collections
import hashlib
import os
import random
import string
import subprocess
import time
import json


def random_str(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class Executable:
    def __init__(self, src_path, target='', use_testlib=False, lang=None, compiler_flags='',
                 work_dir='.', ml=512, use_precompiled=True, save_compiled=True):
        self.src_path = src_path
        self.target = target
        self.lang = lang or Executable.guess_lang(src_path)
        self.use_testlib = use_testlib
        self.flags = compiler_flags
        self.work_dir = work_dir
        self.ml = int(ml)
        self.use_precompiled = use_precompiled
        self.save_compiled = save_compiled
        self.compile_process = None
        self.compiled = False
        self.exec_cmd = ''
        self.docker_name = None
        self.binary_path = ''
        self.helper_process = None

        self.start_compilation()

    def compile_bash(self):
        self.exec_cmd = 'bash ' + os.path.relpath(self.src_path, self.work_dir)
        self.compiled = True

    def compile_cpp(self):
        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        exec_out = os.path.join('tmp', os.path.basename(self.src_path) + '.out')
        # if work_dir is 'tmp' we should call './binary' instead of 'binary'
        self.exec_cmd = os.path.join('./', os.path.relpath(exec_out, self.work_dir))
        self.binary_path = exec_out

        if self.use_precompiled and Executable.check_hash(self.src_path):
            print('Using previous version of binary\n')
            self.compiled = True
            return  # TODO check for preprocessor and compiler flags

        cxx_compiler = 'g++ {} '.format(self.flags or '-O2 -Wall -xc++ -std=c++11 -DONLINE_JUDGE')
        if self.use_testlib:
            cxx_compiler += '-I{0} '.format(os.path.join('..', '..', 'lib'))
        self.compile_process = subprocess.Popen('{0} "{1}" -o {2}'.format(cxx_compiler, self.src_path, exec_out),
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def compile_delphi(self):
        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        exec_out = os.path.join('tmp', os.path.basename(self.src_path) + '.out')
        # if work_dir is 'tmp' we should call './binary' instead of 'binary'
        self.exec_cmd = os.path.join('./', os.path.relpath(exec_out, self.work_dir))

        if self.use_precompiled and Executable.check_hash(self.src_path):
            print('Using previous version of binary\n')
            self.compiled = True
            return  # TODO check for preprocessor and compiler flags

        pas_compiler = 'fpc -MDELPHI {0} '.format(self.flags)  # TODO java testlib
        self.compile_process = subprocess.Popen('{0} "{1}" -o{2}'.format(pas_compiler, self.src_path, exec_out),
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def compile_java(self):
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        out_folder = os.path.join('tmp', os.path.basename(self.src_path[:-len('.java')]))
        if not os.path.exists(out_folder):
            os.mkdir(out_folder)

        ml = self.ml
        self.exec_cmd = 'java -cp {0} -Xmx{2}M -Xss{3}M {1}'.format(os.path.relpath(out_folder, self.work_dir),
                                                                    os.path.basename(self.src_path[:-len('.java')]),
                                                                    ml, ml // 2)

        if self.use_precompiled and Executable.check_hash(self.src_path):
            print('Using previous version of binary\n')
            self.compiled = True
            return  # TODO check for preprocessor and compiler flags

        java_compiler = 'javac {0}'.format(self.flags)  # TODO java testlib
        self.compile_process = subprocess.Popen('{0} "{1}" -d {2}'.format(java_compiler, self.src_path, out_folder),
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def compile_pascal(self):
        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        exec_out = os.path.join('tmp', os.path.basename(self.src_path) + '.out')
        # if work_dir is 'tmp' we should call './binary' instead of 'binary'
        self.exec_cmd = os.path.join('./', os.path.relpath(exec_out, self.work_dir))
        self.binary_path = exec_out

        if self.use_precompiled and Executable.check_hash(self.src_path):
            print('Using previous version of binary\n')
            self.compiled = True
            return  # TODO check for preprocessor and compiler flags

        pas_compiler = 'fpc {0} '.format(self.flags)  # TODO java testlib
        self.compile_process = subprocess.Popen('{0} "{1}" -o{2}'.format(pas_compiler, self.src_path, exec_out),
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def compile_python3(self):
        if os.system('python3 -V') == 0:  # command 'python3' doesn't exists on Windows
            self.exec_cmd = 'python3 ' + os.path.relpath(self.src_path, self.work_dir)
        else:
            self.exec_cmd = 'python ' + os.path.relpath(self.src_path, self.work_dir)
        self.binary_path = self.src_path
        self.compiled = True

    def compile_shell(self):
        self.exec_cmd = 'sh ' + os.path.relpath(self.src_path, self.work_dir)
        self.compiled = True

    def start_compilation(self):
        print('Starting compilation of {0}'.format(self.target))

        lang_to_comp = {
            'Bash': self.compile_bash,
            'C': self.compile_cpp,
            'C++': self.compile_cpp,
            'Delphi': self.compile_delphi,
            'Java': self.compile_java,
            'Pascal': self.compile_pascal,
            'Python': self.compile_python3,
            'Python3': self.compile_python3,
            'Shell': self.compile_shell,
        }

        (lang_to_comp[self.lang])()

    def finish_compilation(self):
        if self.compiled:
            return

        print('Finishing compilation of {0}'.format(self.target))
        cout, cerr = self.compile_process.communicate()

        cout = self.process_output(cout)
        cerr = self.process_output(cerr)

        for x in (cout, cerr):
            if x:
                print(x)

        res = self.compile_process.returncode

        if res != 0:
            raise Exception('Compilation error ({})'.format(self.src_path))

        if self.save_compiled:
            Executable.write_hash(self.src_path)

        print('Compilation of {0} finished'.format(self.target))

        self.compiled = True

    def execute(self, stdin=None, stdout=None, stderr=None, tl=None, args=''):
        if not self.compiled:
            self.finish_compilation()

        start_time = time.time()

        process = subprocess.Popen((self.exec_cmd + ' ' + args).split(),
                                   stdin=stdin, stdout=stdout, stderr=stderr,
                                   preexec_fn=self.get_limit_func(),
                                   cwd=self.work_dir)

        try:
            cout, cerr = process.communicate(timeout=tl)
        except subprocess.TimeoutExpired:
            process.kill()
            raise

        cout = self.process_output(cout)
        cerr = self.process_output(cerr)

        res = process.returncode

        end_time = time.time()
        exec_time = end_time - start_time

        exec_res_type = collections.namedtuple('exec_res_type',
                                               ['returncode', 'exec_time', 'stdout', 'stderr'])
        return exec_res_type(res, exec_time, cout, cerr)

    def get_piped_popen_object(self, args=''):
        if not self.compiled:
            self.finish_compilation()

        return subprocess.Popen((self.exec_cmd + ' ' + args).split(),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                preexec_fn=self.get_limit_func(),
                                cwd=self.work_dir,
                                universal_newlines=True)

    def get_piped_popen_object_in_docker(self, args=''):
        if not self.compiled:
            self.finish_compilation()

        if self.docker_name is None:
            self.docker_name = self.target + '_' + random_str(5)
            create_cmd = \
                'docker run -d --log-driver=none --net=none --name={name} --memory={memory}M --memory-swap=-1 ' \
                ' -v {host_path}:{guest_path}:ro ubuntu:14.04 bash'.format(
                    name=self.docker_name,
                    host_path=os.path.abspath(self.binary_path),
                    guest_path=os.path.join('/', self.binary_path),
                    memory=self.ml,
                    cmd=self.exec_cmd
                )
            print(create_cmd)
            subprocess.call(create_cmd.split())
            while not self.is_docker_running():
                time.sleep(0.02)
                print(0.02)

        self.exec_cmd = 'docker exec -i {name}'.format(name=self.docker_name)
        print(self.exec_cmd)

        return subprocess.Popen((self.exec_cmd + ' ' + args).split(),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                preexec_fn=self.get_limit_func(),
                                cwd=self.work_dir,
                                universal_newlines=True)

    def run_piped_popen_object_in_docker(self, input_data='', tl=1, args=''):
        if not self.compiled:
            self.finish_compilation()

        if self.docker_name is None:
            self.docker_name = self.target + '_' + random_str(5)
            create_cmd = \
                'docker run -dt --log-driver=none --net=none --name={name} --memory={memory}M --memory-swap=-1 ' \
                ' -v {host_path}:{guest_path}:ro ubuntu:14.04 bash'.format(
                    name=self.docker_name,
                    host_path=os.path.abspath(self.binary_path),
                    guest_path=os.path.join('/', self.binary_path),
                    memory=self.ml,
                    cmd=self.exec_cmd
                )
            print(create_cmd)
            subprocess.call(create_cmd.split())
            while not self.is_docker_running():
                time.sleep(0.02)
                print(0.02)

        docker_exec_cmd = 'docker exec -i {name} {cmd}'.format(name=self.docker_name, cmd=self.exec_cmd)
        # print(self.exec_cmd)

        start_time = time.time()

        process = subprocess.Popen((docker_exec_cmd + ' ' + args).split(),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   preexec_fn=self.get_limit_func(),
                                   cwd=self.work_dir,
                                   universal_newlines=True)

        try:
            cout, cerr = process.communicate(input=input_data, timeout=tl)
        except subprocess.TimeoutExpired:
            process.kill()
            raise

        # cout = self.process_output(cout)
        # cerr = self.process_output(cerr)

        res = process.returncode

        end_time = time.time()
        exec_time = end_time - start_time

        return {
            'returncode': res,
            'exec_time': exec_time,
            'stdout': cout,
            'stderr': cerr
        }

    def run_object_through_helper_in_docker(self, input_data='', tl=1):
        if not self.compiled:
            self.finish_compilation()

        if self.docker_name is None:
            self.docker_name = self.target + '_' + random_str(5)
            create_cmd = \
                'docker run -dt --log-driver=none --net=none --name={name} --memory={memory}M --memory-swap=-1 ' \
                ' -v {host_binary_path}:{guest_binary_path}:ro -v {host_helper_path}:{guest_helper_path}:ro ' \
                ' ubuntu:14.04 bash'.format(
                    name=self.docker_name,
                    host_binary_path=os.path.abspath(self.binary_path),
                    guest_binary_path=os.path.join('/', self.binary_path),
                    host_helper_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RunHelper.py'),
                    guest_helper_path=os.path.join('/tmp', 'RunHelper.py'),
                    memory=self.ml,
                    cmd=self.exec_cmd
                )
            print(create_cmd)
            subprocess.call(create_cmd.split())
            while not self.is_docker_running():
                time.sleep(0.02)
                print(0.02)

            docker_exec_cmd = 'docker exec -i {name} {cmd}'.format(name=self.docker_name,
                                                                   cmd='python3 /tmp/RunHelper.py')
            print(docker_exec_cmd)
            self.helper_process = subprocess.Popen(docker_exec_cmd.split(),
                                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                   cwd=self.work_dir,
                                                   universal_newlines=True)

            print(json.dumps({'exec_cmd': self.exec_cmd, 'ml': self.ml, 'work_dir': self.work_dir}),
                  file=self.helper_process.stdin)
            self.helper_process.stdin.flush()

        print(json.dumps({'input_data': input_data, 'tl': tl}), file=self.helper_process.stdin)
        self.helper_process.stdin.flush()
        result_json = self.helper_process.stdout.readline()

        result = json.loads(result_json)
        if result['exec_time'] == -1:
            raise subprocess.TimeoutExpired  # FIXME

        return result

    def kill_helper(self):
        if self.helper_process is not None:
            self.helper_process.kill()

    def get_limit_func(self):
        if self.lang == 'Java':
            return None
        try:
            # works only for Unix
            # noinspection PyUnresolvedReferences
            import resource

            ml = self.ml
            if ml != -1:
                ml *= 1024 ** 2
            hard_limit = resource.getrlimit(resource.RLIMIT_AS)[1]
            return lambda: resource.setrlimit(resource.RLIMIT_AS, (ml, hard_limit))
        except ImportError:
            return None

    def is_docker_running(self):
        if self.docker_name is None:
            return False
        p = subprocess.Popen('docker inspect -f {{{{.State.Running}}}} {0}'.format(self.docker_name).split(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out == b'true\n'

    def kill_docker(self):
        if self.docker_name is not None and self.is_docker_running():
            os.system('docker kill {0}'.format(self.docker_name))

    @staticmethod
    def guess_lang(src_path: str):
        suffix2lang = [
            ('.bash', 'Bash'),
            ('.c', 'C'),
            ('.cpp', 'C++'),
            ('.dpr', 'Delphi'),
            ('.java', 'Java'),
            ('.pas', 'Pascal'),
            ('.py', 'Python3'),
            ('.sh', 'Shell'),
        ]
        for suffix, lang in suffix2lang:
            if src_path.endswith(suffix):
                return lang

        raise Exception('Compilation error (Unknown language, {0})'.format(src_path))

    @staticmethod
    def get_hash(file, info=''):
        with open(file) as f:
            content = info + '-----' + f.read()
            m = hashlib.md5()
            m.update(content.encode('utf-8'))
            return m.hexdigest()

    @staticmethod
    def check_hash(file, info=''):
        cur_hash = Executable.get_hash(file, info)
        prev_hash = ''
        if os.path.exists(os.path.join('tmp', os.path.basename(file) + '.hash')):
            with open(os.path.join('tmp', os.path.basename(file) + '.hash')) as f:
                prev_hash = f.read()

        return prev_hash == cur_hash

    @staticmethod
    def write_hash(file, info=''):
        cur_hash = Executable.get_hash(file, info)
        with open(os.path.join('tmp', os.path.basename(file) + '.hash'), 'w') as f:
            f.write(cur_hash)

    @staticmethod
    def process_output(output):
        if output:
            output = str(output, 'utf-8')
            if output.endswith('\n'):
                output = output[:-1]
        else:
            output = None
        return output
