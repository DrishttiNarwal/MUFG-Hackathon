import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  Alert,
  AlertTitle,
  Button,
  Divider,
} from '@mui/material';
import { useCurrency } from '../context/CurrencyContext';
import { styled } from '@mui/material/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';

const StyledCard = styled(Card)(({ theme, isRecommended }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  border: isRecommended ? `2px solid ${theme.palette.primary.main}` : 'none',
  backgroundColor: isRecommended ? 'rgba(27, 54, 93, 0.02)' : theme.palette.background.paper,
}));

const PriceTag = styled(Typography)(({ theme }) => ({
  color: theme.palette.primary.main,
  fontWeight: 600,
  fontSize: '2rem',
  marginBottom: theme.spacing(2),
  letterSpacing: '-0.02em',
}));

const ConfidenceChip = styled(Chip)(({ theme, confidence }) => ({
  backgroundColor: confidence > 0.7 ? theme.palette.primary.main :
                  confidence > 0.4 ? theme.palette.warning.main :
                  theme.palette.secondary.main,
  color: theme.palette.common.white,
}));

const formatPrice = (price, currencyCode = 'INR') => {
  const locale = currencyCode === 'AUD' ? 'en-AU' : 'en-IN';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
    maximumFractionDigits: 0
  }).format(price);
};

const getInsuranceIcon = (policyType) => {
  switch (policyType?.toLowerCase()) {
    case 'health':
      return <LocalHospitalIcon />;
    case 'vehicle':
      return <DirectionsCarIcon />;
    default:
      return null;
  }
};

const TierCard = ({ tier, price, isRecommended, explanation, confidence }) => {
  const { currency } = useCurrency();
  return (
    <StyledCard isRecommended={isRecommended}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5" component="h2">
            {tier}
          </Typography>
          {isRecommended && (
            <Chip
              icon={<CheckCircleIcon />}
              label="Recommended"
              color="success"
              size="small"
            />
          )}
        </Box>
        <PriceTag>
          {formatPrice(price, currency.code)}
        </PriceTag>
        {confidence > 0 && (
          <ConfidenceChip
            label={`Confidence: ${Math.round(confidence * 100)}%`}
            confidence={confidence}
          />
        )}
        <Typography variant="body2" color="text.secondary" mt={2}>
          {explanation}
        </Typography>
      </CardContent>
    </StyledCard>
  );
};

const RecommendationDisplay = ({ recommendations }) => {
  const { currency, updateCurrency } = useCurrency();
  const pathParts = window.location.pathname.split('/');
  const countryCode = pathParts[2]?.toUpperCase();
  const insuranceType = pathParts[3]?.toLowerCase();

  // Update currency based on URL if needed
  React.useEffect(() => {
    if (countryCode === 'AU') {
      updateCurrency('AU');
      // Store insurance type in localStorage
      localStorage.setItem('insuranceType', insuranceType);
    } else if (countryCode === 'IN') {
      updateCurrency('IN');
      localStorage.setItem('insuranceType', insuranceType);
    }
  }, [countryCode, insuranceType, updateCurrency]);

  // Force currency to be AUD for Australian insurance types
  React.useEffect(() => {
    if (countryCode === 'AU') {
      updateCurrency('AU');
    }
  }, [recommendations, countryCode, updateCurrency]);

  if (!recommendations) {
    return (
      <Alert severity="info" sx={{ mt: 4 }}>
        <AlertTitle>No Recommendations Available</AlertTitle>
        We couldn't generate recommendations at this time. Please check your inputs and try again.
      </Alert>
    );
  }

  // Detect if it's a single or multiple recommendation
  // For single recommendation, wrap it in the same format as multiple
  const recommendationsList = [{ 
    prediction: recommendations.prediction,
    explanation: recommendations.explanation
  }];

  return (
    <Box sx={{ mt: 4 }}>
      {recommendationsList.map((rec, index) => (
        <Box key={index} mb={4}>
          {recommendationsList.length > 1 && (
            <Typography variant="h5" mb={2}>
              Recommendation {index + 1}
              {getInsuranceIcon(rec.prediction?.policytype)}
            </Typography>
          )}

          {/* Warning for low confidence recommendations */}
          {rec.prediction?.confidence?.[rec.prediction.recommended_tier] < 0.5 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <AlertTitle>Low Confidence Recommendation</AlertTitle>
              This recommendation has a low confidence score. Consider reviewing your inputs or consulting with an insurance advisor.
            </Alert>
          )}

          {/* Display tiers in a grid */}
          <Grid container spacing={3}>
            {Object.entries(rec.prediction?.all_tiers || {}).map(([tier, price]) => (
              <Grid item xs={12} sm={6} md={3} key={tier}>
                <TierCard
                  tier={tier}
                  price={price}
                  isRecommended={tier.toLowerCase() === rec.prediction?.recommended_tier?.toLowerCase()}
                  explanation={rec.explanation?.[tier]}
                  confidence={rec.prediction?.confidence?.[tier.toLowerCase()]}
                />
              </Grid>
            ))}
          </Grid>

          {/* Recommendation explanation */}
          {rec.explanation?.why_recommended && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <AlertTitle>Why this is recommended</AlertTitle>
              {rec.explanation.why_recommended}
            </Alert>
          )}

          {recommendationsList.length > 1 && <Divider sx={{ my: 4 }} />}
        </Box>
      ))}
    </Box>
  );
};

export default RecommendationDisplay;
