import { FormEvent, useEffect, useState } from "react";
import Markdown from "react-markdown";
import "./chat.css";

const OLLAMA_API = "/api/ollama";

type ChatMessage = {
    id: number;
    role: "user" | "assistant";
    content: string;
};

type OllamaModel = {
    name: string;
};

export function Chat() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [models, setModels] = useState<OllamaModel[]>([]);
    const [model, setModel] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingModels, setIsLoadingModels] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const controller = new AbortController();
        fetch(`${OLLAMA_API}/api/tags`, { signal: controller.signal })
            .then(async (response) => {
                if (!response.ok) throw new Error(`读取 Ollama 模型失败（HTTP ${response.status}）`);
                return response.json();
            })
            .then((data: { models?: OllamaModel[] }) => {
                const availableModels = data.models ?? [];
                setModels(availableModels);
                if (availableModels.length > 0) setModel(availableModels[0].name);
                else setError("Ollama 已连接，但没有找到已安装的模型。请先运行 ollama pull <模型名>。");
            })
            .catch((cause: unknown) => {
                if (cause instanceof Error && cause.name === "AbortError") return;
                setError(cause instanceof Error ? cause.message : "无法连接 Ollama。请确认 Ollama 正在运行。");
            })
            .finally(() => setIsLoadingModels(false));
        return () => controller.abort();
    }, []);

    const sendMessage = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const content = input.trim();
        if (!content || !model || isLoading) return;

        const userMessage: ChatMessage = { id: Date.now(), role: "user", content };
        const assistantId = Date.now() + 1;
        const assistantMessage: ChatMessage = { id: assistantId, role: "assistant", content: "" };
        const conversation = [...messages, userMessage];
        setMessages([...conversation, assistantMessage]);
        setInput("");
        setError("");
        setIsLoading(true);

        try {
            const response = await fetch(`${OLLAMA_API}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    model,
                    messages: conversation.map(({ role, content: messageContent }) => ({ role, content: messageContent })),
                    stream: true,
                }),
            });
            if (!response.ok) {
                const detail = await response.text();
                throw new Error(`Ollama 请求失败（HTTP ${response.status}）：${detail || response.statusText}`);
            }
            if (!response.body) throw new Error("Ollama 没有返回可读取的响应流。");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let pending = "";
            const addChunk = (line: string) => {
                if (!line.trim()) return;
                const data = JSON.parse(line) as { message?: { content?: string }; error?: string };
                if (data.error) throw new Error(data.error);
                const chunk = data.message?.content ?? "";
                if (chunk) {
                    setMessages((current) => current.map((item) => item.id === assistantId
                        ? { ...item, content: item.content + chunk }
                        : item));
                }
            };

            while (true) {
                const { value, done } = await reader.read();
                pending += decoder.decode(value, { stream: !done });
                const lines = pending.split("\n");
                pending = lines.pop() ?? "";
                for (const line of lines) addChunk(line);
                if (done) break;
            }
            if (pending.trim()) addChunk(pending);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "请求 Ollama 时发生未知错误。");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="chat-page">
            <section className="chat-panel" aria-label="Ollama 聊天演示">
                <header className="chat-header">
                    <div className="status-dot" aria-hidden="true" />
                    <div className="chat-title">
                        <div>
                            <p className="eyebrow">LOCAL MODEL · OLLAMA</p>
                            <h1>Ollama 聊天</h1>
                        </div>
                        <label className="model-picker">
                            <span>模型</span>
                            <select value={model} onChange={(event) => setModel(event.target.value)} disabled={isLoadingModels || isLoading || models.length === 0}>
                                {models.length === 0 && <option value="">{isLoadingModels ? "读取模型…" : "无可用模型"}</option>}
                                {models.map((availableModel) => <option key={availableModel.name} value={availableModel.name}>{availableModel.name}</option>)}
                            </select>
                        </label>
                    </div>
                </header>

                <div className="messages" aria-live="polite">
                    {messages.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon" aria-hidden="true">✦</div>
                            <h2>{isLoadingModels ? "正在连接 Ollama" : "开始一段对话"}</h2>
                            <p>{isLoadingModels ? "正在读取本机已安装的模型…" : "消息将直接发送给本机 Ollama 模型。"}</p>
                        </div>
                    ) : messages.map((message) => (
                        <div className={`message ${message.role === "user" ? "human-message" : "assistant-message"}`} key={message.id}>
                            {message.role === "assistant" ? <Markdown>{message.content || (isLoading ? "…" : "")}</Markdown> : message.content}
                        </div>
                    ))}
                    {error && <p className="error-message">{error}</p>}
                </div>

                <form className="composer" onSubmit={sendMessage}>
                    <input
                        aria-label="输入消息"
                        placeholder={model ? `发送给 ${model}…` : "等待 Ollama 模型…"}
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        disabled={!model || isLoading}
                    />
                    <button type="submit" disabled={!input.trim() || !model || isLoading}>发送 <span aria-hidden="true">↑</span></button>
                </form>
                <p className="connection-note">直接连接本机 Ollama · localhost:11434</p>
            </section>
        </main>
    );
}
