/**
 * Email Verification Page
 */
import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';
import { authService } from '../services/authService';

const VerifyEmailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');

      if (!token) {
        setStatus('error');
        setMessage('Token de vérification manquant');
        return;
      }

      try {
        const response = await authService.verifyEmail(token);
        setStatus('success');
        setMessage(response.message || 'Email vérifié avec succès !');
      } catch (error: any) {
        setStatus('error');
        setMessage(error.message || 'La vérification a échoué. Le lien est peut-être expiré.');
      }
    };

    verifyEmail();
  }, [searchParams]);

  if (status === 'loading') {
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
          <Paper elevation={3} sx={{ p: 4, borderRadius: 2, textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="body1">
              Vérification de votre email en cours...
            </Typography>
          </Paper>
        </Container>
      </Box>
    );
  }

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
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <img
              src="/neuro-locus-logo.png"
              alt="NeuroLocus"
              style={{ height: '60px', width: 'auto' }}
            />
          </Box>
          {status === 'success' ? (
            <>
              <CheckCircle
                sx={{
                  fontSize: 64,
                  color: '#48c78e',
                  mb: 2,
                }}
              />
              <Typography
                variant="h5"
                gutterBottom
                sx={{
                  fontWeight: 600,
                  color: '#2c3e50',
                  fontFamily: "'Nunito', sans-serif",
                }}
              >
                Email vérifié !
              </Typography>
              <Typography variant="body1" sx={{ mt: 2, mb: 3 }}>
                {message}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Vous pouvez maintenant vous connecter à votre compte.
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/login')}
                sx={{
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
                Se connecter
              </Button>
            </>
          ) : (
            <>
              <Error
                sx={{
                  fontSize: 64,
                  color: '#f44336',
                  mb: 2,
                }}
              />
              <Typography
                variant="h5"
                gutterBottom
                sx={{
                  fontWeight: 600,
                  color: '#2c3e50',
                  fontFamily: "'Nunito', sans-serif",
                }}
              >
                Vérification échouée
              </Typography>
              <Alert severity="error" sx={{ mt: 2, mb: 3, textAlign: 'left' }}>
                {message}
              </Alert>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Le lien de vérification a peut-être expiré. Essayez de vous inscrire à nouveau ou contactez le support.
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/register')}
                sx={{
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
                Retour à l'inscription
              </Button>
            </>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default VerifyEmailPage;
