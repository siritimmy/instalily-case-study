"use client";

import { useState } from "react";
import { DiagnosisResponse } from "@/lib/types";
import PartCard from "./PartCard";

interface DiagnosticFlowProps {
  data: DiagnosisResponse;
}

export default function DiagnosticFlow({ data }: DiagnosticFlowProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-amber-50 border-b border-amber-100 p-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
            <svg
              className="w-6 h-6 text-amber-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-800">Diagnosis Results</h3>
            <p className="text-sm text-gray-600 mt-1">
              <span className="font-medium">Symptom:</span> {data.symptom}
            </p>
            {data.appliance_type && (
              <p className="text-xs text-gray-500 mt-0.5 capitalize">
                {data.appliance_type}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Likely Causes */}
      {data.likely_causes && data.likely_causes.length > 0 && (
        <div className="border-b">
          <button
            onClick={() => toggleSection("causes")}
            className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
          >
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-semibold text-gray-700">
                Likely Causes ({data.likely_causes.length})
              </span>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${
                expandedSection === "causes" ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          {expandedSection === "causes" && (
            <div className="px-4 pb-4">
              <ol className="space-y-2">
                {data.likely_causes.map((cause, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="w-6 h-6 bg-red-100 text-red-700 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{cause}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {/* Troubleshooting Steps */}
      {data.troubleshooting_steps && data.troubleshooting_steps.length > 0 && (
        <div className="border-b">
          <button
            onClick={() => toggleSection("steps")}
            className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
          >
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              <span className="font-semibold text-gray-700">
                Troubleshooting Steps ({data.troubleshooting_steps.length})
              </span>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${
                expandedSection === "steps" ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          {expandedSection === "steps" && (
            <div className="px-4 pb-4">
              <p className="text-sm text-gray-500 mb-3">
                Try these steps to verify the diagnosis before purchasing parts:
              </p>
              <ol className="space-y-3">
                {data.troubleshooting_steps.map((step, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {/* Recommended Parts */}
      {data.recommended_parts && data.recommended_parts.length > 0 && (
        <div>
          <button
            onClick={() => toggleSection("parts")}
            className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
          >
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="font-semibold text-gray-700">
                Recommended Parts ({data.recommended_parts.length})
              </span>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${
                expandedSection === "parts" ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          {expandedSection === "parts" && (
            <div className="p-4 pt-0">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.recommended_parts.map((part) => (
                  <PartCard key={part.part_number} part={part} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
