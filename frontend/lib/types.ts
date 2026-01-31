// Base Part type used across responses
export interface Part {
  part_number: string;
  name: string;
  price: number;
  image_url: string;
  manufacturer: string;
  in_stock: boolean;
  part_select_url: string;
}

// Extended part details from backend PartDetails model
export interface PartDetails {
  part_number: string;
  full_name: string;
  description: string;
  price: number;
  image_urls: string[];
  manufacturer: string;
  in_stock: boolean;
  avg_rating?: number;
  num_reviews: number;
  compatible_models: string[];
  installation_difficulty: "easy" | "moderate" | "difficult";
  warranty_info: string;
  part_select_url: string;
}

// Installation step for InstallationResponse
export interface InstallationStep {
  step_number: number;
  instruction: string;
  warning?: string;
  image_url?: string;
}

// Response Types - each maps to a specific UI component

export interface SearchResponse {
  type: "search";
  message: string;
  parts: Part[];
  total_results: number;
  search_query: string;
  appliance_type?: "refrigerator" | "dishwasher";
}

export interface PartDetailsResponse {
  type: "part_details";
  message: string;
  part?: PartDetails;
  compatible_models: string[];
  related_parts: Part[];
}

export interface CompatibilityResponse {
  type: "compatibility";
  message: string;
  part_number: string;
  model_number: string;
  is_compatible: boolean;
  confidence: "confirmed" | "likely" | "unlikely";
  explanation: string;
  alternative_parts: Part[];
}

export interface InstallationResponse {
  type: "installation";
  message: string;
  part_number: string;
  difficulty: "easy" | "moderate" | "difficult";
  estimated_time_minutes: number;
  tools_required: string[];
  steps: InstallationStep[];
  video_url?: string;
  pdf_url?: string;
  safety_warnings: string[];
}

export interface DiagnosisResponse {
  type: "diagnosis";
  message: string;
  symptom: string;
  appliance_type?: "refrigerator" | "dishwasher";
  likely_causes: string[];
  recommended_parts: Part[];
  diy_difficulty: "easy" | "moderate" | "difficult" | "call_professional";
  troubleshooting_steps: string[];
}

export interface OffTopicResponse {
  type: "off_topic";
  message: string;
}

// Union type for all possible agent responses
export type AgentResponse =
  | SearchResponse
  | PartDetailsResponse
  | CompatibilityResponse
  | InstallationResponse
  | DiagnosisResponse
  | OffTopicResponse;

// Message type with response data
export interface Message {
  role: "user" | "assistant";
  content: string;
  parts?: Part[];
  responseData?: AgentResponse;
  timestamp?: Date;
}

export interface ChatRequest {
  message: string;
  conversationHistory: Message[];
}
