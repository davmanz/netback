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
} from "@mui/material";

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f5f5f5"
  },
  card: {
    width: 350,
    padding: 3,
    textAlign: "center",
    boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
  },
  button: {
    marginTop: 2,
    height: 42
  }
};

const Login = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [usernameError, setUsernameError] = useState("");
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

  return (
    <div style={styles.container}>
      <Card sx={styles.card}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Iniciar Sesión
          </Typography>
          <form onSubmit={handleLogin}>
            <TextField
              fullWidth
              label="Usuario o Correo"
              name="username"
              variant="outlined"
              margin="normal"
              value={formData.username}
              onChange={handleChange}
              required
              error={Boolean(usernameError)}
              helperText={usernameError}
              autoComplete="username"
            />
            <TextField
              fullWidth
              label="Contraseña"
              name="password"
              type="password"
              variant="outlined"
              margin="normal"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={loading}
              sx={styles.button}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : "Iniciar Sesión"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Snackbar
        open={openSnackbar}
        autoHideDuration={3000}
        onClose={() => setOpenSnackbar(false)}
      >
        <Alert
          severity="error"
          onClose={() => setOpenSnackbar(false)}
          variant="filled"
        >
          {error}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default Login;
