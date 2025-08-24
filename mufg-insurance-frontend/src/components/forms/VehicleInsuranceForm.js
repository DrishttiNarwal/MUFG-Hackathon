import React from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { useCurrency } from '../../context/CurrencyContext';
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

const getValidationSchema = (currency) => Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  priceofvehicle: Yup.number()
    .required('Vehicle price is required')
    .min(10000, `Minimum vehicle price should be ${currency.symbol}10,000`),
  ageofvehicle: Yup.number()
    .required('Vehicle age is required')
    .min(0, 'Vehicle age cannot be negative')
    .max(25, 'Vehicle age cannot exceed 25 years'),
  typeofvehicle: Yup.string()
    .required('Vehicle type is required'),
});

const VehicleInsuranceForm = () => {
  const navigate = useNavigate();
  const { currency } = useCurrency();

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      // Map vehicle types to backend expected values
      const vehicleTypeMap = {
        'car': 'car',
        'three wheeler': '2wheeler',
        'bike': '2wheeler',
        'truck': 'commercial',
        'luxury': 'suv'
      };

      const recommendations = await insuranceService.getRecommendations('vehicle', 'IN', {
        age: values.age,
        priceofvehicle: values.priceofvehicle,
        ageofvehicle: values.ageofvehicle,
        typeofvehicle: vehicleTypeMap[values.typeofvehicle] || 'car',
      });
      navigate('/results', { state: { recommendations, insuranceType: 'vehicle' } });
    } catch (error) {
      console.error('Error submitting form:', error);
      // Handle error appropriately
    }
    setSubmitting(false);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary">
        Vehicle Insurance Application
      </Typography>
      
      <Formik
        initialValues={{
          age: '',
          priceofvehicle: '',
          ageofvehicle: '',
          typeofvehicle: '',
        }}
        validationSchema={getValidationSchema(currency)}
        onSubmit={handleSubmit}
      >
        {({ values, errors, touched, handleChange, handleBlur, isSubmitting }) => (
          <Form>
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
                id="priceofvehicle"
                name="priceofvehicle"
                label={`Vehicle Price (${currency.symbol})`}
                type="number"
                value={values.priceofvehicle}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.priceofvehicle && Boolean(errors.priceofvehicle)}
                helperText={touched.priceofvehicle && errors.priceofvehicle}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="ageofvehicle"
                name="ageofvehicle"
                label="Vehicle Age (Years)"
                type="number"
                value={values.ageofvehicle}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.ageofvehicle && Boolean(errors.ageofvehicle)}
                helperText={touched.ageofvehicle && errors.ageofvehicle}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                select
                id="typeofvehicle"
                name="typeofvehicle"
                label="Vehicle Type"
                value={values.typeofvehicle}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.typeofvehicle && Boolean(errors.typeofvehicle)}
                helperText={touched.typeofvehicle && errors.typeofvehicle}
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
