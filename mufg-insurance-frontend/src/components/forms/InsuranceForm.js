import React from 'react';
import { useParams } from 'react-router-dom';
import HealthInsuranceForm from './HealthInsuranceForm';
import VehicleInsuranceForm from './VehicleInsuranceForm';
import HouseInsuranceForm from './HouseInsuranceForm';
import TravelInsuranceForm from './TravelInsuranceForm';

const InsuranceForm = () => {
  const { insuranceType } = useParams();

  const renderForm = () => {
    switch (insuranceType) {
      case 'health':
      case 'life':
        return <HealthInsuranceForm />;
      case 'vehicle':
        return <VehicleInsuranceForm />;
      case 'house':
        return <HouseInsuranceForm />;
      case 'travel':
        return <TravelInsuranceForm />;
      default:
        return <div>Invalid insurance type</div>;
    }
  };

  return <div>{renderForm()}</div>;
};

export default InsuranceForm;
