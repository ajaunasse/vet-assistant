import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../services/api';
import { VeterinaryAssessment } from '../types/api';
import AssessmentDisplay from './AssessmentDisplay';
import SessionManager from '../utils/SessionManager';
import '../styles/ChatInterface.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  assessment?: VeterinaryAssessment;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeSession = useCallback(async () => {
    try {
      console.log('[ChatInterface] Initializing session...');
      const sessionManager = SessionManager.getInstance();
      
      const newSessionId = await sessionManager.getSessionId(async () => {
        console.log('[ChatInterface] Creating session via API...');
        return await apiService.createSession();
      });
      
      console.log('[ChatInterface] Session initialized:', newSessionId);
      setSessionId(newSessionId);
      setIsConnected(true);
      
      // Add welcome message only if we don't already have messages
      if (messages.length === 0) {
        const welcomeMessage: Message = {
          id: 'welcome',
          role: 'assistant',
          content: 'Je suis , votre assistant spécialisé en neurologie vétérinaire canine. Décrivez-moi les symptômes neurologiques observés chez votre patient.',
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('[ChatInterface] Failed to initialize session:', error);
      setIsConnected(false);
    }
  }, [messages.length]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading || !sessionId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const assessment = await apiService.sendMessage(sessionId, inputMessage);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assessment.assessment,
        timestamp: new Date(),
        assessment
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  useEffect(() => {
    initializeSession();
  }, [initializeSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>🧠 NeuroVet - Assistant Diagnostique</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connecté' : '🔴 Déconnecté'}
          </span>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-header">
              <span className="role">
                {message.role === 'user' ? '👩‍⚕️ Vétérinaire' : '🧠 Dr. NeuroVet'}
              </span>
              <span className="timestamp">{formatTime(message.timestamp)}</span>
            </div>
            {message.assessment ? (
              <AssessmentDisplay assessment={message.assessment} />
            ) : (
              <div className="message-content">
                {message.content}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-header">
              <span className="role">🧠 Dr. NeuroVet</span>
            </div>
            <div className="message-content loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              Analyse en cours...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="chat-input-form">
        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Décrivez les symptômes neurologiques observés..."
            disabled={isLoading || !isConnected}
            className="chat-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputMessage.trim() || !isConnected}
            className="send-button"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;