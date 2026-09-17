import { configureStore } from '@reduxjs/toolkit';
import complaintReducer from '../features/complaint/complaintSlice';
import intakeReducer from '../features/intake/intakeSlice';

export const store = configureStore({
  reducer: {
    complaint: complaintReducer,
    intake: intakeReducer,
  },
});
