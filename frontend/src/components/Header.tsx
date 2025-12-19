import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Typography,
  Divider,
} from '@mui/material';
import { Person, ExitToApp, AccountCircle, Add } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Header.css';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleMenuClose();
    navigate('/profile');
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/');
  };

  const getInitials = () => {
    if (!user) return '';
    return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      }}
    >
      <Toolbar
        sx={{
          maxWidth: '1400px',
          width: '100%',
          margin: '0 auto',
          px: { xs: 1.5, sm: 2, md: 3 },
          minHeight: { xs: '56px', md: '64px' },
        }}
      >
        {/* Logo */}
        <Link to="/" style={{ flexGrow: 1, display: 'flex', alignItems: 'center', textDecoration: 'none', gap: '12px' }}>
          <img
            src="/neuro-locus-logo.png"
            alt="NeuroLocus"
            style={{
              height: 'clamp(60px, 15vw, 100px)',
              width: 'auto',
              display: 'block',
              objectFit: 'contain',
              borderRadius: '4px'
            }}
          />

        </Link>

        {/* Navigation */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 0.5, sm: 1, md: 2 } }}>
          {isAuthenticated && user ? (
            <>
              {/* New Consultation Button */}
              <Button
                variant="contained"
                startIcon={<Add sx={{ display: { xs: 'none', sm: 'block' } }} />}
                onClick={() => navigate('/chat')}
                sx={{
                  background: 'linear-gradient(135deg, #48c78e 0%, #3eb07d 100%)',
                  color: '#ffffff',
                  fontWeight: 600,
                  textTransform: 'none',
                  px: { xs: 1.5, sm: 2, md: 2.5 },
                  fontSize: { xs: '0.8rem', sm: '0.875rem' },
                  whiteSpace: 'nowrap',
                  minWidth: 'auto',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #3eb07d 0%, #36a06d 100%)',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 4px 12px rgba(72, 199, 142, 0.3)',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
                  Nouvelle Consultation
                </Box>
                <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>
                  Nouvelle
                </Box>
              </Button>

              {/* User Avatar and Menu */}
              <IconButton
                onClick={handleMenuOpen}
                size="small"
                sx={{
                  p: 0,
                  '&:hover': {
                    backgroundColor: 'transparent',
                  },
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: '#48c78e',
                    width: 40,
                    height: 40,
                    fontSize: '14px',
                    fontWeight: 600,
                  }}
                >
                  {getInitials()}
                </Avatar>
              </IconButton>

              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                sx={{
                  mt: 1,
                }}
                PaperProps={{
                  sx: {
                    minWidth: 200,
                    borderRadius: 2,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                  },
                }}
              >
                <Box sx={{ px: 2, py: 1.5 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#2c3e50' }}>
                    {user.first_name} {user.last_name}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748b' }}>
                    {user.email}
                  </Typography>
                </Box>

                <Divider />

                <MenuItem onClick={handleProfile} sx={{ py: 1.5, px: 2 }}>
                  <AccountCircle sx={{ mr: 1.5, color: '#48c78e' }} />
                  Mon profil
                </MenuItem>

                <MenuItem onClick={handleLogout} sx={{ py: 1.5, px: 2 }}>
                  <ExitToApp sx={{ mr: 1.5, color: '#ef4444' }} />
                  Déconnexion
                </MenuItem>
              </Menu>
            </>
          ) : (
            <>
              {/* Login and Register Buttons */}
              <Button
                variant="text"
                startIcon={<Person sx={{ display: { xs: 'none', sm: 'inline-flex' } }} />}
                onClick={() => navigate('/login')}
                sx={{
                  color: '#475569',
                  fontWeight: 500,
                  textTransform: 'none',
                  px: { xs: 1, sm: 1.5 },
                  fontSize: { xs: '0.8rem', sm: '0.875rem' },
                  minWidth: 'auto',
                  '&:hover': {
                    backgroundColor: '#f1f5f9',
                    color: '#48c78e',
                  },
                }}
              >
                Connexion
              </Button>

              <Button
                variant="contained"
                onClick={() => navigate('/register')}
                sx={{
                  background: 'linear-gradient(135deg, #48c78e 0%, #3eb07d 100%)',
                  color: '#ffffff',
                  fontWeight: 600,
                  textTransform: 'none',
                  px: { xs: 1.5, sm: 2, md: 2.5 },
                  fontSize: { xs: '0.8rem', sm: '0.875rem' },
                  minWidth: 'auto',
                  whiteSpace: 'nowrap',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #3eb07d 0%, #36a06d 100%)',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 4px 12px rgba(72, 199, 142, 0.3)',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                S'inscrire
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
