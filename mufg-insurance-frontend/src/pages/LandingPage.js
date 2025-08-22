import React from 'react';
import { Box, Container, Typography, Button, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import SecurityIcon from '@mui/icons-material/Security';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1B365D 0%, #2A5298 100%)',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={6} alignItems="center">
          {/* Left Side - Text + Button */}
          <Grid item xs={12} md={6}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Typography
                variant="h2"
                color="white"
                gutterBottom
                sx={{ fontWeight: 700 }}
              >
                MUFG Shield
              </Typography>
              <Typography
                variant="h5"
                color="white"
                sx={{ mb: 4, opacity: 0.9 }}
              >
                Secure Your Tomorrow with Japan&apos;s Leading Financial Group
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                size="large"
                onClick={() => navigate('/select-country')}
                sx={{
                  fontSize: '1.1rem',
                  py: 1.5,
                  px: 4,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                Protect Your Future
              </Button>
            </motion.div>
          </Grid>

          {/* Right Side - Icon + Illustration */}
          <Grid item xs={12} md={6} sx={{ textAlign: 'center' }}>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 3,
                }}
              >
               

                {/* Illustration */}
                <Box
                  component="img"
                  src="/insurance-illustration.svg"
                  alt="Insurance Protection"
                  sx={{
                    width: '100%',
                    maxWidth: '350px',
                    borderRadius: 4,
                  }}
                />
              </Box>
            </motion.div>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default LandingPage;
