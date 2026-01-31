import { NextResponse } from "next/server";

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${FASTAPI_URL}/health`);

    if (!response.ok) {
      return NextResponse.json(
        { status: "backend_down" },
        { status: 503 }
      );
    }

    return NextResponse.json({ status: "healthy" });
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: String(error) },
      { status: 503 }
    );
  }
}
