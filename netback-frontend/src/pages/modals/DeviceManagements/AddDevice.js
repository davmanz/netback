import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  createDevice,
  getVaultCredentials,
  getCountries,
  getSites,
  getAreas,
  getManufacturers,
  getDeviceTypes,
} from "../../../api"
import {
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Box,
  CircularProgress,
  Typography,
} from "@mui/material";

const AddDevice = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [countries, setCountries] = useState([]);
  const [sites, setSites] = useState([]);
  const [areas, setAreas] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [deviceTypes, setDeviceTypes] = useState([]);
  const [vaultCredentials, setVaultCredentials] = useState([]);

  const [credentialType, setCredentialType] = useState("");

  const [formData, setFormData] = useState({
    hostname: "",
    ipAddress: "",
    deviceType: "",
    manufacturer: "",
    model: "",
    country: "",
    site: "",
    area: "",
    username: "",
    password: "",
    vaultCredential: "",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setCountries(await getCountries());
        setManufacturers(await getManufacturers());
        setDeviceTypes(await getDeviceTypes());

        const credentials = await getVaultCredentials();
        setVaultCredentials(credentials);

        setLoading(false);
      } catch (error) {
        setErrorMessage("Error al cargar datos.");
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (formData.country) {
      getSites(formData.country).then((data) => setSites(data || []));
    } else {
      setSites([]);
      setAreas([]);
      setFormData((prev) => ({ ...prev, site: "", area: "" }));
    }
  }, [formData.country]);

  useEffect(() => {
    if (formData.site) {
      getAreas(formData.site).then((data) => setAreas(data || []));
    } else {
      setAreas([]);
      setFormData((prev) => ({ ...prev, area: "" }));
    }
  }, [formData.site]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === "credentialType") {
      setCredentialType(value);
      setFormData({
        ...formData,
        username: value === "personalizado" ? "" : formData.username,
        password: value === "personalizado" ? "" : formData.password,
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isSaving) return; // Evita envíos dobles

    setIsSaving(true);

    if (
      !formData.hostname ||
      !formData.ipAddress ||
      !formData.deviceType ||
      !formData.manufacturer ||
      !formData.model ||
      !formData.country ||
      !formData.site ||
      !formData.area
    ) {
      setErrorMessage("Todos los campos son obligatorios.");
      setIsSaving(false);
      return;
    }

    if (credentialType === "vault" && !formData.vaultCredential) {
      setErrorMessage("Debes seleccionar una credencial del Vault.");
      setIsSaving(false);
      return;
    }

    if (credentialType === "personalizado" && (!formData.username || !formData.password)) {
      setErrorMessage("Debes ingresar un usuario y contraseña.");
      setIsSaving(false);
      return;
    }

    try {
      const result = await createDevice(formData);

      if (result) {
        setSuccessMessage("Dispositivo agregado correctamente.");
        setTimeout(() => navigate("/dashboard"), 2000);
      } else {
        setErrorMessage("Error al agregar el dispositivo.");
      }
    } catch (error) {
      setErrorMessage("Error en la conexión con el servidor.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, margin: "auto", padding: 4, boxShadow: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom>
        Agregar Nuevo Dispositivo
      </Typography>
       {errorMessage && (
        <Typography color="error" sx={{ mb: 2 }}>
          {errorMessage}
        </Typography>
      )}

      {successMessage && (
        <Typography color="success.main" sx={{ mb: 2 }}>
          {successMessage}
        </Typography>
      )}

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "200px" }}>
          <CircularProgress />
        </Box>
      ) : (
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            {/* Fila 1: HOSTNAME ----------- IP Address */}
            <Grid item xs={6}>
              <TextField fullWidth label="Hostname" name="hostname" value={formData.hostname} onChange={handleChange} required />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="IP Address" name="ipAddress" value={formData.ipAddress} onChange={handleChange} required />
            </Grid>

            {/* Fila 2: Fabricante ----------- Tipo de Dispositivo */}
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Fabricante</InputLabel>
                <Select name="manufacturer" value={formData.manufacturer} onChange={handleChange} required>
                  {manufacturers.map((m) => (
                    <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Dispositivo</InputLabel>
                <Select name="deviceType" value={formData.deviceType} onChange={handleChange} required>
                  {deviceTypes.map((d) => (
                    <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Fila 3: Modelo */}
            <Grid item xs={12}>
              <TextField fullWidth label="Modelo" name="model" value={formData.model} onChange={handleChange} required />
            </Grid>

            {/* Fila 4: País ------------ Sitio */}
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>País</InputLabel>
                <Select name="country" value={formData.country} onChange={handleChange} required>
                  {countries.map((country) => (
                    <MenuItem key={country.id} value={country.id}>{country.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Sitio</InputLabel>
                <Select name="site" value={formData.site} onChange={handleChange} required>
                  {sites.map((site) => (
                    <MenuItem key={site.id} value={site.id}>{site.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Fila 5: Área --------- Tipo de Credencial */}
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Área</InputLabel>
                <Select name="area" value={formData.area} onChange={handleChange} required>
                  {areas.map((area) => (
                    <MenuItem key={area.id} value={area.id}>{area.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Credencial</InputLabel>
                <Select name="credentialType" value={credentialType} onChange={handleChange} required>
                  <MenuItem value="vault">Usar credencial del Vault</MenuItem>
                  <MenuItem value="personalizado">Usar credenciales personalizadas</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Credenciales del Vault o personalizadas */}
            {credentialType === "vault" && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel id="vault-credential-label">Seleccionar Credencial del Vault</InputLabel>
                  <Select
                    labelId="vault-credential-label"
                    name="vaultCredential"
                    value={formData.vaultCredential}
                    onChange={handleChange}
                    required
                  >
                    {vaultCredentials.map((cred) => (
                      <MenuItem key={cred.id} value={cred.id}>
                        {cred.nick} {/* Usa cred.nick directamente */}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}

            {credentialType === "personalizado" && (
              <>
                <Grid item xs={6}>
                  <TextField fullWidth label="Usuario" name="username" value={formData.username} onChange={handleChange} required />
                </Grid>
                <Grid item xs={6}>
                  <TextField fullWidth type="password" label="Contraseña" name="password" value={formData.password} onChange={handleChange} required />
                </Grid>
              </>
            )}

            {/* Botón de envío */}
            <Grid item xs={12}>
              <Button type="submit" fullWidth variant="contained" disabled={isSaving}>
                {isSaving ? <CircularProgress size={24} /> : "Agregar Dispositivo"}
              </Button>
            </Grid>
          </Grid>
        </form>
      )}
    </Box>
  );
};

export default AddDevice;