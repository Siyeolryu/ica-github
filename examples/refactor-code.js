const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api/code';

async function refactorCode() {
  try {
    console.log('Refactoring code...\n');

    const codeToRefactor = `
function calculate(a, b, c) {
  var result = 0;
  if (c == 'add') {
    result = a + b;
  } else if (c == 'subtract') {
    result = a - b;
  } else if (c == 'multiply') {
    result = a * b;
  } else if (c == 'divide') {
    result = a / b;
  }
  return result;
}
    `.trim();

    const response = await axios.post(`${API_BASE_URL}/refactor`, {
      code: codeToRefactor,
      language: 'javascript',
      instructions: 'Use modern ES6+ syntax, implement better patterns, and improve maintainability',
    });

    console.log('Original Code:');
    console.log('='.repeat(50));
    console.log(response.data.data.originalCode);
    console.log('='.repeat(50));
    console.log('\nRefactored Code:');
    console.log('='.repeat(50));
    console.log(response.data.data.refactoredCode);
    console.log('='.repeat(50));
    console.log('\nChanges Made:');
    response.data.data.changes.forEach((change, index) => {
      console.log(`${index + 1}. ${change}`);
    });
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

refactorCode();
