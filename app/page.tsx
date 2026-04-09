import type { NextPage } from 'next';
import Head from 'next/head';
import data from '../lib/vat-data';

const Home: NextPage = () => {
  return (
    <div>
      <Head>
        <title>EU VAT Rate Lookup API</title>
      </Head>
      <h1>EU VAT Rate Lookup API</h1>
      <p>This API provides EU VAT rates for all 27 countries.</p>
      <h2>Endpoints</h2>
      <ul>
        <li>
          <code>GET /api/vat-rates</code>: Returns all 27 countries with their standard VAT rates.
        </li>
        <li>
          <code>GET /api/vat-rates?country=DE</code>: Returns the VAT rates for Germany.
        </li>
        <li>
          <code>GET /api/vat-rates?country=DE&category=digital_services</code>: Returns the VAT rate for digital services in Germany.
        </li>
      </ul>
      <h2>Example Responses</h2>
      <pre>
        <code>
          {{
            "success": true,
            "country": "DE",
            "name": "Germany",
            "rates": {
              "standard": 19,
              "reduced_1": null,
              "reduced_2": 7,
              "super_reduced": null,
              "parking": null,
              "zero": 0
            },
            "last_updated": "2026"
          }}
        </code>
      </pre>
      <pre>
        <code>
          {{
            "success": true,
            "country": "DE",
            "category": "digital_services",
            "rate": 19,
            "rate_type": "standard"
          }}
        </code>
      </pre>
      <h2>Table of EU Countries and Standard VAT Rates</h2>
      <table>
        <thead>
          <tr>
            <th>Country</th>
            <th>Standard VAT Rate</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(data.countries).map((countryCode) => (
            <tr key={countryCode}>
              <td>{countryCode}</td>
              <td>{data.countries[countryCode].standard}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        Note: The digital services destination principle applies to all EU countries.
      </p>
    </div>
  );
};

export default Home;