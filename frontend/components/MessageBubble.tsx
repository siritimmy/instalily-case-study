"use client";

import { Message, AgentResponse } from "@/lib/types";
import PartCard from "./PartCard";
import CompatibilityCard from "./CompatibilityCard";
import InstallationWizard from "./InstallationWizard";
import DiagnosticFlow from "./DiagnosticFlow";
import DetailedProductView from "./DetailedProductView";
import { marked } from "marked";
import { useEffect, useState } from "react";

interface MessageBubbleProps {
  message: Message;
}

// Format relative time (e.g., "just now", "2m ago")
function formatRelativeTime(date?: Date): string {
  if (!date) return "";
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

// User avatar icon
function UserAvatar() {
  return (
    <div className="w-8 h-8 rounded-full bg-partselect-teal flex items-center justify-center flex-shrink-0">
      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
      </svg>
    </div>
  );
}

// Assistant avatar icon
function AssistantAvatar() {
  return (
    <div className="w-8 h-8 rounded-full bg-partselect-gold flex items-center justify-center flex-shrink-0">
      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
      </svg>
    </div>
  );
}

function renderAgentResponse(response: AgentResponse) {
  switch (response.type) {
    case "search":
      // SearchResponse uses a compact grid of PartCards (2 per row)
      if (response.parts && response.parts.length > 0) {
        return (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
            {response.parts.map((part) => (
              <PartCard key={part.part_number} part={part} />
            ))}
          </div>
        );
      }
      return null;

    case "part_details":
      return (
        <div className="mt-4">
          <DetailedProductView data={response} />
        </div>
      );

    case "compatibility":
      return (
        <div className="mt-4">
          <CompatibilityCard data={response} />
        </div>
      );

    case "installation":
      return (
        <div className="mt-4">
          <InstallationWizard data={response} />
        </div>
      );

    case "diagnosis":
      return (
        <div className="mt-4">
          <DiagnosticFlow data={response} />
        </div>
      );

    case "off_topic":
      // Off-topic just shows the message, no special component
      return null;

    default:
      return null;
  }
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
    <div className={`flex gap-3 animate-fade-in-up ${isUser ? "justify-end" : "justify-start"}`}>
      {/* Assistant avatar on left */}
      {!isUser && <AssistantAvatar />}

      <div className={"flex flex-col " + (isUser ? "max-w-[80%]" : "max-w-[60%]")}>
        <div
          className={`rounded-2xl px-4 py-3 shadow-chat-bubble ${
            isUser
              ? "bg-partselect-teal text-white"
              : "bg-white text-partselect-dark border border-gray-100"
          }`}
        >
          {/* Message text with markdown */}
          <div
            className={`prose prose-sm max-w-none ${isUser ? "prose-invert" : ""}`}
            dangerouslySetInnerHTML={{
              __html: htmlContent,
            }}
          />

          {/* Render specialized UI component based on response type */}
          {message.responseData && renderAgentResponse(message.responseData)}

          {/* Fallback: Legacy support for parts array without responseData */}
          {!message.responseData && message.parts && message.parts.length > 0 && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
              {message.parts.map((part) => (
                <PartCard key={part.part_number} part={part} />
              ))}
            </div>
          )}
        </div>

        {/* Timestamp */}
        {message.timestamp && (
          <span className={`text-xs text-gray-400 mt-1 ${isUser ? "text-right" : "text-left"}`}>
            {formatRelativeTime(message.timestamp)}
          </span>
        )}
      </div>

      {/* User avatar on right */}
      {isUser && <UserAvatar />}
    </div>
  );
}
