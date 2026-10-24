const conditions = ['晴朗', '局部多云', '小雨', '多云'];

export async function weatherTool({city}) {
    const name = String(city ?? '').trim();
    if (!name) throw new Error('请提供城市名称。');
    // 固定算法让同一个城市始终得到同一份演示数据。
    const seed = Array.from(name).reduce((sum, character) => sum + character.codePointAt(0), 0);
    return {
        city: name,
        temperature: 15 + seed % 17,
        feelsLike: 14 + seed % 17,
        humidity: 35 + seed % 50,
        windSpeed: 3 + seed % 15,
        condition: conditions[seed % conditions.length],
        source: '本地模拟数据',
    };
}
