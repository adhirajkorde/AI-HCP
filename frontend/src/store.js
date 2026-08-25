import { configureStore } from '@reduxjs/toolkit';
import authReducer from './features/authSlice';
import hcpReducer from './features/hcpSlice';
import interactionReducer from './features/interactionSlice';
import followupReducer from './features/followupSlice';
import analyticsReducer from './features/analyticsSlice';
import automationReducer from './features/automationSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    hcps: hcpReducer,
    interactions: interactionReducer,
    followups: followupReducer,
    analytics: analyticsReducer,
    automation: automationReducer,
  },
});
export default store;
