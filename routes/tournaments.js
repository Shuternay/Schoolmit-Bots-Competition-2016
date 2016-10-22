var express = require('express');
var fs = require('fs');
var util = require('util');
var router = express.Router();

function pad(n, size) {
    var s = String(n);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
}

router.get('/:id', function(req, res, next) {
    var official = req.query.official;

    var teams_path = '../wov_workdir/users/users.json';
    var table_path = '../wov_workdir/logs/tournament_' + pad(req.params.id, 4) + '/table.json';
    var submits_path = '../wov_workdir/logs/tournament_' + pad(req.params.id, 4) + '/submits.json';
    var scores_path = '';
    if (official) {
        scores_path = '../wov_workdir/logs/tournament_' + pad(req.params.id, 4) + '/official_scores.json';
    } else {
        scores_path = '../wov_workdir/logs/tournament_' + pad(req.params.id, 4) + '/official_scores.json';
    }


    var teams_data = JSON.parse(fs.readFileSync(teams_path, 'utf-8'));
    var standings_data = JSON.parse(fs.readFileSync(table_path, 'utf-8'));
    var scores_data = JSON.parse(fs.readFileSync(scores_path, 'utf-8'));
    var submits_data = JSON.parse(fs.readFileSync(submits_path, 'utf-8'));

    for (var i = 0; i < teams_data.length; ++i) {
        teams_data[i].skip = false;
        if (official && !teams_data[i].official) {
            teams_data[i].skip = true;
            continue;
        }

        teams_data[i].submit_id = submits_data.last_submits[teams_data[i].name];
        teams_data[i].scores = [];
        teams_data[i].sum_score = scores_data[teams_data[i].name];

        if (!teams_data[i].submit_id) {
            teams_data[i].skip = true;
        }
    }

    for (var i = 0; i < teams_data.length; ++i) {
        if (teams_data[i].skip) {
            continue;
        }

        for (var j = 0; j < teams_data.length; ++j) {
            if ((official && !teams_data[j].official) || teams_data[j].skip) {
                continue;
            }

            var type = '';
            if (standings_data[i][j][0] == 0) {
                if (standings_data[i][j][1] > standings_data[i][j][2]) type = 'stdrawwin';
                else if (standings_data[i][j][1] < standings_data[i][j][2]) type = 'stdrawloose';
                else type = 'stdraw';
            } else if (standings_data[i][j][0] == 1) {
                if (standings_data[i][j][1] == 1) type = 'sttechwin';
                else if (standings_data[i][j][1] == 2) type = 'stdrawwin';
                else type = 'stwin';
            } else {
                if (standings_data[i][j][2] == 1) type = 'sttechfail';
                else if (standings_data[i][j][2] == 2) type = 'stdrawloose';
                else type = 'stfail';
            }

            teams_data[i].scores.push({
                value: i == j ? '*' : standings_data[i][j][1] + ':' + standings_data[i][j][2],
                opponent_name: teams_data[j].name,
                type: i == j ? '' : type
            })
        }
    }

    res.render('tournament', {
        id: req.params.id,
        teams: teams_data
    });
});

router.get('/:id/game/:team1/:team2', function(req, res, next) {
    var json_log_path = '../wov_workdir/logs/tournament_' + pad(req.params.id, 4) +
        '/' + req.params.team1 + '_' + req.params.team2 + '.json';
    var text_log_path = '../wov_workdir/logs/tournament_' + pad(req.params.id, 4) +
        '/' + req.params.team1 + '_' + req.params.team2 + '.txt';


    var json_log = fs.readFileSync(json_log_path, 'utf-8');
    var parsed_json_log = JSON.parse(json_log);
    res.render('game', {
        log: json_log,
        first_name: parsed_json_log.first,
        second_name: parsed_json_log.second
    });
});

module.exports = router;
