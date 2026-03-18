import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getDatabaseSchema = async () => {
  const response = await api.get('/schema');
  return response.data;
};

export const sendQuery = async (question, selectedTables = []) => {
  const response = await api.post('/query', { 
    question,
    selected_tables: selectedTables 
  });
  return response.data;
};

export default api;
