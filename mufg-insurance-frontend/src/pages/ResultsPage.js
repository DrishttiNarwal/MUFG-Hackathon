import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import RecommendationDisplay from '../components/RecommendationDisplay';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { recommendations, insuranceType, userInput } = location.state || {};

  if (!recommendations) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h5" color="error" gutterBottom>
          No recommendations found
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate('/')}
        >
          Return Home
        </Button>
      </Box>
    );
  }

  const { prediction, explanation } = recommendations;

  const formatValue = (value) => {
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (Array.isArray(value)) return value.join(', ');
    return value?.toString() || '';
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom color="primary">
          Insurance Recommendations
        </Typography>
        
        <RecommendationDisplay 
          recommendations={recommendations}
          insuranceType={insuranceType}
        />

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Your Information
          </Typography>
          <List>
            {Object.entries(userInput || {}).map(([key, value]) => (
              <ListItem key={key}>
                <ListItemText
                  primary={key.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                  secondary={Array.isArray(value) 
                    ? value.join(', ') 
                    : formatValue(value)}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ResultsPage;
