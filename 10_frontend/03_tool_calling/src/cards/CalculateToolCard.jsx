export function CalculateToolCard({toolCall}) {
    const {input = {}, output, error, status} = toolCall;
    return <div className="tool-card calculator-card">
        <div className="tool-card-heading">
            <span className="tool-icon">ƒx</span>
            <span>计算器</span>
            <span className="tool-status">{status === 'running' ? '执行中' : error ? '失败' : '完成'}</span>
        </div>
        <div className="expression">{input.expression || '等待表达式…'}</div>
        {
            error ? <p className="tool-error">{error}</p> : output &&
                <div className="calculation-result">= {output.result}</div>
        }
    </div>;
}
