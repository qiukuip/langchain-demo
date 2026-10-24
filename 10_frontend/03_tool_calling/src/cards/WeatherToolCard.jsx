const iconFor = (condition = '') => /雨|雪|雷/.test(condition) ? '🌧️' : /晴/.test(condition) ? '☀️' : '☁️';

export function WeatherToolCard({toolCall}) {
    const {input = {}, output, error, status} = toolCall;
    return <div className="tool-card weather-card">
        <div className="tool-card-heading">
            <span className="tool-icon">{output ? iconFor(output.condition) : '◌'}</span>
            <span>模拟天气</span>
            <span className="tool-status">{status === 'running' ? '查询中' : error ? '失败' : '完成'}</span>
        </div>
        {
            error ? <p className="tool-error">{error}</p> : output ? <>
                <div className="weather-main">
                    <div>
                        <strong>{output.city}</strong>
                        <span>{output.condition}</span>
                    </div>
                    <div className="weather-temperature">
                        {output.temperature}°
                    </div>
                </div>
                <div className="weather-details">
                    <span>体感 {output.feelsLike}°C</span>
                    <span>湿度 {output.humidity}%</span>
                    <span>风速 {output.windSpeed} km/h</span>
                </div>
                <small>来源：{output.source} · 非实时天气</small>
            </> : <p className="tool-pending">正在查询 {input.city || '城市'}…</p>
        }
    </div>;
}
