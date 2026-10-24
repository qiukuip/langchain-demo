export async function searchWebTool({query}) {
    const term = String(query ?? '').trim();
    if (!term) throw new Error('请提供搜索关键词。');
    return {
        query: term,
        source: '本地模拟数据',
        results: [
            {title: `${term}：概览`, snippet: `这是关于“${term}”的模拟搜索摘要，用于展示模型读取工具结果的流程。`},
            {title: `${term}：入门指南`, snippet: `模拟结果：可以让模型根据这段文本继续回答，并观察完整的工具调用链。`},
            {title: `${term}：相关资料`, snippet: `模拟结果：本示例没有访问搜索引擎或其他外部服务。`},
        ],
    };
}
