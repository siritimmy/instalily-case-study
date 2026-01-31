import { Part } from "@/lib/types";

interface PartCardProps {
  part: Part;
}

export default function PartCard({ part }: PartCardProps) {
  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition">
      <div className="relative w-full h-48 bg-gray-100 rounded mb-3 flex items-center justify-center">
        <img
          src={part.imageUrl}
          alt={part.name}
          className="max-h-full max-w-full object-contain"
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect fill='%23f5f5f5' width='100' height='100'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' font-family='sans-serif' font-size='12' fill='%23999'%3ENo Image%3C/text%3E%3C/svg%3E";
          }}
        />
      </div>

      <h3 className="font-semibold text-sm text-gray-900 mb-1 line-clamp-2">
        {part.name}
      </h3>

      <p className="text-xs text-gray-600 mb-1">{part.manufacturer}</p>

      <p className="text-xs text-gray-500 mb-3">Part #{part.partNumber}</p>

      <div className="flex justify-between items-center mb-3">
        <span className="text-lg font-bold text-partselect-blue">
          ${part.price.toFixed(2)}
        </span>
        <span
          className={`text-xs font-semibold px-2 py-1 rounded ${
            part.inStock
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {part.inStock ? "In Stock" : "Out of Stock"}
        </span>
      </div>

      <a
        href={part.partSelectUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-center bg-partselect-orange hover:bg-orange-700 text-white py-2 rounded text-sm font-semibold transition"
      >
        View on PartSelect
      </a>
    </div>
  );
}
