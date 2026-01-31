export interface Part {
  partNumber: string;
  name: string;
  price: number;
  imageUrl: string;
  manufacturer: string;
  inStock: boolean;
  partSelectUrl: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  parts?: Part[];
}

export interface ChatRequest {
  message: string;
  conversationHistory: Message[];
}

export interface ChatResponse {
  message: string;
  parts: Part[];
}
