import axios from 'axios';

// Backend URL (gerekirse farklı bir URL veya environment variable kullanılabilir)
const API_BASE_URL = 'http://localhost:8000';

// Boş string değerleri temizleyen fonksiyon
function cleanFilters(filters) {
  return Object.fromEntries(
    Object.entries(filters).filter(([key, value]) => value !== "")
  );
}

/**
 * Belirtilen filtre parametrelerine göre SalarySurvey kayıtlarını getirir.
 * @param {Object} filters - Filtre parametreleri (title, min_company_size, max_company_size, min_experience, max_experience, area, currency, work_area)
 * @returns {Promise<Array>} - SalarySurvey kayıtları dizisi
 */
export async function getSalaries(filters = {}) {
  try {
    const cleanedFilters = cleanFilters(filters);
    const response = await axios.get(`${API_BASE_URL}/salaries`, { params: cleanedFilters });
    return response.data;
  } catch (error) {
    console.error('Error fetching salaries:', error);
    throw error;
  }
}

/**
 * Belirtilen filtre parametrelerine göre maaş aralığı özetini getirir.
 * @param {Object} filters - Filtre parametreleri (title, min_company_size, max_company_size, min_experience, max_experience, area, currency, work_area)
 * @returns {Promise<Array>} - Maaş aralığı özet verisi
 */
export async function getPayRangeSummary(filters = {}) {
  try {
    const cleanedFilters = cleanFilters(filters);
    const response = await axios.get(`${API_BASE_URL}/salaries/pay_range_summary`, { params: cleanedFilters });
    return response.data;
  } catch (error) {
    console.error('Error fetching pay range summary:', error);
    throw error;
  }
}
