import React, { useState, useEffect } from 'react';
import '../styles/PreConsultationForm.css';

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

const PreConsultationForm: React.FC<PreConsultationFormProps> = ({ onSubmit, onCancel }) => {
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
  const [filteredBreeds, setFilteredBreeds] = useState<DogBreed[]>([]);
  const [showBreedDropdown, setShowBreedDropdown] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Load data from API
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
        } else {
          console.error('Failed to load reference data');
        }
      } catch (error) {
        console.error('Error loading reference data:', error);
      } finally {
        setIsLoadingData(false);
      }
    };

    loadReferenceData();
  }, []);

  const handleRaceChange = (value: string) => {
    setFormData({ ...formData, race: value });
    
    if (value.length > 0) {
      const filtered = dogBreeds.filter(breed =>
        breed.name.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredBreeds(filtered);
      setShowBreedDropdown(filtered.length > 0);
    } else {
      setShowBreedDropdown(false);
    }
  };

  const selectBreed = (breed: DogBreed) => {
    setFormData({ ...formData, race: breed.name });
    setShowBreedDropdown(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation simple
    if (!formData.race || !formData.age || !formData.sexe || !formData.motif_consultation || !formData.premiers_symptomes || !formData.etat_conscience || !formData.comportement || !formData.convulsions) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    onSubmit(formData);
  };

  const isFormValid = formData.race && formData.age && formData.sexe && formData.motif_consultation && formData.premiers_symptomes && formData.etat_conscience && formData.comportement && formData.convulsions;

  return (
    <div className="pre-consultation-overlay">
      <div className="pre-consultation-form">
        <div className="form-header">
          <h2>
            <i className="fas fa-clipboard-check"></i>
            <span>Informations Pré-Consultation</span>
          </h2>
          <button className="close-btn" onClick={onCancel}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="form-content">
          <div className="form-grid">
            {/* Race */}
            <div className="form-group breed-group">
              <label htmlFor="race">
                <i className="fas fa-dog"></i>
                Race du chien *
              </label>
              <div className="breed-input-container">
                <input
                  type="text"
                  id="race"
                  value={formData.race}
                  onChange={(e) => handleRaceChange(e.target.value)}
                  onFocus={() => {
                    if (formData.race.length > 0) {
                      const filtered = dogBreeds.filter(breed =>
                        breed.name.toLowerCase().includes(formData.race.toLowerCase())
                      );
                      setFilteredBreeds(filtered);
                      setShowBreedDropdown(true);
                    }
                  }}
                  onBlur={() => {
                    // Delay hiding to allow click on dropdown
                    setTimeout(() => setShowBreedDropdown(false), 150);
                  }}
                  placeholder="Tapez pour rechercher une race..."
                  className="form-input"
                  required
                  disabled={isLoadingData}
                />
                {showBreedDropdown && filteredBreeds.length > 0 && (
                  <div className="breed-dropdown">
                    {filteredBreeds.slice(0, 10).map((breed) => (
                      <div
                        key={breed.id}
                        className="breed-option"
                        onClick={() => selectBreed(breed)}
                      >
                        {breed.name}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Âge */}
            <div className="form-group">
              <label htmlFor="age">
                <i className="fas fa-calendar-alt"></i>
                Âge *
              </label>
              <input
                type="text"
                id="age"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                placeholder="Ex: 3 ans, 8 mois, 2 ans et demi..."
                className="form-input"
                required
              />
            </div>

            {/* Sexe et Castré sur la même ligne */}
            <div className="form-row">
              <div className="form-group">
                <label>
                  <i className="fas fa-venus-mars"></i>
                  Sexe *
                </label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="sexe"
                      value="Mâle"
                      checked={formData.sexe === 'Mâle'}
                      onChange={(e) => setFormData({ ...formData, sexe: e.target.value as 'Mâle' })}
                    />
                    <span className="radio-custom"></span>
                    Mâle
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="sexe"
                      value="Femelle"
                      checked={formData.sexe === 'Femelle'}
                      onChange={(e) => setFormData({ ...formData, sexe: e.target.value as 'Femelle' })}
                    />
                    <span className="radio-custom"></span>
                    Femelle
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.castre}
                    onChange={(e) => setFormData({ ...formData, castre: e.target.checked })}
                  />
                  <span className="checkbox-custom"></span>
                  <i className="fas fa-cut"></i>
                  Castré/Stérilisé
                </label>
              </div>
            </div>
          </div>

          {/* Motif de consultation */}
          <div className="form-group">
            <label htmlFor="motif">
              <i className="fas fa-stethoscope"></i>
              Motif de consultation *
            </label>
            <select
              id="motif"
              value={formData.motif_consultation}
              onChange={(e) => setFormData({ ...formData, motif_consultation: e.target.value })}
              className="form-input"
              required
              disabled={isLoadingData}
            >
              <option value="">{isLoadingData ? 'Chargement...' : 'Sélectionnez le motif de consultation'}</option>
              {consultationReasons.map((reason) => (
                <option key={reason.id} value={reason.name}>
                  {reason.name}
                </option>
              ))}
            </select>
          </div>

          {/* État de conscience, Comportement et Convulsions */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="etat_conscience">
                <i className="fas fa-brain"></i>
                État de conscience *
              </label>
              <select
                  id="etat_conscience"
                  value={formData.etat_conscience}
                  onChange={(e) => setFormData({ ...formData, etat_conscience: e.target.value as 'NSP' | 'Normal' | 'Altéré' | '' })}
                  className="form-input"
                  required
              >
                <option value="">Sélectionnez</option>
                <option value="NSP">NSP</option>
                <option value="Normal">Normal</option>
                <option value="Altéré">Altéré (apathie, stupeur, coma)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="comportement">
                <i className="fas fa-eye"></i>
                Comportement *
              </label>
              <select
                  id="comportement"
                  value={formData.comportement}
                  onChange={(e) => setFormData({ ...formData, comportement: e.target.value as 'NSP' | 'Normal' | 'Compulsif' | '' })}
                  className="form-input"
                  required
              >
                <option value="">Sélectionnez</option>
                <option value="NSP">NSP</option>
                <option value="Normal">Normal</option>
                <option value="Compulsif">Compulsif (Déambulation, poussé au mur, vocalise, hyperexcitabilité, hagard)</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="convulsions">
              <i className="fas fa-exclamation-circle"></i>
              Convulsions *
            </label>
            <select
                id="convulsions"
                value={formData.convulsions}
                onChange={(e) => setFormData({ ...formData, convulsions: e.target.value as 'Oui' | 'Non' | 'NSP' | '' })}
                className="form-input"
                required
            >
              <option value="">Sélectionnez</option>
              <option value="Oui">Oui</option>
              <option value="Non">Non</option>
              <option value="NSP">NSP</option>
            </select>
          </div>

          {/* Premiers symptômes */}
          <div className="form-group">
            <label htmlFor="symptomes">
              <i className="fas fa-exclamation-triangle"></i>
              Description des premiers symptômes *
            </label>
            <textarea
              id="symptomes"
              value={formData.premiers_symptomes}
              onChange={(e) => setFormData({ ...formData, premiers_symptomes: e.target.value })}
              placeholder="Décrivez en détail les symptômes observés, leur durée, leur évolution..."
              className="form-textarea"
              rows={4}
              required
            />
          </div>

          {/* Examens réalisés */}
          <div className="form-group">
            <label htmlFor="examens">
              <i className="fas fa-clipboard-list"></i>
              Examens réalisés
            </label>
            <textarea
              id="examens"
              value={formData.examens_realises}
              onChange={(e) => setFormData({ ...formData, examens_realises: e.target.value })}
              placeholder="Listez les examens déjà réalisés (prise de sang, radiographies, échographies, IRM, etc.)..."
              className="form-textarea"
              rows={3}
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn-cancel">
              <i className="fas fa-times"></i>
              Annuler
            </button>
            <button type="submit" className="btn-submit" disabled={!isFormValid}>
              <i className="fas fa-paper-plane"></i>
              Commencer la consultation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PreConsultationForm;