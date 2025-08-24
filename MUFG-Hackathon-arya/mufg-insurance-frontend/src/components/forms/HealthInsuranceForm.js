import React from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  Typography,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Grid,
  Chip,
  Autocomplete,
  MenuItem,
  Select,
  FormHelperText,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import insuranceService from '../../services/api';

const diseases = [
  'None',
  'Diabetes',
  'Heart Disease',
  'Hypertension',
  'Asthma',
  'Cancer',
  'Others'
];

const validationSchema = Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  sum_assured: Yup.number()
    .required('Sum assured is required')
    .min(100000, 'Minimum sum assured should be ₹1,00,000'),
  smoker_drinker: Yup.string()
    .required('Please specify smoking/drinking habits'),
  diseases: Yup.array()
    .min(1, 'Please select at least one option')
    .of(Yup.string())
    .required('Please select any pre-existing conditions'),
});

const HealthInsuranceForm = () => {
  const navigate = useNavigate();

  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    try {
      const formattedValues = {
        ...values,
        smoker_drinker: values.smoker_drinker === 'yes' ? 'Yes' : 'No',
        // Remove 'None' from diseases if it's selected along with other conditions
        diseases: values.diseases.filter(d => d !== 'None' || values.diseases.length === 1),
      };

      const recommendations = await insuranceService.getRecommendations('HEALTH', 'INDIA', formattedValues);
      
      if (recommendations.prediction) {
        navigate('/results', { 
          state: { 
            recommendations,
            insuranceType: 'health',
            userInput: formattedValues
          } 
        });
      } else {
        setStatus({ error: 'Failed to get recommendations. Please try again.' });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setStatus({ 
        error: error.response?.data?.detail || 'Failed to get recommendations. Please try again.' 
      });
    }
    setSubmitting(false);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary">
        Health Insurance Application
      </Typography>
      
      <Formik
        initialValues={{
          age: '',
          sum_assured: '',
          smoker_drinker: 'no',
          diseases: ['None'],
        }}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        {({ values, errors, touched, handleChange, handleBlur, isSubmitting, status }) => (
          <Form>
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                id="age"
                name="age"
                label="Age"
                type="number"
                value={values.age}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.age && Boolean(errors.age)}
                helperText={touched.age && errors.age}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="sum_assured"
                name="sum_assured"
                label="Sum Assured (₹)"
                type="number"
                value={values.sum_assured}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.sum_assured && Boolean(errors.sum_assured)}
                helperText={touched.sum_assured && errors.sum_assured}
                sx={{ mb: 2 }}
              />

              <FormControl component="fieldset" sx={{ mb: 2 }}>
                <FormLabel component="legend">Are you a smoker/drinker?</FormLabel>
                <RadioGroup
                  name="smoker_drinker"
                  value={values.smoker_drinker}
                  onChange={handleChange}
                >
                  <FormControlLabel value="no" control={<Radio />} label="No" />
                  <FormControlLabel value="yes" control={<Radio />} label="Yes" />
                </RadioGroup>
              </FormControl>

              <FormControl fullWidth error={touched.diseases && Boolean(errors.diseases)}>
                <FormLabel>Pre-existing Conditions</FormLabel>
                <Select
                  multiple
                  id="diseases"
                  name="diseases"
                  value={values.diseases}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {diseases.map((disease) => (
                    <MenuItem key={disease} value={disease}>
                      {disease}
                    </MenuItem>
                  ))}
                </Select>
                {touched.diseases && errors.diseases && (
                  <FormHelperText>{errors.diseases}</FormHelperText>
                )}
              </FormControl>
            </Box>

            {status && status.error && (
              <Typography color="error" sx={{ mt: 2, mb: 2 }}>
                {status.error}
              </Typography>
            )}
            
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={isSubmitting}
              size="large"
            >
              {isSubmitting ? 'Getting Recommendations...' : 'Get Recommendations'}
            </Button>
          </Form>
        )}
      </Formik>
    </Box>
  );
};

export default HealthInsuranceForm;
