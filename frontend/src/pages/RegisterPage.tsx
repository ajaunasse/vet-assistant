/**
 * Register Page
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
  Grid,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { RegisterData } from '../types/auth';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    clinic_name: '',
    order_number: '',
    specialty: '',
    is_student: false,
    school_name: '',
  });

  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    setLoading(true);

    try {
      await register(formData);
      setSuccess(true);

      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      setError(err.message || "Échec de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
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
            <Typography variant="h5" gutterBottom color="success.main" sx={{ fontWeight: 600 }}>
              ✓ Inscription réussie !
            </Typography>
            <Typography variant="body1" sx={{ mt: 2, mb: 3 }}>
              Un email de vérification a été envoyé à <strong>{formData.email}</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Veuillez vérifier votre boîte de réception et cliquer sur le lien pour activer votre compte.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Redirection vers la page de connexion...
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
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2, border: '1px solid #e1e8ed' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
              <img
                src="/neuro-locus-logo.png"
                alt="NeuroLocus"
                style={{ height: '60px', width: 'auto' }}
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
              Inscription
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Créez votre compte vétérinaire NeuroLocus
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Prénom"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  autoComplete="given-name"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Nom"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  autoComplete="family-name"
                />
              </Grid>

              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  autoComplete="email"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Mot de passe"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
                  required
                  helperText="Minimum 8 caractères"
                  autoComplete="new-password"
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
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Confirmer le mot de passe"
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
              </Grid>

              <Grid size={12}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Informations professionnelles (optionnel)
                </Typography>
              </Grid>

              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Nom de la clinique"
                  name="clinic_name"
                  value={formData.clinic_name}
                  onChange={handleChange}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Numéro d'ordre"
                  name="order_number"
                  value={formData.order_number}
                  onChange={handleChange}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Spécialité"
                  name="specialty"
                  value={formData.specialty}
                  onChange={handleChange}
                />
              </Grid>

              <Grid size={12}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_student || false}
                      onChange={(e) => setFormData({ ...formData, is_student: e.target.checked, school_name: e.target.checked ? formData.school_name : '' })}
                      sx={{
                        color: '#48c78e',
                        '&.Mui-checked': {
                          color: '#48c78e',
                        },
                      }}
                    />
                  }
                  label="Étudiant"
                />
              </Grid>

              {formData.is_student && (
                <Grid size={12}>
                  <TextField
                    fullWidth
                    label="Nom de l'école"
                    name="school_name"
                    value={formData.school_name}
                    onChange={handleChange}
                    helperText="École vétérinaire"
                  />
                </Grid>
              )}
            </Grid>

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
              {loading ? 'Inscription...' : "S'inscrire"}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Vous avez déjà un compte ?{' '}
                <Link
                  component={RouterLink}
                  to="/login"
                  sx={{
                    color: '#48c78e',
                    textDecoration: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Se connecter
                </Link>
              </Typography>
            </Box>
          </form>
        </Paper>
      </Container>
    </Box>
  );
};

export default RegisterPage;
