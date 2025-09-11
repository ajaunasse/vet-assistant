interface ConversationSummary {
  slug: string;
  sessionId: string;
  title: string;
  firstMessage?: string;
  lastActivity: Date;
  messageCount: number;
}

class ConversationHistoryService {
  private readonly STORAGE_KEY = 'neurovet_conversations';

  /**
   * Get all saved conversations
   */
  getConversations(): ConversationSummary[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (!stored) return [];
      
      const conversations = JSON.parse(stored);
      return conversations.map((conv: any) => ({
        ...conv,
        lastActivity: new Date(conv.lastActivity)
      })).sort((a: ConversationSummary, b: ConversationSummary) => 
        b.lastActivity.getTime() - a.lastActivity.getTime()
      );
    } catch (error) {
      console.error('Failed to load conversation history:', error);
      return [];
    }
  }

  /**
   * Save or update a conversation
   */
  saveConversation(conversation: ConversationSummary): void {
    try {
      const conversations = this.getConversations();
      const existingIndex = conversations.findIndex(c => c.sessionId === conversation.sessionId);
      
      if (existingIndex >= 0) {
        conversations[existingIndex] = conversation;
      } else {
        conversations.unshift(conversation);
      }

      // Keep only the last 50 conversations
      const limited = conversations.slice(0, 50);
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(limited));
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }
  }

  /**
   * Update conversation activity (when new message sent)
   */
  updateActivity(sessionId: string, messageCount: number): void {
    const conversations = this.getConversations();
    const conversation = conversations.find(c => c.sessionId === sessionId);
    
    if (conversation) {
      conversation.lastActivity = new Date();
      conversation.messageCount = messageCount;
      this.saveConversation(conversation);
    }
  }

  /**
   * Update conversation activity by slug (legacy support)
   */
  updateActivityBySlug(slug: string, messageCount: number): void {
    const conversations = this.getConversations();
    const conversation = conversations.find(c => c.slug === slug);
    
    if (conversation) {
      conversation.lastActivity = new Date();
      conversation.messageCount = messageCount;
      this.saveConversation(conversation);
    }
  }

  /**
   * Generate a friendly title from the first message
   */
  generateTitle(firstMessage: string): string {
    // Remove common prefixes and clean up
    let title = firstMessage
      .replace(/^(bonjour|salut|hello),?\s*/i, '')
      .replace(/^(j'ai|nous avons|mon chien|ma chienne|notre chien)\s*/i, '')
      .trim();

    // Limit length and add ellipsis if needed
    if (title.length > 50) {
      title = title.substring(0, 47) + '...';
    }

    return title || 'Nouvelle conversation';
  }

  /**
   * Remove a conversation from history
   */
  removeConversation(sessionId: string): void {
    try {
      const conversations = this.getConversations();
      const filtered = conversations.filter(c => c.sessionId !== sessionId);
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to remove conversation:', error);
    }
  }

  /**
   * Clear all conversation history
   */
  clearHistory(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  }
}

export const conversationHistory = new ConversationHistoryService();
export type { ConversationSummary };