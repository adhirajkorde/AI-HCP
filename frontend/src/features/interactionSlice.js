import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const logStructuredInteraction = createAsyncThunk(
  'interactions/logStructured',
  async (interactionData, { rejectWithValue }) => {
    try {
      const response = await api.post('/interactions', interactionData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to log interaction');
    }
  }
);

export const analyzeConversationalText = createAsyncThunk(
  'interactions/analyzeConversational',
  async (text, { rejectWithValue }) => {
    try {
      const response = await api.post('/interactions/ai', { text });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to analyze text');
    }
  }
);

export const confirmAIInteraction = createAsyncThunk(
  'interactions/confirmAI',
  async (interactionData, { rejectWithValue }) => {
    try {
      const response = await api.post('/interactions/ai/confirm', interactionData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to confirm interaction');
    }
  }
);

const initialState = {
  recent: [],
  aiExtraction: null, // Holds parsed entities from LangGraph
  loading: false,
  aiLoading: false,
  error: null,
};

const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    clearAIExtraction: (state) => {
      state.aiExtraction = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Log Structured Interaction
      .addCase(logStructuredInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(logStructuredInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.recent.unshift(action.payload);
      })
      .addCase(logStructuredInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Analyze Conversational Text (LangGraph Agent)
      .addCase(analyzeConversationalText.pending, (state) => {
        state.aiLoading = true;
        state.error = null;
        state.aiExtraction = null;
      })
      .addCase(analyzeConversationalText.fulfilled, (state, action) => {
        state.aiLoading = false;
        state.aiExtraction = action.payload;
      })
      .addCase(analyzeConversationalText.rejected, (state, action) => {
        state.aiLoading = false;
        state.error = action.payload;
      })
      // Confirm and Sync AI Interaction
      .addCase(confirmAIInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmAIInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.aiExtraction = null;
        state.recent.unshift(action.payload);
      })
      .addCase(confirmAIInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearAIExtraction } = interactionSlice.actions;
export default interactionSlice.reducer;
