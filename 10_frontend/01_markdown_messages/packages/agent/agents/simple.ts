import { createAgent } from "langchain";

export const agent = createAgent({
  model: "ollama:llama3.1"
});
