"use client";

import { Message } from "@/lib/types";
import PartCard from "./PartCard";
import { marked } from "marked";
import { useEffect, useState } from "react";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [htmlContent, setHtmlContent] = useState("");
  const isUser = message.role === "user";

  useEffect(() => {
    const renderMarkdown = async () => {
      const html = await marked(message.content);
      setHtmlContent(html as string);
    };
    renderMarkdown();
  }, [message.content]);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-full ${
          isUser ? "max-w-[80%]" : "max-w-[95%]"
        } rounded-lg p-3 ${
          isUser
            ? "bg-partselect-blue text-white"
            : "bg-gray-100 text-gray-900"
        }`}
      >
        {/* Message text with markdown */}
        <div
          className="prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{
            __html: htmlContent,
          }}
        />

        {/* Product cards if present */}
        {message.parts && message.parts.length > 0 && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            {message.parts.map((part) => (
              <PartCard key={part.partNumber} part={part} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
