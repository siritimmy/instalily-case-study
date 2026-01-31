"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
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
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = { role: "user", content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call FastAPI via NextJS API route
      const response = await sendMessage(input, messages);

      // Extract parts from response types that have them
      const parts = 'parts' in response ? response.parts :
                    ('recommended_parts' in response ? response.recommended_parts : undefined);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.message,
          parts: parts,
          responseData: response,
          timestamp: new Date(),
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
          timestamp: new Date(),
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
      <div className="bg-partselect-teal text-white p-4 shadow-md">
        <div className="flex items-center gap-3 max-w-4xl mx-auto">
          <Image
            src="/logo.png"
            alt="PartSelect"
            width={40}
            height={40}
            className="rounded"
          />
          <div>
            <h1 className="text-xl font-bold">PartSelect Assistant</h1>
            <p className="text-sm text-teal-100">
              Refrigerator & Dishwasher Parts Expert
            </p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-partselect-light">
        {messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4 shadow-lg">
        <div className="flex gap-3 max-w-4xl mx-auto">
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
            className="flex-1 px-5 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-partselect-teal focus:border-transparent focus:shadow-input-focus transition-shadow"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-partselect-gold hover:bg-amber-600 disabled:bg-gray-300 text-white w-12 h-12 rounded-full font-semibold transition-all disabled:cursor-not-allowed flex items-center justify-center shadow-md hover:shadow-lg"
            aria-label="Send message"
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
