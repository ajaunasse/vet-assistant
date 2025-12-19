import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LandingPage.css';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const handleStartConsultation = () => {
    navigate('/chat');
  };

  const handleScrollToFeatures = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      const navHeight = 70; // Hauteur approximative de la navbar
      const elementPosition = featuresSection.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navHeight;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <img src="/neuro-locus-logo.png" alt="NeuroLocus" style={{ height: '40px', marginRight: '10px' }} />
            <span>NeuroLocus</span>
          </div>
          <button className="nav-cta" onClick={handleStartConsultation}>
            Commencer
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Assistant IA pour le diagnostic
              <span className="hero-highlight"> neurologique vétérinaire</span>
            </h1>
            <p className="hero-subtitle">
              NeuroLocus vous accompagne dans l'analyse des troubles neurologiques canins.
              Un outil d'aide au diagnostic basé sur l'intelligence artificielle,
              conçu par et pour les vétérinaires.
            </p>
            <div className="hero-cta-group">
              <button className="hero-cta-primary" onClick={handleStartConsultation}>
                <i className="fas fa-comments"></i>
                Commencer une consultation
              </button>
              <a href="#features" className="hero-cta-secondary" onClick={handleScrollToFeatures}>
                En savoir plus
                <i className="fas fa-arrow-down"></i>
              </a>
            </div>
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">150+</span>
                <span className="stat-label">Pathologies référencées</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">24/7</span>
                <span className="stat-label">Disponible en continu</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">IA</span>
                <span className="stat-label">Dernière génération</span>
              </div>
            </div>
          </div>
          <div className="hero-illustration">
            <div className="hero-image-container">
              <div className="hero-blob"></div>
              <div className="hero-icon-main">
                <i className="fas fa-dog"></i>
              </div>
              <div className="floating-icon floating-icon-1">
                <i className="fas fa-brain"></i>
              </div>
              <div className="floating-icon floating-icon-2">
                <i className="fas fa-stethoscope"></i>
              </div>
              <div className="floating-icon floating-icon-3">
                <i className="fas fa-heartbeat"></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="section-container">
          <div className="section-header">
            <span className="section-badge">Fonctionnalités</span>
            <h2 className="section-title">Un assistant conçu pour les professionnels</h2>
            <p className="section-subtitle">
              Des outils puissants pour vous aider dans votre pratique quotidienne
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-robot"></i>
              </div>
              <h3 className="feature-title">Diagnostic assisté par IA</h3>
              <p className="feature-description">
                Notre intelligence artificielle analyse les symptômes et propose
                des diagnostics différentiels pertinents basés sur les dernières
                connaissances en neurologie vétérinaire.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-book-medical"></i>
              </div>
              <h3 className="feature-title">Base de connaissances complète</h3>
              <p className="feature-description">
                Plus de 150 pathologies neurologiques canines documentées avec
                leurs symptômes, causes, traitements et pronostics détaillés.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-clipboard-list"></i>
              </div>
              <h3 className="feature-title">Suivi des données patient</h3>
              <p className="feature-description">
                Collecte et organisation automatique des informations cliniques
                pour un suivi optimal et une traçabilité complète des consultations.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-comments"></i>
              </div>
              <h3 className="feature-title">Interface conversationnelle</h3>
              <p className="feature-description">
                Dialoguez naturellement avec l'assistant comme avec un confrère.
                Posez vos questions, décrivez les symptômes, obtenez des réponses claires.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-container">
          <div className="section-header">
            <span className="section-badge">Comment ça marche</span>
            <h2 className="section-title">Simple et efficace</h2>
            <p className="section-subtitle">
              Trois étapes pour obtenir une aide au diagnostic
            </p>
          </div>
          <div className="steps-container">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-icon">
                <i className="fas fa-edit"></i>
              </div>
              <h3 className="step-title">Décrivez le cas</h3>
              <p className="step-description">
                Renseignez les informations du patient (race, âge, sexe) et
                décrivez les symptômes neurologiques observés.
              </p>
            </div>
            <div className="step-connector">
              <i className="fas fa-arrow-right"></i>
            </div>
            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-icon">
                <i className="fas fa-search"></i>
              </div>
              <h3 className="step-title">L'IA analyse</h3>
              <p className="step-description">
                Notre assistant pose des questions pertinentes pour affiner
                l'analyse et identifier les pathologies possibles.
              </p>
            </div>
            <div className="step-connector">
              <i className="fas fa-arrow-right"></i>
            </div>
            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-icon">
                <i className="fas fa-file-medical-alt"></i>
              </div>
              <h3 className="step-title">Recevez le diagnostic</h3>
              <p className="step-description">
                Obtenez un diagnostic différentiel avec les probabilités,
                examens recommandés et options de traitement.
              </p>
            </div>
          </div>
          <div className="how-cta">
            <button className="hero-cta-primary" onClick={handleStartConsultation}>
              <i className="fas fa-play"></i>
              Essayer maintenant
            </button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="section-container">
          <div className="cta-content">
            <h2 className="cta-title">
              Prêt à améliorer vos diagnostics neurologiques ?
            </h2>
            <p className="cta-subtitle">
              Rejoignez les vétérinaires qui utilisent déjà NeuroLocus pour
              offrir les meilleurs soins à leurs patients.
            </p>
            <button className="cta-button" onClick={handleStartConsultation}>
              <i className="fas fa-rocket"></i>
              Commencer gratuitement
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-main">
            <div className="footer-brand">
              <div className="footer-logo">
                <i className="fas fa-brain"></i>
                <span>NeuroLocus</span>
              </div>
              <p className="footer-description">
                Assistant IA pour le diagnostic neurologique vétérinaire.
                Un outil d'aide à la décision conçu pour les professionnels.
              </p>
            </div>
            <div className="footer-links">

            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; {new Date().getFullYear()} NeuroLocus. Tous droits réservés.</p>
            <p className="footer-disclaimer">
              Outil d'aide au diagnostic - Ne remplace pas l'avis d'un vétérinaire qualifié.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
