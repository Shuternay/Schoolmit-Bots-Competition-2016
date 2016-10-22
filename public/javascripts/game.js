var N = 10;

var GAMELOG = null;
var DEFAUL_STEP = 400.0;
var STEP = DEFAUL_STEP;

var timerId = null;
var currentMove = -1;

var FIELD = null;

function createEmptyField() {
    var field = [];
    for (var i = 0; i < N; ++i) {
        field.push([]);
        for (var j = 0; j < N; ++j) {
            field[i].push({value: 0, dark: false});
        }
    }
    return field;
}

function clearField() {
    FIELD = createEmptyField();
}

function renderField() {
    for (var i = 0; i < N; ++i) {
        for (var j = 0; j < N; ++j) {
            //var img_name = (FIELD[i][j].dark ? 'dark' : '') + FIELD[i][j].value.toString();
            var img_name = FIELD[i][j].value.toString();
            var cell_html = '<img src="/images/' + img_name + '.png" width="32" height="32"/>';
            $('#cell' + i.toString() + '_' + j.toString()).html($(cell_html));
        }
    }
}

function onInit() {
    GAMELOG = JSON.parse($('#data').text());
    clearField();
    renderField();
    $('#totalmoves').text(GAMELOG.log.length.toString());
    $('#currmove').text(currentMove + 1);
}

function applyCurrentMove() {
    if (currentMove == -1) {
        clearField();
    } else {
        var nf = GAMELOG.log[currentMove].field;
        for (var i = 0; i < N; ++i) {
            for (var j = 0; j < N; ++j) {
                FIELD[i][j].value = nf[i][j];
                var pf = 0;
                if (currentMove > 0) {
                    pf = GAMELOG.log[currentMove - 1].field[i][j]
                }
                FIELD[i][j].dark = nf[i][j] != pf;
            }
        }
    }

    renderField();
    if (currentMove == -1) {
        $('#currmove').text(0);
    } else {
        $('#currmove').html($('<span class="pl' + GAMELOG.log[currentMove].from + '">' + (currentMove + 1).toString() + '</span>'));
    }
    if (currentMove == -1) {
        $('#status').text('');
    } else {
        var comment = GAMELOG.log[currentMove].comment;
        if (comment == 'ok') {
            comment = '';
        }
        if (comment.indexOf('Skip') != -1) {
            comment = 'Пропуск хода';
        }
        if (comment.indexOf('No turns') != -1) {
            comment = 'Нет ходов';
        }
        $('#status').text(comment);
    }

    if (currentMove + 1 == GAMELOG.log.length) {
        var wid = GAMELOG.result.winner;
        if (wid == 0) {
            $('#winner').text('Ничья!');
        } else {
            var winnername = wid == 1 ? GAMELOG.first : GAMELOG.second;
            $('#winner').html($('<span/>Победитель: <span class="pl' + wid.toString()+ '">' + winnername + '</span>'));
        }
        $('#score').html($('<span/>Счет: <span class="pl1">' + GAMELOG.result.score_1.toString() + '</span>:' +
            '<span class="pl2">' + GAMELOG.result.score_2.toString() + '</span>'));
    } else {
        $('#winner').text('');
        $('#score').text('');
    }
}

function nextMove() {
    applyCurrentMove();
    currentMove++;
    if (currentMove < GAMELOG.log.length) {
        timerId = setTimeout(nextMove, STEP);
    }
}

function onNextMove() {
    clearTimeout(timerId);
    timerId = null;
    if (currentMove + 1 < GAMELOG.log.length) {
        currentMove++;
    }
    applyCurrentMove();
}

function onPrevMove() {
    clearTimeout(timerId);
    timerId = null;
    if (currentMove >= 0) {
        currentMove--;
    }
    applyCurrentMove();
}

// Handler to start game
function onStartGame() {
    STEP = DEFAUL_STEP;

    if (currentMove == GAMELOG.log.length) {
        currentMove = -1;
        clearField();
    }
    renderField();
    clearTimeout(timerId);
    timerId = null;
    timerId = setTimeout(nextMove, STEP);
}

function onPauseGame() {
    clearTimeout(timerId);
    timerId = null;
}

function onFaster() {
    STEP /= 1.1;
}

function onSlower() {
    STEP *= 1.1;
}

function onStopGame() {
    clearTimeout(timerId);
    timerId = null;
    currentMove = -1;
    applyCurrentMove();
}

document.onkeydown = function(event) {
    console.log(event);
    if (event.keyCode == 32) { //space
        if (timerId) {
            onPauseGame();
        } else {
            onStartGame();
        }
    } else if (event.keyCode == 37) { // left
        onPrevMove();
    } else if (event.keyCode == 39) { // right
        onNextMove();
    }
};

window.onload = function() {
    onInit();
};