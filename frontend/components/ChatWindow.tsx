"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import LoadingIndicator from "./LoadingIndicator";
import { sendMessage } from "@/lib/api";
import { Message } from "@/lib/types";

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to PartSelect Assistant! I can help you find refrigerator and dishwasher parts, check compatibility, provide installation guides, and troubleshoot issues. What do you need help with?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call FastAPI via NextJS API route
      const response = await sendMessage(input, messages);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.message,
          parts: response.parts,
        },
      ]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I encountered an error. Please make sure the backend is running and try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="bg-partselect-blue text-white p-4 shadow-md">
        <h1 className="text-2xl font-bold">PartSelect Assistant</h1>
        <p className="text-sm text-blue-100 mt-1">
          Refrigerator & Dishwasher Parts Expert
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-partselect-gray">
        {messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-300 bg-white p-4 shadow-lg">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about parts, compatibility, installation, troubleshooting..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-partselect-blue focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-partselect-orange hover:bg-orange-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition disabled:cursor-not-allowed"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-2 text-center">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
