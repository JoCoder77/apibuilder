import type { NextApiRequest, NextApiResponse } from 'next';
import data from '../../lib/vat-data';

const vatRates = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.method === 'GET') {
    const country = req.query.country;
    const category = req.query.category;
    const includeNotes = req.query.include_notes === 'true';

    if (country) {
      const countryCode = country.toUpperCase();
      const countryData = data.countries[countryCode];
      if (!countryData) {
        return res.status(404).json({ error: 'Country not found' });
      }

      if (category) {
        const rate = getRateForCategory(countryData, category);
        if (!rate) {
          return res.status(400).json({ error: 'Invalid category' });
        }
        return res.json({
          success: true,
          country: countryCode,
          category,
          rate,
          rateType: getRateTypeForCategory(category),
        });
      }

      const response = {
        success: true,
        country: countryCode,
        name: countryData.name,
        rates: countryData,
        lastUpdated: data.meta.last_updated,
      };
      if (includeNotes && countryData.notes) {
        response.notes = countryData.notes;
      }
      return res.json(response);
    }

    const allCountries = Object.keys(data.countries).map((countryCode) => ({
      country: countryCode,
      name: data.countries[countryCode].name,
      standardRate: data.countries[countryCode].standard,
    }));
    return res.json(allCountries);
  }

  return res.status(405).json({ error: 'Method not allowed' });
};

const getRateForCategory = (countryData: any, category: string) => {
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

const getRateTypeForCategory = (category: string) => {
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

export default vatRates;