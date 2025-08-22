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

const propertyTypes = [
  'Apartment',
  'House',
  'Bungalow'
];

const validationSchema = Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  sum_insured: Yup.number()
    .required('Sum insured is required')
    .min(100000, 'Minimum sum insured should be ₹1,00,000'),
  property_value: Yup.number()
    .required('Property value is required')
    .min(100000, 'Minimum property value should be ₹1,00,000'),
  property_age: Yup.number()
    .required('Property age is required')
    .min(0, 'Property age cannot be negative')
    .max(100, 'Property age cannot exceed 100 years'),
  property_type: Yup.string()
    .required('Property type is required'),
  property_size_sq_feet: Yup.number()
    .required('Property size is required')
    .min(100, 'Minimum size should be 100 sq ft'),
});

const HouseInsuranceForm = () => {
  const navigate = useNavigate();

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      const recommendations = await insuranceService.getRecommendations('house', 'IN', {
        ...values,
        propertyvalue: values.property_value,
        propertyage: values.property_age,
        propertytype: values.property_type,
        propertysizesqfeet: values.property_size_sq_feet,
      });
      navigate('/results', { state: { recommendations, insuranceType: 'house' } });
    } catch (error) {
      console.error('Error submitting form:', error);
      // Handle error appropriately
    }
    setSubmitting(false);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary">
        House Insurance Application
      </Typography>
      
      <Formik
        initialValues={{
          age: '',
          sum_insured: '',
          property_value: '',
          property_age: '',
          property_type: '',
          property_size_sq_feet: '',
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
                id="property_value"
                name="property_value"
                label="Property Value (₹)"
                type="number"
                value={values.property_value}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.property_value && Boolean(errors.property_value)}
                helperText={touched.property_value && errors.property_value}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="property_age"
                name="property_age"
                label="Property Age (Years)"
                type="number"
                value={values.property_age}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.property_age && Boolean(errors.property_age)}
                helperText={touched.property_age && errors.property_age}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                select
                id="property_type"
                name="property_type"
                label="Property Type"
                value={values.property_type}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.property_type && Boolean(errors.property_type)}
                helperText={touched.property_type && errors.property_type}
                sx={{ mb: 2 }}
              >
                {propertyTypes.map((type) => (
                  <MenuItem key={type} value={type.toLowerCase()}>
                    {type}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                fullWidth
                id="property_size_sq_feet"
                name="property_size_sq_feet"
                label="Property Size (sq ft)"
                type="number"
                value={values.property_size_sq_feet}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.property_size_sq_feet && Boolean(errors.property_size_sq_feet)}
                helperText={touched.property_size_sq_feet && errors.property_size_sq_feet}
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

export default HouseInsuranceForm;
