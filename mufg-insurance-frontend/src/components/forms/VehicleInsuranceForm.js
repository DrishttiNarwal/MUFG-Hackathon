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

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      const recommendations = await insuranceService.getRecommendations('vehicle', 'IN', {
        ...values,
        priceofvehicle: values.price_of_vehicle,
        ageofvehicle: values.age_of_vehicle,
        typeofvehicle: values.type_of_vehicle,
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
          price_of_vehicle: '',
          age_of_vehicle: '',
          type_of_vehicle: '',
        }}
        validationSchema={validationSchema}
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
