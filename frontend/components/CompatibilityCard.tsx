"use client";

import { useState } from "react";
import { CompatibilityResponse } from "@/lib/types";
import PartCard from "./PartCard";

interface CompatibilityCardProps {
  data: CompatibilityResponse;
}

export default function CompatibilityCard({ data }: CompatibilityCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Clickable Compatibility Result Header */}
      <div
        className={`p-6 cursor-pointer hover:opacity-90 transition-opacity ${
          data.is_compatible ? "bg-green-50" : "bg-red-50"
        }`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-4">
          {/* Compatibility Icon */}
          <div
            className={`w-16 h-16 rounded-full flex items-center justify-center ${
              data.is_compatible ? "bg-green-100" : "bg-red-100"
            }`}
          >
            {data.is_compatible ? (
              <svg
                className="w-10 h-10 text-green-600"
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
            ) : (
              <svg
                className="w-10 h-10 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            )}
          </div>

          {/* Result Text */}
          <div className="flex-1">
            <h3
              className={`text-xl font-bold ${
                data.is_compatible ? "text-green-700" : "text-red-700"
              }`}
            >
              {data.is_compatible ? "Compatible!" : "Not Compatible"}
            </h3>
          </div>

          {/* Expand/Collapse Icon */}
          <svg
            className={`w-6 h-6 text-gray-400 transition-transform flex-shrink-0 ${
              isExpanded ? "rotate-180" : ""
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
        </div>
      </div>

      {/* Collapsible Details Section */}
      {isExpanded && (
        <div className="p-6 space-y-4 animate-fade-in-up">
          {/* Part and Model Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Part Number</p>
              <p className="font-semibold text-partselect-blue">{data.part_number}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Model Number</p>
              <p className="font-semibold text-partselect-blue">{data.model_number}</p>
            </div>
          </div>

          {/* Explanation */}
          {data.explanation && (
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-700 mb-2">Details</h4>
              <p className="text-gray-600 text-sm">{data.explanation}</p>
            </div>
          )}

          {/* Alternative Parts (if not compatible) */}
          {!data.is_compatible && data.alternative_parts && data.alternative_parts.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-700 mb-3">
                Alternative Parts That Fit Your Model
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.alternative_parts.map((part) => (
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
