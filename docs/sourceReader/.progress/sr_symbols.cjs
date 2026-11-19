const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../../../..');
const ts = require(require.resolve('typescript', { paths: [root] }));
const files = cp.execFileSync('git', ['ls-files', '-z'], { cwd: root, encoding: 'utf8' }).split('\0');
const requested = process.argv.slice(2);
const sources = requested.length ? requested : files.filter(p => /^(server|client|cli|shared|desktop|scripts)\//.test(p) && /\.(tsx|ts|mjs|cjs|js)$/.test(p) && !/(\/dist\/|\/build\/|\.d\.ts$)/.test(p));
const result = [];
for (const file of sources) {
  const text = fs.readFileSync(path.resolve(root, file), 'utf8');
  const source = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true);
  function visit(node, owners = []) {
    const named = ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node) || ts.isClassDeclaration(node) || ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node) || ts.isVariableDeclaration(node) || ts.isEnumDeclaration(node);
    let scope = owners;
    const routeCall = ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression) && /^(?:get|post|put|patch|delete|head|options|all)$/.test(node.expression.name.text) && /^(?:\w*[Rr]outer|app)$/.test(node.expression.expression.getText(source));
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression) && node.arguments.length && (ts.isStringLiteral(node.arguments[0]) || (routeCall && (node.arguments[0].kind === ts.SyntaxKind.RegularExpressionLiteral || ts.isArrayLiteralExpression(node.arguments[0])))) && (routeCall || node.arguments.some(arg => ts.isArrowFunction(arg) || ts.isFunctionExpression(arg)))) {
      const target = ts.isStringLiteral(node.arguments[0]) ? `'${node.arguments[0].text}'` : node.arguments[0].getText(source);
      const name = `${node.expression.getText(source)}(${target})`;
      const symbol = [...owners, name].join('.');
      result.push({ file, symbol, name, kind: 'RegisteredCallback', start: source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1, end: source.getLineAndCharacterOfPosition(node.end).line + 1, top: owners.length === 0, summary: '' });
      scope = [...owners, name];
    }
    if (named && node.name && (ts.isIdentifier(node.name) || ts.isStringLiteral(node.name))) {
      const name = node.name.text;
      const symbol = [...owners, name].join('.');
      const kind = ts.isVariableDeclaration(node) && node.initializer && (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer)) ? 'Function' : ts.SyntaxKind[node.kind];
      const start = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
      const end = source.getLineAndCharacterOfPosition(node.end).line + 1;
      const doc = node.jsDoc?.[0]?.comment;
      result.push({ file, symbol, name, kind, start, end, top: owners.length === 0, summary: typeof doc === 'string' ? doc.split('\n')[0] : '' });
      scope = [...owners, name];
    }
    ts.forEachChild(node, child => visit(child, scope));
  }
  visit(source);
}
process.stdout.write(JSON.stringify(result));
