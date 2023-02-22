var config = {
    scriptTitle: { label: 'This script was written by BHVN. Go make it rain!', type: 'title' },
    testWallet: { label: 'Test Wallet:', value: 0, type: 'number' },
    baseDiv: { label: 'Base Dividend:', value: 103, type: 'number' },
    playDiv: { label: 'Play Dividend:', value: 16, type: 'number' },
    jumpMul: { label: 'Jump Multiplier:', value: 8, type: 'number' },
    maxWager: { label: 'Maximum Wager:', value: currency.maxAmount, type: 'number' },
    minWager: { label: 'Minimum Wager:', value: currency.minAmount, type: 'number' },
    cPayout: { label: 'Crash Payout:', value: 10, type: 'number' },
    winRepeat: { label: 'Reset After Win Streak of:', value: 1, type: 'number' },
    loseRepeat: { label: 'Reset After Lose Streak of:', value: 20, type: 'number' },
    increasePercent: { label: 'Increase Percent:', value: 1.15, type: 'number' }
}

function main() {
    // Define variables
    var testWallet = config.testWallet.value
    var baseDiv = config.baseDiv.value
    var playDiv = config.playDiv.value
    var jumpMul = config.jumpMul.value
    var maxWager = config.maxWager.value
    var minWager = config.minWager.value
    var cPayout = config.cPayout.value
    var winRepeat = config.winRepeat.value
    var loseRepeat = config.loseRepeat.value
    var increasePercent = config.increasePercent.value

    // Define wallets and wagers
    var mainWallet = testWallet > 0 ? testWallet : currency.amount
    var playWallet = 0
    var jumpWallet = 0
    var baseWager = 0
    var currentWager = 0

    // Define modes and counters
    var gameMode = 'play'
    var to = 'jump'
    var loseCount = 0


    // Define functions
    function calculateMainWallet(currentWager, win) {
        if (win) {
            mainWallet += (currentWager * cPayout)
            log.success('Won! ' + (currentWager * cPayout).toFixed(4) + ' INR')
        }
        else {
            mainWallet -= currentWager
        }
    }

    function calculatePlayWallet() {
        playWallet = mainWallet / playDiv
    }

    function calculateJumpWallet() {
        jumpWallet = playWallet * jumpMul
    }

    function calculateBaseWager() {
        if (gameMode == 'play') {
            calculatePlayWallet()
            baseWager = playWallet / baseDiv
        }
        else if (gameMode == 'jump') {
            calculateJumpWallet()
            baseWager = jumpWallet / baseDiv
        }
        else if (gameMode == 'monitor') {
            baseWager = minWager
        }
    }

    function calculateCurrentWager() {
        if (gameMode == 'monitor') {
            currentWager = minWager
        }
        else {
            currentWager = baseWager * increasePercent ** loseCount
            if (currentWager < minWager) {
                currentWager = minWager
            }
        }
    }

    function streakReset() {
        if (gameMode != 'monitor') {
            loseCount = 0
        }
        calculateBaseWager()
        calculateCurrentWager()
    }

    function switchToPlayMode() {
        gameMode = 'play'
        log.info('Play mode on!')
        streakReset()
    }

    function maintainPlayMode() {
        gameMode = 'play'
        log.info('Play mode maintained.')
        loseCount = 0
        baseWager > 1 ? currentWager = baseWager : currentWager = 1
    }

    function switchToJumpMode() {
        gameMode = 'jump'
        log.info('Jump mode on!!')
        streakReset()
    }

    function switchToMonitorMode() {
        gameMode = 'monitor'
        log.info('Monitor mode on!!!')
        currentWager = minWager
    }

    function playMode(payout) {
        if (payout >= cPayout) {
            maintainPlayMode()
        }
        else {
            if (loseCount >= loseRepeat - 1) {
                loseCount++
                to = 'jump'
                switchToMonitorMode()
            }
            else {
                loseCount++
                calculateCurrentWager()
                log.error('Lost! #' + loseCount)
            }
        }
    }

    function jumpMode(payout) {
        if (payout >= cPayout) {
            switchToPlayMode()
        }
        else {
            if (loseCount >= loseRepeat - 1) {
                loseCount++
                to = 'play'
                switchToMonitorMode()
            }
            else {
                loseCount++
                calculateCurrentWager()
                log.error('Lost! #' + loseCount)
            }
        }
    }

    function monitorMode(payout) {
        if (payout >= cPayout) {
            if (to == 'jump') {
                switchToJumpMode()
            }
            else if (to == 'play') {
                switchToPlayMode()
            }
            else {
                log.error('Invalid mode to go')
            }
        }
        else {
            loseCount++
            calculateCurrentWager()
            log.error('Lost! #' + loseCount)
        }
    }

    streakReset()

    game.onBet = function () {
        log.info('Wagered: ' + currentWager.toFixed(4) + ' INR')
        game.bet(currentWager, cPayout).then(function (payout) {
            calculateMainWallet(currentWager, payout >= cPayout)
            switch (gameMode) {
                case 'play':
                    playMode(payout)
                    break
                case 'jump':
                    jumpMode(payout)
                    break
                case 'monitor':
                    monitorMode(payout)
                    break
                default:
                    log.error('Invalid game mode')
            }
        })
    }
}