import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Header.css';

const Header: React.FC = () => {
  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <i className="fas fa-brain"></i>
          <span className="logo-text">NeuroLocus</span>
        </Link>

        <nav className="header-nav">
          {/* Espace pour d'autres liens à ajouter plus tard */}
        </nav>
      </div>
    </header>
  );
};

export default Header;
