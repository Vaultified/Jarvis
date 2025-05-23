import React, { useState, useRef, useEffect } from "react";
import "../styles/Chat.css";

interface Message {
  role: "user" | "assistant";
  content: string;
}

async function speakText(text: string) {
  await fetch("http://localhost:8000/api/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: input }),
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const data = await response.json();
      const assistantMessage: Message = { role: "assistant", content: data.response };
      setMessages((prev) => [...prev, assistantMessage]);
      speakText(data.response);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMicClick = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/listen", { method: "POST" });
      const data = await res.json();
      if (data.text && data.text.trim()) {
        const userMessage: Message = { role: "user", content: data.text };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        const response = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt: data.text }),
        });
        if (!response.ok) throw new Error("Network response was not ok");
        const respData = await response.json();
        const assistantMessage: Message = { role: "assistant", content: respData.response };
        setMessages((prev) => [...prev, assistantMessage]);
        speakText(respData.response);
      }
    } catch (error) {
      console.error("STT error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role === "user" ? "user-message" : "assistant-message"}`}
          >
            {message.content}
          </div>
        ))}
        {isLoading && <div className="message assistant-message loading">Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !input.trim()}>
          Send
        </button>
        <button type="button" className="mic-button" onClick={handleMicClick} disabled={isLoading}>
          🎤
        </button>
      </form>
    </div>
  );
};

export default Chat;
