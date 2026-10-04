import React from "react";
import { Bot, User, Zap } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { SourceList } from "./SourceList";
import { Badge } from "../ui/badge";
import { cn } from "../../lib/utils";

export function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full gap-3 py-4 text-sm animate-in fade-in duration-200",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <div className="h-8 w-8 rounded-full bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-xs">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div
        className={cn(
          "relative max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 py-3 leading-relaxed",
          isUser
            ? "bg-slate-900 text-white rounded-tr-xs shadow-xs"
            : "bg-white text-slate-900 border border-slate-200/90 rounded-tl-xs shadow-xs",
        )}
      >
        <div className="flex items-center justify-between gap-2 mb-1">
          <span
            className={cn(
              "text-[11px] font-semibold tracking-wide uppercase",
              isUser ? "text-slate-300" : "text-slate-500",
            )}
          >
            {isUser ? "You" : "Assistant"}
          </span>

          {/* Step 8: Redis Cache indicator */}
          {!isUser && message.cached && (
            <Badge
              variant="outline"
              className="text-[10px] py-0 px-1.5 h-4 font-normal gap-1 text-slate-500 border-slate-200 bg-slate-50"
              title="Answer retrieved from instant cache"
            >
              <Zap className="h-2.5 w-2.5 text-amber-500 fill-amber-500" />
              Cached
            </Badge>
          )}
        </div>

        {/* Content with whitespace and paragraph rendering */}
        <div
          className={cn(
            "whitespace-pre-wrap text-sm",
            isUser ? "text-white" : "text-slate-800",
          )}
        >
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown
              components={{
                strong: ({ node, ...props }) => (
                  <strong className="font-bold text-slate-950" {...props} />
                ),
                p: ({ node, ...props }) => (
                  <p className="mb-2 last:mb-0" {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul className="list-disc pl-4 mb-2" {...props} />
                ),
                ol: ({ node, ...props }) => (
                  <ol className="list-decimal pl-4 mb-2" {...props} />
                ),
                li: ({ node, ...props }) => <li className="mb-1" {...props} />,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Step 7: Sources rendered beneath assistant answer */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceList sources={message.sources} />
        )}
      </div>

      {isUser && (
        <div className="h-8 w-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center shrink-0">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
