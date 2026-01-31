"use client";

import { useState } from "react";
import { PartDetailsResponse } from "@/lib/types";
import PartCard from "./PartCard";

interface DetailedProductViewProps {
  data: PartDetailsResponse;
}

export default function DetailedProductView({ data }: DetailedProductViewProps) {
  const [showAllModels, setShowAllModels] = useState(false);
  const [activeTab, setActiveTab] = useState<"specs" | "models" | "related">("specs");
  const [isExpanded, setIsExpanded] = useState(false);

  if (!data.part) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
        <svg
          className="w-12 h-12 text-gray-400 mx-auto mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-gray-600">Part information not found</p>
      </div>
    );
  }

  const part = data.part;
  const displayModels = showAllModels
    ? data.compatible_models
    : data.compatible_models.slice(0, 10);

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Clickable Product Header - Always Visible */}
      <div 
        className="md:flex cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* Product Image */}
        <div className="md:w-1/3 p-4 bg-gray-50 flex items-center justify-center">
          <img
            src={part.image_urls?.[0] || ""}
            alt={part.full_name}
            className="max-h-64 max-w-full object-contain"
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23f5f5f5' width='200' height='200'/%3E%3Ctext x='100' y='100' text-anchor='middle' dy='.3em' font-family='sans-serif' font-size='14' fill='%23999'%3ENo Image%3C/text%3E%3C/svg%3E";
            }}
          />
        </div>

        {/* Product Info */}
        <div className="md:w-2/3 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{part.full_name}</h3>
              <p className="text-sm text-gray-600 mb-1">
                <span className="font-medium">Manufacturer:</span> {part.manufacturer}
              </p>
              <p className="text-sm text-gray-600 mb-4">
                <span className="font-medium">Part #:</span> {part.part_number}
              </p>
            </div>
            
            {/* Expand/Collapse Icon */}
            <svg
              className={`w-6 h-6 text-gray-400 transition-transform flex-shrink-0 ml-4 ${
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

          {/* Price and Stock */}
          <div className="flex items-center gap-4 mb-4">
            <span className="text-2xl font-bold text-partselect-teal">
              ${part.price.toFixed(2)}
            </span>
            <span
              className={`px-3 py-1 rounded-full text-sm font-semibold ${
                part.in_stock
                  ? "bg-green-100 text-green-700"
                  : "bg-red-100 text-red-700"
              }`}
            >
              {part.in_stock ? "In Stock" : "Out of Stock"}
            </span>
          </div>

          {/* Rating */}
          {part.avg_rating !== undefined && part.avg_rating !== null && (
            <div className="flex items-center gap-2 mb-4">
              {/* Star symbols only */}
              <div className="flex items-center gap-0.5">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg
                    key={star}
                    className={`w-5 h-5 ${
                      star <= Math.round(part.avg_rating!)
                        ? "text-partselect-gold"
                        : "text-gray-300"
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              
              {/* Number of reviews only (no rating number) */}
              {part.num_reviews !== undefined && part.num_reviews !== null && part.num_reviews > 0 && (
                <span className="text-sm text-gray-600">
                  ({part.num_reviews} {part.num_reviews === 1 ? 'review' : 'reviews'})
                </span>
              )}
            </div>
          )}

          {/* CTA Button */}
          <a
            href={part.part_select_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-partselect-teal text-white px-6 py-3 rounded-lg font-semibold transition"
            onClick={(e) => { e.stopPropagation(); }}
          >
            View on PartSelect
          </a>
        </div>
      </div>

      {/* Collapsible Content - Description, Tabs, etc. */}
      {isExpanded && (
        <div className="animate-fade-in-up">
          {/* Description */}
          {part.description && (
            <div className="p-6 border-t">
              <h4 className="font-semibold text-gray-700 mb-2">Description</h4>
              <p className="text-gray-600 text-sm">{part.description}</p>
            </div>
          )}

          {/* Tabs */}
          <div className="border-t">
            <div className="flex border-b">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveTab("specs");
                }}
                className={`flex-1 py-3 text-sm font-semibold transition ${
                  activeTab === "specs"
                    ? "text-partselect-teal border-b-2 border-partselect-teal"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Specifications
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveTab("models");
                }}
                className={`flex-1 py-3 text-sm font-semibold transition ${
                  activeTab === "models"
                    ? "text-partselect-teal border-b-2 border-partselect-teal"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Compatible Models ({data.compatible_models.length})
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveTab("related");
                }}
                className={`flex-1 py-3 text-sm font-semibold transition ${
                  activeTab === "related"
                    ? "text-partselect-teal border-b-2 border-partselect-teal"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Related Parts
              </button>
            </div>

            {/* Tab Content */}
            <div className="p-4">
              {/* Specifications Tab */}
              {activeTab === "specs" && (
                <div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">
                        Part Number
                      </p>
                      <p className="font-medium text-gray-800">{part.part_number}</p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">
                        Manufacturer
                      </p>
                      <p className="font-medium text-gray-800">{part.manufacturer}</p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">
                        Installation Difficulty
                      </p>
                      <p className="font-medium text-gray-800 capitalize">
                        {part.installation_difficulty}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">
                        Warranty
                      </p>
                      <p className="font-medium text-gray-800">
                        {part.warranty_info || "No warranty information available"}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Compatible Models Tab */}
              {activeTab === "models" && (
                <div>
                  {data.compatible_models.length > 0 ? (
                    <>
                      <div className="flex flex-wrap gap-2">
                        {displayModels.map((model, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-gray-100 rounded text-sm text-gray-700 font-mono"
                          >
                            {model}
                          </span>
                        ))}
                      </div>
                      {data.compatible_models.length > 10 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowAllModels(!showAllModels);
                          }}
                          className="mt-3 text-partselect-teal hover:text-partselect-teal-dark text-sm font-semibold"
                        >
                          {showAllModels
                            ? "Show Less"
                            : `Show All ${data.compatible_models.length} Models`}
                        </button>
                      )}
                    </>
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      No compatible models listed
                    </p>
                  )}
                </div>
              )}

              {/* Related Parts Tab */}
              {activeTab === "related" && (
                <div>
                  {data.related_parts && data.related_parts.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {data.related_parts.map((relatedPart) => (
                        <PartCard key={relatedPart.part_number} part={relatedPart} />
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No related parts found</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}