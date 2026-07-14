import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchFollowUps = createAsyncThunk(
  'followups/fetchAll',
  async (status, { rejectWithValue }) => {
    try {
      const url = status ? `/followups?status=${status}` : '/followups';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch follow-ups');
    }
  }
);

export const updateFollowUpStatus = createAsyncThunk(
  'followups/updateStatus',
  async ({ id, status }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/followups/${id}`, { status });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update follow-up status');
    }
  }
);

const initialState = {
  list: [],
  loading: false,
  error: null,
};

const followupSlice = createSlice({
  name: 'followups',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchFollowUps.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFollowUps.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchFollowUps.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(updateFollowUpStatus.fulfilled, (state, action) => {
        const index = state.list.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) {
          // Update the updated item in place or filter out if viewing pending
          state.list[index] = action.payload;
        }
      });
  },
});

export default followupSlice.reducer;
