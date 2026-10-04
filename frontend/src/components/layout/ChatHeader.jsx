import React from 'react'
import { Menu, Plus, FileText, Layers } from 'lucide-react'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'

export function ChatHeader({
  conversationTitle,
  selectedDoc,
  onOpenMobileMenu,
  onNewChat,
}) {
  return (
    <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-4 sm:px-6 shrink-0 z-10">
      <div className="flex items-center gap-3 min-w-0">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden h-8 w-8 text-slate-600"
          onClick={onOpenMobileMenu}
          title="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </Button>

        <div className="min-w-0">
          <h1 className="text-sm font-semibold text-slate-900 truncate">
            {conversationTitle || 'New Chat'}
          </h1>
        </div>

        {selectedDoc ? (
          <Badge
            variant="outline"
            className="hidden sm:inline-flex items-center gap-1 text-[11px] font-normal border-slate-300 text-slate-700 bg-slate-50"
          >
            <FileText className="h-3 w-3 text-slate-500" />
            <span className="truncate max-w-[140px]">{selectedDoc.filename}</span>
          </Badge>
        ) : (
          <Badge
            variant="outline"
            className="hidden sm:inline-flex items-center gap-1 text-[11px] font-normal border-slate-200 text-slate-500 bg-slate-50"
          >
            <Layers className="h-3 w-3 text-slate-400" />
            <span>All Documents</span>
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onNewChat}
          className="h-8 gap-1.5 text-xs text-slate-700 hover:text-slate-900"
        >
          <Plus className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">New Chat</span>
        </Button>
      </div>
    </header>
  )
}

