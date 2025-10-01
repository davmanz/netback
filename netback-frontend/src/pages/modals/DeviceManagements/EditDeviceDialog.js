import { useState, useEffect, useMemo, useCallback } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button,
  Snackbar, Alert, Select, MenuItem, FormControl, InputLabel, CircularProgress, Typography,Grid
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import {
  updateDevice, getDeviceById, getVaultCredentials, getCountries, getSites,
  getAreas, getManufacturers, getDeviceTypes
} from "../../../api";

const EditDeviceDialog = ({ open, onClose, deviceId, onDeviceUpdated }) => {
  const [deviceData, setDeviceData] = useState({});
  const [changedFields, setChangedFields] = useState({});
  const [enabledFields, setEnabledFields] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });
  const [error, setError] = useState("");
  const [countries, setCountries] = useState([]);
  const [sites, setSites] = useState([]);
  const [areas, setAreas] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [deviceTypes, setDeviceTypes] = useState([]);
  const [vaultCredentials, setVaultCredentials] = useState([]);
  // Agregar nuevo estado para manejar la edición de ubicación
  const [locationEditing, setLocationEditing] = useState(false);
  // Agregar al inicio del componente, junto a los otros estados
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  // Primero agregamos el nuevo estado para el control de edición de credenciales
  const [credentialsEditing, setCredentialsEditing] = useState(false);

  const validationRules = {
    hostname: (value) => value.trim() ? null : "El hostname es obligatorio",
    ipAddress: (value) => /^(\d{1,3}\.){3}\d{1,3}$/.test(value) ? null : "Formato IP inválido",
  };

  const validateField = (name, value) => validationRules[name]?.(value) || null;

  // Modificar el fetchDeviceData para manejar la estructura correcta
  const fetchDeviceData = useCallback(async () => {
    const data = await getDeviceById(deviceId);
    if (data) {
      // Primero obtener el país basado en country_name
      const countries = await getCountries();
      const country = countries.find(c => c.name === data.country_name);
      
      if (country) {
        // Obtener los sitios del país
        const sites = await getSites(country.id);
        const site = sites.find(s => s.name === data.site_name);

        setDeviceData({
          ...data,
          country: country.id,
          site: site?.id || '',
          area: data.area || '',
          credentialType: data.vaultCredential ? "vault" : "personalizado"
        });

        // Actualizar los dropdowns iniciales
        setCountries(countries);
        setSites(sites);
        
        // Si hay un sitio, obtener sus áreas
        if (site) {
          const areas = await getAreas(site.id);
          setAreas(areas);
        }
      }
    }
  }, [deviceId]);

  const fetchDropdowns = async () => {
    const [c, m, t, v] = await Promise.all([
      getCountries(), getManufacturers(), getDeviceTypes(), getVaultCredentials()
    ]);
    setCountries(c); setManufacturers(m); setDeviceTypes(t); setVaultCredentials(v);
  };

  useEffect(() => {
    if (deviceId) {
      fetchDeviceData();
      fetchDropdowns();
    }
  }, [deviceId, fetchDeviceData]);

  useEffect(() => {
    if (deviceData.country) {
      getSites(deviceData.country).then(sites => {
        setSites(sites);
        // Limpiar site y area si cambia el país
        if (!sites.find(s => s.id === deviceData.site)) {
          setDeviceData(prev => ({
            ...prev,
            site: '',
            site_name: '',
            area: '',
            area_name: ''
          }));
        }
      });
    } else {
      setSites([]);
      setDeviceData(prev => ({
        ...prev,
        site: '',
        site_name: '',
        area: '',
        area_name: ''
      }));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deviceData.country]);

  useEffect(() => {
    if (deviceData.site) {
      getAreas(deviceData.site).then(areas => {
        setAreas(areas);
        // Limpiar area si cambia el sitio
        if (!areas.find(a => a.id === deviceData.area)) {
          setDeviceData(prev => ({
            ...prev,
            area: '',
            area_name: ''
          }));
        }
      });
    } else {
      setAreas([]);
      setDeviceData(prev => ({
        ...prev,
        area: '',
        area_name: ''
      }));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deviceData.site]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'country') {
      // Al cambiar el país, resetear site y area
      setDeviceData(prev => ({
        ...prev,
        country: value,
        country_name: countries.find(c => c.id === value)?.name || '',
        site: '',
        site_name: '',
        area: '',
        area_name: ''
      }));
      setChangedFields(prev => ({
        ...prev,
        country: true,
        site: true,
        area: true
      }));
    } else if (name === 'site') {
      // Al cambiar el sitio, resetear solo area
      setDeviceData(prev => ({
        ...prev,
        site: value,
        site_name: sites.find(s => s.id === value)?.name || '',
        area: '',
        area_name: ''
      }));
      setChangedFields(prev => ({
        ...prev,
        site: true,
        area: true
      }));
    } else if (name === 'area') {
      setDeviceData(prev => ({
        ...prev,
        area: value,
        area_name: areas.find(a => a.id === value)?.name || ''
      }));
      setChangedFields(prev => ({
        ...prev,
        area: true
      }));
    } else {
      setDeviceData(prev => ({ ...prev, [name]: value }));
      setChangedFields(prev => ({ ...prev, [name]: true }));
    }
  };

  const handleSave = async () => {
    setError("");

    for (const field in enabledFields) {
      if (enabledFields[field]) {
        const err = validateField(field, deviceData[field]);
        if (err) return setError(err);
      }
    }

    const payload = Object.keys(enabledFields)
      .filter((k) => enabledFields[k] && changedFields[k] && k !== 'credentialType')
      .reduce((acc, k) => ({ ...acc, [k]: deviceData[k] }), {});

    if (Object.keys(payload).length === 0) {
      return setError("No hay cambios para guardar");
    }

    setIsLoading(true);
    const success = await updateDevice(deviceId, payload);
    setIsLoading(false);

    if (success) {
      setSnackbar({ open: true, message: "Dispositivo actualizado correctamente", severity: "success" });
      onDeviceUpdated?.();
      onClose();
    } else {
      setSnackbar({ open: true, message: "Error al actualizar el dispositivo", severity: "error" });
    }
  };

  // Modificar el handleClose
  const handleClose = () => {
    if (Object.values(changedFields).some(Boolean)) {
      setConfirmDialogOpen(true);
    } else {
      onClose();
    }
  };

  const ConfirmDialog = () => (
    <Dialog
      open={confirmDialogOpen}
      onClose={() => setConfirmDialogOpen(false)}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">
        ¿Desea salir sin guardar?
      </DialogTitle>
      <DialogContent>
        <Typography color="text.secondary">
          Hay cambios sin guardar. Si sale ahora, perderá todos los cambios realizados.
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button 
          onClick={() => setConfirmDialogOpen(false)} 
          color="primary"
        >
          Cancelar
        </Button>
        <Button
          onClick={() => {
            setConfirmDialogOpen(false);
            onClose();
          }}
          color="error"
          variant="contained"
          autoFocus
        >
          Salir sin guardar
        </Button>
      </DialogActions>
    </Dialog>
  );

  const memoizedOptions = useMemo(() => ({
    countries: countries.map(c => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>),
    sites: sites.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>),
    areas: areas.map(a => <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>),
    manufacturers: manufacturers.map(m => <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>),
    deviceTypes: deviceTypes.map(d => <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>),
    vaults: vaultCredentials.map(v => <MenuItem key={v.id} value={v.id}>{v.nick}</MenuItem>)
  }), [countries, sites, areas, manufacturers, deviceTypes, vaultCredentials]);

  const EditableField = ({ name, label, value, type = "text", component: Component = TextField, children, ...props }) => {
    const isEnabled = enabledFields[name] || false;

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <Component
          label={label}
          name={name}
          value={value}
          onChange={handleChange}
          disabled={!isEnabled}
          fullWidth
          type={type}
          {...props}
        >
          {children}
        </Component>
        <Button
          size="small"
          variant={isEnabled ? "contained" : "outlined"}
          onClick={() => setEnabledFields((prev) => ({ ...prev, [name]: !isEnabled }))}
          color={isEnabled ? "primary" : "default"}
          sx={{ minWidth: '40px', height: '40px' }}
        >
          <EditIcon fontSize="small" />
        </Button>
      </div>
    );
  };

  // Crear un componente para la sección de ubicación
  const LocationSection = () => {
    return (
      <div style={{ 
        border: '1px solid #e0e0e0', 
        padding: '16px', 
        borderRadius: '4px',
        marginBottom: '16px'
      }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '16px' 
        }}>
          <Typography variant="subtitle1" component="div">
            Ubicación del dispositivo
          </Typography>
          <Button
            size="small"
            variant={locationEditing ? "contained" : "outlined"}
            onClick={() => {
              setLocationEditing(!locationEditing);
              if (locationEditing) {
                const newEnabledFields = { ...enabledFields };
                delete newEnabledFields.country;
                delete newEnabledFields.site;
                delete newEnabledFields.area;
                setEnabledFields(newEnabledFields);
              } else {
                setEnabledFields(prev => ({
                  ...prev,
                  country: true,
                  site: true,
                  area: true
                }));
              }
            }}
            color={locationEditing ? "primary" : "default"}
            sx={{ minWidth: '40px', height: '40px' }}
          >
            <EditIcon fontSize="small" />
          </Button>
        </div>

        <div style={{ display: 'flex', gap: '16px' }}>
          <FormControl sx={{ flex: 1 }}>
            <InputLabel>País</InputLabel>
            <Select
              name="country"
              value={countries.find(c => c.id === deviceData.country) ? deviceData.country : ""}
              onChange={handleChange}
              disabled={!locationEditing}
              label="País"
            >
              {memoizedOptions.countries}
            </Select>
          </FormControl>

          <FormControl sx={{ flex: 1 }}>
            <InputLabel>Sitio</InputLabel>
            <Select
              name="site"
              value={sites.find(s => s.id === deviceData.site) ? deviceData.site : ""}
              onChange={handleChange}
              disabled={!locationEditing || !deviceData.country}
              label="Sitio"
            >
              {memoizedOptions.sites}
            </Select>
          </FormControl>

          <FormControl sx={{ flex: 1 }}>
            <InputLabel>Área</InputLabel>
            <Select
              name="area"
              value={areas.find(a => a.id === deviceData.area) ? deviceData.area : ""}
              onChange={handleChange}
              disabled={!locationEditing || !deviceData.site}
              label="Área"
            >
              {memoizedOptions.areas}
            </Select>
          </FormControl>
        </div>

      </div>
    );
  };

  // Agregar después del LocationSection
  const CredentialsSection = () => {
    return (
      <div style={{ 
        border: '1px solid #e0e0e0', 
        padding: '16px', 
        borderRadius: '4px',
        marginBottom: '16px'
      }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '16px' 
        }}>
          <Typography variant="subtitle1" component="div">
            Credenciales del dispositivo
          </Typography>
          <Button
            size="small"
            variant={credentialsEditing ? "contained" : "outlined"}
            onClick={() => {
              setCredentialsEditing(!credentialsEditing);
              if (credentialsEditing) {
                const newEnabledFields = { ...enabledFields };
                delete newEnabledFields.credentialType;
                delete newEnabledFields.vaultCredential;
                delete newEnabledFields.customUser;
                delete newEnabledFields.customPass;
                setEnabledFields(newEnabledFields);
              } else {
                setEnabledFields(prev => ({
                  ...prev,
                  credentialType: true,
                  vaultCredential: true,
                  customUser: true,
                  customPass: true
                }));
              }
            }}
            color={credentialsEditing ? "primary" : "default"}
            sx={{ minWidth: '40px', height: '40px' }}
          >
            <EditIcon fontSize="small" />
          </Button>
        </div>

        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: '200px' }}>
            <InputLabel>Tipo de Credencial</InputLabel>
            <Select
              name="credentialType"
              value={deviceData.credentialType || ""}
              onChange={handleChange}
              disabled={!credentialsEditing}
              label="Tipo de Credencial"
            >
              <MenuItem value="vault">Usar credencial del Vault</MenuItem>
              <MenuItem value="personalizado">Usar credenciales personalizadas</MenuItem>
            </Select>
          </FormControl>

          {deviceData.credentialType === "vault" && (
            <FormControl sx={{ minWidth: '200px' }}>
              <InputLabel>Credencial Vault</InputLabel>
              <Select
                name="vaultCredential"
                value={vaultCredentials.find(v => v.id === deviceData.vaultCredential) ? deviceData.vaultCredential : ""}
                onChange={handleChange}
                disabled={!credentialsEditing}
                label="Credencial Vault"
              >
                {memoizedOptions.vaults}
              </Select>
            </FormControl>
          )}

          {deviceData.credentialType === "personalizado" && (
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={6}>
                <TextField
                  name="customUser"
                  label="Usuario"
                  value={deviceData.customUser || ""}
                  onChange={handleChange}
                  disabled={!credentialsEditing}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  name="customPass"
                  label="Contraseña"
                  type="password"
                  value={deviceData.customPass || ""}
                  onChange={handleChange}
                  disabled={!credentialsEditing}
                  fullWidth
                />
              </Grid>
            </Grid>
          )}
        </div>
      </div>
    );
  };

  return (
    <>
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>
          Editar Dispositivo
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Habilite los campos que desea modificar usando el botón de edición
          </Typography>
        </DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {isLoading && <CircularProgress sx={{ my: 2 }} />}

          {/* Información básica */}
          <EditableField
            name="hostname"
            label="Hostname *"
            value={deviceData.hostname || ""}
            error={enabledFields.hostname && !deviceData.hostname?.trim()}
            helperText={enabledFields.hostname && !deviceData.hostname?.trim() && "Campo obligatorio"}
          />
          
          <EditableField 
            name="ipAddress" 
            label="Dirección IP" 
            value={deviceData.ipAddress || ""} 
          />

          {/* Información del dispositivo */}
          <EditableField 
            name="deviceType" 
            label="Tipo de Dispositivo" 
            value={deviceData.deviceType || ""} 
            component={Select}
          >
            {memoizedOptions.deviceTypes}
          </EditableField>

          <EditableField 
            name="manufacturer" 
            label="Fabricante" 
            value={deviceData.manufacturer || ""} 
            component={Select}
          >
            {memoizedOptions.manufacturers}
          </EditableField>
          
          <EditableField 
            name="model" 
            label="Modelo" 
            value={deviceData.model || ""} 
          />

          {/* Ubicación */}
          <LocationSection />

          {/* Credenciales */}
          <CredentialsSection />
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} color="secondary">Cancelar</Button>
          <Button onClick={handleSave} color="primary" variant="contained">Guardar Cambios</Button>
        </DialogActions>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={3000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
        </Snackbar>
      </Dialog>
      <ConfirmDialog />
    </>
  );
};

export default EditDeviceDialog;
