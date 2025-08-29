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

  return (
    <div className="assessment-display">
      <div className="assessment-header">
        <h3>📋 Évaluation Diagnostique</h3>
        <span className="confidence-badge">
          {getConfidenceIcon(assessment.confidence_level)} 
          Confiance: {assessment.confidence_level}
        </span>
      </div>

      {/* Message principal en évidence */}
      <div className="assessment-message">
        <p className="main-assessment">{assessment.assessment}</p>
      </div>

      {/* Sections collapsibles */}
      <div className="collapsible-sections">
        <button 
          className="expand-button"
          onClick={handleExpandToggle}
          aria-expanded={isExpanded}
        >
          <span className="expand-icon">{isExpanded ? '−' : '+'}</span>
          Détails de l'analyse
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

            <div className="assessment-section">
              <h4>💊 Approche Thérapeutique</h4>
              <p className="treatment">{assessment.treatment}</p>
            </div>

            <div className="assessment-section">
              <h4>📈 Pronostic</h4>
              <p className="prognosis">{assessment.prognosis}</p>
            </div>

            {assessment.questions.length > 0 && (
              <div className="assessment-section">
                <h4>❓ Questions Clarifiantes</h4>
                <ul className="questions-list">
                  {assessment.questions.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssessmentDisplay;