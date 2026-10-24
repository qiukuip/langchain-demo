import {calculatorTool} from './tools/calculator';
import {weatherTool} from './tools/weather';
import {searchWebTool} from './tools/search-web';

export const toolDefinitions = [
    {
        type: 'function', function: {
            name: 'calculate', description: '计算四则运算表达式，支持括号、小数和取余。',
            parameters: {
                type: 'object',
                properties: {expression: {type: 'string', description: '例如 (12.5 + 3) * 2'}},
                required: ['expression']
            }
        }
    },
    {
        type: 'function', function: {
            name: 'get_weather', description: '返回城市的模拟天气，仅用于学习工具调用流程，并非实时数据。',
            parameters: {
                type: 'object',
                properties: {city: {type: 'string', description: '城市名，例如北京'}},
                required: ['city']
            }
        }
    },
    {
        type: 'function', function: {
            name: 'search_web', description: '返回本地模拟搜索结果，仅用于学习工具调用流程，并非真实网页。',
            parameters: {
                type: 'object',
                properties: {query: {type: 'string', description: '搜索关键词'}},
                required: ['query']
            }
        }
    },
];

const implementations = {calculate: calculatorTool, get_weather: weatherTool, search_web: searchWebTool};

export async function runTool(name, args, signal) {
    const implementation = implementations[name];
    if (!implementation) throw new Error(`未知工具：${name}`);
    // 留出短暂时间展示“执行中”状态，方便观察工具调用的完整过程。
    await new Promise((resolve, reject) => {
        if (signal?.aborted) return reject(new DOMException('已停止', 'AbortError'));
        const timer = setTimeout(() => {
            signal?.removeEventListener('abort', onAbort);
            resolve();
        }, 500);

        function onAbort() {
            clearTimeout(timer);
            reject(new DOMException('已停止', 'AbortError'));
        }

        signal?.addEventListener('abort', onAbort, {once: true});
    });
    return implementation(args, signal);
}

export async function requestAgent(model, messages, signal) {
    const response = await fetch('/api/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, signal,
        body: JSON.stringify({
            model, messages, tools: toolDefinitions, stream: false,
            options: {temperature: 0.2}
        }),
    });
    if (!response.ok) {
        const detail = await response.text();
        throw new Error(`Ollama 请求失败（HTTP ${response.status}）：${detail.slice(0, 240)}`);
    }
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    if (!data.message) throw new Error('Ollama 没有返回消息。');
    return data.message;
}
