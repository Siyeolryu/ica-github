const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api/code';

async function analyzeCode() {
  try {
    console.log('Analyzing code...\n');

    const codeToAnalyze = `
function processData(data) {
  for (var i = 0; i < data.length; i++) {
    console.log(data[i]);
    var result = data[i] * 2;
    setTimeout(function() {
      console.log(result);
    }, 100);
  }
}
    `.trim();

    const response = await axios.post(`${API_BASE_URL}/analyze`, {
      code: codeToAnalyze,
      language: 'javascript',
      analysisType: 'bugs',
    });

    console.log('Analysis Results:');
    console.log('='.repeat(50));
    console.log(response.data.data.analysis);
    console.log('='.repeat(50));
    console.log('\nSuggestions:');
    response.data.data.suggestions.forEach((suggestion, index) => {
      console.log(`${index + 1}. ${suggestion}`);
    });
    console.log(`\nSeverity: ${response.data.data.severity}`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

analyzeCode();
