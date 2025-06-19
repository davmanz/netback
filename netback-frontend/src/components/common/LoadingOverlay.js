import { Box, CircularProgress } from "@mui/material";

const LoadingOverlay = () => (
  <Box sx={{ 
    position: 'absolute', 
    top: 0, left: 0, right: 0, bottom: 0, 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    backgroundColor: 'rgba(255, 255, 255, 0.7)',
    zIndex: 999 
  }}>
    <CircularProgress />
  </Box>
);

export default LoadingOverlay;
