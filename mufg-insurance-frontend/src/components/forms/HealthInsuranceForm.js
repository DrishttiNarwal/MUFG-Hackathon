import React from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { useParams } from 'react-router-dom';
import { useCurrency } from '../../context/CurrencyContext';
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

const HealthInsuranceForm = () => {
  const navigate = useNavigate();
  const { countryCode } = useParams();
  const { currency } = useCurrency();

const getValidationSchema = (currency) => Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  sumassured: Yup.number()
    .required('Sum assured is required')
    .min(100000, `Minimum sum assured should be ${currency.symbol}1,00,000`),
  smokerdrinker: Yup.string()
    .required('Please specify smoking/drinking habits'),
  diseases: Yup.array()
    .min(1, 'Please select at least one option')
    .of(Yup.string())
    .required('Please select any pre-existing conditions'),
});  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    try {
      const formattedValues = {
        age: parseInt(values.age),
        sumassured: parseFloat(values.sumassured),
        smokerdrinker: values.smokerdrinker === 'yes' ? 'Yes' : 'No',
        // Remove 'None' from diseases if it's selected along with other conditions
        diseases: values.diseases.filter(d => d !== 'None' || values.diseases.length === 1).join(','),
      };

      const recommendations = await insuranceService.getRecommendations('HEALTH', countryCode, formattedValues);
      
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
          sumassured: '',
          smokerdrinker: 'no',
          diseases: ['None'],
        }}
        validationSchema={getValidationSchema(currency)}
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
                id="sumassured"
                name="sumassured"
                label={`Sum Assured (${currency.symbol})`}
                type="number"
                value={values.sumassured}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.sumassured && Boolean(errors.sumassured)}
                helperText={touched.sumassured && errors.sumassured}
                sx={{ mb: 2 }}
              />

              <FormControl component="fieldset" sx={{ mb: 2 }}>
                <FormLabel component="legend">Are you a smoker/drinker?</FormLabel>
                <RadioGroup
                  name="smokerdrinker"
                  value={values.smokerdrinker}
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
