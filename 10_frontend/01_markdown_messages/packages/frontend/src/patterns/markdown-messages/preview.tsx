import { useRef, useState } from "react";
import { useStream } from "@langchain/react";
import { HumanMessage, AIMessage } from "langchain";
import type { simpleAgent } from "@langchain/playground-agents";

import { AGENT_SERVER_URL, SLUG_TO_ASSISTANT } from "@/constants";
import {
  ChatContainer,
  AIBubble,
  HumanBubble,
  ChatInput,
  TypingIndicator,
  PresetPrompts,
  Markdown,
} from "@/components/playground";

const PRESETS = [
  "Write a quick-start guide for building a REST API with Express.js",
  "Compare Python and Rust in a table with pros and cons",
  "Explain the merge sort algorithm with code examples",
];

export default function MarkdownMessagesChat() {
  const [threadId, setThreadId] = useState<string | null>(null);
  const stream = useStream<typeof simpleAgent>({
    apiUrl: AGENT_SERVER_URL,
    assistantId: SLUG_TO_ASSISTANT["markdown-messages"],
    threadId,
    onThreadId: setThreadId,
  });

  const bottomRef = useRef<HTMLDivElement>(null);
  const handleSubmit = (text: string) => {
    stream.submit({ messages: [{ type: "human" as const, content: text }] });
  };

  return (
    <ChatContainer
      input={
        <ChatInput
          onSubmit={handleSubmit}
          disabled={stream.isLoading}
          onNewThread={stream.messages.length > 0 ? () => setThreadId(null) : undefined}
        />
      }
    >
      {stream.messages.length === 0 && <PresetPrompts prompts={PRESETS} onSelect={handleSubmit} />}

      {stream.messages.map((msg) => {
        if (HumanMessage.isInstance(msg)) {
          return (
            <HumanBubble key={msg.id}>
              <Markdown>{msg.text}</Markdown>
            </HumanBubble>
          );
        }

        if (AIMessage.isInstance(msg)) {
          return (
            <AIBubble key={msg.id}>
              <Markdown>{msg.text}</Markdown>
            </AIBubble>
          );
        }

        return null;
      })}

      {stream.isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </ChatContainer>
  );
}
