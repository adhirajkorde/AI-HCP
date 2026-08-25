import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// AI Action Center
export const fetchAIActionCenter = createAsyncThunk(
  'automation/fetchAIActionCenter',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/action-center');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch AI Action Center');
    }
  }
);

// Approvals
export const fetchApprovals = createAsyncThunk(
  'automation/fetchApprovals',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/approvals');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch approvals');
    }
  }
);

export const approveRequest = createAsyncThunk(
  'automation/approveRequest',
  async ({ id, decision_reason }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/automation/approvals/${id}`, { status: 'approved', decision_reason });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to approve request');
    }
  }
);

export const rejectRequest = createAsyncThunk(
  'automation/rejectRequest',
  async ({ id, decision_reason }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/automation/approvals/${id}`, { status: 'rejected', decision_reason });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to reject request');
    }
  }
);

// Notifications
export const fetchNotifications = createAsyncThunk(
  'automation/fetchNotifications',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/notifications');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch notifications');
    }
  }
);

export const markNotificationRead = createAsyncThunk(
  'automation/markNotificationRead',
  async (notificationId, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/automation/notifications/${notificationId}/read`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to mark notification as read');
    }
  }
);

export const markAllNotificationsRead = createAsyncThunk(
  'automation/markAllNotificationsRead',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.post('/automation/notifications/read-all');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to mark all notifications as read');
    }
  }
);

// Email Drafts
export const fetchEmailDrafts = createAsyncThunk(
  'automation/fetchEmailDrafts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/email-drafts');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch email drafts');
    }
  }
);

export const sendEmailDraft = createAsyncThunk(
  'automation/sendEmailDraft',
  async (draftId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/automation/email-drafts/${draftId}/send`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to send email draft');
    }
  }
);

// Automation Events
export const fetchAutomationEvents = createAsyncThunk(
  'automation/fetchEvents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/events');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch automation events');
    }
  }
);

export const processAutomationEvents = createAsyncThunk(
  'automation/processEvents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.post('/automation/events/process-pending');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to process events');
    }
  }
);

// Documents
export const fetchDocuments = createAsyncThunk(
  'automation/fetchDocuments',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/documents');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch documents');
    }
  }
);

export const uploadDocument = createAsyncThunk(
  'automation/uploadDocument',
  async (formData, { rejectWithValue }) => {
    try {
      const response = await api.post('/automation/documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload document');
    }
  }
);

