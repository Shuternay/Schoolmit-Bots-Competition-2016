var express = require('express');
var fs = require('fs');
var spawn = require('child_process').spawn;
var router = express.Router();

function pad(n, size) {
    var s = String(n);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
}

router.get('/', function(req, res, next) {
    res.render('submit');
});

router.get('/view', function(req, res, next) {
    var submits_path = '../wov_workdir/submits/submits.json';
    var submits = JSON.parse(fs.readFileSync(submits_path, 'utf-8'));
    res.render('submits', {
        submits: submits.submits
    });
});

router.post('/', function(req, res, next) {
    var login = req.body.login;
    var password = req.body.pass;
    var code = req.body.code;
    var language = req.body.language;

    if (login.indexOf('/') != -1 || login.indexOf('_') != -1) {
        res.render('error', {
            message: 'Странный логин (' + login + ')'
        });
    }

    var password_path = '../wov_workdir/users/' + login + '_pass.txt';
    if (!fs.existsSync(password_path)) {
        res.render('error', {
            message: 'Неверный логин (' + login + ')'
        });
    }
    var correct_password = fs.readFileSync(password_path, 'utf-8').trim();

    if (password != correct_password) {
        res.render('error', {
            message: 'Неверный пароль'
        });
    }

    var submits_path = '../wov_workdir/submits/submits.json';
    var submits = JSON.parse(fs.readFileSync(submits_path, 'utf-8'));
    var submit_number = submits.submits.length;
    var submit_path = '../wov_workdir/submits/run_' + pad(submit_number, 4);
    fs.writeFileSync(submit_path, code);

    submits.submits.push({owner: login, lang: language, time: new Date().toString()});
    submits.last_submits[login] = submit_number;
    fs.writeFileSync(submits_path, JSON.stringify(submits, null, ' '));

    var p = spawn('python3', ['../war_of_viruses/scripts/RunTournament.py'], {cwd: '../wov_workdir'});

    //p.stdout.on('data', function (data) {
    //    console.log('stdout: ${data}');
    //});
    //
    //p.stderr.on('data', function (data) {
    //    console.log('stderr: ${data}');
    //});


    res.redirect('/submit/view');
});

module.exports = router;