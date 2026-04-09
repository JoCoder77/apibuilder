export const getRateForCategory = (countryData: any, category: string) => {
  switch (category) {
    case 'digital_services':
      return countryData.standard;
    case 'food':
    case 'books':
    case 'medicine':
    case 'transport':
      return countryData.reduced_1 || countryData.reduced_2 || countryData.standard;
    case 'accommodation':
      return countryData.reduced_2 || countryData.reduced_1 || countryData.standard;
    default:
      return null;
  }
};

export const getRateTypeForCategory = (category: string) => {
  switch (category) {
    case 'digital_services':
      return 'standard';
    case 'food':
    case 'books':
    case 'medicine':
    case 'transport':
      return 'reduced';
    case 'accommodation':
      return 'reduced';
    default:
      return null;
  }
};