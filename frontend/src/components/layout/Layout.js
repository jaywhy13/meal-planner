import React from 'react';
import { Box } from '@mui/material';
import { semantic } from '../../theme/tokens';
import Sidebar from './Sidebar';

const Layout = ({ children }) => (
  <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: semantic.bgApp }}>
    <Sidebar />
    <Box component="main" sx={{ flex: 1, minWidth: 0 }}>
      {children}
    </Box>
  </Box>
);

export default Layout;
