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
  Typography,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import insuranceService from '../../services/api';

const validationSchema = Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  sum_insured: Yup.number()
    .required('Sum insured is required')
    .min(100000, 'Minimum sum insured should be ₹1,00,000'),
  destination_country: Yup.string()
    .required('Destination country is required')
    .min(2, 'Please enter a valid country name'),
  trip_duration_days: Yup.number()
    .required('Trip duration is required')
    .min(1, 'Minimum duration is 1 day')
    .max(180, 'Maximum duration is 180 days'),
  existing_medical_condition: Yup.string()
    .required('Please specify if you have any existing medical conditions'),
  health_coverage: Yup.string()
    .required('Please specify if you want health coverage'),
  baggage_coverage: Yup.string()
    .required('Please specify if you want baggage coverage'),
  trip_cancellation_coverage: Yup.string()
    .required('Please specify if you want trip cancellation coverage'),
  accident_coverage: Yup.string()
    .required('Please specify if you want accident coverage'),
});

const TravelInsuranceForm = () => {
  const navigate = useNavigate();

  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    try {
      console.log('Submitting travel insurance form with values:', values);
      
      const formattedValues = {
        ...values,
        destination_country: values.destination_country,
        trip_duration_days: parseInt(values.trip_duration_days),
        existing_medical_condition: values.existing_medical_condition === 'yes' ? 'Yes' : 'No',
        health_coverage: values.health_coverage === 'yes' ? 'Yes' : 'No',
        baggage_coverage: values.baggage_coverage === 'yes' ? 'Yes' : 'No',
        trip_cancellation_coverage: values.trip_cancellation_coverage === 'yes' ? 'Yes' : 'No',
        accident_coverage: values.accident_coverage === 'yes' ? 'Yes' : 'No',
        sum_assured: parseFloat(values.sum_insured)  // Convert to match backend expectations
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
          sum_insured: '',
          destination_country: '',
          trip_duration_days: '',
          existing_medical_condition: 'no',
          health_coverage: 'yes',
          baggage_coverage: 'yes',
          trip_cancellation_coverage: 'yes',
          accident_coverage: 'yes',
        }}
        validationSchema={validationSchema}
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
                id="sum_insured"
                name="sum_insured"
                label="Sum Insured (₹)"
                type="number"
                value={values.sum_insured}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.sum_insured && Boolean(errors.sum_insured)}
                helperText={touched.sum_insured && errors.sum_insured}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="destination_country"
                name="destination_country"
                label="Destination Country"
                value={values.destination_country}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.destination_country && Boolean(errors.destination_country)}
                helperText={touched.destination_country && errors.destination_country}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="trip_duration_days"
                name="trip_duration_days"
                label="Trip Duration (Days)"
                type="number"
                value={values.trip_duration_days}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.trip_duration_days && Boolean(errors.trip_duration_days)}
                helperText={touched.trip_duration_days && errors.trip_duration_days}
                sx={{ mb: 2 }}
              />

              <RadioOption
                label="Do you have any existing medical conditions?"
                name="existing_medical_condition"
                value={values.existing_medical_condition}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.existing_medical_condition}
                touched={touched.existing_medical_condition}
              />

              <RadioOption
                label="Do you want health coverage?"
                name="health_coverage"
                value={values.health_coverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.health_coverage}
                touched={touched.health_coverage}
              />

              <RadioOption
                label="Do you want baggage coverage?"
                name="baggage_coverage"
                value={values.baggage_coverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.baggage_coverage}
                touched={touched.baggage_coverage}
              />

              <RadioOption
                label="Do you want trip cancellation coverage?"
                name="trip_cancellation_coverage"
                value={values.trip_cancellation_coverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.trip_cancellation_coverage}
                touched={touched.trip_cancellation_coverage}
              />

              <RadioOption
                label="Do you want accident coverage?"
                name="accident_coverage"
                value={values.accident_coverage}
                handleChange={handleChange}
                handleBlur={handleBlur}
                error={errors.accident_coverage}
                touched={touched.accident_coverage}
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
