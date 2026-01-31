// Assistant avatar icon (matching MessageBubble)
function AssistantAvatar() {
  return (
    <div className="w-8 h-8 rounded-full bg-partselect-gold flex items-center justify-center flex-shrink-0">
      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
      </svg>
    </div>
  );
}

export default function LoadingIndicator() {
  return (
    <div className="flex gap-3 justify-start animate-fade-in-up">
      <AssistantAvatar />
      <div className="flex items-center gap-2 bg-white text-partselect-dark rounded-2xl px-4 py-3 shadow-chat-bubble border border-gray-100">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 bg-partselect-teal rounded-full animate-pulse-dot" />
          <div className="w-2 h-2 bg-partselect-teal rounded-full animate-pulse-dot [animation-delay:0.2s]" />
          <div className="w-2 h-2 bg-partselect-teal rounded-full animate-pulse-dot [animation-delay:0.4s]" />
        </div>
        <span className="text-sm text-gray-500">Assistant is typing...</span>
      </div>
    </div>
  );
}
