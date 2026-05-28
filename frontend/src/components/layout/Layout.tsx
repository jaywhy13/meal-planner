import React, { ReactNode } from 'react';
import { Box } from '@mui/material';
import { semantic } from '../../theme/tokens';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps): React.ReactElement => (
  <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: semantic.bgApp }}>
    <Sidebar />
    <Box component="main" sx={{ flex: 1, minWidth: 0 }}>
      {children}
    </Box>
  </Box>
);

export default Layout;
