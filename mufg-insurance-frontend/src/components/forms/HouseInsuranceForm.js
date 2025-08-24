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

const propertyTypes = [
  'Apartment',
  'House',
  'Villa',
  'Commercial'
];

const getValidationSchema = (currency) => Yup.object({
  age: Yup.number()
    .required('Age is required')
    .min(18, 'Must be at least 18 years old')
    .max(100, 'Must be less than 100 years old'),
  sum_insured: Yup.number()
    .required('Sum insured is required'),
  propertyvalue: Yup.number()
    .required('Property value is required'),
  propertyage: Yup.number()
    .required('Property age is required')
    .min(0, 'Property age cannot be negative')
    .max(100, 'Property age cannot exceed 100 years'),
  propertytype: Yup.string()
    .required('Property type is required'),
  propertysizesqfeet: Yup.number()
    .required('Property size is required')
    .min(100, 'Minimum size should be 100 sq ft'),
});

const HouseInsuranceForm = () => {
  const navigate = useNavigate();
  const { currency } = useCurrency();

  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    try {
      // Convert values to proper types and match backend field names
      const formattedValues = {
        age: parseInt(values.age),
        suminsured: parseFloat(values.sum_insured),
        propertyvalue: parseFloat(values.propertyvalue),
        propertyage: parseInt(values.propertyage),
        propertytype: values.propertytype.toLowerCase(),
        propertysizesqfeet: parseFloat(values.propertysizesqfeet),
      };

      console.log('Submitting house insurance form with values:', formattedValues);
      const recommendations = await insuranceService.getRecommendations('house', 'IN', formattedValues);
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
          propertyvalue: '',
          propertyage: '',
          propertytype: '',
          propertysizesqfeet: '',
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
                id="sum_insured"
                name="sum_insured"
                label={`Sum Insured (${currency.symbol})`}
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
                id="propertyvalue"
                name="propertyvalue"
                label={`Property Value (${currency.symbol})`}
                type="number"
                value={values.propertyvalue}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.propertyvalue && Boolean(errors.propertyvalue)}
                helperText={touched.propertyvalue && errors.propertyvalue}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                id="propertyage"
                name="propertyage"
                label="Property Age (Years)"
                type="number"
                value={values.propertyage}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.propertyage && Boolean(errors.propertyage)}
                helperText={touched.propertyage && errors.propertyage}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                select
                id="propertytype"
                name="propertytype"
                label="Property Type"
                value={values.propertytype}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.propertytype && Boolean(errors.propertytype)}
                helperText={touched.propertytype && errors.propertytype}
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
                id="propertysizesqfeet"
                name="propertysizesqfeet"
                label="Property Size (sq ft)"
                type="number"
                value={values.propertysizesqfeet}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.propertysizesqfeet && Boolean(errors.propertysizesqfeet)}
                helperText={touched.propertysizesqfeet && errors.propertysizesqfeet}
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
