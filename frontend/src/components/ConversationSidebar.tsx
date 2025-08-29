import React, { useState, useEffect } from 'react';
import { conversationHistory, ConversationSummary } from '../services/conversationHistory';
import '../styles/ConversationSidebar.css';

interface ConversationSidebarProps {
  currentSlug?: string | null;
  onConversationSelect: (slug: string) => void;
  onNewConversation: () => void;
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  currentSlug,
  onConversationSelect,
  onNewConversation
}) => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = () => {
    const history = conversationHistory.getConversations();
    setConversations(history);
  };

  const formatRelativeTime = (date: Date): string => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'À l\'instant';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}min`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}j`;
    
    return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
  };

  const handleDeleteConversation = (e: React.MouseEvent, slug: string) => {
    e.stopPropagation();
    if (window.confirm('Supprimer cette conversation ?')) {
      conversationHistory.removeConversation(slug);
      loadConversations();
      
      // Redirect to new conversation if current one was deleted
      if (slug === currentSlug) {
        onNewConversation();
      }
    }
  };

  return (
    <div className={`conversation-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          className="collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? 'Ouvrir' : 'Fermer'}
        >
          {isCollapsed ? '▶' : '◀'}
        </button>
        
        {!isCollapsed && (
          <>
            <h3>Conversations</h3>
            <button 
              className="new-conversation-btn"
              onClick={onNewConversation}
              title="Nouvelle conversation"
            >
              ➕ Nouveau
            </button>
          </>
        )}
      </div>

      {!isCollapsed && (
        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="no-conversations">
              <p>Aucune conversation</p>
              <small>Commencez votre première consultation !</small>
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.slug}
                className={`conversation-item ${conv.slug === currentSlug ? 'active' : ''}`}
                onClick={() => onConversationSelect(conv.slug)}
              >
                <div className="conversation-header">
                  <span className="conversation-title">{conv.title}</span>
                  <button
                    className="delete-btn"
                    onClick={(e) => handleDeleteConversation(e, conv.slug)}
                    title="Supprimer"
                  >
                    🗑️
                  </button>
                </div>
                
                <div className="conversation-meta">
                  <span className="message-count">{conv.messageCount} messages</span>
                  <span className="last-activity">{formatRelativeTime(conv.lastActivity)}</span>
                </div>

                {conv.firstMessage && (
                  <div className="conversation-preview">
                    {conv.firstMessage.length > 60 
                      ? conv.firstMessage.substring(0, 60) + '...' 
                      : conv.firstMessage}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ConversationSidebar;