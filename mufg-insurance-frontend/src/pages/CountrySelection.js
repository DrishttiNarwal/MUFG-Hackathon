import React from 'react';
import { Box, Container, Typography, Button, Grid, Card, CardContent } from '@mui/material';
import { useCurrency } from '../context/CurrencyContext';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import PublicIcon from '@mui/icons-material/Public';

const countries = [
  {
    name: 'India',
    flag: '🇮🇳',
    code: 'IN',
  },
  {
    name: 'Australia',
    flag: '🇦🇺',
    code: 'AU',
  },
];

const CountrySelection = () => {
  const navigate = useNavigate();
  const { updateCurrency } = useCurrency();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        py: 8,
      }}
    >
      <Container maxWidth="md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography
            variant="h2"
            align="center"
            gutterBottom
            color="primary"
            sx={{ mb: 4 }}
          >
            <PublicIcon sx={{ fontSize: 40, verticalAlign: 'middle', mr: 2 }} />
            Select Your Country
          </Typography>
        </motion.div>

        <Grid container spacing={4} justifyContent="center">
          {countries.map((country, index) => (
            <Grid item xs={12} sm={6} key={country.code}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
              >
                <Card
                  sx={{
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      transition: 'transform 0.3s ease-in-out',
                      boxShadow: '0px 8px 24px rgba(0,0,0,0.1)',
                    },
                  }}
                  onClick={() => {
                    updateCurrency(country.code);
                    navigate(`/insurance-selection/${country.code}`);
                  }}
                >
                  <CardContent>
                    <Typography variant="h1" align="center" sx={{ fontSize: '5rem', mb: 2 }}>
                      {country.flag}
                    </Typography>
                    <Typography variant="h4" align="center" gutterBottom>
                      {country.name}
                    </Typography>
                    <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      sx={{ mt: 2 }}
                    >
                      Select {country.name}
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default CountrySelection;
