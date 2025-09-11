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
  const [isCollapsed, setIsCollapsed] = useState(window.innerWidth <= 768);

  useEffect(() => {
    loadConversations();
    
    // Handle window resize
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setIsCollapsed(true);
      } else if (window.innerWidth > 768 && isCollapsed) {
        setIsCollapsed(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isCollapsed]);

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

  const handleDeleteConversation = (e: React.MouseEvent, sessionId: string, slug: string) => {
    e.stopPropagation();
    if (window.confirm('Supprimer cette conversation ?')) {
      conversationHistory.removeConversation(sessionId);
      loadConversations();
      
      // Redirect to new conversation if current one was deleted
      if (slug === currentSlug) {
        onNewConversation();
      }
    }
  };

  return (
    <>
      <div className={`conversation-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <button 
            className="collapse-btn"
            onClick={() => setIsCollapsed(!isCollapsed)}
            title={isCollapsed ? 'Ouvrir' : 'Fermer'}
          >
            <i className={`fas ${isCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'}`}></i>
          </button>
          
          {!isCollapsed && (
            <>
              <h3>Conversations</h3>
              <button 
                className="new-conversation-btn"
                onClick={onNewConversation}
                title="Nouvelle conversation"
              >
                <i className="fas fa-plus"></i>
                <span>Nouveau</span>
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
                key={conv.sessionId}
                className={`conversation-item ${conv.slug === currentSlug ? 'active' : ''}`}
                onClick={() => onConversationSelect(conv.sessionId)}
              >
                <div className="conversation-header">
                  <span className="conversation-title">{conv.title}</span>
                  <button
                    className="delete-btn"
                    onClick={(e) => handleDeleteConversation(e, conv.sessionId, conv.slug)}
                    title="Supprimer"
                  >
                    <i className="fas fa-trash-alt"></i>
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
      
      {/* Overlay for mobile */}
      <div 
        className={`sidebar-overlay ${!isCollapsed ? 'show' : ''}`}
        onClick={() => setIsCollapsed(true)}
      />
    </>
  );
};

export default ConversationSidebar;