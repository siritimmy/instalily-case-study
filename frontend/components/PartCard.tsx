import { Part } from "@/lib/types";

interface PartCardProps {
  part: Part;
}

export default function PartCard({ part }: PartCardProps) {
  return (
    <div className="border rounded-lg p-3 bg-white shadow-sm hover:shadow-md transition flex gap-3 items-center">
      {/* Thumbnail */}
      <div className="flex-shrink-0 w-16 h-16 bg-gray-100 rounded flex items-center justify-center">
        <img
          src={part.image_url}
          alt={part.name}
          className="max-h-full max-w-full object-contain"
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect fill='%23f5f5f5' width='100' height='100'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' font-family='sans-serif' font-size='12' fill='%23999'%3ENo Image%3C/text%3E%3C/svg%3E";
          }}
        />
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-sm text-gray-900 line-clamp-1">
          {part.name}
        </h3>
        <p className="text-xs text-gray-500">
          {part.manufacturer} · #{part.part_number}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-sm font-bold text-partselect-blue">
            ${part.price.toFixed(2)}
          </span>
          <span
            className={`text-xs px-1.5 py-0.5 rounded ${
              part.in_stock
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {part.in_stock ? "In Stock" : "Out"}
          </span>
        </div>
      </div>

      {/* Action */}
      <a
        href={part.part_select_url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-shrink-0 bg-partselect-orange hover:bg-orange-700 text-white px-3 py-2 rounded text-xs font-semibold transition"
      >
        View
      </a>
    </div>
  );
}
