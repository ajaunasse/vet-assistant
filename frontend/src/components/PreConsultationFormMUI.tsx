import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Radio,
  RadioGroup,
  FormControlLabel,
  Checkbox,
  Button,
  Box,
  IconButton,
  Autocomplete,
  FormLabel,
  Stack,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface PreConsultationData {
  race: string;
  age: string;
  sexe: 'Mâle' | 'Femelle' | '';
  castre: boolean;
  motif_consultation: string;
  premiers_symptomes: string;
  examens_realises: string;
  etat_conscience: 'NSP' | 'Normal' | 'Altéré' | '';
  comportement: 'NSP' | 'Normal' | 'Compulsif' | '';
  convulsions: 'Oui' | 'Non' | 'NSP' | '';
}

interface PreConsultationFormProps {
  onSubmit: (data: PreConsultationData) => void;
  onCancel: () => void;
}

interface DogBreed {
  id: number;
  name: string;
  created_at: string;
}

interface ConsultationReason {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

const PreConsultationFormMUI: React.FC<PreConsultationFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<PreConsultationData>({
    race: '',
    age: '',
    sexe: '',
    castre: false,
    motif_consultation: '',
    premiers_symptomes: '',
    examens_realises: '',
    etat_conscience: '',
    comportement: '',
    convulsions: ''
  });

  const [dogBreeds, setDogBreeds] = useState<DogBreed[]>([]);
  const [consultationReasons, setConsultationReasons] = useState<ConsultationReason[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    const loadReferenceData = async () => {
      try {
        setIsLoadingData(true);
        const [breedsResponse, reasonsResponse] = await Promise.all([
          fetch('/api/v1/dog-breeds'),
          fetch('/api/v1/consultation-reasons')
        ]);

        if (breedsResponse.ok && reasonsResponse.ok) {
          const breeds = await breedsResponse.json();
          const reasons = await reasonsResponse.json();

          setDogBreeds(breeds);
          setConsultationReasons(reasons);
        }
      } catch (error) {
        console.error('Error loading reference data:', error);
      } finally {
        setIsLoadingData(false);
      }
    };

    loadReferenceData();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.race || !formData.age || !formData.sexe || !formData.motif_consultation ||
        !formData.premiers_symptomes || !formData.etat_conscience || !formData.comportement ||
        !formData.convulsions) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    onSubmit(formData);
  };

  const isFormValid = formData.race && formData.age && formData.sexe && formData.motif_consultation &&
                      formData.premiers_symptomes && formData.etat_conscience && formData.comportement &&
                      formData.convulsions;

  return (
    <Dialog
      open={true}
      onClose={onCancel}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { maxWidth: '700px' }
      }}
    >
      <DialogTitle>
        Informations Pré-Consultation
        <IconButton
          aria-label="close"
          onClick={onCancel}
          sx={{
            position: 'absolute',
            right: 24,
            top: 24,
            color: '#94a3b8',
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <Stack spacing={4}>
            {/* Race */}
            <Autocomplete
              options={dogBreeds}
              getOptionLabel={(option) => option.name}
              value={dogBreeds.find(b => b.name === formData.race) || null}
              onChange={(_, newValue) => {
                setFormData({ ...formData, race: newValue?.name || '' });
              }}
              inputValue={formData.race}
              onInputChange={(_, newInputValue) => {
                setFormData({ ...formData, race: newInputValue });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Race du chien *"
                  placeholder="Tapez pour rechercher une race..."
                  required
                />
              )}
              loading={isLoadingData}
            />

            {/* Âge */}
            <TextField
              fullWidth
              label="Âge *"
              value={formData.age}
              onChange={(e) => setFormData({ ...formData, age: e.target.value })}
              placeholder="Ex: 3 ans, 8 mois, 2 ans et demi..."
              required
            />

            {/* Sexe et Castré */}
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'stretch', sm: 'flex-end' }}>
              <Box sx={{ flex: 1 }}>
                <FormControl component="fieldset" required fullWidth>
                  <FormLabel component="legend" sx={{ mb: 1 }}>Sexe *</FormLabel>
                  <RadioGroup
                    row
                    value={formData.sexe}
                    onChange={(e) => setFormData({ ...formData, sexe: e.target.value as 'Mâle' | 'Femelle' })}
                  >
                    <FormControlLabel value="Mâle" control={<Radio />} label="Mâle" />
                    <FormControlLabel value="Femelle" control={<Radio />} label="Femelle" />
                  </RadioGroup>
                </FormControl>
              </Box>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.castre}
                    onChange={(e) => setFormData({ ...formData, castre: e.target.checked })}
                  />
                }
                label="Castré/Stérilisé"
              />
            </Stack>

            {/* Motif de consultation */}
            <FormControl fullWidth required>
              <InputLabel>Motif de consultation *</InputLabel>
              <Select
                value={formData.motif_consultation}
                onChange={(e) => setFormData({ ...formData, motif_consultation: e.target.value })}
                label="Motif de consultation *"
              >
                <MenuItem value="">Sélectionnez le motif de consultation</MenuItem>
                {consultationReasons.map((reason) => (
                  <MenuItem key={reason.id} value={reason.name}>
                    {reason.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* État de conscience et Comportement */}
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <FormControl fullWidth required>
                <InputLabel>État de conscience *</InputLabel>
                <Select
                  value={formData.etat_conscience}
                  onChange={(e) => setFormData({ ...formData, etat_conscience: e.target.value as any })}
                  label="État de conscience *"
                >
                  <MenuItem value="">Sélectionnez</MenuItem>
                  <MenuItem value="NSP">Ne sait pas</MenuItem>
                  <MenuItem value="Normal">Normal</MenuItem>
                  <MenuItem value="Altéré">Altéré</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth required>
                <InputLabel>Comportement *</InputLabel>
                <Select
                  value={formData.comportement}
                  onChange={(e) => setFormData({ ...formData, comportement: e.target.value as any })}
                  label="Comportement *"
                >
                  <MenuItem value="">Sélectionnez</MenuItem>
                  <MenuItem value="NSP">Ne sait pas</MenuItem>
                  <MenuItem value="Normal">Normal</MenuItem>
                  <MenuItem value="Compulsif">Compulsif</MenuItem>
                </Select>
              </FormControl>
            </Stack>

            {/* Convulsions */}
            <FormControl fullWidth required>
              <InputLabel>Convulsions *</InputLabel>
              <Select
                value={formData.convulsions}
                onChange={(e) => setFormData({ ...formData, convulsions: e.target.value as any })}
                label="Convulsions *"
              >
                <MenuItem value="">Sélectionnez</MenuItem>
                <MenuItem value="Oui">Oui</MenuItem>
                <MenuItem value="Non">Non</MenuItem>
                <MenuItem value="NSP">Ne sait pas</MenuItem>
              </Select>
            </FormControl>

            {/* Description des premiers symptômes */}
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Description des premiers symptômes *"
              value={formData.premiers_symptomes}
              onChange={(e) => setFormData({ ...formData, premiers_symptomes: e.target.value })}
              placeholder="Décrivez en détail les symptômes observés, leur durée, leur évolution..."
              required
            />

            {/* Examens réalisés */}
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Examens réalisés"
              value={formData.examens_realises}
              onChange={(e) => setFormData({ ...formData, examens_realises: e.target.value })}
              placeholder="Listez les examens déjà réalisés (prise de sang, radiographies, échographies, IRM, etc.)..."
            />
          </Stack>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onCancel} variant="outlined" color="inherit">
          Annuler
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={!isFormValid}
        >
          Commencer la consultation
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PreConsultationFormMUI;
