import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { logout } from "../api";
import { 
  Box,  CssBaseline,  ThemeProvider, 
  createTheme, useMediaQuery, Fade, Container
} from "@mui/material";
import Sidebar from "../components/Sidebar";
import useIsSmallScreen from "../hooks/useIsSmallScreen";

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const isSmallScreen = useIsSmallScreen();
  const isMobile = useMediaQuery('(max-width:768px)');
  const isTablet = useMediaQuery('(max-width:1024px)');
  
  const [menuOpen, setMenuOpen] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth > 768;
    }
    return true;
  });

  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme) {
        return savedTheme === "dark";
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width <= 768) {
        setMenuOpen(false); // Cerrar menú en móvil
      } else if (width > 1024) {
        setMenuOpen(true); // Abrir menú en desktop
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode((prev) => {
      const newTheme = !prev;
      localStorage.setItem("theme", newTheme ? "dark" : "light");
      return newTheme;
    });
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const theme = useMemo(() => createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: { 
        main: "#1976d2",
        light: "#42a5f5",
        dark: "#1565c0"
      },
      secondary: { 
        main: "#ff9800",
        light: "#ffb74d",
        dark: "#f57c00"
      },
      background: {
        default: darkMode ? "#0a0a0a" : "#fafafa",
        paper: darkMode ? "#1e1e1e" : "#ffffff"
      },
      text: {
        primary: darkMode ? "#ffffff" : "#212121",
        secondary: darkMode ? "#b0b0b0" : "#757575"
      }
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h1: { fontWeight: 300 },
      h2: { fontWeight: 400 },
      h3: { fontWeight: 500 },
      body1: { lineHeight: 1.6 },
      body2: { lineHeight: 1.5 }
    },
    components: {
      MuiButton: { 
        styleOverrides: { 
          root: { 
            textTransform: "none",
            borderRadius: 8,
            fontWeight: 500,
            padding: isMobile ? '8px 16px' : '10px 20px'
          } 
        } 
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: darkMode ? '1px solid #333' : '1px solid #e0e0e0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }
        }
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
          }
        }
      }
    },
    breakpoints: {
      values: {
        xs: 0,
        sm: 600,
        md: 768,
        lg: 1024,
        xl: 1200,
      },
    },
  }), [darkMode, isMobile]);

  const getContentWidth = () => {
    if (isMobile) return '100%';
    if (isTablet) return menuOpen ? 'calc(100% - 240px)' : '100%';
    return menuOpen ? 'calc(100% - 280px)' : 'calc(100% - 80px)';
  };

  const getContentPadding = () => {
    if (isMobile) return '16px';
    if (isTablet) return '20px';
    return menuOpen ? '24px 32px' : '24px';
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        display: "flex", 
        minHeight: "100vh",
        backgroundColor: 'background.default'
      }}>
        <Sidebar
          menuOpen={menuOpen}
          setMenuOpen={setMenuOpen}
          darkMode={darkMode}
          toggleDarkMode={toggleDarkMode}
          isSmallScreen={isSmallScreen}
          isMobile={isMobile}
          isTablet={isTablet}
          handleLogout={handleLogout}
        />
        
        {isMobile && menuOpen && (
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 1200,
              transition: 'opacity 0.3s ease'
            }}
            onClick={() => setMenuOpen(false)}
          />
        )}

        <Box 
          component="main"
          sx={{ 
            flexGrow: 1,
            width: getContentWidth(),
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
            overflow: 'hidden'
          }}
        >
          <Fade in timeout={300}>
            <Container 
              maxWidth={false}
              sx={{ 
                padding: getContentPadding(),
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'auto',
                minHeight: 'calc(100vh - 32px)'
              }}
            >
              {children}
            </Container>
          </Fade>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default Layout;