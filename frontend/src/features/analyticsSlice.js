import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchDashboardData = createAsyncThunk(
  'analytics/fetchDashboard',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/analytics/dashboard');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard data');
    }
  }
);

export const fetchMetricsData = createAsyncThunk(
  'analytics/fetchMetrics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/analytics/metrics');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch metrics data');
    }
  }
);

const initialState = {
  dashboard: null,
  metrics: null,
  loading: false,
  metricsLoading: false,
  error: null,
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Dashboard Summary
      .addCase(fetchDashboardData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardData.fulfilled, (state, action) => {
        state.loading = false;
        state.dashboard = action.payload;
      })
      .addCase(fetchDashboardData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Detail Metrics / Charts
      .addCase(fetchMetricsData.pending, (state) => {
        state.metricsLoading = true;
        state.error = null;
      })
      .addCase(fetchMetricsData.fulfilled, (state, action) => {
        state.metricsLoading = false;
        state.metrics = action.payload;
      })
      .addCase(fetchMetricsData.rejected, (state, action) => {
        state.metricsLoading = false;
        state.error = action.payload;
      });
  },
});

export default analyticsSlice.reducer;
