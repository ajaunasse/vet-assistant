/**
 * Login Page
 */
import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Alert,
  Paper,
  Link,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showResendLink, setShowResendLink] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setShowResendLink(false);
    setResendSuccess(false);
    setLoading(true);

    try {
      await login(email, password);
      navigate('/'); // Redirect to home after successful login
    } catch (err: any) {
      const errorMessage = err.message || 'Échec de la connexion';
      setError(errorMessage);

      // Check if error is about unverified email
      if (errorMessage.includes('Email non vérifié') || errorMessage.includes('not verified')) {
        setShowResendLink(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResendLoading(true);
    setResendSuccess(false);

    try {
      await authService.resendVerification(email);
      setResendSuccess(true);
      setShowResendLink(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Échec de l\'envoi de l\'email');
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafb 0%, #e8f8f1 100%)',
        display: 'flex',
        alignItems: 'center',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
            border: '1px solid #e1e8ed',
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
              <img
                src="/neuro-locus-logo.png"
                alt="NeuroLocus"
                style={{ height: '200px', width: 'auto' }}
              />
            </Box>
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 700,
                color: '#2c3e50',
                fontFamily: "'Nunito', sans-serif",
              }}
            >
              Connexion
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Connectez-vous à votre compte NeuroLocus
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
              {showResendLink && (
                <Box sx={{ mt: 2, pt: 1.5, borderTop: '1px solid rgba(211, 47, 47, 0.2)' }}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={handleResendVerification}
                    disabled={resendLoading}
                    sx={{
                      backgroundColor: '#fff',
                      color: '#d32f2f',
                      fontWeight: 600,
                      textTransform: 'none',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                      '&:hover': {
                        backgroundColor: '#f5f5f5',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
                      },
                      '&:disabled': {
                        backgroundColor: '#e0e0e0',
                        color: '#999',
                      },
                    }}
                  >
                    {resendLoading ? 'Envoi en cours...' : 'Renvoyer l\'email de vérification'}
                  </Button>
                </Box>
              )}
            </Alert>
          )}

          {resendSuccess && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Email de vérification renvoyé avec succès ! Veuillez vérifier votre boîte de réception.
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              margin="normal"
              autoComplete="email"
              autoFocus
            />

            <TextField
              fullWidth
              label="Mot de passe"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              margin="normal"
              autoComplete="current-password"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                mt: 3,
                mb: 2,
                py: 1.5,
                background: 'linear-gradient(135deg, #48c78e 0%, #3eb07d 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #3eb07d 0%, #36a06d 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(72, 199, 142, 0.35)',
                },
                transition: 'all 0.3s ease',
                fontWeight: 600,
              }}
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Pas encore de compte ?{' '}
                <Link
                  component={RouterLink}
                  to="/register"
                  sx={{
                    color: '#48c78e',
                    textDecoration: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  S'inscrire
                </Link>
              </Typography>
            </Box>
          </form>
        </Paper>
      </Container>
    </Box>
  );
};

export default LoginPage;
