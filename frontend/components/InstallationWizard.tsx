"use client";

import { useState } from "react";
import { InstallationResponse } from "@/lib/types";

interface InstallationWizardProps {
  data: InstallationResponse;
}

export default function InstallationWizard({ data }: InstallationWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "bg-green-100 text-green-700";
      case "moderate":
        return "bg-yellow-100 text-yellow-700";
      case "difficult":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "Easy";
      case "moderate":
        return "Moderate";
      case "difficult":
        return "Difficult";
      default:
        return difficulty;
    }
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours} hour${hours > 1 ? "s" : ""}`;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-partselect-blue text-white p-4">
        <h3 className="text-lg font-bold">Installation Guide</h3>
        <p className="text-blue-100 text-sm">Part #{data.part_number}</p>
      </div>

      {/* Safety Warnings */}
      {data.safety_warnings && data.safety_warnings.length > 0 && (
        <div className="bg-red-50 border-b border-red-100 p-4">
          <div className="flex items-start gap-3">
            <svg
              className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div>
              <h4 className="font-semibold text-red-700 mb-1">Safety Warnings</h4>
              <ul className="text-sm text-red-600 space-y-1">
                {data.safety_warnings.map((warning, index) => (
                  <li key={index}>• {warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Quick Info */}
      <div className="grid grid-cols-3 divide-x border-b">
        <div className="p-4 text-center">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Difficulty</p>
          <span
            className={`inline-block mt-1 px-2 py-1 rounded text-sm font-semibold ${getDifficultyColor(
              data.difficulty
            )}`}
          >
            {getDifficultyLabel(data.difficulty)}
          </span>
        </div>
        <div className="p-4 text-center">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Est. Time</p>
          <p className="text-sm font-semibold text-gray-700 mt-1">
            {formatTime(data.estimated_time_minutes)}
          </p>
        </div>
        <div className="p-4 text-center">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Steps</p>
          <p className="text-sm font-semibold text-gray-700 mt-1">
            {data.steps?.length || 0}
          </p>
        </div>
      </div>

      {/* Tools Required */}
      {data.tools_required && data.tools_required.length > 0 && (
        <div className="p-4 border-b bg-gray-50">
          <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            Tools Required
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.tools_required.map((tool, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 border"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Steps */}
      {data.steps && data.steps.length > 0 && (
        <div className="p-4">
          <h4 className="font-semibold text-gray-700 mb-4">Installation Steps</h4>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>
                {currentStep + 1} of {data.steps.length}
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-partselect-orange transition-all duration-300"
                style={{
                  width: `${((currentStep + 1) / data.steps.length) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Current Step */}
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-partselect-blue text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                {data.steps[currentStep].step_number}
              </div>
              <div className="flex-1">
                <p className="text-gray-800">{data.steps[currentStep].instruction}</p>
                {data.steps[currentStep].warning && (
                  <p className="mt-2 text-sm text-amber-600 flex items-center gap-1">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                    {data.steps[currentStep].warning}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              onClick={() => setCurrentStep((prev) => Math.max(0, prev - 1))}
              disabled={currentStep === 0}
              className="px-4 py-2 text-sm font-semibold rounded disabled:opacity-50 disabled:cursor-not-allowed bg-gray-100 hover:bg-gray-200 text-gray-700"
            >
              Previous
            </button>
            <button
              onClick={() =>
                setCurrentStep((prev) => Math.min(data.steps.length - 1, prev + 1))
              }
              disabled={currentStep === data.steps.length - 1}
              className="px-4 py-2 text-sm font-semibold rounded disabled:opacity-50 disabled:cursor-not-allowed bg-partselect-orange hover:bg-orange-700 text-white"
            >
              Next Step
            </button>
          </div>
        </div>
      )}

      {/* Video and PDF Links */}
      {(data.video_url || data.pdf_url) && (
        <div className="p-4 border-t bg-gray-50 flex gap-3">
          {data.video_url && (
            <a
              href={data.video_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm font-semibold transition"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z" />
              </svg>
              Watch Video
            </a>
          )}
          {data.pdf_url && (
            <a
              href={data.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm font-semibold transition"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Download PDF
            </a>
          )}
        </div>
      )}
    </div>
  );
}
