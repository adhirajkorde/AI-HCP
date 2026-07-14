import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchHCPs = createAsyncThunk(
  'hcps/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/hcps');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch HCPs');
    }
  }
);

export const fetchHCPProfile = createAsyncThunk(
  'hcps/fetchProfile',
  async (hcpId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/hcps/${hcpId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch HCP profile');
    }
  }
);

export const createHCP = createAsyncThunk(
  'hcps/create',
  async (hcpData, { rejectWithValue }) => {
    try {
      const response = await api.post('/hcps', hcpData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create HCP');
    }
  }
);

const initialState = {
  list: [],
  selectedHCP: null, // Holds hcp details, interactions, followups, and ai_insight
  loading: false,
  profileLoading: false,
  error: null,
};

const hcpSlice = createSlice({
  name: 'hcps',
  initialState,
  reducers: {
    clearSelectedHCP: (state) => {
      state.selectedHCP = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch All HCPs
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch HCP Profile Details
      .addCase(fetchHCPProfile.pending, (state) => {
        state.profileLoading = true;
        state.error = null;
      })
      .addCase(fetchHCPProfile.fulfilled, (state, action) => {
        state.profileLoading = false;
        state.selectedHCP = action.payload;
      })
      .addCase(fetchHCPProfile.rejected, (state, action) => {
        state.profileLoading = false;
        state.error = action.payload;
      })
      // Create HCP
      .addCase(createHCP.fulfilled, (state, action) => {
        state.list.push(action.payload);
      });
  },
});

export const { clearSelectedHCP } = hcpSlice.actions;
export default hcpSlice.reducer;
