import React, { useState, useRef, useEffect } from "react";
import { processMessage } from "../services/chatService";
import "./Chat.css";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { type: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await processMessage(userMessage);
      console.log("Received response:", response);

      if (response.type === "image") {
        setMessages((prev) => [
          ...prev,
          {
            type: "assistant",
            content: response.message,
            isImage: true,
          },
        ]);
      } else if (response.type === "gmail") {
        setMessages((prev) => [
          ...prev,
          {
            type: "assistant",
            content: response.message,
            isGmail: true,
            success: response.success,
            error: response.error,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            type: "assistant",
            content: response.message || response.content,
          },
        ]);
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          content: "Sorry, I encountered an error processing your request.",
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (message) => {
    if (message.isImage) {
      return (
        <div className="image-container">
          <img
            src={message.content}
            alt="Shared image"
            className="shared-image"
            onError={(e) => {
              console.error("Error loading image:", e);
              e.currentTarget.style.display = "none";
              e.currentTarget.parentElement.innerHTML =
                '<div class="error-message">Failed to load image</div>';
            }}
          />
        </div>
      );
    }

    return (
      <div className="message-content">
        {message.content}
        {message.isGmail && (
          <div className={`gmail-status ${message.success ? "success" : "error"}`}>
            {message.success ? "✓" : "✗"}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.type} ${message.isError ? "error" : ""} ${
              message.isGmail ? "gmail" : ""
            } ${message.isImage ? "image-message" : ""}`}
          >
            {renderMessageContent(message)}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
