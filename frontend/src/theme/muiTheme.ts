import { createTheme } from '@mui/material/styles';

// Thème personnalisé NeuroLocus
export const neuroLocusTheme = createTheme({
  palette: {
    primary: {
      main: '#48c78e',
      dark: '#3eb07d',
      light: '#e8f8f1',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#4a90d9',
      light: '#e8f1fb',
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
    },
    background: {
      default: '#f8fafb',
      paper: '#ffffff',
    },
    divider: '#e2e8f0',
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: {
      fontFamily: '"Nunito", sans-serif',
      fontWeight: 700,
    },
    h2: {
      fontFamily: '"Nunito", sans-serif',
      fontWeight: 600,
    },
    h3: {
      fontFamily: '"Nunito", sans-serif',
      fontWeight: 600,
    },
    h4: {
      fontFamily: '"Nunito", sans-serif',
      fontWeight: 600,
    },
    h5: {
      fontFamily: '"Nunito", sans-serif',
      fontWeight: 600,
    },
    h6: {
      fontFamily: '"Nunito", sans-serif',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 10,
          padding: '12px 24px',
        },
        contained: {
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(72, 199, 142, 0.25)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            backgroundColor: '#ffffff',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#cbd5e1',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#48c78e',
              borderWidth: 1,
            },
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundColor: '#ffffff',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          fontSize: '20px',
          fontWeight: 600,
          color: '#0f172a',
          padding: '24px 32px',
          borderBottom: '1px solid #f1f5f9',
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          padding: '36px 40px',
        },
      },
    },
    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: '24px 40px 36px',
          borderTop: '1px solid #f1f5f9',
        },
      },
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          fontSize: '13px',
          fontWeight: 500,
          color: '#475569',
          marginBottom: '4px',
          '&.Mui-focused': {
            color: '#475569',
          },
        },
      },
    },
    MuiRadio: {
      styleOverrides: {
        root: {
          color: '#cbd5e1',
          '&.Mui-checked': {
            color: '#48c78e',
          },
        },
      },
    },
    MuiCheckbox: {
      styleOverrides: {
        root: {
          color: '#cbd5e1',
          '&.Mui-checked': {
            color: '#48c78e',
          },
        },
      },
    },
  },
});
