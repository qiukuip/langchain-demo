export function GenericToolCard({toolCall}) {
    return <div className="tool-card">
        <div className="tool-card-heading">
            <span className="tool-icon">⌘</span><span>{toolCall.name}</span>
            <span className="tool-status">{toolCall.status === 'running' ? '执行中' : '完成'}</span>
        </div>
        <pre>
            {
                JSON.stringify(toolCall.input, null, 2)}
        </pre>
        {
            toolCall.error ? <p className="tool-error">{toolCall.error}</p> : toolCall.output &&
                <pre>{JSON.stringify(toolCall.output, null, 2)}</pre>
        }
    </div>;
}
