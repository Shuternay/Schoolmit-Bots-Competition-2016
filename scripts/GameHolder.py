#!/usr/bin/python3

import json
import subprocess
import time
import argparse

import Executable
from WovInteractor import Interactor

# solutions = {}


# def send_data(process, msg):
#     # print(str, file=process.stdin)
#     process.stdin.write(msg + '\n')
#     process.stdin.flush()


# def read_data(process, tl=0.2, lines=1):
#     def _readerthread(fh, buffer):
#         for i in range(lines):
#             buffer.append(fh.readline())
#             # buffer = fh.read().split('\n')

#     buffer = []

#     read_thread = threading.Thread(target=_readerthread, args=(process.stdout, buffer))
#     read_thread.daemon = True
#     read_thread.start()
#     read_thread.join(tl)
#     if read_thread.is_alive():
#         raise subprocess.TimeoutExpired(process.args, tl)

#     return [x.strip() for x in buffer]


def run_game(args):
    interactor = Interactor()

    json_log = {'first': args['player1_name'], 'second': args['player2_name'], 'log': []}
    text_log = ''

    print('\n\n=================================================================================')
    print('1: {0}'.format(args['player1_name']))
    print('2: {0}'.format(args['player2_name']))

    containers = [None, None]
    containers[0] = Executable.Executable(args['player1_path'],
                                          '{0}_{1}'.format(1, args['player1_name']),
                                          lang=args['player1_lang'])

    containers[1] = Executable.Executable(args['player2_path'],
                                          '{0}_{1}'.format(2, args['player2_name']),
                                          lang=args['player2_lang'])

    flag = 1
    try:
        containers[0].finish_compilation()
    except Exception as e:
        print(e)
        json_log['result'] = {'winner': 2,
                              'status': 'CE. {0}'.format(e)}
        text_log += 'Can\'t compile {0}\'s solution\n'.format(1)
        flag = 0
    try:
        containers[1].finish_compilation()
    except Exception as e:
        print(e)
        json_log['result'] = {'winner': 1,
                              'status': 'CE. {0}'.format(e)}
        text_log += 'Can\'t compile {0}\'s solution\n'.format(2)
        flag = 0

    if flag:
        print('GO!')

        current_player = 1  # 1 or 2
        text_to_send = None
        tl = args['tl'] or 1
        # exc_obj = None

        while True:
            try:
                text_to_send, lines = interactor.get_data(current_player)
                # print('"{0}" -> {1}'.format(text_to_send, current_player))
                text_log += '"{0}" -> {1}\n'.format(text_to_send, current_player)
                # json_log['log'].append({'from': 'judge', 'to': str(current_player), 'msg': text_to_send})

                res = containers[current_player - 1].run_object_through_helper_in_docker(text_to_send, tl)

                # print('{1} -> "{0}" ({2:.2f} s.)'.format(res['stdout'].strip('\n'), current_player, res['exec_time']))
                text_log += '{1} -> "{0}" ({2:.2f} s.)\n'.format(res['stdout'].strip('\n'), current_player,
                                                                 res['exec_time'])
                json_log['log'].append({'from': str(current_player), 'to': 'judge', 'msg': res['stdout'].strip('\n'),
                                        'time': res['exec_time'], 'return_code': res['returncode']})
                verdict = interactor.put_data(current_player, res['stdout'])

                json_log['log'][-1]['field'] = [[zz for zz in z] for z in interactor.field]

                if len(verdict) > 1 and verdict[2] != 'ok':
                    print(verdict[2])

                if len(verdict) > 1:
                    json_log['log'][-1]['comment'] = verdict[2]
                    text_log += 'Comment: {0}\n'.format(verdict[2])

                if verdict[0] == interactor.TERMINATE:
                    json_log['result'] = {'winner': verdict[1][0], 'msg': verdict[2]}
                    json_log['result']['score_{0}'.format(current_player)] = verdict[1][1]
                    json_log['result']['score_{0}'.format(3 - current_player)] = verdict[1][2]
                    print('{0} player wins {2}-{3}: {1}'.format(verdict[1][0], verdict[2],
                                                                json_log['result']['score_1'],
                                                                json_log['result']['score_2']))
                    text_log += '{0} player wins {2}-{3}: {1}\n'.format(verdict[1][0], verdict[2],
                                                                        json_log['result']['score_1'],
                                                                        json_log['result']['score_2'])
                    break

                current_player = verdict[1]

            except subprocess.TimeoutExpired:
                print('TL. {0} player wins'.format(3 - current_player))
                text_log += 'TL. {0} player wins\n'.format(3 - current_player)
                # json_log['result'] = {'winner': 3 - current_player, 'status': 'TL'}
                json_log['log'].append({'from': str(current_player), 'to': 'judge', 'msg': '...nothing...'})

                if True:  # interactor.turn - interactor.last_remove >= 20 or interactor.stage == 1:
                    containers[0].kill_helper()
                    containers[0].kill_docker()
                    containers[1].kill_helper()
                    containers[1].kill_docker()

                    json_log['result'] = {'winner': 3 - current_player, 'status': 'slowpokes attack!'}
                    json_log['result']['score_{0}'.format(current_player)] = 0
                    json_log['result']['score_{0}'.format(3 - current_player)] = 3

                    print('slowpokes attack!')
                    text_log += 'slowpokes attack!\n'

                    break
                else:
                    current_player = 3 - current_player
                    interactor.turn += 1
                    continue
                    # if exc:
                    #     kill_docker(exc.docker_name)
                    # # TODO should we finish the game?
                    # break
            except KeyboardInterrupt as e:
                print(e)
                print('Interrupted')
                json_log['result'] = {'winner': 0, 'status': 'IR'}
                containers[0].kill_helper()
                containers[0].kill_docker()
                containers[1].kill_helper()
                containers[1].kill_docker()
                break
            except BaseException as e:  # WTF Exception
                print(e)
                print('WTF. nobody wins')
                text_log += 'WTF. nobody wins\n'
                json_log['result'] = {'winner': 0, 'status': 'WTF'}
                # containers[0].kill_helper()
                containers[0].kill_docker()
                # containers[1].kill_helper()
                containers[1].kill_docker()
                subprocess.call('docker rm -f {0} {1}'.format(containers[0].docker_name,
                                                              containers[1].docker_name).split())
                raise

    containers[0].kill_helper()
    containers[0].kill_docker()
    containers[1].kill_helper()
    containers[1].kill_docker()
    subprocess.call('docker rm -f {0} {1}'.format(containers[0].docker_name, containers[1].docker_name).split())

    with open(args['json_log'], 'w') as fp:
        json.dump(json_log, fp, indent=True)

    with open(args['text_log'], 'w') as fp:
        print(text_log, file=fp)

    return json_log['result']['winner'], json_log['result']['score_1'], json_log['result']['score_2']


