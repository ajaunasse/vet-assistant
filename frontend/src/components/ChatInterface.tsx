import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../services/api';
import { VeterinaryAssessment, PatientData } from '../types/api';
import AssessmentDisplay from './AssessmentDisplay';
import PatientDataDisplay from './PatientDataDisplay';
import ConversationSidebar from './ConversationSidebar';
import PreConsultationForm from './PreConsultationForm';
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

interface PreConsultationData {
  race: string;
  age: string;
  sexe: 'Mâle' | 'Femelle' | '';
  castre: boolean;
  motif_consultation: string;
  premiers_symptomes: string;
  examens_realises: string;
  etat_conscience: 'NSP' | 'Normal' | 'Altéré' | '';
  comportement: 'NSP' | 'Normal' | 'Compulsif' | '';
  convulsions: 'Oui' | 'Non' | 'NSP' | '';
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
  const [showPreConsultationForm, setShowPreConsultationForm] = useState(false);
  const [isNewConsultation, setIsNewConsultation] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Extract session ID from URL path
  const getSessionIdFromUrl = () => {
    const path = window.location.pathname;
    const sessionId = path.split('/').pop();
    return sessionId && sessionId !== '' ? sessionId : null;
  };

  const handleConversationSelect = (sessionId: string) => {
    window.location.href = `/${sessionId}`;
  };

  const handleNewConversation = () => {
    setIsNewConsultation(true);
    setShowPreConsultationForm(true);
  };

