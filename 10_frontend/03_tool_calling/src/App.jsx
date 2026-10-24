import {useEffect, useRef, useState} from 'react';
import {requestAgent, runTool} from './agent';
import {ToolCallCard} from './cards/ToolCallCard';
import './App.css';

const suggestions = [
    '用模拟工具查询北京天气',
    '帮我算一下 (125 + 37) * 2.5',
    '用模拟工具搜索 LangChain',
];
const initialMessages = [{
    role: 'system',
    content: '你是工具调用教学助手。用户询问天气时调用 get_weather，要求计算时调用 calculate，' +
        '要求搜索时调用 search_web。get_weather 和 search_web 返回的都是本地模拟数据，' +
        '不是真实天气或真实网页。回答时必须明确说明这些数据是模拟的；计算器返回真实计算结果。'
}];
let nextId = 0;
const makeId = () => ++nextId;

function parseArguments(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) return value;
    try {
        const parsed = JSON.parse(value || '{}');
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed;
    } catch (_) { /* Show an error on this tool call and continue the conversation. */
    }
    throw new Error('模型返回的工具参数不是有效的 JSON 对象。');
}

function App() {
    const [models, setModels] = useState([]);
    const [model, setModel] = useState('');
    const [modelLoading, setModelLoading] = useState(true);
    const [input, setInput] = useState('');
    const [turns, setTurns] = useState([]);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const conversation = useRef([...initialMessages]);
    const activeRequest = useRef(null);
    const endRef = useRef(null);

    useEffect(() => {
        const controller = new AbortController();
        fetch('/api/tags', {signal: controller.signal})
            .then(async (response) => {
                if (!response.ok) throw new Error(`读取模型失败（HTTP ${response.status}）`);
                return response.json();
            })
            .then((data) => {
                const names = (data.models || []).map((item) => item.name).filter(Boolean);
                setModels(names);
                setModel(names.find((name) => name.startsWith('llama3.1')) || names[0] || '');
                if (!names.length) setError('Ollama 已连接，但没有安装模型。请先运行 ollama pull llama3.1。');
            })
            .catch((cause) => {
                if (cause.name !== 'AbortError') setError('无法连接 Ollama。请确认服务正在运行，然后刷新页面。');
            })
            .finally(() => {
                if (!controller.signal.aborted) setModelLoading(false);
            });
        return () => controller.abort();
    }, []);

    useEffect(() => {
        endRef.current?.scrollIntoView({behavior: 'smooth'});
    }, [turns, busy, error]);

    function updateTool(id, changes) {
        setTurns((current) => current.map((turn) => turn.id === id ? {...turn, ...changes} : turn));
    }

    async function sendMessage(text) {
        const content = text.trim();
        if (!content || !model || busy) return;
        const previousMessages = conversation.current.slice();
        const previousTurnId = nextId;
        const controller = new AbortController();
        activeRequest.current = controller;
        setBusy(true);
        setError('');
        setInput('');
        setTurns((current) => [...current, {id: makeId(), role: 'user', content}]);
        conversation.current.push({role: 'user', content});

        try {
            for (let round = 0; round < 6; round++) {
                const assistant = await requestAgent(model, conversation.current, controller.signal);
                if (controller.signal.aborted) return;
                conversation.current.push(assistant);
                const reply = typeof assistant.content === 'string' ? assistant.content.trim() : '';
                if (reply) setTurns((current) => [...current, {id: makeId(), role: 'assistant', content: reply}]);
                const calls = Array.isArray(assistant.tool_calls) ? assistant.tool_calls : [];
                if (!calls.length) {
                    if (!reply) setTurns((current) => [...current, {
                        id: makeId(),
                        role: 'assistant',
                        content: '模型没有返回文字。请重试或更换模型。'
                    }]);
                    return;
                }

                for (const call of calls) {
                    if (controller.signal.aborted) return;
                    const name = call.function?.name || 'unknown';
                    const id = makeId();
                    let args = {};
                    let output;
                    let toolError = '';
                    try {
                        args = parseArguments(call.function?.arguments);
                    } catch (cause) {
                        toolError = cause.message;
                    }
                    setTurns((current) => [...current, {id, role: 'tool', name, input: args, status: 'running'}]);
                    if (!toolError) {
                        try {
                            output = await runTool(name, args, controller.signal);
                        } catch (cause) {
                            if (controller.signal.aborted) return;
                            toolError = cause.message || String(cause);
                        }
                    }
                    if (controller.signal.aborted) return;
                    updateTool(id, {status: 'finished', output, error: toolError});
                    conversation.current.push({
                        role: 'tool', tool_name: name,
                        content: JSON.stringify(toolError ? {error: toolError} : output)
                    });
                }
            }
            throw new Error('工具调用次数过多，已停止本轮对话。');
        } catch (cause) {
            if (!controller.signal.aborted) setError(cause.message || '请求失败，请重试。');
        } finally {
            if (activeRequest.current === controller) {
                if (controller.signal.aborted) {
                    conversation.current = previousMessages;
                    setTurns((current) => current.filter((turn) => turn.id <= previousTurnId));
                    setInput(content);
                }
                activeRequest.current = null;
                setBusy(false);
            }
        }
    }

    function clearConversation() {
        activeRequest.current?.abort();
        activeRequest.current = null;
        conversation.current = [...initialMessages];
        setTurns([]);
        setBusy(false);
        setError('');
    }

    return <main className="app-shell">
        <section className="chat-panel" aria-label="工具调用聊天演示">
            <header className="chat-header">
                <div className="brand">
                    <div className="brand-mark">✦</div>
                    <div><p className="eyebrow">OLLAMA · TOOL CALLING</p><h1>工具调用演示</h1></div>
                </div>
                <div className="header-actions">
                    <label className="model-picker"><span>模型</span><select aria-label="选择模型" value={model}
                                                                             disabled={modelLoading || busy || !models.length}
                                                                             onChange={(event) => {
                                                                                 clearConversation();
                                                                                 setModel(event.target.value);
                                                                             }}>
                        {!models.length && <option value="">{modelLoading ? '连接中…' : '无可用模型'}</option>}
                        {models.map((name) => <option key={name} value={name}>{name}</option>)}
                    </select></label>
                    <button className="clear-button" type="button" onClick={clearConversation}
                            disabled={!turns.length}>清空对话
                    </button>
                </div>
            </header>

            <div className="messages" role="log" aria-live="polite">
                {turns.length === 0 && <div className="empty-state">
                    <div className="empty-symbol">✧</div>
                    <h2>让模型调用工具</h2><p>询问模拟天气、计算表达式，或查看模拟搜索结果。工具执行过程会显示在对话中。</p>
                    <div className="suggestions">{suggestions.map((suggestion) => <button key={suggestion} type="button"
                                                                                          disabled={!model || busy}
                                                                                          onClick={() => sendMessage(suggestion)}>{suggestion}<span>↗</span>
                    </button>)}</div>
                </div>}
                {turns.map((turn) => turn.role === 'tool' ?
                    <div className="turn tool-turn" key={turn.id}><ToolCallCard toolCall={turn}/></div> :
                    <div className={`turn ${turn.role}-turn`} key={turn.id}>
                        <div className="avatar">{turn.role === 'user' ? '你' : '✦'}</div>
                        <div className="message-bubble"><span
                            className="role-label">{turn.role === 'user' ? '你' : '助手'}</span><p>{turn.content}</p>
                        </div>
                    </div>)}
                {busy && <div className="thinking"><span className="thinking-dot"/>模型正在处理…</div>}
                {error && <div className="error-message" role="alert">{error}</div>}
                <div ref={endRef}/>
            </div>

            <div className="composer-area">
                <form className="composer" onSubmit={(event) => {
                    event.preventDefault();
                    sendMessage(input);
                }}>
                    <input aria-label="输入消息" value={input} onChange={(event) => setInput(event.target.value)}
                           placeholder={model ? '输入消息，让模型决定何时使用工具…' : '等待 Ollama 模型…'}
                           disabled={!model || busy}/>
                    {busy ? <button type="button" className="stop-button"
                                    onClick={() => activeRequest.current?.abort()}>停止</button> :
                        <button type="submit" disabled={!input.trim() || !model}>发送 <span aria-hidden="true">↑</span>
                        </button>}
                </form>
                <p className="footer-note">本机 Ollama · 天气与搜索均为本地模拟数据</p>
            </div>
        </section>
    </main>;
}

export default App;
