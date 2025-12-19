/**
 * User Profile Page
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Alert,
  Paper,
  Grid,
  Chip,
  Divider,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { CheckCircle, Warning, ArrowBack } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import { UpdateProfileData } from '../types/auth';

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, updateUser } = useAuth();

  const [formData, setFormData] = useState<UpdateProfileData>({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    clinic_name: user?.clinic_name || '',
    order_number: user?.order_number || '',
    specialty: user?.specialty || '',
    is_student: user?.is_student || false,
    school_name: user?.school_name || '',
  });

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
    setSuccess(false);
    setLoading(true);

    try {
      const updatedUser = await authService.updateProfile(formData);
      updateUser(updatedUser);
      setSuccess(true);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Échec de la mise à jour du profil');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null; // ProtectedRoute should handle this
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
          <Box sx={{ mb: 3 }}>
            <Button
              startIcon={<ArrowBack />}
              onClick={() => navigate('/')}
              sx={{
                color: '#48c78e',
                mb: 2,
                '&:hover': {
                  backgroundColor: 'rgba(72, 199, 142, 0.08)',
                },
              }}
            >
              Retour
            </Button>

            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography
                variant="h4"
                component="h1"
                sx={{
                  fontWeight: 700,
                  color: '#2c3e50',
                  fontFamily: "'Nunito', sans-serif",
                }}
              >
                <i className="fas fa-user-circle" style={{ color: '#48c78e', marginRight: '10px' }}></i>
                Mon Profil
              </Typography>

              {user.is_verified ? (
                <Chip
                  icon={<CheckCircle />}
                  label="Email vérifié"
                  color="success"
                  size="small"
                />
              ) : (
                <Chip
                  icon={<Warning />}
                  label="Email non vérifié"
                  color="warning"
                  size="small"
                />
              )}
            </Box>

            <Typography variant="body2" color="text.secondary">
              Gérez vos informations personnelles et professionnelles
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Profil mis à jour avec succès !
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              {/* Email - Read-only */}
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Email"
                  value={user.email}
                  disabled
                  helperText="L'adresse email ne peut pas être modifiée"
                />
              </Grid>

              {/* Personal Information */}
              <Grid size={12}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#2c3e50', mb: 1 }}>
                  Informations personnelles
                </Typography>
              </Grid>

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

              {/* Professional Information */}
              <Grid size={12}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#2c3e50', mb: 1, mt: 2 }}>
                  Informations professionnelles
                </Typography>
              </Grid>

              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Nom de la clinique"
                  name="clinic_name"
                  value={formData.clinic_name}
                  onChange={handleChange}
                  autoComplete="organization"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Numéro d'ordre"
                  name="order_number"
                  value={formData.order_number}
                  onChange={handleChange}
                  helperText="Numéro d'inscription à l'ordre des vétérinaires"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Spécialité"
                  name="specialty"
                  value={formData.specialty}
                  onChange={handleChange}
                  helperText="Ex: Neurologie, Médecine interne, etc."
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
                mt: 4,
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
              {loading ? 'Enregistrement...' : 'Enregistrer les modifications'}
            </Button>
          </form>

          {/* Account Info */}
          <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid #e1e8ed' }}>
            <Typography variant="body2" color="text.secondary">
              Compte créé le : {new Date(user.created_at).toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default ProfilePage;
