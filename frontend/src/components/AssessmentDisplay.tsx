import React, { useState, useRef, useEffect } from 'react';
import { VeterinaryAssessment } from '../types/api';
import '../styles/AssessmentDisplay.css';

interface AssessmentDisplayProps {
  assessment: VeterinaryAssessment;
}

const AssessmentDisplay: React.FC<AssessmentDisplayProps> = ({ assessment }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const expandedContentRef = useRef<HTMLDivElement>(null);

  const handleExpandToggle = () => {
    setIsExpanded(!isExpanded);
  };

  useEffect(() => {
    if (isExpanded && expandedContentRef.current) {
      // Attendre que l'animation se termine avant de scroller
      setTimeout(() => {
        expandedContentRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'nearest' 
        });
      }, 100);
    }
  }, [isExpanded]);

  const getProbabilityColor = (probability: string) => {
    switch (probability) {
      case 'haute': return '#e74c3c';
      case 'moyenne': return '#f39c12';
      case 'faible': return '#27ae60';
      default: return '#95a5a6';
    }
  };

  const getConfidenceIcon = (confidence: string) => {
    switch (confidence) {
      case 'haute': return '🔴';
      case 'moyenne': return '🟡';
      case 'faible': return '🟢';
      default: return '⚪';
    }
  };

  const isCompleted = assessment.status === 'completed';

  return (
    <div className="assessment-display">
      <div className="assessment-header">
        <h3>{isCompleted ? '📋 Diagnostic Final' : '🔍 Analyse en cours'}</h3>
        <div className="header-badges">
          <span className={`status-badge ${assessment.status}`}>
            {assessment.status === 'completed' ? '✅ Complété' : '🔄 En cours'}
          </span>
          {isCompleted && (
            <span className="confidence-badge">
              {getConfidenceIcon(assessment.confidence_level)} 
              Confiance: {assessment.confidence_level}
            </span>
          )}
        </div>
      </div>

      {/* Message principal en évidence */}
      <div className="assessment-message">
        <p className="main-assessment">{assessment.assessment}</p>
      </div>

      {/* Questions pour la phase de collecte */}
      {!isCompleted && assessment.questions.length > 0 && (
        <div className="questions-section">
          <h4>❓ Questions de suivi</h4>
          <ul className="questions-list">
            {assessment.questions.map((question, index) => (
              <li key={index}>{question}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Diagnostic complet affiché seulement si status === 'completed' */}
      {isCompleted && (
        <div className="collapsible-sections">
          <button 
            className="expand-button"
            onClick={handleExpandToggle}
            aria-expanded={isExpanded}
          >
            <span className="expand-icon">{isExpanded ? '−' : '+'}</span>
            Détails du diagnostic
          </button>

          {isExpanded && (
            <div className="expanded-content" ref={expandedContentRef}>
              {assessment.localization && (
                <div className="assessment-section">
                  <h4>🎯 Localisation Neuroanatomique</h4>
                  <p className="localization">{assessment.localization}</p>
                </div>
              )}

              {assessment.differentials.length > 0 && (
                <div className="assessment-section">
                  <h4>🔍 Diagnostics Différentiels</h4>
                  <div className="differentials-list">
                    {assessment.differentials.map((differential, index) => (
                      <div key={index} className="differential-item">
                        <div className="differential-header">
                          <span className="condition-name">{differential.condition}</span>
                          <span 
                            className="probability-badge"
                            style={{ backgroundColor: getProbabilityColor(differential.probability) }}
                          >
                            {differential.probability}
                          </span>
                        </div>
                        <p className="rationale">{differential.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {assessment.diagnostics.length > 0 && (
                <div className="assessment-section">
                  <h4>🧪 Examens Recommandés</h4>
                  <ul className="diagnostics-list">
                    {assessment.diagnostics.map((diagnostic, index) => (
                      <li key={index}>{diagnostic}</li>
                    ))}
                  </ul>
                </div>
              )}

              {assessment.treatment && (
                <div className="assessment-section">
                  <h4>💊 Approche Thérapeutique</h4>
                  <p className="treatment">{assessment.treatment}</p>
                </div>
              )}

              {assessment.prognosis && (
                <div className="assessment-section">
                  <h4>📈 Pronostic</h4>
                  <p className="prognosis">{assessment.prognosis}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AssessmentDisplay;