export const processDocument = createAsyncThunk(
  'automation/processDocument',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/automation/documents/${docId}/process`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to process document');
    }
  }
);

// Knowledge Sources
export const fetchKnowledgeSources = createAsyncThunk(
  'automation/fetchKnowledgeSources',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/knowledge-sources');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch knowledge sources');
    }
  }
);

export const createKnowledgeSource = createAsyncThunk(
  'automation/createKnowledgeSource',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/automation/knowledge-sources', data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create knowledge source');
    }
  }
);

// AI Query
export const queryKnowledgeBase = createAsyncThunk(
  'automation/queryKnowledgeBase',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/automation/ai/query', data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to query knowledge base');
    }
  }
);

// Alerts
export const fetchAlerts = createAsyncThunk(
  'automation/fetchAlerts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/automation/alerts');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch alerts');
    }
  }
);

const initialState = {
  // AI Action Center
  actionCenter: null,
  actionCenterLoading: false,
  
  // Approvals
  approvals: [],
  approvalsLoading: false,
  
  // Notifications
  notifications: [],
  notificationsLoading: false,
  unreadCount: 0,
  
  // Email Drafts
  emailDrafts: [],
  emailDraftsLoading: false,
  
  // Automation Events
  events: [],
  eventsLoading: false,
  
  // Documents
  documents: [],
  documentsLoading: false,
  
  // Knowledge Sources
  knowledgeSources: [],
  knowledgeSourcesLoading: false,
  
  // AI Query
  aiAnswer: null,
  aiQueryLoading: false,
  
  // Alerts
  alerts: [],
  alertsLoading: false,
  
  // General
  error: null,
};

const automationSlice = createSlice({
  name: 'automation',
  initialState,
  reducers: {
    clearAIAnswer: (state) => {
      state.aiAnswer = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // AI Action Center
      .addCase(fetchAIActionCenter.pending, (state) => {
        state.actionCenterLoading = true;
        state.error = null;
      })
      .addCase(fetchAIActionCenter.fulfilled, (state, action) => {
        state.actionCenterLoading = false;
        state.actionCenter = action.payload;
      })
      .addCase(fetchAIActionCenter.rejected, (state, action) => {
        state.actionCenterLoading = false;
        state.error = action.payload;
      })
      
      // Approvals
      .addCase(fetchApprovals.pending, (state) => {
        state.approvalsLoading = true;
        state.error = null;
      })
      .addCase(fetchApprovals.fulfilled, (state, action) => {
        state.approvalsLoading = false;
        state.approvals = action.payload;
      })
      .addCase(fetchApprovals.rejected, (state, action) => {
        state.approvalsLoading = false;
        state.error = action.payload;
      })
      .addCase(approveRequest.fulfilled, (state, action) => {
        const index = state.approvals.findIndex(a => a.id === action.payload.id);
        if (index !== -1) {
          state.approvals[index] = action.payload;
        }
      })
      .addCase(rejectRequest.fulfilled, (state, action) => {
        const index = state.approvals.findIndex(a => a.id === action.payload.id);
        if (index !== -1) {
          state.approvals[index] = action.payload;
        }
      })
      
      // Notifications
      .addCase(fetchNotifications.pending, (state) => {
        state.notificationsLoading = true;
        state.error = null;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.notificationsLoading = false;
        state.notifications = action.payload;
        state.unreadCount = action.payload.filter(n => !n.read).length;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.notificationsLoading = false;
        state.error = action.payload;
      })
      .addCase(markNotificationRead.fulfilled, (state, action) => {
        const index = state.notifications.findIndex(n => n.id === action.payload.id);
        if (index !== -1) {
          state.notifications[index] = action.payload;
          state.unreadCount = state.notifications.filter(n => !n.read).length;
        }
      })
      .addCase(markAllNotificationsRead.fulfilled, (state) => {
        state.notifications = state.notifications.map(n => ({ ...n, read: true, read_at: new Date().toISOString() }));
        state.unreadCount = 0;
      })
      
      // Email Drafts
      .addCase(fetchEmailDrafts.pending, (state) => {
        state.emailDraftsLoading = true;
        state.error = null;
      })
      .addCase(fetchEmailDrafts.fulfilled, (state, action) => {
        state.emailDraftsLoading = false;
        state.emailDrafts = action.payload;
      })
      .addCase(fetchEmailDrafts.rejected, (state, action) => {
        state.emailDraftsLoading = false;
        state.error = action.payload;
      })
      .addCase(sendEmailDraft.fulfilled, (state, action) => {
        const index = state.emailDrafts.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.emailDrafts[index] = { ...state.emailDrafts[index], status: 'sent', sent_at: new Date().toISOString() };
        }
      })
      
      // Automation Events
      .addCase(fetchAutomationEvents.pending, (state) => {
        state.eventsLoading = true;
        state.error = null;
      })
      .addCase(fetchAutomationEvents.fulfilled, (state, action) => {
        state.eventsLoading = false;
        state.events = action.payload;
      })
      .addCase(fetchAutomationEvents.rejected, (state, action) => {
        state.eventsLoading = false;
        state.error = action.payload;
      })
      .addCase(processAutomationEvents.fulfilled, (state) => {
        // Events will be refetched
      })
      
      // Documents
      .addCase(fetchDocuments.pending, (state) => {
        state.documentsLoading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.documentsLoading = false;
        state.documents = action.payload;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.documentsLoading = false;
        state.error = action.payload;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.documents.unshift(action.payload);
      })
      .addCase(processDocument.fulfilled, (state, action) => {
        const index = state.documents.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.documents[index] = action.payload;
        }
      })
      
      // Knowledge Sources
      .addCase(fetchKnowledgeSources.pending, (state) => {
        state.knowledgeSourcesLoading = true;
        state.error = null;
      })
      .addCase(fetchKnowledgeSources.fulfilled, (state, action) => {
        state.knowledgeSourcesLoading = false;
        state.knowledgeSources = action.payload;
      })
      .addCase(fetchKnowledgeSources.rejected, (state, action) => {
        state.knowledgeSourcesLoading = false;
        state.error = action.payload;
      })
      .addCase(createKnowledgeSource.fulfilled, (state, action) => {
        state.knowledgeSources.push(action.payload);
      })
      
      // AI Query
      .addCase(queryKnowledgeBase.pending, (state) => {
        state.aiQueryLoading = true;
        state.error = null;
      })
      .addCase(queryKnowledgeBase.fulfilled, (state, action) => {
        state.aiQueryLoading = false;
        state.aiAnswer = action.payload;
      })
      .addCase(queryKnowledgeBase.rejected, (state, action) => {
        state.aiQueryLoading = false;
        state.error = action.payload;
      })
      
      // Alerts
      .addCase(fetchAlerts.pending, (state) => {
        state.alertsLoading = true;
        state.error = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.alertsLoading = false;
        state.alerts = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.alertsLoading = false;
        state.error = action.payload;
      });
  },
});

export const { clearAIAnswer, clearError } = automationSlice.actions;
export default automationSlice.reducer;