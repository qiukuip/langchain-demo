export function SearchToolCard({toolCall}) {
    const {input = {}, output, error, status} = toolCall;
    return <div className="tool-card search-card">
        <div className="tool-card-heading"><span className="tool-icon">⌕</span><span>模拟搜索</span><span
            className="tool-status">{status === 'running' ? '搜索中' : error ? '失败' : '完成'}</span></div>
        <p className="search-query">“{input.query || '…'}”</p>
        {error ? <p className="tool-error">{error}</p> : output ? output.results.length ?
            <div className="search-results">{output.results.map((result, index) => <div className="search-result"
                                                                                        key={index}>
                <strong>{result.title}</strong><p>{result.snippet}</p>
            </div>)}</div> : <p className="tool-pending">没有找到相关条目。</p> : null}
    </div>;
}
