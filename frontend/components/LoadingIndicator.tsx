export default function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-2 bg-gray-100 text-black rounded-lg p-3">
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce [animation-delay:0.2s]" />
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce [animation-delay:0.4s]" />
        </div>
        <span className="text-sm text-gray-600">Thinking...</span>
      </div>
    </div>
  );
}