  const initializeSession = useCallback(async () => {
    try {
      console.log('[ChatInterface] Initializing session...');
      const sessionIdFromUrl = getSessionIdFromUrl();
      
      if (sessionIdFromUrl) {
        // Load existing session by ID
        console.log('[ChatInterface] Loading session by ID:', sessionIdFromUrl);
        const sessionData = await apiService.getSession(sessionIdFromUrl);
        
        setSessionId(sessionData.session.id);
        setCurrentSlug(sessionData.session.slug || '');
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
          conversationHistory.updateActivity(sessionData.session.id, sessionData.messages.length);
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
        
        // Check if we should show pre-consultation form for new sessions
        if (messages.length === 0 && !getSessionIdFromUrl()) {
          setShowPreConsultationForm(true);
          setIsNewConsultation(true);
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
      
      // Redirect to session URL after first message (if not already there)
      const currentSessionUrl = getSessionIdFromUrl();
      if (!currentSessionUrl && messages.length === 1) { // Only welcome message before
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
            window.history.pushState({}, '', `/${sessionId}`);
          }
        } catch (error) {
          console.error('Failed to get session slug:', error);
        }
      } else if (currentSessionUrl) {
        // Update existing conversation activity
        conversationHistory.updateActivity(currentSessionUrl, messages.length + 1);
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

  const generateInitialPrompt = (data: PreConsultationData): string => {
    const castreText = data.castre ? 'castré/stérilisé' : 'non castré/stérilisé';
    
    let prompt = `Bonjour, je consulte pour mon chien avec les informations suivantes :

**Informations du patient :**
- Race : ${data.race}
- Âge : ${data.age}
- Sexe : ${data.sexe} (${castreText})
- Motif de consultation : ${data.motif_consultation}

**Description des symptômes :**
${data.premiers_symptomes}

**Examen clinique :**
- État de conscience : ${data.etat_conscience}
- Comportement : ${data.comportement}
- Convulsions : ${data.convulsions}`;

    if (data.examens_realises.trim()) {
      prompt += `

**Examens déjà réalisés :**
${data.examens_realises}`;
    }

    prompt += `

Pouvez-vous m'aider à établir un diagnostic neurologique basé sur ces informations ?`;

    return prompt;
  };

  const handlePreConsultationSubmit = async (data: PreConsultationData) => {
    try {
      setShowPreConsultationForm(false);
      
      let currentSessionId = sessionId;
      
      if (isNewConsultation) {
        // Reset session for new consultation
        apiService.resetSession();
        
        // Initialize new session
        const sessionManager = SessionManager.getInstance();
        const newSessionId = await sessionManager.getSessionId(async () => {
          return await apiService.createSession();
        });
        
        setSessionId(newSessionId);
        setIsConnected(true);
        setMessages([]);
        currentSessionId = newSessionId;
      }

      // First, save patient data from form
      await apiService.savePatientData(currentSessionId, data);

      // Generate and send initial prompt
      const initialPrompt = generateInitialPrompt(data);
      setInputMessage('');
      setIsLoading(true);

      // Create user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: initialPrompt,
        timestamp: new Date()
      };

      setMessages([userMessage]);

      // Send to API
      const assessment = await apiService.sendMessage(currentSessionId, initialPrompt);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assessment.assessment,
        timestamp: new Date(),
        assessment
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Fetch updated patient data
      await fetchPatientData(currentSessionId);
      
      // Handle URL and conversation history for new consultation
      if (isNewConsultation) {
        try {
          const sessionData = await apiService.getSession(currentSessionId);
          if (sessionData.session.slug) {
            conversationHistory.saveConversation({
              slug: sessionData.session.slug,
              sessionId: currentSessionId,
              title: `${data.race} - ${data.motif_consultation}`,
              firstMessage: `Consultation ${data.race} (${data.sexe})`,
              lastActivity: new Date(),
              messageCount: 2
            });
            
            setCurrentSlug(sessionData.session.slug);
            window.history.pushState({}, '', `/${sessionId}`);
          }
        } catch (error) {
          console.error('Failed to get session slug:', error);
        }
        setIsNewConsultation(false);
      }
      
    } catch (error) {
      console.error('Failed to process pre-consultation data:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Désolé, une erreur est survenue lors du traitement des informations. Veuillez réessayer.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreConsultationCancel = () => {
    setShowPreConsultationForm(false);
    if (isNewConsultation) {
      // If it's a new consultation and user cancels, redirect to home
      setIsNewConsultation(false);
      if (!getSessionIdFromUrl()) {
        // Add welcome message for cancelled new consultation
        const welcomeMessage: Message = {
          id: 'welcome',
          role: 'assistant',
          content: 'Bonjour ! Je suis votre assistant spécialisé en neurologie vétérinaire canine. Cliquez sur "Nouveau" pour commencer une consultation avec le formulaire pré-rempli, ou tapez directement votre question.',
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      }
    }
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
        <div className="chat-card">
          <div className="chat-header">
            <h1>
              <i className="fas fa-brain"></i>
              <span>NeuroVet - Assistant Diagnostique</span>
            </h1>
            <div className="header-controls">
              <button 
                className={`patient-data-toggle ${showPatientData ? 'active' : ''}`}
                onClick={() => setShowPatientData(!showPatientData)}
                disabled={!patientData || patientData.collected_fields.length === 0}
              >
                <i className="fas fa-chart-bar"></i>
                <span>Données Patient</span>
                {patientData && patientData.collected_fields.length > 0 && (
                  <span className="data-count">{patientData.collected_fields.length}</span>
                )}
              </button>
              <div className="connection-status">
                <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                  <i className={`fas ${isConnected ? 'fa-circle' : 'fa-circle'}`}></i>
                  <span>{isConnected ? 'Connecté' : 'Déconnecté'}</span>
                </span>
              </div>
            </div>
          </div>

          <div className="chat-messages">
            <div className="messages-container">
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-header">
                    <span className="role">
                      <i className={`fas ${message.role === 'user' ? 'fa-user-md' : 'fa-robot'}`}></i>
                      <span>{message.role === 'user' ? 'Vétérinaire' : 'Dr. NeuroVet'}</span>
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
                    <span className="role">
                      <i className="fas fa-robot"></i>
                      <span>Dr. NeuroVet</span>
                    </span>
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
          </div>

          {/* Affichage des données patient */}
          {showPatientData && patientData && (
            <PatientDataDisplay 
              patientData={patientData} 
              onClose={() => setShowPatientData(false)}
            />
          )}

          <form onSubmit={sendMessage} className="chat-input-form">
            <div className="input-wrapper">
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
                  {isLoading ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-paper-plane"></i>}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Pre-consultation form */}
        {showPreConsultationForm && (
          <PreConsultationForm
            onSubmit={handlePreConsultationSubmit}
            onCancel={handlePreConsultationCancel}
          />
        )}
      </div>
    </>
  );
};

export default ChatInterface;