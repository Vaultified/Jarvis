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
    if (!isPassiveListening) {
      return;
    }
    try {
      const response = await fetch("http://localhost:8000/api/passive-listen", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        console.error(`HTTP error! status: ${response.status}`);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Error connecting to listening service: HTTP status ${response.status}.`,
          },
        ]);
        if (isPassiveListening) {
          setTimeout(awaitPassiveSpeech, 3000);
        }
        return;
      }

      const data = await response.json();
      console.log("Passive listen response:", data);

      switch (data.status) {
        case "success":
          if (data.text && data.text.trim()) {
            const transcribedText = data.text.trim();
            console.log("Transcribed Text:", transcribedText);

            setMessages((prev) => [...prev, { role: "user", content: transcribedText }]);
            setInput("");

            const chatResponse = await fetch("http://localhost:8000/api/chat", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ prompt: transcribedText }),
            });

            if (!chatResponse.ok) {
              const chatErrorData = await chatResponse.json();
              console.error(`Chat API error! status: ${chatResponse.status}`, chatErrorData);
              setMessages((prev) => [
                ...prev,
                {
                  role: "assistant",
                  content: `Error getting response from AI: ${
                    chatErrorData.detail || "Unknown error"
                  }`,
                },
              ]);
            } else {
              const chatData = await chatResponse.json();
              console.log("Chat response:", chatData);

              setMessages((prev) => [...prev, { role: "assistant", content: chatData.response }]);

              const speakResponse = await fetch("http://localhost:8000/api/speak", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: chatData.response }),
              });

              if (!speakResponse.ok) {
                console.error("Failed to speak response", await speakResponse.text());
              }
            }
          } else {
            console.log("Success status but no text returned.");
          }
          break;

        case "waiting":
          console.log(data.message);
          break;

        case "timeout":
          console.log(data.message);
          break;

        case "too_short":
          console.log(data.message);
          break;

        case "no_speech":
          console.log(data.message);
          break;

        case "error":
          console.error("Error in passive listening:", data.message);
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: `Listening error: ${data.message}. Please try again.`,
            },
          ]);
          break;

        default:
          console.warn("Unknown status from passive listening:", data.status);
      }

      if (isPassiveListening) {
        setTimeout(awaitPassiveSpeech, 100);
      }
    } catch (error) {
      console.error("Caught error in passive listening:", error);
      if (isPassiveListening) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "An unexpected listening error occurred. Please restart listening.",
          },
        ]);
        setTimeout(awaitPassiveSpeech, 5000);
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
