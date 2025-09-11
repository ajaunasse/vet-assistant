import React from 'react';
import '../styles/PatientDataDisplay.css';

interface PatientData {
  age?: string;
  sex?: string;
  race?: string;
  weight?: string;
  symptoms: string[];
  symptom_duration?: string;
  symptom_progression?: string;
  medical_history: string[];
  current_medications: string[];
  is_complete: boolean;
  collected_fields: string[];
}

interface PatientDataDisplayProps {
  patientData: PatientData;
  onClose: () => void;
}

const PatientDataDisplay: React.FC<PatientDataDisplayProps> = ({ patientData, onClose }) => {
  if (!patientData || patientData.collected_fields.length === 0) {
    return (
      <div className="patient-data-empty">
        <p>🔍 Aucune donnée patient collectée</p>
      </div>
    );
  }

  const getCompletionPercentage = () => {
    const requiredFields = ['age', 'sex', 'race', 'symptoms'];
    const collectedRequired = requiredFields.filter(field => 
      patientData.collected_fields.includes(field)
    ).length;
    return Math.round((collectedRequired / requiredFields.length) * 100);
  };

  return (
    <>
      <div className="patient-data-overlay" onClick={onClose}></div>
      <div className="patient-data-display">
        <div className="patient-data-header">
          <h3>
            <i className="fas fa-chart-bar"></i>
            <span>Données Patient Collectées</span>
          </h3>
          <div className="header-controls">
            <div className="completion-badge">
              {getCompletionPercentage()}% complété
            </div>
            <button className="close-btn" onClick={onClose} title="Fermer">
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>

      <div className="patient-data-grid">
        {/* Informations de base */}
        <div className="data-section basic-info">
          <h4>
            <i className="fas fa-info-circle"></i>
            <span>Informations de base</span>
          </h4>
          
          {patientData.age && (
            <div className="data-item">
              <span className="data-label">Âge:</span>
              <span className="data-value">{patientData.age}</span>
            </div>
          )}
          
          {patientData.sex && (
            <div className="data-item">
              <span className="data-label">Sexe:</span>
              <span className="data-value">{patientData.sex}</span>
            </div>
          )}
          
          {patientData.race && (
            <div className="data-item">
              <span className="data-label">Race:</span>
              <span className="data-value">{patientData.race}</span>
            </div>
          )}
          
          {patientData.weight && (
            <div className="data-item">
              <span className="data-label">Poids:</span>
              <span className="data-value">{patientData.weight}</span>
            </div>
          )}
        </div>

        {/* Symptômes */}
        {patientData.symptoms.length > 0 && (
          <div className="data-section symptoms">
            <h4>
              <i className="fas fa-exclamation-triangle"></i>
              <span>Symptômes observés</span>
            </h4>
            <div className="symptoms-list">
              {patientData.symptoms.map((symptom, index) => (
                <span key={index} className="symptom-tag">
                  {symptom}
                </span>
              ))}
            </div>
            
            {patientData.symptom_duration && (
              <div className="data-item">
                <span className="data-label">Durée:</span>
                <span className="data-value">{patientData.symptom_duration}</span>
              </div>
            )}
            
            {patientData.symptom_progression && (
              <div className="data-item">
                <span className="data-label">Évolution:</span>
                <span className="data-value">{patientData.symptom_progression}</span>
              </div>
            )}
          </div>
        )}

        {/* Antécédents médicaux */}
        {patientData.medical_history.length > 0 && (
          <div className="data-section medical-history">
            <h4>
              <i className="fas fa-clipboard-list"></i>
              <span>Antécédents médicaux</span>
            </h4>
            <ul className="history-list">
              {patientData.medical_history.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Médicaments actuels */}
        {patientData.current_medications.length > 0 && (
          <div className="data-section medications">
            <h4>
              <i className="fas fa-pills"></i>
              <span>Médicaments actuels</span>
            </h4>
            <ul className="medications-list">
              {patientData.current_medications.map((med, index) => (
                <li key={index}>{med}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Indicateur de complétude */}
      <div className="completion-indicator">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${getCompletionPercentage()}%` }}
          ></div>
        </div>
        <p className="completion-text">
          {patientData.is_complete 
            ? <><i className="fas fa-check-circle"></i> Données complètes pour diagnostic</>
            : <><i className="fas fa-hourglass-half"></i> Collecte en cours...</>
          }
        </p>
      </div>
      </div>
    </>
  );
};

export default PatientDataDisplay;