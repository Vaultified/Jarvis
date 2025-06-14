import React, { useState, useRef, useEffect } from "react";
import { processMessage } from "../services/chatService";
import "../styles/Chat.css";

interface Message {
  role: "user" | "assistant";
  content: string;
  isError?: boolean;
  isImage?: boolean;
}

const Chat: React.FC = () => {
  console.log("Chat component rendering");

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Add effect to log messages changes
  useEffect(() => {
    console.log("Messages state updated:", messages);
    console.log("Messages length:", messages.length);
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Form submitted");
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input.trim() };
    console.log("Adding user message:", userMessage);

    // Update messages with user message
    setMessages((prev) => {
      const newMessages = [...prev, userMessage];
      console.log("Updated messages after user message:", newMessages);
      return newMessages;
    });

    setInput("");
    setIsLoading(true);

    try {
      console.log("Sending message:", userMessage.content);
      const response = await processMessage(userMessage.content);
      console.log("Received response:", response);

      if (!response || !response.message) {
        throw new Error("Invalid response format from server");
      }

      // Add the response message with proper type
      const newMessage: Message = {
        role: "assistant",
        content: response.message,
        isImage: response.type === "image",
      };
      console.log("Creating new message:", newMessage);

      // Force a state update with a new array
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages, newMessage];
        console.log("Updated messages after assistant response:", updatedMessages);
        return updatedMessages;
      });

      // Add a debug log after state update
      console.log("State update triggered for assistant response");
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content:
          error instanceof Error
            ? error.message
            : "Sorry, I encountered an error. Please try again.",
        isError: true,
      };
      setMessages((prev) => {
        const updatedMessages = [...prev, errorMessage];
        console.log("Updated messages after error:", updatedMessages);
        return updatedMessages;
      });
    } finally {
      setIsLoading(false);
      // Add a debug log after loading state update
      console.log("Loading state set to false");
    }
  };

  // Add a new useEffect to log component updates
  useEffect(() => {
    console.log("Chat component updated");
    console.log("Current messages state:", messages);
  }, []);

  // Add a new useEffect to log state changes
  useEffect(() => {
    console.log("Messages state changed");
    console.log("New messages state:", messages);
  }, [messages]);

  const renderMessageContent = (message: Message) => {
    console.log("renderMessageContent called with message:", message);
    console.log("Message type:", message.isImage ? "image" : "text");
    console.log("Message content type:", typeof message.content);
    console.log("Message content length:", message.content.length);

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
              e.currentTarget.parentElement!.innerHTML =
                '<div class="error-message">Failed to load image</div>';
            }}
          />
        </div>
      );
    }

    return <div className="message-content">{message.content}</div>;
  };

  console.log("Current messages:", messages);
  console.log("Messages length:", messages.length);

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.length > 0 ? (
          messages.map((message, index) => {
            console.log("Rendering message at index", index, ":", message);
            const messageContent = renderMessageContent(message);
            console.log("Rendered content for message", index, ":", messageContent);

            return (
              <div
                key={`${index}-${message.isImage ? "image" : "text"}`}
                className={`message ${
                  message.role === "user" ? "user-message" : "assistant-message"
                } ${message.isError ? "error" : ""} ${message.isImage ? "image-message" : ""}`}
              >
                {messageContent}
              </div>
            );
          })
        ) : (
          <div className="message assistant-message">
            <div className="message-content">
              No messages yet. Messages length: {messages.length}
            </div>
          </div>
        )}
        {isLoading && (
          <div className="message assistant-message loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
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
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
