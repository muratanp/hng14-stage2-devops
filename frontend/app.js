const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

const API_URL = process.env.API_URL || 'http://api:8000';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to submit job' });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    const status = err.response ? err.response.status : 500;
    res.status(status).json({ error: 'Failed to fetch job status' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
});
