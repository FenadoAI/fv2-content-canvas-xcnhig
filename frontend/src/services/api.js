import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API = `${API_BASE}/api`;

// Configure axios defaults
axios.defaults.baseURL = API;

// Add token to requests
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// ===== AUTH APIS =====

export const register = async (email, password, name) => {
  try {
    const response = await axios.post('/auth/register', { email, password, name });
    return response.data;
  } catch (error) {
    return { success: false, error: error.response?.data?.detail || 'Registration failed' };
  }
};

export const login = async (email, password) => {
  try {
    const response = await axios.post('/auth/login', { email, password });
    return response.data;
  } catch (error) {
    return { success: false, error: error.response?.data?.detail || 'Login failed' };
  }
};

export const googleAuth = async (token) => {
  try {
    const response = await axios.post('/auth/google', { token });
    return response.data;
  } catch (error) {
    return { success: false, error: error.response?.data?.detail || 'Google auth failed' };
  }
};

export const getCurrentUser = async () => {
  const response = await axios.get('/auth/me', { headers: getAuthHeader() });
  return response.data;
};

// ===== ARTICLE APIS =====

export const getArticles = async (params = {}) => {
  const response = await axios.get('/articles', { params });
  return response.data;
};

export const getArticle = async (id) => {
  const response = await axios.get(`/articles/${id}`);
  return response.data;
};

export const createArticle = async (data) => {
  const response = await axios.post('/articles', data, { headers: getAuthHeader() });
  return response.data;
};

export const updateArticle = async (id, data) => {
  const response = await axios.put(`/articles/${id}`, data, { headers: getAuthHeader() });
  return response.data;
};

export const deleteArticle = async (id) => {
  const response = await axios.delete(`/articles/${id}`, { headers: getAuthHeader() });
  return response.data;
};

export const publishArticle = async (id) => {
  const response = await axios.put(`/articles/${id}/publish`, {}, { headers: getAuthHeader() });
  return response.data;
};

export const likeArticle = async (id) => {
  const response = await axios.post(`/articles/${id}/like`, {}, { headers: getAuthHeader() });
  return response.data;
};

export const getTrendingArticles = async (limit = 10) => {
  const response = await axios.get('/articles/trending/list', { params: { limit } });
  return response.data;
};

export const getFeaturedArticles = async (limit = 10) => {
  const response = await axios.get('/articles/featured/list', { params: { limit } });
  return response.data;
};

// ===== COMMENT APIS =====

export const getComments = async (articleId) => {
  const response = await axios.get(`/comments/${articleId}`);
  return response.data;
};

export const createComment = async (data) => {
  const response = await axios.post('/comments', data, { headers: getAuthHeader() });
  return response.data;
};

export const getPendingComments = async (articleId = null) => {
  const params = articleId ? { article_id: articleId } : {};
  const response = await axios.get('/comments/pending/list', {
    params,
    headers: getAuthHeader()
  });
  return response.data;
};

export const approveComment = async (id) => {
  const response = await axios.put(`/comments/${id}/approve`, {}, { headers: getAuthHeader() });
  return response.data;
};

export const deleteComment = async (id) => {
  const response = await axios.delete(`/comments/${id}`, { headers: getAuthHeader() });
  return response.data;
};

// ===== USER APIS =====

export const getUsers = async () => {
  const response = await axios.get('/users', { headers: getAuthHeader() });
  return response.data;
};

export const getUser = async (id) => {
  const response = await axios.get(`/users/${id}`);
  return response.data;
};

export const updateUserRole = async (id, role) => {
  const response = await axios.put(`/users/${id}/role`, { role }, { headers: getAuthHeader() });
  return response.data;
};

// ===== SETTINGS APIS =====

export const getSetting = async (key) => {
  const response = await axios.get(`/settings/${key}`);
  return response.data;
};

export const updateSetting = async (key, value) => {
  const response = await axios.put(`/settings/${key}`, { value }, { headers: getAuthHeader() });
  return response.data;
};

export { API_BASE, API };
