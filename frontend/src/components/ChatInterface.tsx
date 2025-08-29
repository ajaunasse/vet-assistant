import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../services/api';
import { VeterinaryAssessment, PatientData } from '../types/api';
import AssessmentDisplay from './AssessmentDisplay';
import PatientDataDisplay from './PatientDataDisplay';
import ConversationSidebar from './ConversationSidebar';
import SessionManager from '../utils/SessionManager';
import { conversationHistory } from '../services/conversationHistory';
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
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [showPatientData, setShowPatientData] = useState(false);
  const [currentSlug, setCurrentSlug] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Extract slug from URL path
  const getSlugFromUrl = () => {
    const path = window.location.pathname;
    const slug = path.split('/').pop();
    return slug && slug !== 'neuro-vet-assistant' ? slug : null;
  };

  const handleConversationSelect = (slug: string) => {
    window.location.href = `/neuro-vet-assistant/${slug}`;
  };

  const handleNewConversation = () => {
    apiService.resetSession();
    window.location.href = '/neuro-vet-assistant/';
  };

  const initializeSession = useCallback(async () => {
    try {
      console.log('[ChatInterface] Initializing session...');
      const slug = getSlugFromUrl();
      
      if (slug) {
        // Load existing session by slug
        console.log('[ChatInterface] Loading session by slug:', slug);
        const sessionData = await apiService.getSessionBySlug(slug);
        
        setSessionId(sessionData.session.id);
        setCurrentSlug(slug);
        setIsConnected(true);
        
        // Load messages from the session
        const loadedMessages = sessionData.messages.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          assessment: msg.role === 'assistant' ? sessionData.session.current_assessment : undefined
        }));
        
        setMessages(loadedMessages);
        
        // Load patient data if available
        if (sessionData.session.patient_data) {
          setPatientData(sessionData.session.patient_data);
        }
        
        // Update conversation in history
        const firstUserMessage = sessionData.messages.find((m: any) => m.role === 'user')?.content;
        if (firstUserMessage) {
          conversationHistory.updateActivity(slug, sessionData.messages.length);
        }
        
      } else {
        // Create new session
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
            content: 'Bonjour ! Je suis votre assistant spécialisé en neurologie vétérinaire canine. Pour établir un diagnostic précis, j\'ai besoin des informations suivantes : âge, race, sexe du patient, ainsi qu\'une description détaillée des symptômes neurologiques observés.',
            timestamp: new Date()
          };
          setMessages([welcomeMessage]);
        }
      }
    } catch (error) {
      console.error('[ChatInterface] Failed to initialize session:', error);
      setIsConnected(false);
    }
  }, []);

  const fetchPatientData = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/patient-data`);
      if (response.ok) {
        const data = await response.json();
        setPatientData(data);
      }
    } catch (error) {
      console.error('[ChatInterface] Failed to fetch patient data:', error);
    }
  }, []);

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
      
      // Fetch updated patient data after each message
      await fetchPatientData(sessionId);
      
      // Redirect to slug URL after first message (if not already there)
      const currentSlugUrl = getSlugFromUrl();
      if (!currentSlugUrl && messages.length === 1) { // Only welcome message before
        try {
          const sessionData = await apiService.getSession(sessionId);
          if (sessionData.session.slug) {
            // Save new conversation to history
            conversationHistory.saveConversation({
              slug: sessionData.session.slug,
              sessionId: sessionId,
              title: conversationHistory.generateTitle(inputMessage),
              firstMessage: inputMessage,
              lastActivity: new Date(),
              messageCount: 2 // User message + assistant response
            });
            
            setCurrentSlug(sessionData.session.slug);
            window.history.pushState({}, '', `/neuro-vet-assistant/${sessionData.session.slug}`);
          }
        } catch (error) {
          console.error('Failed to get session slug:', error);
        }
      } else if (currentSlugUrl) {
        // Update existing conversation activity
        conversationHistory.updateActivity(currentSlugUrl, messages.length + 1);
      }
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
    <>
      <ConversationSidebar
        currentSlug={currentSlug}
        onConversationSelect={handleConversationSelect}
        onNewConversation={handleNewConversation}
      />
      
      <div className="chat-interface main-content">
        <div className="chat-header">
        <h1>🧠 NeuroVet - Assistant Diagnostique</h1>
        <div className="header-controls">
          <button 
            className={`patient-data-toggle ${showPatientData ? 'active' : ''}`}
            onClick={() => setShowPatientData(!showPatientData)}
            disabled={!patientData || patientData.collected_fields.length === 0}
          >
            📊 Données Patient
            {patientData && patientData.collected_fields.length > 0 && (
              <span className="data-count">({patientData.collected_fields.length})</span>
            )}
          </button>
          <div className="connection-status">
            <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '🟢 Connecté' : '🔴 Déconnecté'}
            </span>
          </div>
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

      {/* Affichage des données patient */}
      {showPatientData && patientData && (
        <PatientDataDisplay patientData={patientData} />
      )}

      <form onSubmit={sendMessage} className="chat-input-form">
        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ex: Mon chien Malinois mâle de 3 ans présente des tremblements et troubles de l'équilibre depuis 2 jours..."
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
    </>
  );
};

export default ChatInterface;