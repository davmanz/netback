import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";
import {
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Snackbar,
  Alert,
  Box,
  InputAdornment,
  IconButton,
} from "@mui/material";
import { Visibility, VisibilityOff, Router, Security } from "@mui/icons-material";

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    padding: 2
  },
  card: {
    width: { xs: "90%", sm: 400 },
    maxWidth: 400,
    borderRadius: 3,
    boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
    backdropFilter: "blur(10px)",
    background: "rgba(255,255,255,0.95)"
  },
  cardContent: {
    padding: 4,
    "&:last-child": {
      paddingBottom: 4
    }
  },
  header: {
    textAlign: "center",
    marginBottom: 3
  },
  icon: {
    fontSize: 48,
    color: "#667eea",
    marginBottom: 1
  },
  title: {
    fontWeight: 600,
    color: "#2c3e50",
    marginBottom: 0.5
  },
  subtitle: {
    color: "#7f8c8d",
    fontSize: "0.9rem"
  },
  textField: {
    "& .MuiOutlinedInput-root": {
      borderRadius: 2,
      "&:hover .MuiOutlinedInput-notchedOutline": {
        borderColor: "#667eea"
      },
      "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
        borderColor: "#667eea"
      }
    }
  },
  button: {
    marginTop: 3,
    height: 48,
    borderRadius: 2,
    fontSize: "1rem",
    fontWeight: 600,
    background: "linear-gradient(45deg, #667eea 30%, #764ba2 90%)",
    "&:hover": {
      background: "linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)",
      boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)"
    },
    "&:disabled": {
      background: "#e0e0e0"
    }
  },
  form: {
    width: "100%"
  }
};

const Login = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [usernameError, setUsernameError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const validateUsername = (value) => {
    const isEmail = value.includes("@");
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (isEmail && !emailRegex.test(value)) {
      return "Formato de correo inválido";
    }
    return "";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (name === "username") {
      const msg = validateUsername(value);
      setUsernameError(msg);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const usernameErr = validateUsername(formData.username);
    if (usernameErr) {
      setUsernameError(usernameErr);
      setLoading(false);
      return;
    }

    try {
      const data = await login(formData.username, formData.password);
      if (data && data.access) {
        sessionStorage.setItem("token", data.access);
        navigate("/dashboard");
      } else {
        throw new Error("Credenciales inválidas");
      }
    } catch (err) {
      setError("Usuario o contraseña incorrectos");
      setOpenSnackbar(true);
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box sx={styles.container}>
      <Card sx={styles.card}>
        <CardContent sx={styles.cardContent}>
          <Box sx={styles.header}>
            <Router sx={styles.icon} />
            <Typography variant="h4" sx={styles.title}>
              NetBackup Pro
            </Typography>
            <Typography variant="body2" sx={styles.subtitle}>
              Sistema de Respaldo de Equipos de Red
            </Typography>
          </Box>

          <Box component="form" onSubmit={handleLogin} sx={styles.form}>
            <TextField
              fullWidth
              label="Usuario"
              name="username"
              variant="outlined"
              margin="normal"
              value={formData.username}
              onChange={handleChange}
              required
              error={Boolean(usernameError)}
              helperText={usernameError}
              autoComplete="username"
              sx={styles.textField}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Security color="action" />
                  </InputAdornment>
                ),
              }}
            />
            
            <TextField
              fullWidth
              label="Contraseña"
              name="password"
              type={showPassword ? "text" : "password"}
              variant="outlined"
              margin="normal"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
              sx={styles.textField}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={togglePasswordVisibility}
                      edge="end"
                      size="small"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <Button
              type="submit"
              variant="contained"
              fullWidth
              disabled={loading || Boolean(usernameError)}
              sx={styles.button}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "Iniciar Sesión"
              )}
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Snackbar
        open={openSnackbar}
        autoHideDuration={4000}
        onClose={() => setOpenSnackbar(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          severity="error"
          onClose={() => setOpenSnackbar(false)}
          variant="filled"
          sx={{ borderRadius: 2 }}
        >
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Login;