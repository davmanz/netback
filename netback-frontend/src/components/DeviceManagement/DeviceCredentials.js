import { Grid, FormControl, InputLabel, Select, MenuItem, TextField } from "@mui/material";

const DeviceCredentials = ({ formData, onChange, vaultCredentials }) => (
  <Grid container spacing={2} sx={{ mt: 1 }}>
    <Grid item xs={12}>
      <FormControl fullWidth>
        <InputLabel>Tipo de Credencial</InputLabel>
        <Select name="credentialType" value={formData.credentialType} onChange={onChange} required>
          <MenuItem value="vault">Usar Vault</MenuItem>
          <MenuItem value="personalizado">Usuario/Contraseña</MenuItem>
        </Select>
      </FormControl>
    </Grid>

    {formData.credentialType === "vault" && (
      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Credencial Vault</InputLabel>
          <Select name="vaultCredential" value={formData.vaultCredential} onChange={onChange} required>
            {vaultCredentials.map((v) => (
              <MenuItem key={v.id} value={v.id}>{v.nick}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
    )}

    {formData.credentialType === "personalizado" && (
      <>
        <Grid item xs={6}>
          <TextField fullWidth name="username" label="Usuario" value={formData.username} onChange={onChange} required />
        </Grid>
        <Grid item xs={6}>
          <TextField fullWidth type="password" name="password" label="Contraseña" value={formData.password} onChange={onChange} required />
        </Grid>
      </>
    )}
  </Grid>
);

export default DeviceCredentials;
