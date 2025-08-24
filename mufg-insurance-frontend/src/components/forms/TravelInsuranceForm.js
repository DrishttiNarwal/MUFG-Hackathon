import React from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
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
  Typography,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import insuranceService from '../../services/api';

const getValidationSchema = (currency) => Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  sumassured: Yup.number()
    .required('Sum assured is required')
    .min(100000, `Minimum sum assured should be ${currency.symbol}1,00,000`),
  destinationcountry: Yup.string()
    .required('Destination country is required')
    .min(2, 'Please enter a valid country name'),
  tripdurationdays: Yup.number()
    .required('Trip duration is required')
    .min(1, 'Minimum duration is 1 day')
    .max(180, 'Maximum duration is 180 days'),
  existingmedicalcondition: Yup.string()
    .required('Please specify if you have any existing medical conditions'),
  healthcoverage: Yup.string()
    .required('Please specify if you want health coverage'),
  baggagecoverage: Yup.string()
    .required('Please specify if you want baggage coverage'),
  tripcancellationcoverage: Yup.string()
    .required('Please specify if you want trip cancellation coverage'),
  accidentcoverage: Yup.string()
    .required('Please specify if you want accident coverage'),
});

const TravelInsuranceForm = () => {
  const navigate = useNavigate();
  const { currency } = useCurrency();

  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    try {
      console.log('Submitting travel insurance form with values:', values);
      
      const formattedValues = {
        age: parseInt(values.age),
        destinationcountry: values.destinationcountry,
        tripdurationdays: parseInt(values.tripdurationdays),
        existingmedicalcondition: values.existingmedicalcondition === 'yes' ? 'Yes' : 'No',
        // Map coverage values to tiers
        healthcoverage: values.healthcoverage === 'yes' ? 'Standard' : 'Basic',
        baggagecoverage: values.baggagecoverage === 'yes' ? 'Standard' : 'Basic',
        tripcancellationcoverage: values.tripcancellationcoverage === 'yes' ? 'Yes' : 'No',
        accidentcoverage: values.accidentcoverage === 'yes' ? 'Standard' : 'Basic',
        sumassured: parseFloat(values.sumassured)
      };

      console.log('Calling API with formatted values:', formattedValues);
      const recommendations = await insuranceService.getRecommendations('TRAVEL', 'INDIA', formattedValues);
      
      console.log('Received recommendations:', recommendations);
      if (recommendations) {
        navigate('/results', { 
          state: { 
            recommendations,
            insuranceType: 'travel',
            userInput: formattedValues
          } 
        });
      } else {
        setStatus({ error: 'No recommendations received from server' });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setStatus({ 
        error: error.message || 'Failed to get recommendations. Please try again.' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  const RadioOption = ({ label, name, value, handleChange, handleBlur, error, touched }) => (
    <FormControl component="fieldset" sx={{ mb: 2 }} error={touched && Boolean(error)}>
      <FormLabel component="legend">{label}</FormLabel>
      <RadioGroup
        name={name}
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
      >
        <FormControlLabel value="yes" control={<Radio />} label="Yes" />
        <FormControlLabel value="no" control={<Radio />} label="No" />
      </RadioGroup>
      {touched && error && (
        <Typography color="error" variant="caption">
          {error}
        </Typography>
      )}
    </FormControl>
  );

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary">
        Travel Insurance Application
      </Typography>
      
      <Formik
        initialValues={{
          age: '',
          sumassured: '',
          destinationcountry: '',
          tripdurationdays: '',
          existingmedicalcondition: 'no',
          healthcoverage: 'yes',
          baggagecoverage: 'yes',
          tripcancellationcoverage: 'yes',
          accidentcoverage: 'yes',
        }}
        validationSchema={getValidationSchema(currency)}
        onSubmit={handleSubmit}
      >
        {({ values, errors, touched, handleChange, handleBlur, isSubmitting, status: formStatus }) => (
          <Form>
            {/* Display form-level errors */}
            {formStatus && formStatus.error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {formStatus.error}
              </Alert>
            )}
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                id="age"
                name="age"
                label="Your Age"
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

              <TextField
                fullWidth
                id="destinationcountry"
                name="destinationcountry"
                label="Destination Country"
                value={values.destinationcountry}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.destinationcountry && Boolean(errors.destinationcountry)}
                helperText={touched.destinationcountry && errors.destinationcountry}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="tripdurationdays"
                name="tripdurationdays"
                label="Trip Duration (Days)"
                type="number"
                value={values.tripdurationdays}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.tripdurationdays && Boolean(errors.tripdurationdays)}
                helperText={touched.tripdurationdays && errors.tripdurationdays}
                sx={{ mb: 2 }}
              />

              <RadioOption
                label="Do you have any existing medical conditions?"
                name="existingmedicalcondition"
                value={values.existingmedicalcondition}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.existingmedicalcondition}
                touched={touched.existingmedicalcondition}
              />

              <RadioOption
                label="Do you want health coverage?"
                name="healthcoverage"
                value={values.healthcoverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.healthcoverage}
                touched={touched.healthcoverage}
              />

              <RadioOption
                label="Do you want baggage coverage?"
                name="baggagecoverage"
                value={values.baggagecoverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.baggagecoverage}
                touched={touched.baggagecoverage}
              />

              <RadioOption
                label="Do you want trip cancellation coverage?"
                name="tripcancellationcoverage"
                value={values.tripcancellationcoverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.tripcancellationcoverage}
                touched={touched.tripcancellationcoverage}
              />

              <RadioOption
                label="Do you want accident coverage?"
                name="accidentcoverage"
                value={values.accidentcoverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.accidentcoverage}
                touched={touched.accidentcoverage}
              />
            </Box>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={isSubmitting}
              size="large"
            >
              Get Recommendations
            </Button>
          </Form>
        )}
      </Formik>
    </Box>
  );
};

export default TravelInsuranceForm;