def main():
    parser = argparse.ArgumentParser()
    # subparsers = parser.add_subparsers(help='sub-command help')

    # (build) build tests
    parser.add_argument('player1_path', help='First strategy path')
    parser.add_argument('player2_path', help='Second strategy path')
    parser.add_argument('--player1_name', type=str, help='First player name')
    parser.add_argument('--player2_name', type=str, help='Second player name')
    parser.add_argument('--player1_lang', type=str, help='First player lang')
    parser.add_argument('--player2_lang', type=str, help='First player lang')
    parser.add_argument('--text_log', type=str, help='File to write text log')
    parser.add_argument('--json_log', type=str, help='File to write json log')
    parser.add_argument('--tl', type=int, help='Time limit')
    parser.set_defaults(func=run_game)

    in_args = parser.parse_args()
    if in_args.__contains__('func'):
        in_args.func(vars(in_args))
    else:
        parser.print_help()


    # if sys.argv[1] == '1':
    #     run_game(sys.argv[2], sys.argv[3])
    #     # ...

    # else if sys.argv[1] == '2':
    #     strategies = sys.argv[2:]
    #     run_tournament(strategies)
    #     # ...


    # if len(sys.argv) == 3:
    #     run_game({'name': 'tmp1', 'submit': int(sys.argv[1]), 'lang': 'C++'},
    #              {'name': 'tmp2', 'submit': int(sys.argv[2]), 'lang': 'C++'})
    #     exit(0)

    # with open('teams.json') as fp:
    #     teams = json.load(fp)

    # global solutions

    # for team in teams['teams']:
    #     solutions[team['name']] = Executable(get_submit_path(team['submit']),
    #                                          '{0}_{1}'.format(1, team['name']),
    #                                          lang=team['lang'])

    # res_table = [[0 for i in range(len(teams['teams']))] for j in range(len(teams['teams']))]

    # scores = {}

    # for team1_no, team1 in enumerate(teams['teams']):
    #     for team2_no, team2 in enumerate(teams['teams']):
    #         res = run_game(team1, team2)
    #         res_table[team1_no][team2_no] = res
    #         if team1_no != team2_no:
    #             scores[team1['name']] = scores.get(team1['name'], 0) + res[1]
    #             scores[team2['name']] = scores.get(team2['name'], 0) + res[2]

    # with open('logs/table.json', 'w') as fp:
    #     json.dump(res_table, fp)

    # with open('logs/scores.json', 'w') as fp:
    #     json.dump(scores, fp, sort_keys=True, indent=True)

    # with open('logs/table.txt', 'w') as fp:
    #     print('\n'.join([' '.join(str(x) for x in res_table[i])
    #                      for i in range(len(res_table))]), file=fp)

    # for solution, exc in solutions.items():
    #     subprocess.call('docker rm -f {0}'.format(exc.docker_name).split())


if __name__ == '__main__':
    main()
