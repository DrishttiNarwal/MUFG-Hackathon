import React from 'react';
import { Box, Container, Typography, Grid, Card, CardContent, CardMedia, Button } from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import HomeIcon from '@mui/icons-material/Home';
import FlightIcon from '@mui/icons-material/Flight';
import FavoriteIcon from '@mui/icons-material/Favorite';

const insuranceTypes = [
  {
    id: 'health',
    title: 'Health Insurance',
    description: 'Comprehensive medical coverage for you and your family',
    icon: HealthAndSafetyIcon,
    color: '#4CAF50',
  },
  {
    id: 'life',
    title: 'Life Insurance',
    description: "Secure your family's financial future",
    icon: FavoriteIcon,
    color: '#E91E63',
  },
  {
    id: 'travel',
    title: 'Travel Insurance',
    description: 'Protection for your journeys worldwide',
    icon: FlightIcon,
    color: '#2196F3',
  },
  {
    id: 'house',
    title: 'House Insurance',
    description: 'Protect your home and belongings',
    icon: HomeIcon,
    color: '#FF9800',
  },
  {
    id: 'vehicle',
    title: 'Vehicle Insurance',
    description: 'Coverage for your car and other vehicles',
    icon: DirectionsCarIcon,
    color: '#9C27B0',
  },
];

const InsuranceSelection = () => {
  const navigate = useNavigate();
  const { countryCode } = useParams();

  const handleSelect = (insuranceType) => {
    navigate(`/insurance-form/${countryCode}/${insuranceType}`);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        py: 8,
      }}
    >
      <Container maxWidth="lg">
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
            sx={{ mb: 6 }}
          >
            Choose Your Insurance
          </Typography>
        </motion.div>

        <Grid container spacing={4}>
          {insuranceTypes.map((insurance, index) => {
            const Icon = insurance.icon;
            return (
              <Grid item xs={12} sm={6} md={4} key={insurance.id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      cursor: 'pointer',
                      '&:hover': {
                        transform: 'translateY(-8px)',
                        transition: 'transform 0.3s ease-in-out',
                        boxShadow: '0px 8px 24px rgba(0,0,0,0.1)',
                      },
                    }}
                    onClick={() => handleSelect(insurance.id)}
                  >
                    <Box
                      sx={{
                        p: 3,
                        backgroundColor: `${insurance.color}15`,
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                      }}
                    >
                      <Icon
                        sx={{
                          fontSize: 60,
                          color: insurance.color,
                        }}
                      />
                    </Box>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography variant="h5" gutterBottom component="div">
                        {insurance.title}
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        {insurance.description}
                      </Typography>
                      <Button
                        variant="contained"
                        fullWidth
                        sx={{
                          mt: 2,
                          bgcolor: insurance.color,
                          '&:hover': {
                            bgcolor: insurance.color,
                            filter: 'brightness(0.9)',
                          },
                        }}
                      >
                        Select
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            );
          })}
        </Grid>
      </Container>
    </Box>
  );
};

export default InsuranceSelection;
