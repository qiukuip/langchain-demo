export function calculatorTool({expression}) {
    const source = String(expression ?? '').replace(/\s+/g, '');
    if (!source || source.length > 120 || !/^[\d.+\-*/()%]+$/.test(source)) {
        throw new Error('请输入 120 字符以内的四则运算表达式。');
    }
    let position = 0;

    function parseExpression() {
        let value = parseTerm();
        while (source[position] === '+' || source[position] === '-') {
            const operator = source[position++];
            const right = parseTerm();
            value = operator === '+' ? value + right : value - right;
        }
        return value;
    }

    function parseTerm() {
        let value = parseFactor();
        while (source[position] === '*' || source[position] === '/' || source[position] === '%') {
            const operator = source[position++];
            const right = parseFactor();
            if ((operator === '/' || operator === '%') && right === 0) throw new Error('除数不能为 0。');
            value = operator === '*' ? value * right : operator === '/' ? value / right : value % right;
        }
        return value;
    }

    function parseFactor() {
        if (source[position] === '+' || source[position] === '-') {
            const operator = source[position++];
            const value = parseFactor();
            return operator === '-' ? -value : value;
        }
        if (source[position] === '(') {
            position++;
            const value = parseExpression();
            if (source[position++] !== ')') throw new Error('括号不匹配。');
            return value;
        }
        const match = /^(?:\d+(?:\.\d*)?|\.\d+)/.exec(source.slice(position));
        if (!match) throw new Error('表达式格式错误。');
        position += match[0].length;
        return Number(match[0]);
    }

    const result = parseExpression();
    if (position !== source.length || !Number.isFinite(result)) throw new Error('表达式格式错误或结果超出范围。');
    return {expression: source, result: Number(result.toPrecision(12))};
}
