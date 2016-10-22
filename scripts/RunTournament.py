import json
import GameHolder
import os
import shutil


def main():
    with open('users/users.json') as fp:
        users = json.load(fp)
    with open('submits/submits.json') as fp:
        submits = json.load(fp)
        last_submits = submits['last_submits']

    res_table = [[0 for i in range(len(users))] for j in range(len(users))]

    scores = {}
    official_scores = {}

    if not os.path.exists('logs'):
        os.mkdir('logs')
    if not os.path.exists('logs/tournament_0000'):
        os.mkdir('logs/tournament_0000')

    tournament_num = int(max([f for f in os.listdir('logs') if f.startswith('tournament')])[len('tournament_'):]) + 1
    os.mkdir('logs/tournament_{:0>4}'.format(tournament_num))

    shutil.copy('submits/submits.json', 'logs/tournament_{:0>4}'.format(tournament_num))

    for team1_no, team1 in enumerate(users):
        if last_submits.get(team1['name']) is None:
            continue
        team1_path = 'submits/run_{:0>4}'.format(last_submits[team1['name']])

        for team2_no, team2 in enumerate(users):
            if last_submits.get(team2['name']) is None:
                continue
            team2_path = 'submits/run_{:0>4}'.format(last_submits[team2['name']])

            res = GameHolder.run_game(
                {
                    'player1_path': team1_path,
                    'player2_path': team2_path,
                    'player1_name': team1['name'],
                    'player2_name': team2['name'],
                    'player1_lang': submits['submits'][last_submits[team1['name']]]['lang'],
                    'player2_lang': submits['submits'][last_submits[team2['name']]]['lang'],
                    'text_log': 'logs/tournament_{0:0>4}/{1}_{2}.txt'.format(tournament_num,
                                                                             team1['name'], team2['name']),
                    'json_log': 'logs/tournament_{0:0>4}/{1}_{2}.json'.format(tournament_num,
                                                                              team1['name'], team2['name']),
                    'tl': 1
                })
            res_table[team1_no][team2_no] = res
            if team1_no != team2_no:
                scores[team1['name']] = scores.get(team1['name'], 0) + res[1]
                scores[team2['name']] = scores.get(team2['name'], 0) + res[2]

                if team1['official'] and team2['official']:
                    official_scores[team1['name']] = official_scores.get(team1['name'], 0) + res[1]
                    official_scores[team2['name']] = official_scores.get(team2['name'], 0) + res[2]

    with open('logs/tournament_{0:0>4}/table.json'.format(tournament_num), 'w') as fp:
        json.dump(res_table, fp)

    with open('logs/tournament_{0:0>4}/scores.json'.format(tournament_num), 'w') as fp:
        json.dump(scores, fp, sort_keys=True, indent=True)

    with open('logs/tournament_{0:0>4}/official_scores.json'.format(tournament_num), 'w') as fp:
        json.dump(official_scores, fp, sort_keys=True, indent=True)

    with open('logs/tournament_{0:0>4}/table.txt'.format(tournament_num), 'w') as fp:
        print('\n'.join([' '.join(str(x) for x in res_table[i])
                         for i in range(len(res_table))]), file=fp)

    shutil.rmtree('logs/tournament_0000')
    shutil.copytree('logs/tournament_{0:0>4}'.format(tournament_num), 'logs/tournament_0000')

    shutil.rmtree('../war_of_viruses/public/logs')
    shutil.copytree('logs', '../war_of_viruses/public/logs')


if __name__ == '__main__':
    main()
