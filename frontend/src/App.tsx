import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ChatInterface from './components/ChatInterface';
import LandingPage from './pages/LandingPage';
import Header from './components/Header';
import { neuroLocusTheme } from './theme/muiTheme';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={neuroLocusTheme}>
      <CssBaseline />
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/chat" element={<ChatInterface />} />
          <Route path="/chat/:sessionId" element={<ChatInterface />} />
          {/* Legacy route for existing session URLs */}
          <Route path="/:sessionId" element={<ChatInterface />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
