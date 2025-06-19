import { Link } from "react-router-dom";
import { IconButton, Box, Button, Tooltip } from "@mui/material";
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  ExitToApp as LogoutIcon,
} from "@mui/icons-material";

const Sidebar = ({ menuOpen, setMenuOpen, darkMode, toggleDarkMode, isSmallScreen, handleLogout }) => {
  const role = localStorage.getItem("role");

  const linkStyle = {
    color: "white",
    textDecoration: "none",
    display: "flex",
    alignItems: "center",
    padding: "12px 16px",
    margin: "4px 0",
    borderRadius: "8px",
    transition: "all 0.2s ease",
  };

  const iconContainerStyle = {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "32px",
    height: "32px",
    marginRight: "12px",
    backgroundColor: "rgba(255,255,255,0.1)",
    borderRadius: "8px",
  };

  const divider = (
    <Box
      sx={{
        height: "1px",
        margin: "12px 0",
        background: "linear-gradient(to right, rgba(255,255,255,0.1), rgba(255,255,255,0.05))",
      }}
    />
  );

  const renderLink = (to, icon, label, condition = true) => {
    if (!condition) return null;

    const content = (
      <Box
        component={Link}
        to={to}
        sx={{
          ...linkStyle,
          "&:hover": {
            backgroundColor: "rgba(255,255,255,0.1)",
            transform: "translateX(4px)",
          },
        }}
      >
        <span style={iconContainerStyle}>{icon}</span>
        {!isSmallScreen && menuOpen && label}
      </Box>
    );

    return isSmallScreen && !menuOpen ? (
      <Tooltip title={label} placement="right">{content}</Tooltip>
    ) : (
      content
    );
  };

  return (
    <Box
      component="nav"
      sx={{
        width: isSmallScreen ? "60px" : menuOpen ? "250px" : "60px",
        background: darkMode
          ? "linear-gradient(180deg, #1a1a1a 0%, #121212 100%)"
          : "linear-gradient(180deg, #424242 0%, #333333 100%)",
        color: "white",
        minHeight: "100vh",
        padding: "20px",
        transition: "width 0.3s ease",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <Box>
        {!isSmallScreen && (
          <IconButton
            onClick={() => setMenuOpen(!menuOpen)}
            sx={{
              color: "white",
              backgroundColor: "rgba(255,255,255,0.2)",
              borderRadius: "50%",
              padding: "5px",
              marginBottom: "20px",
            }}
          >
            {menuOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
        )}

        <IconButton
          onClick={toggleDarkMode}
          sx={{
            color: "white",
            backgroundColor: "rgba(255,255,255,0.2)",
            borderRadius: "50%",
            padding: "5px",
            marginBottom: "20px",
          }}
        >
          {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
        </IconButton>

        {renderLink("/dashboard", "📊", "Dashboard")}
        {renderLink("/users", "👤", "Gestión de Usuarios", role !== "viewer")}
        {renderLink("/vault-credentials", "🔑", "Credenciales Vault", role !== "viewer")}
        {renderLink("/manage-devices", "🛠️", "Gestión de Equipos")}
        {renderLink("/compare-backups", "🔍", "Comparar Backups")}
        {renderLink("/sites-and-areas", "🌍", "Sitios y Áreas", role !== "viewer")}
        {renderLink("/backup-schedule", "⏳", "Configurar Respaldo", role === "admin")}
        {renderLink("/zabbix-status", "🧪", "Diagnóstico Zabbix")}
        {renderLink("/bulk-import", "📥", "Importación Masiva", role === "admin")}
        {renderLink("/classification-rules", "🧠", "Reglas de Clasificación", role === "admin")}

        {divider}
      </Box>

      <Box sx={{ padding: "10px 0", textAlign: "center" }}>
        <Button
          variant="contained"
          color="error"
          fullWidth
          onClick={handleLogout}
          startIcon={<LogoutIcon />}
          sx={{
            transition: "all 0.3s ease",
            display: "flex",
            justifyContent: "center",
            width: menuOpen ? "80%" : "50px",
            minWidth: "50px",
            height: "40px",
            fontSize: menuOpen ? "14px" : "0",
            margin: "auto",
            borderRadius: "12px",
            boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
            "&:hover": {
              transform: "translateY(-2px)",
              boxShadow: "0 6px 8px rgba(0,0,0,0.2)",
            },
          }}
        >
          {!isSmallScreen && menuOpen && "Cerrar Sesión"}
        </Button>
      </Box>
    </Box>
  );
};

export default Sidebar;
