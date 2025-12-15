const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api/code';

async function generateCode() {
  try {
    console.log('Generating code...\n');

    const response = await axios.post(`${API_BASE_URL}/generate`, {
      prompt: 'Create a function to validate email addresses using regex',
      language: 'javascript',
      maxTokens: 2048,
      temperature: 0.7,
    });

    console.log('Generated Code:');
    console.log('='.repeat(50));
    console.log(response.data.data.code);
    console.log('='.repeat(50));
    console.log('\nExplanation:');
    console.log(response.data.data.explanation);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

generateCode();
