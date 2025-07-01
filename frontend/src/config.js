export const BASE_URL =
  process.env.REACT_APP_ENV === 'prod'
    ? 'https://prod.example.com'
    : process.env.REACT_APP_API_URL;