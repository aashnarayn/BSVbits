const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

function runBsvbitsCli(args, outputChannel) {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders || folders.length === 0) {
        vscode.window.showErrorMessage('Open the BSVbits repository folder in VS Code first.');
        return;
    }
    const root = folders[0].uri.fsPath;
    const cli = path.join(root, 'bsvbits');
    outputChannel.show(true);
    outputChannel.appendLine(`\n$ ./bsvbits ${args.join(' ')}`);
    cp.execFile('python3', [cli, ...args], { cwd: root }, (err, stdout, stderr) => {
        if (stdout) outputChannel.appendLine(stdout);
        if (stderr) outputChannel.appendLine(stderr);
        if (!err && args[0] === 'submit') {
            vscode.window.showInformationMessage('BSVbits: Passed all Bluesim tests!');
        } else if (err && args[0] === 'submit') {
            vscode.window.showWarningMessage('BSVbits: Check output panel or workspace/last_result.md for diagnostics.');
        }
    });
}

function activate(context) {
    const out = vscode.window.createOutputChannel('BSVbits BSC');
    context.subscriptions.push(
        vscode.commands.registerCommand('bsvbits.submit', () => {
            vscode.workspace.saveAll(false).then(() => runBsvbitsCli(['submit'], out));
        }),
        vscode.commands.registerCommand('bsvbits.hint', () => runBsvbitsCli(['hint'], out)),
        vscode.commands.registerCommand('bsvbits.generateCp', () => runBsvbitsCli(['generate'], out)),
        vscode.commands.registerCommand('bsvbits.nextProblem', () => runBsvbitsCli(['next'], out))
    );
}

function deactivate() {}

module.exports = { activate, deactivate };
