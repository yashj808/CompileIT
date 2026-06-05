const BASE_URL = ""; // Proxy handles this

export async function compilePrompt(prompt, onStageComplete) {
  const response = await fetch(`${BASE_URL}/api/compile/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, max_retries: 2 })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const lines = decoder.decode(value).split("\n\n");
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          onStageComplete(data);
        } catch (e) {
          console.error("Error parsing SSE line:", line, e);
        }
      }
    }
  }
}
