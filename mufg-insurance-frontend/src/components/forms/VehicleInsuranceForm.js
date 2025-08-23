import React from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Typography,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import insuranceService from '../../services/api';

const vehicleTypes = [
  'Car',
  'Three Wheeler',
  'Bike',
  'Truck',
  'Luxury'
];

// Mapping of frontend vehicle types to backend types
const vehicleTypeMapping = {
  'car': 'car',
  'three wheeler': 'three wheeler',
  'bike': 'bike',
  'truck': 'truck',
  'luxury': 'luxury'
};

const validationSchema = Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  price_of_vehicle: Yup.number()
    .required('Vehicle price is required')
    .min(10000, 'Minimum vehicle price should be ₹10,000'),
  age_of_vehicle: Yup.number()
    .required('Vehicle age is required')
    .min(0, 'Vehicle age cannot be negative')
    .max(25, 'Vehicle age cannot exceed 25 years'),
  type_of_vehicle: Yup.string()
    .required('Vehicle type is required'),
});

const VehicleInsuranceForm = () => {
  const navigate = useNavigate();

  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    try {
      console.log('Starting form submission with values:', values);
      const countryCode = window.localStorage.getItem('selectedCountry') || 'IN';
      console.log('Country code:', countryCode);

      // Check if backend is available first
      try {
        await insuranceService.healthCheck();
      } catch (healthError) {
        console.error('Health check failed:', healthError);
        throw new Error('Cannot connect to server. Please ensure the backend server is running.');
      }

      const formattedData = {
        ...values,
        price_of_vehicle: parseFloat(values.price_of_vehicle),
        age_of_vehicle: parseInt(values.age_of_vehicle),
        type_of_vehicle: vehicleTypeMapping[values.type_of_vehicle.toLowerCase()] || 'car',
        age: parseInt(values.age)
      };
      console.log('Formatted data:', formattedData);

      // Add retry logic
      let retryCount = 0;
      const maxRetries = 3;
      let recommendations;

      while (retryCount < maxRetries) {
        try {
          recommendations = await insuranceService.getRecommendations('VEHICLE', countryCode, formattedData);
          console.log('Received recommendations:', recommendations);
          break; // Success, exit loop
        } catch (apiError) {
          retryCount++;
          if (retryCount === maxRetries) {
            throw apiError; // Last retry failed
          }
          console.log(`Retry attempt ${retryCount} of ${maxRetries}`);
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount)); // Exponential backoff
        }
      }

      if (!recommendations) {
        throw new Error('No recommendations received from server');
      }

      navigate('/results', { 
        state: { 
          recommendations, 
          insuranceType: 'vehicle',
          userInput: formattedData 
        } 
      });
    } catch (error) {
      console.error('Error submitting form:', error);
      setStatus({
        error: error.message || 'Failed to get recommendations. Please try again.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary">
        Vehicle Insurance Application
      </Typography>
      
      <Formik
        initialValues={{
          age: '',
          price_of_vehicle: '',
          age_of_vehicle: '',
          type_of_vehicle: '',
        }}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        {({ values, errors, touched, handleChange, handleBlur, isSubmitting, status }) => (
          <Form>
            {status && status.error && (
              <Box sx={{ mb: 2 }}>
                <Typography color="error" variant="body2">
                  {status.error}
                </Typography>
              </Box>
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
                id="price_of_vehicle"
                name="price_of_vehicle"
                label="Vehicle Price (₹)"
                type="number"
                value={values.price_of_vehicle}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.price_of_vehicle && Boolean(errors.price_of_vehicle)}
                helperText={touched.price_of_vehicle && errors.price_of_vehicle}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="age_of_vehicle"
                name="age_of_vehicle"
                label="Vehicle Age (Years)"
                type="number"
                value={values.age_of_vehicle}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.age_of_vehicle && Boolean(errors.age_of_vehicle)}
                helperText={touched.age_of_vehicle && errors.age_of_vehicle}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                select
                id="type_of_vehicle"
                name="type_of_vehicle"
                label="Vehicle Type"
                value={values.type_of_vehicle}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.type_of_vehicle && Boolean(errors.type_of_vehicle)}
                helperText={touched.type_of_vehicle && errors.type_of_vehicle}
              >
                {vehicleTypes.map((type) => (
                  <MenuItem key={type} value={type.toLowerCase()}>
                    {type}
                  </MenuItem>
                ))}
              </TextField>
            </Box>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={isSubmitting}
              size="large"
            >
              Calculate IDV & Get Recommendations
            </Button>
          </Form>
        )}
      </Formik>
    </Box>
  );
};

export default VehicleInsuranceForm;
