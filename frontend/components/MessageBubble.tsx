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

function renderAgentResponse(response: AgentResponse) {
  switch (response.type) {
    case "search":
      // SearchResponse uses the existing grid of PartCards
      if (response.parts && response.parts.length > 0) {
        return (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
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

        {/* Render specialized UI component based on response type */}
        {message.responseData && renderAgentResponse(message.responseData)}

        {/* Fallback: Legacy support for parts array without responseData */}
        {!message.responseData && message.parts && message.parts.length > 0 && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            {message.parts.map((part) => (
              <PartCard key={part.part_number} part={part} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
