import React, { useState, useRef, useEffect } from 'react';
import { VeterinaryAssessment } from '../types/api';
import MarkdownRenderer from './MarkdownRenderer';
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
        <div className="main-assessment">
          <MarkdownRenderer content={assessment.assessment} />
        </div>
      </div>

      {/* Question pour la phase de collecte */}
      {!isCompleted && assessment.question && (
        <div className="questions-section">
          <h4>❓ Question de suivi</h4>
          <div className="question-item">
            <MarkdownRenderer content={assessment.question} />
          </div>
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
                  <div className="localization">
                    <MarkdownRenderer content={assessment.localization} />
                  </div>
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
                        <div className="rationale">
                          <MarkdownRenderer content={differential.rationale} />
                        </div>
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
                  <div className="treatment">
                    <MarkdownRenderer content={assessment.treatment} />
                  </div>
                </div>
              )}

              {assessment.prognosis && (
                <div className="assessment-section">
                  <h4>📈 Pronostic</h4>
                  <div className="prognosis">
                    <MarkdownRenderer content={assessment.prognosis} />
                  </div>
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