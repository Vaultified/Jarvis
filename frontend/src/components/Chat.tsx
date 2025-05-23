import React, { useState, useRef, useEffect } from "react";
import "../styles/Chat.css";

interface Message {
  role: "user" | "assistant";
  content: string;
}

async function speakText(text: string) {
  try {
    await fetch("http://localhost:8000/api/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
  } catch (error) {
    console.error("TTS error:", error);
    // Optionally show a frontend error message
  }
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isPassiveListening, setIsPassiveListening] = useState(false);
  const [passiveListenRetryCount, setPassiveListenRetryCount] = useState(0);
  const MAX_PASSIVE_LISTEN_RETRIES = 5;
  const RETRY_DELAY_MS = 5000;
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const awaitPassiveSpeech = async () => {
    if (isPassiveListening) {
      console.log("Frontend: Passive listening already active, skipping.");
      return;
    }

    setIsPassiveListening(true);
    console.log(
      `Frontend: Awaiting passive speech via /api/passive-listen (Attempt ${
        passiveListenRetryCount + 1
      })`
    );

    try {
      const res = await fetch("http://localhost:8000/api/passive-listen", { method: "POST" });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Passive listen API error: ${res.status} - ${errorText}`);
      }

      const data = await res.json();

      setIsPassiveListening(false);
      setPassiveListenRetryCount(0);

      if (data.text && data.text.trim()) {
        console.log("Frontend: Received transcribed text:", data.text);
        const userMessage: Message = { role: "user", content: data.text };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        setIsLoading(true);
        try {
          const response = await fetch("http://localhost:8000/api/chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ prompt: data.text }),
          });

          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(
              `Chat network response after passive listen was not ok: ${response.status} - ${errorText}`
            );
          }

          const respData = await response.json();
          const assistantMessage: Message = { role: "assistant", content: respData.response };
          setMessages((prev) => [...prev, assistantMessage]);
          speakText(respData.response);
        } catch (chatError: any) {
          console.error("Chat API error after passive listen:", chatError);
          const errorMessage: Message = {
            role: "assistant",
            content: `Sorry, I had trouble processing that request after listening. Error: ${
              chatError.message || chatError
            }`,
          };
          setMessages((prev) => [...prev, errorMessage]);
        } finally {
          setIsLoading(false);
          setTimeout(awaitPassiveSpeech, 1000);
        }
      } else {
        console.log("Frontend: Received empty transcribed text.");
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Didn't catch that. Please try again after saying 'Hey Jarvis'.",
          },
        ]);
        setTimeout(awaitPassiveSpeech, 1000);
      }
    } catch (error: any) {
      console.error("Passive listen API error:", error);
      setIsPassiveListening(false);

      if (passiveListenRetryCount < MAX_PASSIVE_LISTEN_RETRIES) {
        const nextRetryCount = passiveListenRetryCount + 1;
        setPassiveListenRetryCount(nextRetryCount);
        console.log(
          `Frontend: Retrying passive listen in ${
            RETRY_DELAY_MS / 1000
          } seconds (Retry ${nextRetryCount}/${MAX_PASSIVE_LISTEN_RETRIES})`
        );
        setTimeout(awaitPassiveSpeech, RETRY_DELAY_MS);
      } else {
        console.error("Frontend: Max passive listen retries reached.");
        setPassiveListenRetryCount(0);

        const errorMessage: Message = {
          role: "assistant",
          content: `Sorry, I encountered a persistent issue with voice input. Error: ${
            error.message || error
          }`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    }
  };

  useEffect(() => {
    awaitPassiveSpeech();

    return () => {
      // You could add a call to a backend endpoint like /stop-listening here
      // if your backend PassiveListener had a stop method accessible via API.
      // listener.stop() is already available in the backend service,
      // but needs an API endpoint to be triggered from frontend cleanup.
    };
  }, []);

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
      console.error("Chat error:", error);
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
      console.log("Frontend: Recording 5 seconds via /api/listen");
      const res = await fetch("http://localhost:8000/api/listen", { method: "POST" });
      const data = await res.json();

      if (data.text && data.text.trim()) {
        console.log("Frontend: Received transcribed text (5s):", data.text);
        const userMessage: Message = { role: "user", content: data.text };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        setIsLoading(true);
        try {
          const response = await fetch("http://localhost:8000/api/chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ prompt: data.text }),
          });

          if (!response.ok) throw new Error("Chat network response was not ok");

          const respData = await response.json();
          const assistantMessage: Message = { role: "assistant", content: respData.response };
          setMessages((prev) => [...prev, assistantMessage]);
          speakText(respData.response);
        } catch (chatError) {
          console.error("Chat API error after 5s listen:", chatError);
          const errorMessage: Message = {
            role: "assistant",
            content: "Sorry, I had trouble processing that request after 5s listen.",
          };
          setMessages((prev) => [...prev, errorMessage]);
        } finally {
          setIsLoading(false);
        }
      } else {
        console.log("Frontend: Received empty transcribed text (5s).");
      }
    } catch (error) {
      console.error("5s listen API error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an issue with 5s voice input.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      {isPassiveListening ? (
        <div className="passive-listening-status">
          <span role="img" aria-label="microphone">
            👂
          </span>{" "}
          Listening for "Hey Jarvis"...
        </div>
      ) : (
        <div className="passive-listening-status">
          <span role="img" aria-label="speaker">
            🔇
          </span>{" "}
          Passive listening idle.
        </div>
      )}

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
          placeholder={isPassiveListening ? "Speak after 'Hey Jarvis'" : "Type your message..."}
          className="chat-input"
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !input.trim()}>
          Send
        </button>
        <button
          type="button"
          className="mic-button"
          onClick={handleMicClick}
          disabled={isLoading || isPassiveListening}
        >
          🎤
        </button>
      </form>
    </div>
  );
};

export default Chat;
