import { useEffect, useState } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, CircularProgress, Snackbar, Alert
} from "@mui/material";

import {
  getCountries, getSites, getAreas,
  getManufacturers, getDeviceTypes, getVaultCredentials, createDevice
} from "../../api";

import DeviceBasicInfo from "./DeviceBasicInfo";
import DeviceHardwareInfo from "./DeviceHardwareInfo";
import DeviceLocationInfo from "./DeviceLocationInfo";
import DeviceCredentials from "./DeviceCredentials";
import StepperNavigation from "./StepperNavigation";

const AddDeviceModal = ({ open, onClose, onDeviceAdded }) => {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    hostname: "", ipAddress: "", manufacturer: "", deviceType: "", model: "",
    country: "", site: "", area: "", credentialType: "", username: "", password: "", vaultCredential: ""
  });

  const [countries, setCountries] = useState([]);
  const [sites, setSites] = useState([]);
  const [areas, setAreas] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [deviceTypes, setDeviceTypes] = useState([]);
  const [vaultCredentials, setVaultCredentials] = useState([]);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (open) {
      setLoading(true);
      Promise.all([
        getCountries(), getManufacturers(), getDeviceTypes(), getVaultCredentials()
      ]).then(([c, m, d, v]) => {
        setCountries(c);
        setManufacturers(m);
        setDeviceTypes(d);
        setVaultCredentials(v);
        setLoading(false);
      });
    }
  }, [open]);

  useEffect(() => {
    if (formData.country) {
      getSites(formData.country).then(setSites);
    } else {
      setSites([]);
    }
    setFormData(prev => ({ ...prev, site: "", area: "" }));
  }, [formData.country]);

  useEffect(() => {
    if (formData.site) {
      getAreas(formData.site, formData.country).then(setAreas);
    } else {
      setAreas([]);
    }
    setFormData(prev => ({ ...prev, area: "" }));
  }, [formData.site, formData.country]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "credentialType") {
      setFormData(prev => ({
        ...prev,
        credentialType: value,
        username: value === "personalizado" ? "" : prev.username,
        password: value === "personalizado" ? "" : prev.password,
        vaultCredential: value === "vault" ? prev.vaultCredential : ""
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError("");

    if (!formData.hostname || !formData.ipAddress || !formData.deviceType || !formData.manufacturer || !formData.model ||
        !formData.country || !formData.site || !formData.area) {
      setError("Completa todos los campos obligatorios.");
      setSubmitting(false);
      return;
    }

    if (formData.credentialType === "vault" && !formData.vaultCredential) {
      setError("Selecciona una credencial del Vault.");
      setSubmitting(false);
      return;
    }

    if (formData.credentialType === "personalizado" && (!formData.username || !formData.password)) {
      setError("Ingresa usuario y contraseña.");
      setSubmitting(false);
      return;
    }

    const result = await createDevice(formData);
    setSubmitting(false);

    if (result) {
      setSuccess(true);
      onDeviceAdded?.();
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 1500);
    } else {
      setError("Error al crear el dispositivo.");
    }
  };

  const steps = [
    { label: "Información Básica", content: <DeviceBasicInfo formData={formData} onChange={handleChange} /> },
    { label: "Hardware", content: <DeviceHardwareInfo formData={formData} onChange={handleChange} manufacturers={manufacturers} deviceTypes={deviceTypes} /> },
    { label: "Ubicación", content: <DeviceLocationInfo formData={formData} onChange={handleChange} countries={countries} sites={sites} areas={areas} /> },
    { label: "Credenciales", content: <DeviceCredentials formData={formData} onChange={handleChange} vaultCredentials={vaultCredentials} /> },
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Agregar Dispositivo</DialogTitle>
      <DialogContent>
        {loading ? <CircularProgress /> : steps[step].content}
      </DialogContent>

      <DialogActions sx={{ justifyContent: "space-between", px: 3 }}>
        <StepperNavigation step={step} steps={steps} setStep={setStep} onSubmit={handleSubmit} loading={submitting} />
        <Button onClick={onClose}>Cancelar</Button>
      </DialogActions>

      <Snackbar open={!!error} autoHideDuration={4000} onClose={() => setError("")}>
        <Alert severity="error" onClose={() => setError("")}>{error}</Alert>
      </Snackbar>

      <Snackbar open={success} autoHideDuration={2000} onClose={() => setSuccess(false)}>
        <Alert severity="success">Dispositivo creado</Alert>
      </Snackbar>
    </Dialog>
  );
};

export default AddDeviceModal;
